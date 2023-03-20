import os
from agent.plugin.common import writeFile, readFile
from agent.domain.base import BaseDomain


class Audio(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)

    def _domainReady(self):
        self.avaliable_config = []
        for device in ['snd_hda_intel','snd_ac97_codec']:
            _path = "/sys/module/{device}/parameters/power_save".format(device = device)
            if os.path.exists(_path):
                self.avaliable_config.append(_path)
        
        if self.avaliable_config.__len__() == 0:
            raise Exception("No device is avaliable in this environment.")
            
    def _listAllParameters(self) -> list:
        return ['timeout']
    
    def _setParam(self, param_name:str, param_value):
        if param_name == "timeout":
            if isinstance(param_value, list):
                if len(param_value) != len(self.avaliable_config):
                    raise Exception("{} paths to set but {} values is given".format(
                        len(self.avaliable_config), len(param_value)))
                else:
                    for _path, _value in zip(self.avaliable_config, param_value):
                        writeFile(_path, _value)
                    
            else:
                for _path in self.avaliable_config:
                    writeFile(_path, param_value)
        
    def _getParam(self, param_name:str):
        values = []
        
        if param_name == "timeout":
            for _path in self.avaliable_config:
                values.append(int(readFile(_path)))    
            return values