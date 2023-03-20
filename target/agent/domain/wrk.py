import os
import re
from agent.common.config import Config
from agent.domain.base import BaseBenchmark

class Wrk(BaseBenchmark):
    def __init__(self):
        self.cmd = "wrk"
        self.default_param = {
            "connections": 10,
            "threads": 2
        }
        self.script_path = os.path.join(Config.BENCKMARK_FIlE, "benchmark/wrk/wrk_parameter_tuning.py")
        self.parameters_list = [
            "connections",
            "duration",
            "threads",
            "script",
            "header",
            "latency",
            "timeout",
            "version"
        ]        
        super().__init__(domain_name = __class__.__name__)

    def _persistenceSetting(self):
        args = " ".join(["--{} {}".format(k, v) for k,v in self.param_value.items()])
        with open(self.script_path, "r") as f:
            data = f.read()
            data = re.sub(r'DEFAULT = "[a-zA-Z0-9\-=\s]*"', 'DEFAULT = "{}"'.format(args), data)

        with open(self.script_path, "w") as f:
            f.write(data)
        self.param_value = self.default_param