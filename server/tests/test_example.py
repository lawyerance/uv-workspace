import pytest


@pytest.mark.unit
def test_example_unit():
    """Example unit test to verify marker works."""
    assert 1 + 1 == 2


@pytest.mark.api
def test_example_api(client):
    """Example API test to verify client fixture works."""
    response = client.get("/docs")
    assert response.status_code == 200
