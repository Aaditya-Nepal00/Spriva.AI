from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    GOOGLE_CLOUD_PROJECT: str = "spriva-ai"
    GOOGLE_CLOUD_LOCATION: str = "us-central1"
    ELASTIC_ENDPOINT: str = ""
    ELASTIC_API_KEY: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:5000/auth/callback"
    SECRET_KEY: str = "spriva-secret-2026"
    PORT: int = 5000

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your-gemini-api-key-here":
    raise ValueError("Please set a real GEMINI_API_KEY in your .env file")
else:
    print(f"Spriva AI config loaded — running on port {settings.PORT}")
