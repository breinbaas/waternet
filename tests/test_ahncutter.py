import pytest
from shared.ahn import AHNVersion
from shared.ahncutter import AHNCutter
from shared.levees import Levee, LeveeSections

VALID_POINTS_AHN4 = [
    (124999.99, 485685.7, -0.1342),
    (125000, 485685.7, -0.0284),
    (125000.01, 485685.7, -0.0284),
]


def test_cut_points():
    left = round(min(p[0] for p in VALID_POINTS_AHN4)) - 10.0
    right = round(max(p[0] for p in VALID_POINTS_AHN4)) + 10.0
    top = round(max(p[1] for p in VALID_POINTS_AHN4)) + 10.0
    bottom = round(min(p[1] for p in VALID_POINTS_AHN4)) - 10.0

    ahncutter = AHNCutter()
    cut = ahncutter.execute(
        left=left,
        top=top,
        right=right,
        bottom=bottom,
        ahn_version=AHNVersion.AHN4,
    )

    for x, y, z in VALID_POINTS_AHN4:
        assert round(cut.z_at(x, y), 4) == z


def test_cut():
    levee = LeveeSections().get_from_code("A117")[0]

    ahncutter = AHNCutter()
    cut = ahncutter.execute(
        left=120000,
        top=481250,
        right=120100,
        bottom=481200,
        ahn_version=AHNVersion.AHN4,
    )
    cut.write("tests/testdata/output/test.tif")

    assert cut.bottom == 481200.0
    assert cut.nrows == 100

    assert round(cut.z_at(120086.3, 481226.73), 3) == -5.009
