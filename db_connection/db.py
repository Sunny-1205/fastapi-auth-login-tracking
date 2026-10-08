import os
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DATABASE_URL:
    raise RuntimeError("The DATABASE_URL environment variable must be set")

parsed_url = urlparse(DATABASE_URL)
query_params = dict(parse_qsl(parsed_url.query, keep_blank_values=True))
if parsed_url.scheme.startswith("postgres") and "sslmode" not in query_params:
    query_params["sslmode"] = "require"
    DATABASE_URL = urlunparse(
        parsed_url._replace(query=urlencode(query_params, doseq=True))
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

print("DATABASE_URL loaded:", bool(DATABASE_URL))
print("DATABASE_URL length:", len(DATABASE_URL) if DATABASE_URL else 0)
