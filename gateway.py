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


def load(lst, start=0, length=16, group=1):
    
    MAX_READ_LENGTH = 16
    toRead = MAX_READ_LENGTH
    if length > MAX_READ_LENGTH:
        toRead = length
    
    param = 1
    offset = 0
    while toRead > 0:
        address = start+offset+100

        if toRead < MAX_READ_LENGTH:
            readCount = toRead
        else:
            readCount = MAX_READ_LENGTH

        response = read(address,  readCount)
        registers = response.registers

        if len(registers) == 0: 
            _logger.error('Register is empty, address ' + str(address) + ', length: ' + str(readCount))
            return lst 

        for i in range(0, readCount):
            lst[i] = registers[i]
            _logger.info("P"+str(group) + '.' + str(param) + ", value " + str(registers[i]))
            param += 1

        offset += readCount 
        toRead -= readCount 

    return lst 

async def main(client, descriptor):

    driveConf = configparser.RawConfigParser()
    driveConf.read(descriptor)

    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    
    # set up our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    #idx = await server.register_namespace(uri)

    MAX_ITEM_GROUPS = config.getint('Gateway', 'max_item_groups')

    objects = server.nodes.objects
    GROUPS_NUMBER = driveConf.getint('GROUPS', 'number')
    node_list = [None]*GROUPS_NUMBER
    data_list = [[0] * MAX_ITEM_GROUPS] * GROUPS_NUMBER # groups x item (100), 6 * 100
    for i in range(0, GROUPS_NUMBER):
        node_list[i] = await objects.add_variable('ns=2;s='+'group'+str(i+1), 'Group'+str(i+1), data_list[i])

    async def save_in_node(node, list):
        await node.write_value(list)

    _logger.info("Starting server!")
    async with server:
        while True:
            # max = 600 # 6 group 
            for i in range(0, GROUPS_NUMBER):
                data_list[i] = load(data_list[i], start=driveConf.getint('GROUP'+str(i+1), 'min')-1, length=driveConf.getint('GROUP'+str(i+1), 'max'), group=i+1)

            for i in range(0, GROUPS_NUMBER):
                await save_in_node(node_list[i], data_list[i])
            
            await asyncio.sleep(0.100)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)-8s - %(message)s')
    
    config = configparser.RawConfigParser()
    config.read('modbus-gateway.cfg')
    
    client = ModbusSerialClient(
      port=config.get('Gateway', 'port'),
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
