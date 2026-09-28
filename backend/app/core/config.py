from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_NAME: str = "DSA Platform API"
    DEBUG: bool = True
    CORS_ORIGINS: str = "http://localhost:5173"

    # Database
    DATABASE_URL: str = "postgresql+psycopg://dsa_user:dsa_pass@localhost:5432/dsa_platform"

    # Auth (legacy local JWT; Supabase tokens also accepted — see deps.py)
    JWT_SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Supabase (auth via JWKS; db via DATABASE_URL pooler)
    SUPABASE_URL: str = ""
    SUPABASE_SECRET_KEY: str = ""

    @property
    def supabase_configured(self) -> bool:
        return bool(self.SUPABASE_URL)

    # Judge0
    JUDGE0_API_URL: str = ""
    JUDGE0_API_KEY: str = ""
    JUDGE0_API_HOST: str = ""

    # Gemini (hints + reviews use GEMINI_API_KEY; chat uses rotation below)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"
    # Numbered keys for chat rotation: GEMINI_API_KEY1 .. GEMINI_API_KEY5.
    GEMINI_API_KEY1: str = ""
    GEMINI_API_KEY2: str = ""
    GEMINI_API_KEY3: str = ""
    GEMINI_API_KEY4: str = ""
    GEMINI_API_KEY5: str = ""
    # Legacy comma-separated list, e.g. "k1,k2,k3" (still honored as fallback).
    GEMINI_API_KEYS: str = ""
    # Groq fallback for chat when all Gemini keys fail.
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def judge0_configured(self) -> bool:
        return bool(self.JUDGE0_API_URL)

    @property
    def gemini_configured(self) -> bool:
        return bool(self.GEMINI_API_KEY)

    @property
    def gemini_chat_keys(self) -> list[str]:
        numbered = [
            self.GEMINI_API_KEY1,
            self.GEMINI_API_KEY2,
            self.GEMINI_API_KEY3,
            self.GEMINI_API_KEY4,
            self.GEMINI_API_KEY5,
        ]
        keys = [k.strip() for k in numbered if k and k.strip()]
        if not keys:
            keys = [k.strip() for k in self.GEMINI_API_KEYS.split(",") if k.strip()]
        if not keys and self.GEMINI_API_KEY:
            keys = [self.GEMINI_API_KEY]
        return keys

    @property
    def groq_configured(self) -> bool:
        return bool(self.GROQ_API_KEY)


settings = Settings()
