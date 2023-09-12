import asyncio
import logging
import configparser

from asyncua import Server
from pymodbus.client import ModbusSerialClient
from pymodbus.transaction import (
  #    ModbusAsciiFramer,
  #    ModbusBinaryFramer,
  ModbusRtuFramer
  # ModbusSocketFramer,
  #ModbusTlsFramer,
)

_logger = logging.getLogger(__name__)


def read(address, length, address_slave=1):
    #read_holding_registers(address: int, count: int = 1, slave: int = 0, **kwargs: Any) → ModbusResponse
    return client.read_holding_registers(address, length, address_slave)


def load(list, start=0, length=16):
    
    MAX_READ_LENGTH = 16
    toRead = MAX_READ_LENGTH
    if length > MAX_READ_LENGTH:
        toRead = length
    
    offset = 0
    while toRead > 0:
        index = start+offset
        address = index+100
        response = read(address, MAX_READ_LENGTH)
        registers = response.registers

        if len(registers) == 0: 
            _logger.error('Register is empty, address ' + str(address) + ', length: ' + str(MAX_READ_LENGTH))
            return list

        k = 0
        for i in range(index, index+MAX_READ_LENGTH):
            list[i] = registers[k]
            _logger.info("P"+str(i+1) + ", value " + str(registers[k]))
            k = k + 1
            if k == MAX_READ_LENGTH: break

        offset += MAX_READ_LENGTH
        toRead -= MAX_READ_LENGTH

    return list

async def main(client, descriptor):

    config = configparser.RawConfigParser()
    config.read(descriptor)

    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    
    # set up our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    #idx = await server.register_namespace(uri)

    MAX_ITEM_GROUPS = 100

    objects = server.nodes.objects
    node_list = []
    data_list = [[0] * MAX_ITEM_GROUPS]*config.getint('GROUPS', 'number') # groups x item (100), 6 * 100
    for i in range(0, config.getint('GROUPS', 'number')):
        node_list[i] = objects.add_variable('ns=2;s=base', 'Group'+str(i+1), data_list[i])

    async def save_in_node(node, list):
        node.write_value(list)

    _logger.info("Starting server!")
    async with server:
        while True:
            # max = 600 # 6 group 
            for i in range(0, config.getint('GROUPS', 'number')):
                data_list[i] = load(data_list[i], i*MAX_ITEM_GROUPS, length=config.getint('GROUP'+str(i+1), 'max'))

            for i in range(0, config.getint('GROUPS', 'number')):
                await save_in_node(node_list[i], data_list[i])
            
            await asyncio.sleep(0.100)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)-8s - %(message)s')
    
    config = configparser.RawConfigParser()
    config.read('modbus-gateway.cfg')
    
    client = ModbusSerialClient(
      port=config.getint('Gateway', 'port'),
      framer=ModbusRtuFramer,
      # timeout=10,
      # retries=3,
      # retry_on_empty=False,
      # close_comm_on_error=False,
      # strict=True,
      baudrate=config.getint('Gateway', 'baudrate'),
      bytesize=config.getint('Gateway', 'bytesize'),
      parity=config.get('Gateway', 'parity'),
      stopbits=config.getint('Gateway', 'stopbits'),
      # handle_local_echo=False,
    )
    asyncio.run(main(client, config.get('Gateway', 'descriptor')), debug=True)
    client.close()
