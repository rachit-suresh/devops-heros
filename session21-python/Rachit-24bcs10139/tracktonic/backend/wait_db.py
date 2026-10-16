"""Wait for the Alembic-created application table, then exit."""
import os
import time
from sqlalchemy import create_engine, text
engine = create_engine(os.environ["DATABASE_URL"])
for attempt in range(180):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1 FROM albums LIMIT 1"))
        break
    except Exception:
        time.sleep(2)
else:
    raise SystemExit("database migrations not ready within 6 minutes")
