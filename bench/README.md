# KeenTune Bench  
---  
### Introduction
KeenTune-bench is a benchmark controlling components, which is deployed with benchmark tools. It is used in dynamic tuning workflows to run benchmark tools and get evalation metrics.

### Build & Install
Setuptools can build KeenTune-bench as a python lib. We can run setuptools as  
```s
>> pip3 install setuptools
>> python3 setup.py install
>> pip3 install -r requirements.txt
```

### Configuration
After install KeenTune-bench by setuptools or pyInstaller, we can find configuration file in **/etc/keentune/conf/bench.conf**
```conf
[bench]
# Basic Configuration
KeenTune_HOME       = /etc/keentune/    ; KeenTune-bench install path.
KeenTune_WORKSPACE  = /var/keentune/    ; KeenTune-bench workspace.
BENCH_PORT          = 9874              ; KeenTune-bench service port

[log]
# Configuration about log
LOGFILE_PATH        = /var/log/keentune/bench.log   ; Log file of bench
CONSOLE_LEVEL       = INFO                          ; Console Log level
LOGFILE_LEVEL       = DEBUG                         ; File saved log level
LOGFILE_INTERVAL    = 1                             ; The interval of log file replacing
LOGFILE_BACKUP_COUNT= 14                            ; The count of backup log file  
```

### Run
After modify KeenTune-bench configuration file, we can deploy KeenTune-bench and listening to requests as 
```s
>> keentune-bench
```
or depoly KeenTune-bench by systemctl  
```s
>> systemctl start keentune-bench
```
**NOTE**: You need copy the file 'keentune-bench.service' to '/usr/lib/systemd/system' manually, if you installed the keentune-bench by 'setuptools' rather then 'yum install'.

---
### Code Structure
```
bench/
├── bench.conf          # Configuration file
├── bench.py            # Entrance of keentune-bench
├── common              # Common module, includes log, config and tools.
│   ├── config.py
│   ├── __init__.py
│   ├── pylog.py
│   └── system.py
├── controller          # Service response module.
│   ├── benchmark.py
│   ├── __init__.py
│   ├── sendfile.py
│   └── status.py
├── __init__.py
└── modules             # benchmark running module
    ├── benchmark.py
    └── __init__.py

3 directories, 13 files
```