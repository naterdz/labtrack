from alembic import context
from sqlalchemy import create_engine, pool

from backend.app import models  # noqa: F401
from backend.app.core.config import Settings
from backend.app.db import Base

config = context.config
url = config.attributes.get("database_url")
if url is None:
    url = Settings().database_url

if context.is_offline_mode():
    context.configure(url=url, target_metadata=Base.metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=Base.metadata, compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()
