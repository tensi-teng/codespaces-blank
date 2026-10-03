import os
from sqlalchemy import create_engine

def get_engine():
    url = os.getenv('DATABASE_URL', 'postgresql+psycopg2://argus:argus@localhost:5432/argus')
    return create_engine(url, pool_pre_ping=True)
