from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / '.env', extra='ignore'
    )
    nexus_provider: Literal['demo', 'bedrock'] = 'demo'
    aws_region: str = 'ap-south-1'
    bedrock_model_id: str = ''
    allowed_origins: str = 'http://localhost:3000,http://127.0.0.1:3000'
    demo_access_token: str = ''
    tavily_api_key: str = ''
    document_enabled: bool = True
    document_bucket: str = ''

    @property
    def origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(',') if origin.strip()]

    @property
    def search_enabled(self) -> bool:
        return bool(self.tavily_api_key.strip())
