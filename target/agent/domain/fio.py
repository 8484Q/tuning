import os
from agent.common.config import Config
from agent.domain.base import BaseBenchmark


class Fio(BaseBenchmark):
    def __init__(self):
        self.cmd = "fio"
        self.default_param =  {
            "iodepth": 1,
            "bs": "512B",
            "numjobs": 8
        }
        self.script_path = os.path.join(Config.BENCKMARK_FIlE, "benchmark/fio/fio_IOPS_base.py")
        self.parameters_list = [
            "iodepth",
            "bs",
            "numjobs",
        ]        
        super().__init__(domain_name = __class__.__name__)