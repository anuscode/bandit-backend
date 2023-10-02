from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # BACKEND
    env: str = "prod"
    role: str = "MUST SPECIFY SERVICER ONE OF MASTER OR SLAVE"
    max_slave_cache_size: int = 99999999
    master_sync_interval_seconds: int = 2

    # PROMETHEUS
    metrics_port: int = 80

    # TTL
    default_ttl: int = 60 * 60 * 24 * 7
    ttl_cleanup_interval: int = 600 * 12

    bandit_master_grpc_endpoint: str = ""
    bandit_slave_grpc_endpoint: str = ""

    def is_slave(self) -> bool:
        return self.role in ["slave", "SLAVE"]

    def is_master(self) -> bool:
        return self.role in ["master", "MASTER"]


settings = Settings()
