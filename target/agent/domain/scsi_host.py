from agent.domain.base import BaseDomain
from agent.common.tools import stretchWildcard
from agent.common.tools import adaptiveCall
from agent.common.system import sysCommand


class ScsiHost(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)

    def _domainReady(self):
        self.scsi_paths = stretchWildcard("/sys/class/scsi_host/host*/link_power_management_policy")
        if self.scsi_paths.__len__() == 0:
            raise Exception("Can not find any hosts in /sys/class/scsi_host")
        
    def _listAllParameters(self) -> list:
        return ["alpm"]
    
    def _setParam(self, param_name:str, param_value):
        def setAlpm(path, value):
            sysCommand("echo '{value}' > {path}".format(
                value = value,
                path = path
            ))
        
        if param_name == "alpm":
            adaptiveCall(self.scsi_paths, param_value, setAlpm)
    
    def _getParam(self, param_name:str):
        if param_name == "alpm":
            values = []
            for _path in self.scsi_paths:
                values.append(sysCommand("cat {scsi_host}".format(scsi_host = _path)))
            return values