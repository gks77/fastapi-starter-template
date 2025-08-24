from typing import Generator
from app.db.session import get_db as _get_db

# Re-export for convenience
get_db = _get_db
