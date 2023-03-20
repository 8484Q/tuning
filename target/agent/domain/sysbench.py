import os
import re
from agent.common.config import Config
from agent.domain.base import BaseBenchmark

class Sysbench(BaseBenchmark):
    def __init__(self):
        self.cmd = "sysbench"
        self.default_param = {
            "thread-stack-size": 32768,
            "table-size": 100000,
            "tables": 3,
            "threads": 1
        }
        self.script_path = os.path.join(Config.BENCKMARK_FIlE, "benchmark/sysbench/sysbench_mysql_read_write.py")
        self.parameters_list = [
            "thread-stack-size",
            "table-size",
            "tables",
            "threads"
        ]        
        super().__init__(domain_name = __class__.__name__)

    def _persistenceSetting(self):
        args = " ".join(["--{}={}".format(k, v) for k,v in self.param_value.items()])
        with open(self.script_path, "r") as f:
            data = f.read()
            data = re.sub(r'DEFAULT = "[a-zA-Z0-9\-=\s]*"', 'DEFAULT = "{}"'.format(args), data)

        with open(self.script_path, "w") as f:
            f.write(data)
        self.param_value = self.default_param