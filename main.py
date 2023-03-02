import asyncio
import logging.config

import sentry_sdk
import yaml

import directories

from configs import settings
from container import Container
from loggers import logger

with open(directories.logging, "r") as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)


def main():
    container = Container()
    container.init_resources()
    container.wire(modules=["runnable"])

    sentry_sdk.init(
        dsn="https://c1b1b670c72544d8a0be26eef772f3b7@o125846.ingest.sentry.io/4504292360650757",
        environment=settings.stage,
        traces_sample_rate=1.0,
    )

    loop = asyncio.new_event_loop()

    try:
        import runnable

        # run http server for prometheus metrics
        runnable.prometheus()

        # run grpc server for bandit service
        if settings.is_master():
            runnable = runnable.master()
        else:
            runnable = runnable.slave()
        loop.run_until_complete(runnable)
    except KeyboardInterrupt:
        logger.debug("Keyboard interrupt received.")
    finally:
        logger.debug("Shutting down.")
        loop.close()


if __name__ == "__main__":
    main()
