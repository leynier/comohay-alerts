from pydantic import BaseSettings


class Settings(BaseSettings):
    github_access_token: str
    github_repo_full_name_or_id: str
    supabase_url: str
    supabase_key: str
    telegram_bot_token: str
    telegram_chat_id: str

    class Config:
        env_file = ".env"


settings = Settings()


def get_settings():
    return settings
