from client.client import Client
import asyncio
import logging
import asyncio

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)


async def main():
    client = Client(logger, "rorservers.com", "12000", "", 123)
    await client.run()

asyncio.run(main())
