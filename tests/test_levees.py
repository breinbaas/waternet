from shared.levees import LeveeSections, Levees


def test_get_waternet_leveesections():
    levees = LeveeSections()
    assert len(levees.items) == 1046


def test_get_waternet_levees():
    levees = Levees()
    assert len(levees.items) == 278


def test_get_levee_from_code():
    levee = Levees().get_from_code("A117")
    assert levee is not None


def test_get_leveesection_from_code():
    levees = LeveeSections().get_from_code("A117")
    assert len(levees) == 11


def test_get_bounding_box_leveesection():
    levee = LeveeSections().get_from_code("A117")[0]
    assert levee.bounding_box() == (123732, 485517, 124070, 485350)
    assert levee.bounding_box(offset=10) == (123722, 485527, 124080, 485340)


def test_get_bounding_box_levee():
    levee = Levees().get_from_code("A117")
    assert levee.bounding_box() == (122911, 485690, 126229, 484748)
    assert levee.bounding_box(offset=100) == (122811, 485790, 126329, 484648)


def test_regulary_spaced_leveesection_referenceline():
    levee = LeveeSections().get_from_code("A117")[0]
    refline = levee.regulary_spaced_referenceline()
    assert refline[0][0] == 0.0
    assert refline[-1][0] == 380
    assert len(refline) == 77  # 38 * 2 + 1 (380m / 5m with point 0m)


def test_regulary_spaced_levee_referenceline():
    levee = Levees().get_from_code("A117")
    refline = levee.regulary_spaced_referenceline(interval=10)
    assert refline[0][0] == 0.0
    assert refline[-1][0] == 3780.0
    assert len(refline) == 379


def test_perpendicular_line():
    levee = Levees().get_from_code("A117")
    assert levee.perpendicular_line(c=100, left=10, right=20) == (
        122981.23,
        484819.41,
        122998.96,
        484795.20,
    )


def test_perpendicular_points():
    levee = Levees().get_from_code("A117")
    assert len(levee.perpendicular_points(c=100, left=1, right=1)) == 5


def test_levee_coordinates_to_csv():
    levee = Levees().get_from_code("A2029")
    levee.coordinates_to_csv("tests/testdata/output/A2029.coordinates.csv")
