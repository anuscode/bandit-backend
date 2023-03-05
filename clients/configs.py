from pydantic import BaseSettings


class Settings(BaseSettings):
    env: str = "dev"

    # dynamodb
    aws_region_name: str = "us-east-2"
    dynamodb_item_table: str = "item-dev"

    # kafka
    bootstrap_server: str = "kafka-0.trollsoft.io:9094"
    auto_offset_reset: str = "earliest"
    item_topic: str = "item.dev.v1"
    trace_topic: str = "trace.dev.v1"

    # endpoints
    item_http_endpoint: str = "http://item-backend:8000"
    history_http_endpoint: str = "http://history-backend:8000"
    bandit_slave_grpc_endpoint: str = "bandit.slave.dev.trollsoft.io:443"
    bandit_master_grpc_endpoint: str = "bandit.slave.dev.trollsoft.io:443"


settings = Settings()
