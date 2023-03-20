from agent.domain.base import BaseDomain
from agent.plugin.common import writeFile, readFile
from agent.common.tools import stretchWildcard


class Sysfs(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)

    def _domainReady(self):
        pass
    
    def _listAllParameters(self) -> list:
        return ["/sys/bus/workqueue/devices/writeback/cpumask",
                "/sys/devices/virtual/workqueue/cpumask",
                "/sys/devices/virtual/workqueue/*/cpumask",
                "/sys/devices/system/machinecheck/machinecheck*/ignore_ce"]
    
    def _setParam(self, param_name:str, param_value):
        """ Save data to a file or save a list to each files

        """
        all_matched_path = stretchWildcard(path = param_name)
        
        # 1. param_value is a list and whose len is equals to matched path
        if isinstance(param_value, list):
            if len(param_value) != len(all_matched_path):
                raise Exception("{} paths to set but {} values is given".format(
                    len(all_matched_path), len(param_value)))
            else:
                for p, v in zip(all_matched_path, param_value):
                    writeFile(f = p, data = v)
        
        # 2. param_value is not a list, set value to each matched path
        else:
            for p in all_matched_path:
                writeFile(f = p, data = param_value)
    
    def _getParam(self, param_name:str):
        all_matched_path = stretchWildcard(path = param_name)
        values = []
        for p in all_matched_path:
            v = readFile(p)
            values.append(v)
        return values