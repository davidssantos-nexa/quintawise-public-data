def test_percentage_formula():
    property_area = 1000.0
    intersection_area = 250.0
    assert round((intersection_area / property_area) * 100, 2) == 25.0
