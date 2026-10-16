import os

import streamlit as st
from sqlalchemy import create_engine, inspect, text


def _database_url():
    try:
        return st.secrets.get("DATABASE_URL") or os.getenv("DATABASE_URL")
    except FileNotFoundError:
        return os.getenv("DATABASE_URL")


@st.cache_resource(show_spinner=False)
def get_engine(database_url):
    return create_engine(database_url, pool_pre_ping=True)


def database_status():
    url = _database_url()
    if not url:
        return None, "Add DATABASE_URL to .streamlit/secrets.toml or your environment."
    try:
        engine = get_engine(url)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return engine, None
    except Exception as error:
        return None, f"PostgreSQL connection failed: {error}"


def list_tables(engine):
    inspector = inspect(engine)
    return [
        (schema, table)
        for schema in inspector.get_schema_names()
        if schema not in {"information_schema", "pg_catalog"}
        for table in inspector.get_table_names(schema=schema)
    ]


def table_preview(engine, schema, table, limit=100):
    if not 1 <= limit <= 500:
        raise ValueError("Choose between 1 and 500 rows.")
    preparer = engine.dialect.identifier_preparer
    name = f"{preparer.quote_schema(schema)}.{preparer.quote(table)}"
    with engine.connect() as connection:
        with connection.begin():
            connection.execute(text("SET TRANSACTION READ ONLY"))
            return connection.execute(
                text(f"SELECT * FROM {name} LIMIT :limit"), {"limit": limit}
            ).mappings().all()


def save_upload(engine, frame, table):
    """Save a CSV as a new PostgreSQL table; never overwrite existing tables."""
    frame.to_sql(table, engine, schema="public", if_exists="fail", index=False)


def _create_activity_tables(connection):
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS copilot_users (
            email TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            first_login TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            last_login TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS copilot_logins (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            email TEXT NOT NULL,
            logged_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS copilot_uploads (
            id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            table_name TEXT NOT NULL UNIQUE,
            file_name TEXT NOT NULL,
            row_count INTEGER NOT NULL,
            column_count INTEGER NOT NULL,
            uploaded_by TEXT NOT NULL,
            uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))


def record_login(engine, email, full_name):
    email = email.strip().lower()
    with engine.begin() as connection:
        _create_activity_tables(connection)
        connection.execute(text("""
            INSERT INTO copilot_users (email, full_name)
            VALUES (:email, :full_name)
            ON CONFLICT (email) DO UPDATE
            SET full_name = EXCLUDED.full_name, last_login = NOW()
        """), {"email": email, "full_name": full_name})
        connection.execute(text(
            "INSERT INTO copilot_logins (email) VALUES (:email)"
        ), {"email": email})


def record_upload(engine, table_name, file_name, rows, columns, email):
    with engine.begin() as connection:
        _create_activity_tables(connection)
        connection.execute(text("""
            INSERT INTO copilot_uploads
                (table_name, file_name, row_count, column_count, uploaded_by)
            VALUES (:table_name, :file_name, :rows, :columns, :email)
        """), {
            "table_name": table_name,
            "file_name": file_name,
            "rows": rows,
            "columns": columns,
            "email": email.strip().lower(),
        })


def admin_activity(engine):
    with engine.begin() as connection:
        _create_activity_tables(connection)
        counts = connection.execute(text("""
            SELECT
                (SELECT COUNT(*) FROM copilot_users) AS users,
                (SELECT COUNT(*) FROM copilot_logins) AS logins,
                (SELECT COUNT(*) FROM copilot_uploads) AS uploads
        """)).mappings().one()
        logins_by_day = connection.execute(text("""
            SELECT DATE(logged_at) AS date, COUNT(*) AS logins,
                   COUNT(DISTINCT email) AS users
            FROM copilot_logins
            GROUP BY DATE(logged_at)
            ORDER BY date
        """)).mappings().all()
        uploads_by_day = connection.execute(text("""
            SELECT DATE(uploaded_at) AS date, COUNT(*) AS uploads
            FROM copilot_uploads
            GROUP BY DATE(uploaded_at)
            ORDER BY date
        """)).mappings().all()
        uploads = connection.execute(text("""
            SELECT file_name, table_name, row_count, column_count, uploaded_by, uploaded_at
            FROM copilot_uploads
            ORDER BY uploaded_at DESC
        """)).mappings().all()
        users = connection.execute(text("""
            SELECT full_name, email, first_login, last_login
            FROM copilot_users
            ORDER BY last_login DESC
        """)).mappings().all()
    return (
        dict(counts),
        [dict(row) for row in logins_by_day],
        [dict(row) for row in uploads_by_day],
        [dict(row) for row in uploads],
        [dict(row) for row in users],
    )
