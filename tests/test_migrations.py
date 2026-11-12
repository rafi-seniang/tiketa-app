"""The migrations build the schema the code describes."""

import os
import subprocess
import sys
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.core.migrations import ALEMBIC_INI


def test_the_migrations_build_exactly_the_tables_in_the_code(tmp_path: Path) -> None:
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", f"sqlite+aiosqlite:///{(tmp_path / 'fresh.db').as_posix()}")
    command.upgrade(config, "head")
    command.check(config)  # raises when the tables in the code and in the database differ
    command.downgrade(config, "base")
    command.upgrade(config, "head")


def test_the_alembic_command_sees_every_table(tmp_path: Path) -> None:
    """In its own process, as `alembic check` runs in CI, with only what migrations/env.py imports."""
    database_url = f"sqlite+aiosqlite:///{(tmp_path / 'cli.db').as_posix()}"
    environment = {**os.environ, "DATABASE_URL": database_url}
    for command_line in (["upgrade", "head"], ["check"]):
        run = subprocess.run(
            [sys.executable, "-m", "alembic", *command_line], env=environment, capture_output=True, text=True
        )
        assert run.returncode == 0, run.stderr
