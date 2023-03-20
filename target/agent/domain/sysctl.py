import re  
import os  

from agent.common.system import sysCommand
from agent.domain.base import BaseDomain
from agent.common.tools import ConfigFile
from agent.common.pylog import logger


class Sysctl(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)
    
    def _domainReady(self):
        _sysctl_config_path = "/etc/sysctl.conf"
        if not os.path.exists(_sysctl_config_path):
            logger.error("sysctl config file {} is not exists".format(_sysctl_config_path))
            raise Exception("sysctl config file {} is not exists".format(_sysctl_config_path))
        else:
            try:
                all_sysctl = sysCommand("sysctl -a",log=False)
                self.avaliable_param = [re.search(r"^(.+)\s*=\s*.+", i).group(1).strip() \
                                for i in all_sysctl.split('\n') \
                                if re.search(r"^(.+)\s*=\s*.+", i)]
            except Exception as e:
                logger.error("fail to get all sysctl parameters: {}".format(e))
                self.avaliable_param = []
            self.config_file = ConfigFile(_sysctl_config_path)

    def _listAllParameters(self) -> list:
        return self.avaliable_param
    
    def _setParam(self, param_name:str, param_value):
        _ = sysCommand("sysctl -w {param_name}='{param_value}' >> /etc/sysctl.conf".format(
            param_name = param_name,
            param_value = param_value
        ),log=False)
        
    def _getParam(self, param_name:str):
        return sysCommand("sysctl -n {param_name}".format(
            param_name = param_name
        ),log=False)
    
    def _persistenceSetting(self):
        self.config_file.removeDuplicate()