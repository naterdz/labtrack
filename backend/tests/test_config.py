import stat

import pytest
from backend.app.core.config import Settings
from pydantic import ValidationError
from scripts.init_env import ROOT, init_env


def test_environment_is_private_idempotent_and_silent(tmp_path, capsys):
    (tmp_path / ".env.example").write_text((ROOT / ".env.example").read_text())
    assert init_env(tmp_path)
    first = (tmp_path / ".env").read_bytes()
    assert not init_env(tmp_path)
    assert first == (tmp_path / ".env").read_bytes()
    assert stat.S_IMODE((tmp_path / ".env").stat().st_mode) == 0o600
    assert capsys.readouterr().out == ""
    key = next(line for line in first.decode().splitlines() if line.startswith("SECRET_KEY="))
    assert len(key.partition("=")[2]) >= 48


def test_rejects_unsafe_configuration():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, secret_key="short")
    with pytest.raises(ValidationError):
        Settings(_env_file=None, secret_key="t" * 48, app_env="production", cookie_secure=False)
