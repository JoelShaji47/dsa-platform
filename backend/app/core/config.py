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

    # Judge0 (self-hosted or RapidAPI cloud).
    JUDGE0_API_URL: str = ""
    JUDGE0_API_KEY: str = ""
    JUDGE0_API_HOST: str = ""
    # RapidAPI key rotation: comma-separated list, e.g. "k1,k2,k3".
    # Numbered vars JUDGE0_API_KEY1 .. JUDGE0_API_KEY30 are also honored.
    JUDGE0_API_KEYS: str = ""
    JUDGE0_API_KEY1: str = ""
    JUDGE0_API_KEY2: str = ""
    JUDGE0_API_KEY3: str = ""
    JUDGE0_API_KEY4: str = ""
    JUDGE0_API_KEY5: str = ""
    JUDGE0_API_KEY6: str = ""
    JUDGE0_API_KEY7: str = ""
    JUDGE0_API_KEY8: str = ""
    JUDGE0_API_KEY9: str = ""
    JUDGE0_API_KEY10: str = ""
    JUDGE0_API_KEY11: str = ""
    JUDGE0_API_KEY12: str = ""
    JUDGE0_API_KEY13: str = ""
    JUDGE0_API_KEY14: str = ""
    JUDGE0_API_KEY15: str = ""
    JUDGE0_API_KEY16: str = ""
    JUDGE0_API_KEY17: str = ""
    JUDGE0_API_KEY18: str = ""
    JUDGE0_API_KEY19: str = ""
    JUDGE0_API_KEY20: str = ""
    JUDGE0_API_KEY21: str = ""
    JUDGE0_API_KEY22: str = ""
    JUDGE0_API_KEY23: str = ""
    JUDGE0_API_KEY24: str = ""
    JUDGE0_API_KEY25: str = ""
    JUDGE0_API_KEY26: str = ""
    JUDGE0_API_KEY27: str = ""
    JUDGE0_API_KEY28: str = ""
    JUDGE0_API_KEY29: str = ""
    JUDGE0_API_KEY30: str = ""

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
    GROQ_MODEL: str = "openai/gpt-oss-20b"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def judge0_configured(self) -> bool:
        return bool(self.JUDGE0_API_URL)

    @property
    def judge0_keys(self) -> list[str]:
        """All configured RapidAPI keys, deduped, in priority order."""
        keys = [k.strip() for k in self.JUDGE0_API_KEYS.split(",") if k.strip()]
        for i in range(1, 31):
            k = getattr(self, f"JUDGE0_API_KEY{i}", "") or ""
            if k.strip():
                keys.append(k.strip())
        if not keys and self.JUDGE0_API_KEY and self.JUDGE0_API_KEY.strip():
            keys = [self.JUDGE0_API_KEY.strip()]
        return list(dict.fromkeys(keys))

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
