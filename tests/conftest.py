from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def isolated_activities():
    initial_activities = deepcopy(app_module.activities)
    app_module.activities.clear()
    app_module.activities.update(deepcopy(initial_activities))

    yield

    app_module.activities.clear()
    app_module.activities.update(initial_activities)


@pytest.fixture
def client():
    return TestClient(app_module.app)
