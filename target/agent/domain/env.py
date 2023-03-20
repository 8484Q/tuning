import os

from agent.domain.base import BaseDomain
from agent.common.config import Config
from agent.common.tools import sysCommand
from agent.common.pylog import logger


class Env(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)

    def _domainReady(self):
        if not os.path.exists(Config.SCRIPTS_PATH):
            raise Exception("Can not find path {}".format(Config.SCRIPTS_PATH))
        
        self.env_list = {}
        for f in os.listdir(Config.SCRIPTS_PATH):
            if not f.endswith('.sh'):
                continue

            script_path = os.path.join(Config.SCRIPTS_PATH, f)
            try:
                sysCommand("{} verify".format(script_path))
            except Exception as e:
                logger.warning("{}".format(e))

            else:
                self.env_list[f[:-3]] = False

        if self.env_list.__len__() == 0:
            raise Exception("Can not find any script in {}".format(Config.SCRIPTS_PATH))

    def _listAllParameters(self) -> list:
        return list(self.env_list.keys())
    
    def _setParam(self, param_name:str, param_value):
        if param_value not in ['start', 'stop', 'verify']:
            raise Exception("")
        
        if self.env_list[param_name]:
            return
        
        script_path = os.path.join(Config.SCRIPTS_PATH, param_name + ".sh")
        sysCommand("{script_path} {operation}".format(
            script_path = script_path, 
            operation = param_value))

    def _getParam(self, param_name:str):
        if self.env_list[param_name]:
            return "start"
        else:
            return "stop"