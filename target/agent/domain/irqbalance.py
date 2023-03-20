import os

from agent.common.tools import ConfigFile
from agent.common.system import sysCommand
from agent.domain.base import BaseDomain


class Irqbalance(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)

    def _domainReady(self):
        _irq_config_path = "/etc/sysconfig/irqbalance"
        if not os.path.exists(_irq_config_path):
            raise Exception("irqbalance config file {} is not exists".format(_irq_config_path))
        else:
            self.config_file = ConfigFile(_irq_config_path)
            
    def _listAllParameters(self) -> list:
        return ['banned_cpus']
    
    def _setParam(self, param_name:str, param_value):
        if param_name == "banned_cpus":
            self.config_file.writeValue(key = param_name, value = param_value)
    
    def _getParam(self, param_name:str):
        return self.config_file.readValue(key = param_name)
        
    def _persistenceSetting(self):
        sysCommand("systemctl try-restart irqbalance")
        self.config_file.removeDuplicate()