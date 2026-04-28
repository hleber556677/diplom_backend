import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv


load_dotenv()


def normalize_database_url(database_url: str | None) -> str | None:
    if not database_url:
        return database_url

    database_url = database_url.strip()

    if database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)

    return ensure_supabase_ssl(database_url)


def ensure_supabase_ssl(database_url: str) -> str:
    parsed = urlsplit(database_url)

    if "supabase" not in (parsed.hostname or ""):
        return database_url

    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query.setdefault("sslmode", "require")

    return urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urlencode(query),
            parsed.fragment,
        )
    )


def get_cors_origins() -> list[str]:
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    origins.extend(
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    )

    if vercel_url := os.getenv("VERCEL_URL"):
        origins.append(f"https://{vercel_url}")

    return list(dict.fromkeys(origins))


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise RuntimeError(f"{name} is not configured.")

    return value.strip()


class Settings:
    database_url: str | None = normalize_database_url(
        os.getenv("SUPABASE_DATABASE_URL") or os.getenv("DATABASE_URL")
    )
    jwt_secret_key: str = get_required_env("JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    admin_email: str = get_required_env("ADMIN_EMAIL").lower()
    admin_password: str = get_required_env("ADMIN_PASSWORD")
    admin_display_name: str = os.getenv("ADMIN_DISPLAY_NAME", "Администратор")
    admin_emails: list[str] = [
        admin_email,
        *[
            email.strip().lower()
            for email in os.getenv("ADMIN_EMAILS", "").split(",")
            if email.strip()
        ],
    ]
    cors_origins: list[str] = get_cors_origins()


settings = Settings()
