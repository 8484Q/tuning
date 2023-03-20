import os  

from agent.domain.base import BaseDomain
from agent.common.system import sysCommand


class Scheduler(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)

    def _domainReady(self):
        pass  
    
    def _listAllParameters(self) -> list:
        param_list = [
            'sched_min_granularity_ns',    # /proc/sys/kernel/sched_min_granularity_ns
            'sched_latency_ns',            # /proc/sys/kernel/sched_latency_ns
            'sched_features',              # /proc/sys/kernel/sched_features(3183d=110001101111b)
            'sched_wakeup_granularity_ns', # /proc/sys/kernel/sched_wakeup_granularity_ns(4000000ns)
            'sched_child_runs_first',      # /proc/sys/kernel/sched_child_runs_first(0)
            'sched_cfs_bandwidth_slice_us',# /proc/sys/kernel/sched_cfs_bandwidth_slice_us(5000us)
            'sched_rt_period_us',          # /proc/sys/kernel/sched_rt_period_us(1000000us)
            'sched_rt_runtime_us',         # /proc/sys/kernel/sched_rt_runtime_us(950000us)
            'sched_compat_yield',          # /proc/sys/kernel/sched_compat_yield(0)
            'sched_migration_cost',        # /proc/sys/kernel/sched_migration_cost(500000ns)
            'sched_nr_migrate',            # /proc/sys/kernel/sched_nr_migrate(32)
            'sched_tunable_scaling',       # /proc/sys/kernel/sched_tunable_scaling(1)
            'sched_migration_cost_ns',     # /proc/sys/kernel/sched_migration_cost_ns
        ]
        return [p for p in param_list if os.path.exists(os.path.join("/proc/sys/kernel", p))]

    def _setParam(self, param_name:str, param_value):
        if param_value != None:
            sysCommand("echo {value} > /proc/sys/kernel/{param_name}".format(
                value = param_value,
                param_name = param_name
            ))
    
    def _getParam(self, param_name:str):
        return sysCommand("cat /proc/sys/kernel/{param_name}".format(
            param_name = param_name
        ))