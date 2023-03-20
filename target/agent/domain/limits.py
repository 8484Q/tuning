from agent.common.system import sysCommand
from agent.common.tools import ConfigFile
from agent.common.tools import adaptiveCall
from agent.common.pylog import logger

from agent.domain.base import BaseDomain


class Limits(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)

    def _domainReady(self):
        self.file_max_config = "/proc/sys/fs/file-max"
        self.limits_config = ConfigFile(
            path = "/etc/security/limits.conf",
            pattern = r"(.+ \w+) nofile (\d+)")
        
    def _listAllParameters(self) -> list:
        return ["hard_nofile", "soft_nofile", "ulimit", "file-max"]
    
    def _setParam(self, param_name:str, param_value):
        def setNofile(nofile_key, param_value):
            if param_value is None:
                return
            logger.debug("set {} to {}".format(param_value, param_name))
            sysCommand("echo '{nofile_key} nofile {param_value}' >> {config_file}".format(
                nofile_key  = nofile_key,
                param_value = param_value,
                config_file = self.limits_config.path))
        
        if param_name == "hard_nofile":
            adaptiveCall(["* hard", "root hard"], param_value, setNofile)
            
        elif param_name == "soft_nofile":
            adaptiveCall(["* soft", "root soft"], param_value, setNofile)
            
        elif param_name == "ulimit":
            sysCommand("ulimit -n {param_value}".format(param_value = param_value))

        elif param_name == "file-max":
            sysCommand("echo {param_value} > {file_max_config}".format(
                param_value = param_value, 
                file_max_config = self.file_max_config))
    
    def _getParam(self, param_name:str):
        if param_name == "hard_nofile":
            values = []
            values.append(self.limits_config.readValue(key = "* hard"))
            values.append(self.limits_config.readValue(key = "root hard"))
            logger.debug("hard_nofile = {}".format(values))
            return values
        
        elif param_name == "soft_nofile":
            values = []
            values.append(self.limits_config.readValue(key = "* soft"))
            values.append(self.limits_config.readValue(key = "root soft"))
            logger.debug("soft_nofile = {}".format(values))
            return values
        
        elif param_name == "ulimit":
            return sysCommand("ulimit -n")
        
        elif param_name == "file-max":
            return sysCommand("cat {file_max_config}".format(
                file_max_config = self.file_max_config
            ))
            
    def _persistenceSetting(self):
        self.limits_config.removeDuplicate()