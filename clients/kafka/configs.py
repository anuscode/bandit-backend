from pydantic import BaseSettings


class Settings(BaseSettings):
    env: str = "dev"
    bootstrap_server: str = "kafka-0.trollsoft.io:9094"
    topic: str = "item.dev.v1"


settings = Settings()
