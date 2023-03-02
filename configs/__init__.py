from pydantic import BaseSettings


class Settings(BaseSettings):
    # BACKEND
    env: str = "prod"
    role: str = "MUST SPECIFY SERVICER ONE OF MASTER OR SLAVE"
    max_slave_cache_size: int = 99999999
    master_sync_interval_seconds: int = 2

    # KAFKA
    bootstrap_server: str = "kafka-0.trollsoft.io:9094"
    auto_offset_reset: str = "earliest"

    # PROMETHEUS
    metrics_port: int = 80

    # TTL
    default_ttl: int = 60 * 60 * 24 * 30
    ttl_cleanup_interval: int = 600 * 12

    @property
    def master_grpc_address(self) -> str:
        pod = f"bandit-backend-{self.env}-master"
        namespace = f"bandit-backend-{self.env}"
        return f"{pod}.{namespace}.svc.cluster.local:50051"

    @property
    def slave_grpc_address(self) -> str:
        pod = f"bandit-backend-{self.env}-slave"
        namespace = f"bandit-backend-{self.env}"
        return f"{pod}.{namespace}.svc.cluster.local:50051"

    def is_slave(self) -> bool:
        return self.role in ["slave", "SLAVE"]

    def is_master(self) -> bool:
        return self.role in ["master", "MASTER"]


settings = Settings()
