import pytest
from pydantic import ValidationError

from app.settings import Settings


def test_top_k_default_must_be_at_least_one():
    with pytest.raises(ValidationError):
        Settings(TOP_K_DEFAULT=0, _env_file=None)


def test_top_k_default_must_be_at_most_twenty():
    with pytest.raises(ValidationError):
        Settings(TOP_K_DEFAULT=21, _env_file=None)


def test_top_k_default_accepts_api_bounds():
    settings = Settings(TOP_K_DEFAULT=20, _env_file=None)

    assert settings.top_k_default == 20
