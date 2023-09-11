import asyncio
import logging

from asyncua import Server
from pymodbus.client import ModbusSerialClient
from pymodbus.transaction import (
  #    ModbusAsciiFramer,
  #    ModbusBinaryFramer,
  ModbusRtuFramer
  # ModbusSocketFramer,
  #ModbusTlsFramer,
)


def read(address, length, address_slave=1):
    #read_holding_registers(address: int, count: int = 1, slave: int = 0, **kwargs: Any) → ModbusResponse
    return client.read_holding_registers(address, length, address_slave)


def load(array, start=0, length=16):
    response = read(start+100, length) # max read length 16
    registers = response.registers

    if len(registers) == 0: return array

    k = 0
    for i in range(start,start+length):
        if k==length: break
        array[i] = registers[k]
        print("P"+str(i+1) + " , value " + str(registers[k]))
        k = k + 1
    return array

async def main(client):
    _logger = logging.getLogger(__name__)
    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    max_item_groups = 100 
    num_groups = 7

    arry = [0 for i in range(0,max_item_groups*num_groups)]

    # set up our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    objects = server.nodes.objects
    arry_node = await objects.add_variable('ns=2;s=ciao', 'arry', arry)

    _logger.info("Starting server!")
    async with server:
        while True:
            await asyncio.sleep(1)
            #arry = [ random.randrange(100,1000) for i in range(0,max_item_groups)]

            for i in range(0, 600, 100):
                arry = load(arry, i)

            await arry_node.write_value(arry)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    port = '/dev/ttyUSB0'
    client = ModbusSerialClient(
      port,
      framer=ModbusRtuFramer,
      # timeout=10,
      # retries=3,
      # retry_on_empty=False,
      # close_comm_on_error=False,
      # strict=True,
      baudrate=19200,
      bytesize=8,
      parity="N",
      stopbits=2,
      # handle_local_echo=False,
    )

    client.close()
    asyncio.run(main(client), debug=True)
