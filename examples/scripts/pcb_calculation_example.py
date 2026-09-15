"""Reproduce a cited microstrip approximation; this is not a fabrication solver."""

import math


def estimate(er: float, h: float, w: float, t: float) -> float:
    """Evaluate TI SPRABV0 Figure 48 using consistent positive length units."""
    if not all(math.isfinite(v) and v > 0 for v in (er, h, w, t)):
        raise ValueError("Finite positive permittivity and dimensions are required")
    ratio = 5.98 * h / (0.8 * w + t)
    if ratio <= 1:
        raise ValueError("Geometry falls outside this approximation")
    return 87 / math.sqrt(er + 1.41) * math.log(ratio)


def main() -> None:
    """Check source-example rounding, units, and inverse synthesis arithmetic."""
    # Source page 118 says its equation predicts approximately 46 ohms here.
    source = estimate(er=4, h=10, w=20, t=1.4)
    assert 45 < source < 47, source
    mm = estimate(er=4, h=0.254, w=0.508, t=0.03556)
    assert math.isclose(source, mm, abs_tol=1e-10)
    width = (5.98 * 0.254 / math.exp(50 * math.sqrt(4 + 1.41) / 87) - 0.03556) / 0.8
    assert math.isclose(estimate(4, 0.254, width, 0.03556), 50, abs_tol=1e-10)
    for bad in (0, -1, float("nan"), float("inf")):
        try:
            estimate(4, bad, 0.508, 0.03556)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid input accepted")
    print(f"TI source geometry: {source:.3f} ohms; unit conversion verified")
    print(f"Approximate 50-ohm width: {width:.4f} mm")
    print("Arithmetic checked only: no soldermask, coupling or fabrication validation")


if __name__ == "__main__":
    main()
