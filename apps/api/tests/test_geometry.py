import pytest
from app.services.geometry import analyse_polygon


def test_valid_polygon_area_is_positive():
    polygon = {
        "type": "Polygon",
        "coordinates": [
            [
                [-8.0, 39.0],
                [-7.999, 39.0],
                [-7.999, 39.001],
                [-8.0, 39.001],
                [-8.0, 39.0],
            ]
        ],
    }
    result = analyse_polygon(polygon)
    assert result.area_m2 > 0


def test_rejects_polygon_outside_mainland_portugal():
    polygon = {
        "type": "Polygon",
        "coordinates": [
            [
                [0.0, 0.0],
                [0.001, 0.0],
                [0.001, 0.001],
                [0.0, 0.001],
                [0.0, 0.0],
            ]
        ],
    }
    with pytest.raises(ValueError):
        analyse_polygon(polygon)


def test_rejects_polygon_that_extends_beyond_mainland_bounds():
    polygon = {
        "type": "Polygon",
        "coordinates": [
            [
                [-8.0, 39.0],
                [-5.9, 39.0],
                [-5.9, 39.1],
                [-8.0, 39.1],
                [-8.0, 39.0],
            ]
        ],
    }
    with pytest.raises(ValueError):
        analyse_polygon(polygon)


def test_repairs_a_self_intersection_only_when_result_is_polygon():
    polygon = {
        "type": "Polygon",
        "coordinates": [
            [
                [-8.1, 39.0],
                [-8.0, 39.1],
                [-8.1, 39.1],
                [-8.0, 39.0],
                [-8.1, 39.0],
            ]
        ],
    }
    with pytest.raises(ValueError):
        analyse_polygon(polygon)
