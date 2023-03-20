
import re

from agent.domain.base import BaseDomain
from agent.common.system import sysCommand


class Jemalloc(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)

    def _domainReady(self):
        self._conf = {}
    
    def _listAllParameters(self) -> list:
        return [
            "opt.background_thread",
            "opt.max_background_threads",
            "opt.metadata_thp",
            "opt.dirty_decay_ms",
            "opt.muzzy_decay_ms",
            "opt.narenas",
            "opt.percpu_arena",
            "opt.lg_extent_max_active_fit",
            "opt.lg_tcache_max/tcache_max",
            "opt.retain",
            "opt.dss",
            "opt.oversize_threshold",
            # 5.3
            "opt.cache_oblivious",     
            "opt.trust_madvise",
            "opt.mutex_max_spin",
            "opt.tcache_nslots_small_min",
            "opt.tcache_nslots_small_max",
            "opt.tcache_nslots_large",
            "opt.lg_tcache_nslots_mul",
            "opt.tcache_gc_incr_bytes",
            "opt.tcache_gc_delay_bytes",
            "opt.lg_tcache_flush_small_div",
            "opt.lg_tcache_flush_large_div"
        ]
    
    def _setParam(self, param_name:str, param_value):
        if param_value != None:
            self._conf[param_name] = param_value

    def _getParam(self, param_name:str):
        if self._conf.__contains__(param_name):
            return self._conf[param_name]
        else:
            return None
    
    def _settingPrepare(self):
        with open("/etc/profile","r") as f:
            profile = f.read()
        profile = re.sub(r"export MALLOC_CONF=.*","",profile)
        with open("/etc/profile","w") as f:
            f.write(profile)
        self._conf = {}
    
    def _persistenceSetting(self):
        if self._conf.__len__() > 0:
            config_str = ",".join(["{}:{}".format(k,v) for k,v in self._conf.items()])
            sysCommand("echo {} >> /etc/profile".format("export MALLOC_CONF='{}'".format(config_str)))