import pytest
from shared.ahn import AHNVersion
from shared.ahncutter import AHNCutter
from shared.levees import Levee, LeveeSections


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
    cut.write("tests/testdata/test.tif")

    assert cut.bottom == 481200.0
    assert cut.nrows == 100
    # TODO test if the result matches with the original data
