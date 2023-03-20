import os

from agent.common.pylog import logger
from agent.common.tools import getActiveOption
from agent.plugin.common import writeFile, readFile

from agent.domain.base import BaseDomain


class Vm(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)

    def _domainReady(self):
        # Transparent_hugepage is already set in kernel boot cmdline, ingoring value from profile
        cmdline = readFile("/proc/cmdline")
        if cmdline.find("transparent_hugepage=") > 0:
            raise Exception("Can not find transparent_hugepage in /proc/cmdline")
        
        # Transparent_hugepage file exits
        transparent_hugepage_path = "/sys/kernel/mm/transparent_hugepage/enabled"
        if not os.path.exists(transparent_hugepage_path):
            transparent_hugepage_path = "/sys/kernel/mm/redhat_transparent_hugepage/enabled"
        if not os.path.exists(transparent_hugepage_path):
            raise Exception("Can not find /sys/kernel/mm/*transparent_hugepage/enabled file")

        self.transparent_hugepage_path = transparent_hugepage_path

    def _listAllParameters(self) -> list:
        return ["transparent_hugepages"]
    
    def _setParam(self, param_name:str, param_value):
        if param_name == "transparent_hugepages" and param_value in ["always", "never", "madvise"]:
            writeFile(self.transparent_hugepage_path, param_value)
    
    def _getParam(self, param_name:str):
        if param_name == "transparent_hugepages":
            return getActiveOption(readFile(self.transparent_hugepage_path))