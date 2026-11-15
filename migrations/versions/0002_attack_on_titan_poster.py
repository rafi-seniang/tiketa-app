"""Attack on Titan: The Last Attack gets its TMDB poster. It was published without one, and publishing never
updates a film already in the catalogue.

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

TITLE = "Attack on Titan: The Last Attack"
POSTER = "https://image.tmdb.org/t/p/original/wgwldDDlTDDMrluOMkpSA8lyKjv.jpg"
movies = sa.table("movies", sa.column("title", sa.String), sa.column("poster_url", sa.String))


def upgrade() -> None:
    op.execute(movies.update().where(movies.c.title == TITLE, movies.c.poster_url.is_(None)).values(poster_url=POSTER))


def downgrade() -> None:
    op.execute(movies.update().where(movies.c.title == TITLE, movies.c.poster_url == POSTER).values(poster_url=None))
