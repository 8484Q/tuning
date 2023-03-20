def _test(param_list, domain):
    _domain = domain()
    res = _domain.Backup(param_list)
    print("[+] backup result:{}".format(res))
    res = _domain.SetParam(param_list)
    print("[+] set result:{}".format(res))
    res = _domain.Rollback(all=False)
    print("[+] rollback result:{}".format(res))
    res = _domain.Rollback(all=True)
    print("[+] rollback result:{}".format(res))


def test_disk():
    from agent.domain.disk import Disk
    param_list = {
        "readahead":{"value": "4096"},
        "apm":{"value":128},
        "spindown":{"value":6},
    }
    _test(param_list, Disk)

def test_net():
    from agent.domain.net import Net
    param_list = {
        "nf_conntrack_hashsize":{"value":"1048576"},
    }
    _test(param_list, Net)

def test_cpu():
    from agent.domain.cpu import Cpu 
    param_list = {
        "governor":{"value":"performance"},
        "energy_perf_bias":{"value":"performance"},
        "min_perf_pct":{"value":100},
        "force_latency":{"value":"cstate.id:1"},
    }
    _test(param_list, Cpu)

    param_list = {
        "force_latency":{"value":99},
        "governor":{"value":"conservative|powersave"},
        "energy_perf_bias":{"value":"normal"},
    }
    _test(param_list, Cpu)

    param_list = {
        "force_latency":{"value":"cstate.id_no_zero:1|3"},
        "governor":{"value":"ondemand|powersave"},
        "energy_perf_bias":{"value":"powersave|power"},
    }
    _test(param_list, Cpu)


def test_scheduler():
    """
    accelerator-performance.conf
    sched_min_granularity_ns = 10000000

    mysql.conf
    sched_latency_ns=60000000
    sched_migration_cost_ns=500000
    sched_min_granularity_ns=15000000
    sched_wakeup_granularity_ns=2000000

    postgresql.conf
    sched_min_granularity_ns = 10000000
    """
    from agent.domain.scheduler import Scheduler
    param_list = {
        "sched_min_granularity_ns":{"value":10000000},
        "sched_latency_ns":{"value":60000000},
        "sched_migration_cost_ns":{"value":500000},
        "sched_wakeup_granularity_ns":{"value":2000000},
    }
    _test(param_list, Scheduler)

def test_net():
    """
    nf_conntrack_hashsize=1048576
    """
    from agent.domain.net import Net 
    param_list = {
        "nf_conntrack_hashsize":{"value":1048576}
    }
    _test(param_list, Net)

if __name__ == "__main__":
    # test_disk()
    # test_net()
    # test_cpu()
    # test_scheduler()
    test_net()