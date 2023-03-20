import os  

from subprocess import Popen, PIPE

from agent.common.pylog import functionLog, logger


def writeFile(f, data, makedir = False, no_error = False):
    logger.info("writing {value} to file:{file}".format(
        value = data,
        file = f
    ))
    if makedir:
        d = os.path.dirname(f)
        if os.path.isdir(d):
            makedir = False
    try:
        if makedir:
            os.makedirs(d)
        fd = open(f, "w")
        fd.write(str(data))
        fd.close()
        rc = True
    except (OSError,IOError) as e:
        rc = False
        if not no_error:
            logger.warning("writing to file:{}: '{}'".format(f,e))
    return rc


def readFile(fp, err_ret = "", no_error = False):
    old_value = err_ret
    try:
        f = open(fp, "r")
        old_value = f.read()
        f.close()
    except (OSError,IOError) as e:
        if not no_error:
            logger.warning("Failed to read file {}: '{}'".format(fp, e))
    else:
        logger.info("read data {data} from {file}".format(
            file = fp,
            data = old_value
        ))
    return old_value


@functionLog
def parse_ra(value):
    val = str(value).split(None, 1)
    try:
        v = int(val[0])
    except ValueError:
        return None
    if len(val) > 1 and val[1][0] == "s":
        v /= 2
    return v

        
@functionLog
def _execute(args, shell = False, cwd = None, env = {}, no_errors = [], return_err = False):
        retcode = 0
        _environment = os.environ.copy()
        _environment["LC_ALL"] = "C"
        _environment.update(env)

        out = ""
        err_msg = None
        try:
            proc = Popen(args, stdout = PIPE, stderr = PIPE, \
                    env = _environment, \
                    shell = shell, cwd = cwd, \
                    close_fds = True, \
                    universal_newlines = True)
            out, err = proc.communicate()

            retcode = proc.returncode
            if retcode and not retcode in no_errors and not 0 in no_errors:
                err_out = err[:-1]
                if len(err_out) == 0:
                    err_out = out[:-1]
                err_msg = "Executing %s error: %s" % (args[0], err_out)
        except (OSError, IOError) as e:
            retcode = -e.errno if e.errno is not None else -1
            if not abs(retcode) in no_errors and not 0 in no_errors:
                err_msg = "Executing %s error: %s" % (args[0], e)
        if return_err:
            return retcode, out, err_msg
        else:
            return retcode, out


@functionLog
def read_file(f, err_ret = "", no_error = False):
    old_value = err_ret
    try:
        f = open(f, "r")
        old_value = f.read()
        f.close()
    except (OSError,IOError) as e:
        raise
    return old_value


@functionLog
def _bitmask2cpulist(mask):
    cpu = 0
    cpus = []
    while mask > 0:
        if mask & 1:
            cpus.append(cpu)
        mask >>= 1
        cpu += 1
    return cpus


@functionLog
def _hex2cpulist(mask):
    if mask is None:
        return None
    mask = str(mask).replace(",", "")
    try:
        m = int(mask, 16)
    except ValueError:
        return []
    return _bitmask2cpulist(m)


@functionLog
def _cpulist_invert(l):
    cpus = _cpulist_unpack(l)
    online = _cpulist_unpack(read_file("/sys/devices/system/cpu/online"))
    return list(set(online) - set(cpus))


@functionLog
def _cpulist2bitmask(l):
    m = 0
    for v in l:
        m |= pow(2, v)
    return m


@functionLog
def _cpulist2hex(l):
    if l is None:
        return None
    ul = _cpulist_unpack(l)
    if ul is None:
        return None
    m =_cpulist2bitmask(ul)
    s = "%x" % m
    ls = len(s)
    if ls % 8 != 0:
        ls += 8 - ls % 8
    s = s.zfill(ls)
    return ",".join(s[i:i + 8] for i in range(0, len(s), 8))


@functionLog
def _cpulist_unpack(l, strip_chars='\'"'):
        rl = []
        if l is None:
            return l
        ll = l
        if type(ll) is not list:
            if strip_chars is not None:
                ll = str(ll).strip(strip_chars)
            ll = str(ll).split(",")
        ll2 = []
        negation_list = []
        hexmask = False
        hv = ""
        # Remove commas from hexmasks
        for v in ll:
            sv = str(v)
            if hexmask:
                if len(sv) == 0:
                    hexmask = False
                    ll2.append(hv)
                    hv = ""
                else:
                    hv += sv
            else:
                if sv[0:2].lower() == "0x":
                    hexmask = True
                    hv = sv
                elif sv and (sv[0] == "^" or sv[0] == "!"):
                    nl = sv[1:].split("-")
                    try:
                        if (len(nl) > 1):
                            negation_list += list(range(
                                int(nl[0]),
                                int(nl[1]) + 1
                                )
                            )
                        else:
                            negation_list.append(int(sv[1:]))
                    except ValueError:
                        return []
                else:
                    if len(sv) > 0:
                        ll2.append(sv)
        if len(hv) > 0:
            ll2.append(hv)
        for v in ll2:
            vl = v.split("-")
            if v[0:2].lower() == "0x":
                rl += _hex2cpulist(v)
            else:
                try:
                    if len(vl) > 1:
                        rl += list(range(int(vl[0]), int(vl[1]) + 1))
                    else:
                        rl.append(int(vl[0]))
                except ValueError:
                    return []
        cpu_list = sorted(list(set(rl)))

        # Remove negated cpus after expanding
        for cpu in negation_list:
            if cpu in cpu_list:
                cpu_list.remove(cpu)
        return cpu_list

@functionLog
def _read_cstates_latency(cpuidle_states_path):
    cstates_latency = {}
    for d in os.listdir(cpuidle_states_path):
        cstate_path = cpuidle_states_path + "/%s/" % d
        name = readFile(cstate_path + "name", err_ret = None, no_error=True)
        latency = readFile(cstate_path + "latency",err_ret= None , no_error=True)
        if name is not None and latency is not None:
            latency = _str2int(latency)
            if latency is not None:
                cstates_latency[name.strip()] = latency
    return cstates_latency