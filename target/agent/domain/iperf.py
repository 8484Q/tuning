import os
import re
from agent.common.config import Config
from agent.domain.base import BaseBenchmark

class Iperf(BaseBenchmark):
    def __init__(self):
        self.cmd = "iperf"
        self.default_param =  {
            "Parallel": 1,
            "window_size": 10240,
            "length_buffers": 10240
        }
        self.script_path = os.path.join(Config.BENCKMARK_FIlE, "benchmark/iperf/iperf.py")
        self.parameters_list = [
            "Parallel",
            "window_size",
            "length_buffers",
        ]        
        super().__init__(domain_name = __class__.__name__)

    def _persistenceSetting(self):
        args = " ".join(["-{} {}".format(k[0], v) for k,v in self.param_value.items()])
        with open(self.script_path, "r") as f:
            data = f.read()
            data = re.sub(r'DEFAULT = "[a-zA-Z0-9\-=\s]*"', 'DEFAULT = "{}"'.format(args), data)
            data = re.sub(r"PARALLEL = \d+", "PARALLEL = {}".format(self.param_value["Parallel"]), data)

        with open(self.script_path, "w") as f:
            f.write(data)
        self.param_value = self.default_param