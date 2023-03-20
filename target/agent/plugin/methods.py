import re  

from agent.plugin.common import _cpulist2hex, _cpulist_unpack, _cpulist_invert, read_file, _execute
from agent.common.pylog import functionLog
from agent.common.system import sysCommand

@functionLog
def check_net_queue_count(args):
    """
    Checks whether the user has specified a queue count for net devices. If
        not, return the number of housekeeping CPUs.
    """
    if args[0].isdigit():
        return args[0]
    (ret, out) = _execute(["nproc"])
    return out


@functionLog
def cpulist_invert(args):
    """
    Inverts list of CPUs (makes its complement). For the complement it
    gets number of online CPUs from the /sys/devices/system/cpu/online,
    e.g. system with 4 CPUs (0-3), the inversion of list "0,2,3" will be
    "1"
    """
    return ",".join(str(v) for v in _cpulist_invert(",,".join(args)))


@functionLog
def cpulist_online(args):
    """
    Checks whether CPUs from list are online, returns list containing
    only online CPUs
    """
    cpus = _cpulist_unpack(",".join(args))
    online = _cpulist_unpack(read_file("/sys/devices/system/cpu/online"))
    return ",".join(str(v) for v in cpus if v in online)

@functionLog
def cpulist_unpack(args):
    """
    Conversion function: unpacks CPU list in form 1-3,4 to 1,2,3,4
    """
    return ",".join(str(v) for v in _cpulist_unpack(",,".join(args)))


@functionLog
def cpulist2hex_invert(args):
    """
    Converts CPU list to hexadecimal CPU mask and inverts it
    """
    return _cpulist2hex(",".join(str(v) for v in _cpulist_invert(",,".join(args))))

@functionLog
def cpulist2hex(args):

    """
    Conversion function: converts CPU list to hexadecimal CPU mask
    """
    return _cpulist2hex(",,".join(args))

@functionLog
def execute(args):
    """
    Executes process and substitutes its output.
    """
    (ret, out) = _execute(args)
    if ret == 0:
        return out
    return None

@functionLog
def regex_search_ternary(args):
    """
    Ternary regex operator, it takes arguments in the following form
    STR1, REGEX, STR2, STR3
    If REGEX matches STR1 (re.search is used), STR2 is returned,
    otherwise STR3 is returned
    """
    if re.search(args[1], args[0]):
        return args[2]
    else:
        return args[3]
    
    
@functionLog
def strip(args):
    """
    Makes string from all arguments and strip it
    """
    return "".join(args).strip()

@functionLog
def cpu_core(args):
    return sysCommand("cat /proc/cpuinfo | grep process | wc -l")

@functionLog
def mem_total(args):
    return sysCommand("free -g| grep 'Mem' | awk '{print $2}'")

@functionLog
def mem_free(args):
    return sysCommand("free -g| grep 'Mem' | awk '{print $4}'")

@functionLog
def uname_arch(args):
    return sysCommand("arch")

@functionLog
def thunderx_cpu_info(args):
    return sysCommand("cat /proc/cpuinfo | grep 'CPU part'| uniq")

@functionLog
def amd_cpu_model(args):
    return sysCommand("cat /proc/cpuinfo | grep 'model name'| uniq")

@functionLog
def os_release(args):
    return sysCommand("cat /etc/redhat-release")

@functionLog
def virt(args):
    return sysCommand("virt-what")

@functionLog
def system(args):
    return sysCommand("cat /etc/system-release-cpe")