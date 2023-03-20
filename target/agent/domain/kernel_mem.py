import os

from agent.common.system import sysCommand
from agent.domain.base import BaseDomain


class KernelMem(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)

    def _domainReady(self):
        self.hugepage_file = "/sys/kernel/mm/transparent_hugepage/hugetext_enabled"
        if not os.path.exists(self.hugepage_file):
            raise Exception("Can not find hugepage config file: {}".format(self.hugepage_file))
    
    def _listAllParameters(self) -> list:
        return ["code_hugepage"]
    
    def _setParam(self, param_name:str, param_value):
        if param_name.strip() == "code_hugepage":
            if int(param_value) == 0:
                sysCommand("echo 1 > /sys/kernel/debug/split_huge_pages")
                sysCommand("echo 3 > /proc/sys/vm/drop_caches")
            
            sysCommand("echo {param_value} > {hugepage_file}".format(
                param_value = param_value,
                hugepage_file = self.hugepage_file
            ))
    
    def _getParam(self, param_name:str):
        if param_name.strip() == "code_hugepage":
            return sysCommand("cat {hugepage_file}".format(
                hugepage_file = self.hugepage_file
            ))