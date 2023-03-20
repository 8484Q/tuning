# Target API

### /configure
funciton: 设置或者读取参数  

#### input
```json
{
    "data": {
        "{domain name 1}": {
            "{param_name 1}": {"value": "1"},
            "{param_name 2}": {"value": "1"},
        },
        "{domain name 2}": {
            "{param_name 3}": {"value": "1"},
            "{param_name 4}": {"value": "1"},
        },
    }, 
    "resp_ip": "{response ip address}", 
    "resp_port": "{response port}",
    "readonly":true, // read param value if readonly is True
    "target_id":1
}
```
#### output
```json
{
    "{domain name 1}": {
        "{param_name 1}": {"value": "1", "suc": true, "msg": ""},
        "{param_name 1}": {"value": "1", "suc": false, "msg": "error message"}, // param setting error
    },
    "{domain name 2}": "domain error message"   // if a domain is invalid
}
```

### /backup
#### input
```json
{
    "sysctl": {
        "fs.aio-max-nr": {},
        "fs.file-max": {}
    }
}
```
#### output
```json
{
    "sysctl": {
        "fs.aio-max-nr": "5556566", //backup value
        "fs.file-max": "3152040"    //backup value
    }
}
```

### /rollback
回退参数配置，可以通过all字段选择回退部分domain上次备份状态或者回退所有domain到初始状态
#### input
```json
{
    "domains":["sysctl", "nginx"],
    "all": true
}
```
all 字段如果为True, 回退所有active的domain到**初始状态**，此时domains为无效字段
如果all字段为False, 将 domains 字段定义的参数域回退到上次**备份的状态**

#### output
###### case: all == false
```json
{
    "sysctl": {"suc": true, "msg": null},
    "nginx": {"suc": false, "msg": "domain rollback error message"},
}
```

###### case: all == true
```json
{
    "sysctl": {"suc": true, "msg": null}, 
    "systemd": {"suc": true, "msg": null}, 
    "disk": {"suc": false, "msg": "rollback
parameter apm failed: sda: No such file or directoryrollback parameter spindown failed: -S: bad/missing standby-interval
value (0..255)"}, 
    "irqbalance": {"suc": true, "msg": null}, 
    "sysfs": {"suc": true, "msg": null}, 
    "vm": {"suc": true,"msg": null}
}
```

### /method
调用内置方法, 可以一次调用多个，key是方法名，value是参数列表
目前支持的内置方法有
##### tuned 迁移方法
+ check_net_queue_count
+ cpulist_invert
+ cpulist_online
+ cpulist_unpack
+ cpulist2hex_invert
+ cpulist2hex
+ exec
+ regex_search_ternary
+ strip
##### 其他内置方法
+ cpu_core
+ mem_total
+ mem_free
+ uname_arch
+ thunderx_cpu_info
+ amd_cpu_model

#### input
```json
[
    {
        "method_name": "strip",
        "mehtod_args": [
            {
                "method_name": "exec",
                "mehtod_args": ["mktemp", "-d"]
            },
        ]
    },
]
```

#### output
```json
[
    {
        "method_name": "strip",
        "suc":true,
        "res":32
    }
]
```