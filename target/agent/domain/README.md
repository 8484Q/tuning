## Parameter Domain

### Audio
#### timeout
将参数值写入以下文件中
```
/sys/module/snd_hda_intel/parameters/power_save
/sys/module/snd_ac97_codec/parameters/power_save
```

### CPU 
#### governor 
检测系统的负载状况，然后根据当前的负载，选择出某个可供使用的工作频率，然后把该工作频率传递给cpufreq_driver，完成频率的动态调节.  
+ performance. 强制使用最高的时钟频率
+ powersave. 强制使用最低的时钟频率
+ ondemand. 根据系统负载灵活调整
+ userspace. 用户态程序自行设置
+ conservative. 类似ondemand, 更保守

查看目前支持的governor  
```sh
cpupower --cpu all frequency-info --governors
```
查看正在使用的governor  
```sh
cpupower --cpu all frequency-info --policy
```
设置所有cpu到性能模式  
```sh
cpupower -c all frequency-set -g performance
```

#### energy_perf_bias
能耗和性能平衡
+ performance: 处理器不为了节省能源而牺牲性能
+ normal: 处理器为了可能明显的节省能源而容许牺牲较小的性能
+ powersave: 处理器为了最有效率的节省能源而接受可能明显的性能减少

查看当前设置
```sh
x86_energy_perf_policy -r
```

设置为performance状态
```sh
x86_energy_perf_policy performance
```

#### force_latency
根据CPU的负载动态的调节PM QoS CPU DMA延迟。当CPU负载低于 “load_threshold” 参数时，延迟被设为 “latency_high” 参数的数值，否则的话设为 “latency_low”。如果不希望动态调节延迟，可以通过设置 “force_latency” 参数，将延迟固定。  

Tuned操作的是/dev/cpu_dma_latency文件, 如果要对它进行写操作，要open之后写数据之后不close,如果释放掉了文件描述符它就又会恢复到默认值，

#### min_perf_pct, max_perf_pct, no_turbo
参数值分别写入以下文件
```
/sys/devices/system/cpu/intel_pstate/min_perf_pct
/sys/devices/system/cpu/intel_pstate/max_perf_pct
/sys/devices/system/cpu/intel_pstate/no_turbo
```

### Disk
`agent/common/system.py` 文件中的listDevice函数可以列出环境中所有存储设备, 在路径`/sys/block/`下也可以找到设备列表  
对环境中的所有存储设备进行如下设置  
#### elevator
参数值写入文件`/sys/block/{device_name}/queue/scheduler`  
#### apm
执行命令`hdparm -B {value} /dev/{device_name}`    
#### spindown
执行命令`hdparm -S {value} /dev/{device_name}`    
#### readahead
参数值写入文件`/sys/block/{device_name}/queue/read_ahead_kb`

### Env
执行某内置脚本
参数名为脚本名，目前内置脚本有, 在路径`agent/scripts`下
+ cpu-partitioning
+ powersave
+ realtime
+ spindown-disk
+ tuned-pre-udev

参数值为脚本参数
+ start
+ stop

### hugepage
#### code_hugepage
如果参数值为1，2，3，则将参数值写入文件`/sys/kernel/mm/transparent_hugepage/hugetext_enabled` 
如果参数值为0，将参数值写入文件的同时，需要执行以下两个命令来清除缓存
```
echo 1 > /sys/kernel/debug/split_huge_pages
echo 3 > /proc/sys/vm/drop_caches
```

### irqbalance
#### banned_cpus
参数名和参数值写入`/etc/sysconfig/irqbalance`文件，格式为`param_name=param_value` 

### jemalloc
修改环境变量到`/etc/profile`, 格式为`export MALLOC_CONF={param_name}:{param_value},{param_name}:{param_value}` 

### limits
#### hard_nofile
`* hard nofile {param_value}`和`root hard nofile {param_value}`写入文件`/etc/security/limits.conf`  
#### soft_nofile
`* soft nofile {param_value}`和`root soft nofile {param_value}`写入文件`/etc/security/limits.conf`  
#### ulimit
执行命令`ulimit -n {param_value}` 
#### file-max
参数值写入文件`/proc/sys/fs/file-max`

### net
#### xps
如果参数值为off, 将0值写入路径`/sys/class/net/{dev_name}/queues/{queue_id}/xps_cpus`  
如果参数值为different，将队列一一绑定到每个cpu核上，e.g.以8个逻辑核为例，将前8个队列依次绑定到每个核上,`/sys/class/net/{dev_name}/queues/{queue_id}/xps_cpus` 文件值根据不同的 queue_id 依次为1, 2, 4, 8, 10, 20, 40, 80  
其中`dev_name`是环境中所用网卡名，`agent/common/system.py` 文件中getNetInfo()函数可以返回当前环境网卡名列表  
queue_id是tx_queue队列的id, 如果队列数多余cpu核数，最多设置cpu核数等量的队列数，tx_queue可以通过getNetInfo()函数获得，cpu逻辑核数通过getCPUInfo()函数获得  

#### rps
如果参数值为off, 将0值写入路径`/sys/class/net/{dev_name}/queues/{queue_id}/rps_cpus`  
如果参数值为different，将队列一一绑定到每个cpu核上，e.g.以8个逻辑核为例，将前8个队列依次绑定到每个核上,`/sys/class/net/{dev_name}/queues/{queue_id}/rps_cpus` 文件值根据不同的 queue_id 依次为1, 2, 4, 8, 10, 20, 40, 80  
其中`dev_name`是环境中所用网卡名，`agent/common/system.py` 文件中getNetInfo()函数可以返回当前环境网卡名列表  
queue_id是 rx_queue 队列的id, 如果队列数多余cpu核数，最多设置cpu核数等量的队列数，rx_queue 可以通过getNetInfo()函数获得，cpu逻辑核数通过getCPUInfo()函数获得  

#### smp_affinity
将设置代码写入文件`/proc/irq/{queue_id}/smp_affinity_list` 
如果参数值为dedicated, 设置代码为numa_node范围的小值  
如果参数值为different, 根据queue_id的不同，设置代码为numa_node范围内不同值  
如果参数值为off, 设置代码为`{MIN_numa_node}-{MAX_numa_node}`  

### sheduler
根据参数名，将参数值写入 `/proc/sys/kernel` 下的文件 
```
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
```

### scsi
#### alpm
将参数值写入所以符合以下路径格式`/sys/class/scsi_host/host*/link_power_management_policy`的文件中  

### sysctl
执行命令`sysctl -w {param_name}={param_key}`, 并将命令写入文件/etc/sysctl.conf  

### sysfs
参数值写入所以符合以下路径格式的文件中
```
/sys/bus/workqueue/devices/writeback/cpumask
/sys/devices/virtual/workqueue/cpumask
/sys/devices/virtual/workqueue/*/cpumask
/sys/devices/system/machinecheck/machinecheck*/ignore_ce
```

### systemd
#### cpu_affinity
参数值写入配置文件`/etc/systemd/system.conf`, 格式为`CPUAffinity={param_value}`

### vm
#### transparent_hugepages
参数值写入以下配置文件中的一个, 允许的参数值为always, never, madvise
```
/sys/kernel/mm/transparent_hugepage/enabled
/sys/kernel/mm/redhat_transparent_hugepage/enabled
```

## Basic Domain
```python
class MyDomain(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)

    def _domainReady(self):
        pass  
    
    def _listAllParameters(self) -> list:
        pass  
    
    def _setParam(self, param_name:str, param_value):
        pass
    
    def _getParam(self, param_name:str):
        pass  
        
    def _persistenceSetting(self):
        pass
```