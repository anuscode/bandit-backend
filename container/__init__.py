from dependency_injector import containers, providers

import backends.grpc.servers
import schedulers
from configs import settings


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    updatable = providers.Singleton(
        "observable.Observable",
        max_size=10,
    )

    deletable = providers.Singleton(
        "observable.Observable",
        max_size=10,
    )

    ttl = providers.Singleton(
        "caches.TTL",
        default_ttl=settings.default_ttl,
    )

    multi_armed_bandit = providers.Singleton(
        "mab.ThompsonMultiArmedBandit",
    )

    item_stream = providers.Singleton(
        "streamable.ItemStream",
        updatable=updatable,
        deletable=deletable,
    )

    ttl_connector = providers.Singleton(
        "connectors.TTLConnector",
        ttl=ttl,
        updatable=updatable,
        deletable=deletable,
    )

    mab_connector = providers.Singleton(
        "connectors.MABConnector",
        mab=multi_armed_bandit,
        updatable=updatable,
        deletable=deletable,
    )

    ttl_interceptor = providers.Singleton(
        "backends.grpc.interceptors.ttl.TTLInterceptor",
        ttl=ttl,
    )

    welcome_interceptor = providers.Singleton(
        "backends.grpc.interceptors.WelcomeInterceptor",
    )

    request_counter_interceptor = providers.Singleton(
        "backends.grpc.interceptors.RequestCounterInterceptor",
    )

    request_latency_interceptor = providers.Singleton(
        "backends.grpc.interceptors.RequestLatencyInterceptor",
    )

    debug_interceptor = providers.Singleton(
        "backends.grpc.interceptors.DebugInterceptor",
    )

    master_interceptors = providers.List(
        welcome_interceptor,
        request_counter_interceptor,
        request_latency_interceptor,
        ttl_interceptor,
    )

    slave_interceptors = providers.List(
        welcome_interceptor,
        request_counter_interceptor,
        request_latency_interceptor,
        debug_interceptor,
    )

    master_bandit_servicer = providers.Singleton(
        "backends.grpc.servicers.MasterBanditServicer",
        multi_armed_bandit=multi_armed_bandit,
    )

    slave_bandit_servicer = providers.Singleton(
        "backends.grpc.servicers.SlaveBanditServicer",
    )

    health_servicer = providers.Singleton(
        "grpc_health.v1._async.HealthServicer",
    )

    master_server = providers.Singleton(
        backends.grpc.servers.build,
        bandit_servicer=master_bandit_servicer,
        health_servicer=health_servicer,
        interceptors=master_interceptors,
    )

    slave_server = providers.Singleton(
        backends.grpc.servers.build,
        bandit_servicer=slave_bandit_servicer,
        health_servicer=health_servicer,
        interceptors=slave_interceptors,
    )

    master_scheduler = providers.Callable(
        schedulers.master.scheduler,
        deletable=deletable,
        ttl=ttl,
        seconds=settings.ttl_cleanup_interval,
    )

    slave_scheduler = providers.Callable(
        schedulers.slave.scheduler,
        slave_bandit_servicer=slave_bandit_servicer,
        seconds=settings.master_sync_interval_seconds,
    )
