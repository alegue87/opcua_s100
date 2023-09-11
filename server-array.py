import asyncio
import logging

from asyncua import Server
import random


async def main():
    _logger = logging.getLogger(__name__)
    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    max_item_groups = 7*100

    objects = server.nodes.objects
    arry = [i for i in range(0,max_item_groups)]

    # set up our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    arry_node = await objects.add_variable('ns=2;s=ciao', 'arry', arry)

    _logger.info("Starting server!")
    async with server:
        while True:
            await asyncio.sleep(1)
            arry = [ random.randrange(100,1000) for i in range(0,max_item_groups)]
            await arry_node.write_value(arry)
            print('write')


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(), debug=True)
