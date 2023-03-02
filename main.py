import asyncio
import logging.config

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
    import runnable

    loop = asyncio.new_event_loop()

    try:
        # run http server for prometheus metrics
        runnable.prometheus()

        # run grpc server for bandit service
        if settings.is_master():
            runnable = runnable.master()
        elif settings.is_slave():
            runnable = runnable.slave()
        else:
            raise ValueError("Invalid role.")

        loop.run_until_complete(runnable)
    except KeyboardInterrupt:
        logger.debug("Keyboard interrupt received.")
    finally:
        logger.debug("Shutting down.")
        loop.close()


if __name__ == "__main__":
    main()
