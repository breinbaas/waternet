from shared.tile import Tile
import pytest
import numpy as np


def test_multiply():
    t = Tile.from_filename("tests/testdata/small_area.tif")
    assert t.data[0][0] == pytest.approx(-5.323, 0.001)
    num_nans = np.count_nonzero(np.isnan(t.data))
    t.multiply(3.0)
    assert t.data[0][0] == pytest.approx(-15.969, 0.001)
    # next check if the number of nans did not change
    assert np.count_nonzero(np.isnan(t.data)) == num_nans


def test_divide():
    t = Tile.from_filename("tests/testdata/small_area.tif")
    num_nans = np.count_nonzero(np.isnan(t.data))
    t.divide(2.0)
    assert t.data[0][0] == pytest.approx(-2.661, 0.001)
    assert np.count_nonzero(np.isnan(t.data)) == num_nans


def test_subtract():
    t1 = Tile.from_filename("tests/testdata/small_area.tif")
    t2 = Tile.from_filename("tests/testdata/small_area.tif")
    t1.subtract(t2)
    assert t1.data[0][0] == pytest.approx(0.0, 0.001)


def test_upper_limit():
    t = Tile.from_filename("tests/testdata/small_area.tif")
    num_nans = np.count_nonzero(np.isnan(t.data))
    t.upper_limit(-9.99)
    assert t.data[0][0] == pytest.approx(-9.99)
    assert np.count_nonzero(np.isnan(t.data)) == num_nans


def test_lower_limit():
    t = Tile.from_filename("tests/testdata/small_area.tif")
    num_nans = np.count_nonzero(np.isnan(t.data))
    t.lower_limit(9.99)
    assert t.data[0][0] == pytest.approx(9.99)
    assert np.count_nonzero(np.isnan(t.data)) == num_nans
