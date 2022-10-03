import pytest
from shared.ahn import AHN, AHNVersion

# The next points have been selected in QGis
# They should stay the same unless (somehow?) the AHN data changes

VALID_POINTS_AHN2 = [
    (152957.35, 458805.67, 10.842),
    (121491.34, 460239.77, -1.483),
]

VALID_POINTS_AHN3 = [
    # Test points for left and right of a tile
    (124999.99, 485686.1, -0.084),
    (125000, 485686.1, -0.075),
    (125000.01, 485686.1, -0.075),
    # Test points for bottom and top of a tile
    (124841.75, 487499.99, 1.169),
    (124841.75, 487500, 1.169),
    (124841.75, 487500.01, 0.009),
]

VALID_POINTS_AHN4 = [
    # Test points for left and right of a tile
    (124999.99, 485685.7, -0.1342),
    (125000, 485685.7, -0.0284),
    (125000.01, 485685.7, -0.0284),
    # Test points for bottom and top of a tile
    (124841.75, 487499.99, 2.3594),
    (124841.75, 487500, 2.3594),
    (124841.75, 487500.01, 2.3224),
]

VALID_POINTS_AGZ43 = [
    (140799.76, 459271.77, -0.0159),
    (116405.44, 465295.57, -0.0155),
    (115390.74, 477538.21, -0.0040),
]

VALID_POINTS_AGZ42 = [(131023.81, 466981.31, -0.0336)]

VALID_POINTS_AGZ32 = [(131023.81, 466981.31, -0.0435)]


def test_setup_ahn2():
    ahn = AHN(version=AHNVersion.AHN2)
    assert (ahn) is not None


def test_setup_ahn3():
    ahn = AHN(version=AHNVersion.AHN3)
    assert (ahn) is not None


def test_setup_ahn4():
    ahn = AHN(version=AHNVersion.AHN4)
    assert (ahn) is not None


def test_setup_agz42():
    ahn = AHN(version=AHNVersion.AGZ42)
    assert (ahn) is not None


def test_setup_agz43():
    ahn = AHN(version=AHNVersion.AGZ43)
    assert (ahn) is not None


def test_setup_agz32():
    ahn = AHN(version=AHNVersion.AGZ32)
    assert (ahn) is not None


def test_setup_error():
    with pytest.raises(ValueError):
        ahn = AHN(version=0)


def test_ahn2_get_z():
    ahn = AHN(version=AHNVersion.AHN2)
    for p in VALID_POINTS_AHN2:
        z = ahn.z_at(p[0], p[1])
        assert round(ahn.z_at(p[0], p[1]), 4) == p[2]


def test_ahn3_get_z():
    ahn = AHN(version=AHNVersion.AHN3)
    for p in VALID_POINTS_AHN3:
        z = ahn.z_at(p[0], p[1])
        assert round(ahn.z_at(p[0], p[1]), 4) == p[2]


def test_ahn4_get_z():
    ahn = AHN(version=AHNVersion.AHN4)
    for p in VALID_POINTS_AHN4:
        z = ahn.z_at(p[0], p[1])
        assert round(ahn.z_at(p[0], p[1]), 4) == p[2]


def test_d_ahn43_get_z():
    ahn = AHN(version=AHNVersion.AGZ43)
    for p in VALID_POINTS_AGZ43:
        z = ahn.z_at(p[0], p[1])
        assert round(ahn.z_at(p[0], p[1]), 4) == p[2]


def test_d_ahn42_get_z():
    ahn = AHN(version=AHNVersion.AGZ42)
    for p in VALID_POINTS_AGZ42:
        z = ahn.z_at(p[0], p[1])
        assert round(ahn.z_at(p[0], p[1]), 4) == p[2]


def test_d_ahn32_get_z():
    ahn = AHN(version=AHNVersion.AGZ32)
    for p in VALID_POINTS_AGZ32:
        z = ahn.z_at(p[0], p[1])
        assert round(ahn.z_at(p[0], p[1]), 4) == p[2]


def test_zs_from_polyline():
    ahn = AHN(version=AHNVersion.AHN4)
    # test a polyline that crosses 4 different raster files
    zs = ahn.zs_from_polyline(
        [
            (124973, 468736),
            (124973, 468779),
            (125025, 468779),
            (125025, 468736),
        ]
    )
    assert len(zs) == 276
    assert zs[-1][0] == 137.5
    assert min([z[-1] for z in zs]) == -2.4127


def test_zs_from_polyline_with_offset_cw():
    ahn = AHN(version=AHNVersion.AHN4)
    # test a clockwise polyline with an offset
    zs = ahn.zs_from_polyline(
        [
            (124500, 468700),
            (124510, 468700),
            (124510, 468710),
        ],
        offset=10.0,
    )
    assert zs[0][2] == 468690
    assert max([p[1] for p in zs]) == 124520


def test_zs_from_polyline_with_offset_ccw():
    ahn = AHN(version=AHNVersion.AHN4)
    # test a counterclockwise polyline with an offset
    zs = ahn.zs_from_polyline(
        [
            (124510, 468710),
            (124510, 468700),
            (124500, 468700),
        ],
        offset=5.0,
    )
    assert zs[0][1] == 124505
    assert min([p[2] for p in zs]) == 468705


def test_zs_from_polyline_with_invalid_offset_ccw():
    ahn = AHN(version=AHNVersion.AHN4)
    # test a polyline with an offset that invalidates the polyline
    with pytest.raises(ValueError):
        _ = ahn.zs_from_polyline(
            [
                (124510, 468710),
                (124510, 468700),
                (124500, 468700),
            ],
            offset=15.0,
        )


def test_get_tile_by_xy():
    assert AHN(version=AHNVersion.AHN4).get_tile_by_xy(107368, 465173) is not None
    assert AHN(version=AHNVersion.AHN4).get_tile_by_xy(0, 0) is None
