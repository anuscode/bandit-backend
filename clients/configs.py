from pydantic import BaseSettings


class Settings(BaseSettings):

    env: str = "dev"

    # kafka
    bootstrap_server: str = "kafka-0.trollsoft.io:9094"
    item_topic: str = "item.dev.v1"
    auto_offset_reset: str = "earliest"

    # grpc
    bandit_slave_grpc_endpoint: str = "bandit.slave.dev.trollsoft.io:443"
    bandit_master_grpc_endpoint: str = "bandit.slave.dev.trollsoft.io:443"


settings = Settings()
