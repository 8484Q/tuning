import re  

from agent.common.pylog import logger
from agent.common.tools import getActiveOption, adaptiveCall
from agent.common.system import listDevice, sysCommand
from agent.plugin.common import parse_ra, writeFile, readFile
from agent.domain.base import BaseDomain
from agent.common.exception import ParamSettingWarning, ParamSettingError


class Disk(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)

    def _domainReady(self):
        self.devices = listDevice()
        if self.devices.__len__() == 0:
            raise Exception("No device is avaliable in this environment.")
        else:
            logger.info("[{domain_name}] Get devices: {devices}".format(
                domain_name = self.domain_name,
                devices = self.devices
            ))

    def _listAllParameters(self) -> list:
        return ["elevator", "readahead"]

    def __set_elevator(self, dev, value):
        writeFile("/sys/block/{}/queue/scheduler".format(dev),value)

    # def __set_apm(self, dev, value):
    #     sysCommand("hdparm -B {value} /dev/{dev}".format(value=str(value), dev=dev))
    
    # def __set_spindown(self, dev, value):
    #     sysCommand("hdparm -S {value} /dev/{dev}".format(value=str(value), dev=dev))

    def __set_readahead(self, dev, value):
        if type(value) is str and value.startswith(">"):
            value = value[1:]
        sysCommand("blockdev --setra {value} /dev/{dev}".format(dev=dev,value=value))

    def _setParam(self, param_name:str, param_value):
        if param_name == "elevator":
            adaptiveCall(args=self.devices, adaptive_args=param_value, func=self.__set_elevator)

        # elif param_name == "apm":
        #     for device in self.devices:
        #         try:
        #             self.__set_apm(dev = device, value = param_value)
        #         except Exception as e:
        #             if re.search(r"HDIO_DRIVE_CMD failed", "{}".format(e)):
        #                 raise ParamSettingWarning("Device '{}' not supported by hdparm".format(device))
        #             else:
        #                 raise ParamSettingError(e)

        # elif param_name == "spindown":
        #     for device in self.devices:
        #         try:
        #             self.__set_spindown(dev = device, value = param_value)
        #         except Exception as e:
        #             # Known issue 'HDIO_DRIVE_CMD(setidle) failed'
        #             if re.search(r"HDIO_DRIVE_CMD\(setidle\) failed", "{}".format(e)):
        #                 raise ParamSettingWarning("Device '{}' not supported by hdparm".format(device))
        #             else:
        #                 raise ParamSettingError(e)

        elif param_name == "readahead" and param_value is not None:
            adaptiveCall(args=self.devices, adaptive_args=param_value, func=self.__set_readahead)
        
        
    def _getParam(self, param_name:str):
        if param_name == "elevator":
            values = [getActiveOption(readFile("/sys/block/{}/queue/scheduler".format(dev))) \
                    for dev in self.devices]
            return values
        
        # elif param_name == "apm":
        #     return 254

        # elif param_name == "spindown":
        #     return 253

        elif param_name == "readahead":
            values = []
            for dev in self.devices:
                values.append(int(sysCommand("blockdev --getra /dev/{dev}".format(dev = dev))))

            # values = [int(readFile("/sys/block/{}/queue/read_ahead_kb".format(dev)).strip()) \
                    # for dev in self.devices]
            return values