from pydantic import BaseSettings


class Settings(BaseSettings):
    bandit_slave_grpc_endpoint: str = "bandit.slave.dev.trollsoft.io:443"
    bandit_master_grpc_endpoint: str = "bandit.slave.dev.trollsoft.io:443"


settings = Settings()
