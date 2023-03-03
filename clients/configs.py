from pydantic import BaseSettings


class Settings(BaseSettings):

    env: str = "dev"

    # kafka
    bootstrap_server: str = "kafka-0.trollsoft.io:9094"
    topic: str = "item.dev.v1"

    # grpc
    bandit_slave_grpc_endpoint: str = "bandit.slave.dev.trollsoft.io:443"
    bandit_master_grpc_endpoint: str = "bandit.slave.dev.trollsoft.io:443"


settings = Settings()
