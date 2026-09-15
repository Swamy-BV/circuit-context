"""Validated editorial guidance and source provenance."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Source(BaseModel):
    """Identify the source edition used for an editorial summary."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str
    publisher: str
    title: str
    url: str = Field(pattern=r"^https://")
    revision: str
    accessed: date
    sha256: str | None = Field(pattern=r"^[a-f0-9]{64}$")
    capture_note: str


class Citation(BaseModel):
    """Locate supporting evidence in one source."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    source_id: str
    locator: str = Field(min_length=1)


class RoutingPattern(BaseModel):
    """Describe a caller-selected topology without coordinates or CAD writes."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    diagram: str = Field(min_length=1)
    placement: list[str] = Field(min_length=1)
    routing: list[str] = Field(min_length=1)
    return_path: list[str] = Field(min_length=1)
    pitfalls: list[str] = Field(min_length=1)


class Guideline(BaseModel):
    """Keep scope and exceptions attached to each retrievable recommendation."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    id: str = Field(pattern=r"^[a-z][a-z0-9-]+$")
    title: str = Field(min_length=1)
    topic: str = Field(pattern=r"^[a-z][a-z0-9-]+$")
    level: Literal["general", "interface", "mechanical"]
    domains: list[Literal["schematic", "pcb", "mechanical"]] = Field(min_length=1)
    interfaces: list[str]
    keywords: list[str] = Field(min_length=1)
    summary: str = Field(min_length=1, max_length=1200)
    applies_to: str = Field(min_length=1)
    required_inputs: list[str] = Field(min_length=1)
    verification: list[str] = Field(min_length=1)
    limitations: str = Field(min_length=1)
    citations: list[Citation] = Field(min_length=1)
    related_ids: list[str] = Field(default_factory=list)
    kind: Literal[
        "principle", "overview", "routing-pattern", "device-note"
    ] = "principle"
    pattern: RoutingPattern | None = None

    @model_validator(mode="after")
    def validate_pattern(self) -> Guideline:
        """Keep detailed topology content exclusive to routing-pattern records."""
        if (self.kind == "routing-pattern") != (self.pattern is not None):
            raise ValueError("only routing-pattern records must have pattern content")
        return self


class Corpus(BaseModel):
    """Reject duplicate identities and dangling citations before indexing."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    version: str
    sources: list[Source] = Field(min_length=1)
    guidelines: list[Guideline] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_references(self) -> Corpus:
        """Require unique IDs and resolvable source references."""
        source_ids = {source.id for source in self.sources}
        if len(source_ids) != len(self.sources):
            raise ValueError("duplicate source ID")
        guideline_ids = {item.id for item in self.guidelines}
        if len(guideline_ids) != len(self.guidelines):
            raise ValueError("duplicate guideline ID")
        for item in self.guidelines:
            if len(set(item.related_ids)) != len(item.related_ids):
                raise ValueError(f"duplicate related guide: {item.id}")
            for related in item.related_ids:
                if related not in guideline_ids or related == item.id:
                    raise ValueError(f"invalid related guide: {item.id} -> {related}")
            if item.level == "interface" and not item.interfaces:
                raise ValueError(f"interface guidance needs a family: {item.id}")
            if any(not name or "|" in name for name in item.interfaces):
                raise ValueError(f"invalid interface family: {item.id}")
            for citation in item.citations:
                if citation.source_id not in source_ids:
                    raise ValueError(f"unknown citation: {citation.source_id}")
        return self
