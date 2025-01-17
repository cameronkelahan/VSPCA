"""
Configuration for pytest.
"""
import pytest
from pathlib import Path

from libpypsg import settings

import VSPEC

def pytest_addoption(parser: pytest.Parser) -> None:
    """
    Add options to pytest.
    """
    parser.addoption('--external', action='store_true', help='use the external psg URL')
    parser.addoption('--test1', action='store_true', help='rerun test 1')

@pytest.fixture
def psg_url(request: pytest.FixtureRequest)->str:
    """
    Decide which psg URL to use.
    """
    external = request.config.getoption('--external')
    return settings.PSG_URL if external else settings.INTERNAL_PSG_URL

@pytest.fixture
def test1_data(request: pytest.FixtureRequest) -> VSPEC.PhaseAnalyzer:
    """
    Run end-to-end test 1.
    """
    path = Path(__file__).parent / 'end_to_end_tests' / 'test1' / 'test1.yaml'
    model = VSPEC.ObservationModel.from_yaml(path)
    rerun = request.config.getoption('--test1')
    if rerun:
        model.build_planet()
        model.build_spectra()
    return VSPEC.PhaseAnalyzer(model.directories['all_model'])

@pytest.fixture
def test1_model(request: pytest.FixtureRequest) -> VSPEC.ObservationModel:
    """
    Model for test 1.
    """
    path = Path(__file__).parent / 'end_to_end_tests' / 'test1' / 'test1.yaml'
    return VSPEC.ObservationModel.from_yaml(path)