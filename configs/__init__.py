from pydantic import BaseSettings


class Settings(BaseSettings):
    # BACKEND
    stage: str = "prod"
    role: str = "MUST SPECIFY SERVICER ONE OF MASTER OR SLAVE"
    max_slave_cache_size: int = 99999999
    master_sync_interval_seconds: int = 2

    # KAFKA
    bootstrap_server: str = "pkc-e82om.ap-northeast-2.aws.confluent.cloud:9092"
    sasl_username: str = "JICWYCUM5HONLR6U"
    sasl_password: str = (
        "E8lPXuDH3daJbIjeFQBzO7BljKVLRzWvDVP9GJiOqdrimaNP+nkUCRqgZxQuTN3q"
    )
    auto_offset_reset: str = "earliest"
    security_protocol: str = "SASL_SSL"
    sasl_mechanism: str = "PLAIN"

    synchronize_offset: int = 60 * 60 * 24 * 7 * 1000
    kafka_offset_prorated: float = 1
    kafka_retrieve_ttl: int = 60 * 60 * 24 * 2

    # PROMETHEUS
    metrics_port: int = 80

    # TTL
    default_ttl: int = 60 * 60 * 24 * 1
    ttl_cleanup_interval: int = 60 * 10

    @property
    def topics(self):
        return [
            f"oheadline-analytics-{self.stage}-viewDetailArticle",
            f"oheadline-analytics-{self.stage}-viewListArticle",
        ]

    @property
    def master_grpc_address(self) -> str:
        namespace = f"bandit-backend-{self.stage}"
        # POD.NAMESPACE.svc.cluster.local:[PORT_NUMBER]
        return f"{namespace}-master.{namespace}.svc.cluster.local:50051"

    @property
    def slave_grpc_address(self) -> str:
        namespace = f"bandit-backend-{self.stage}"
        return f"{namespace}-slave.{namespace}.svc.cluster.local:50051"

    def is_slave(self) -> bool:
        return self.role in ["slave", "SLAVE"]

    def is_master(self) -> bool:
        return self.role in ["master", "MASTER"]


settings = Settings()
