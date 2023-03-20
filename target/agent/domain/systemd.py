import os

from agent.common.tools import ConfigFile
from agent.domain.base import BaseDomain

class Systemd(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)

    def _domainReady(self):
        _systemd_file = "/etc/systemd/system.conf"
        if not os.path.exists(_systemd_file):
            raise Exception("File {} is not exists".format(_systemd_file))
        else:
            self.config_file = ConfigFile(_systemd_file)
    
    def _listAllParameters(self) -> list:
        return ['cpu_affinity']
    
    def _setParam(self, param_name:str, param_value):
        if param_name == "cpu_affinity" and param_value != "":
            self.config_file.writeValue(key="CPUAffinity", value = param_value)
    
    def _getParam(self, param_name:str):
        if param_name == "cpu_affinity":
            value = self.config_file.readValue(key = "CPUAffinity")
            return value
    
    def _persistenceSetting(self):
        self.config_file.removeDuplicate()