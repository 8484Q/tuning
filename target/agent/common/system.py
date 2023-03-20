import os
import re
import json
import pyudev
import subprocess
import requests

from agent.common.pylog import logger


def httpResponse(response_data, response_ip, response_port):
    logger.info("[HTTP] send response to {ip}:{port}:{data}".format(
        ip = response_ip,
        port = response_port,
        data = response_data
    ))
    try:
        requests.post(
            url = "http://{ip}:{port}/apply_result".format(ip = response_ip, port = response_port),
            data = json.dumps(response_data),
            timeout = 3)
    except requests.exceptions.ConnectTimeout:
        logger.warning("[HTTP] send response timeout!")


def sysCommand(command: str, cwd: str = "./", log: bool = True):
    '''Run system command with subprocess.run and return result
    '''
    result = subprocess.run(
        command,
        shell=True,
        close_fds=True,
        cwd=cwd,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    suc   = (result.returncode == 0)
    out   = result.stdout.decode('UTF-8', 'strict').strip()
    error = result.stderr.decode('UTF-8', 'strict').strip()
    if not suc:
        logger.error("Exec command '{cmd}': {err}".format(
            cmd = command,
            err = error
        ))
        raise Exception(error)
    else:
        if log:
            logger.info("Exec command '{cmd}': {res}".format(
                cmd = command,
                res = out
            ))
        else:
            logger.debug("Exec command '{cmd}': {res}".format(
                cmd = command,
                res = out
            ))
        return out  


def fileAccess(file_path):
    logger.debug("{}: F_OK:{}, R_OK:{}, W_OK:{}".format(
        file_path,
        os.access(file_path,os.F_OK),
        os.access(file_path,os.R_OK),
        os.access(file_path,os.W_OK),
    ))
    return os.access(file_path,os.F_OK) and os.access(file_path,os.R_OK) and os.access(file_path,os.W_OK)


def fileWrite(file_path, data):
    try:
        f = open(file_path,"w")
        f.write(str(data))
        f.close()
    except Exception as e:
        logger.error("writed file: {file_path} error: '{error}'".format(
            file_path = file_path,
            error = e
        ))
    else:
        logger.debug("writed file: {data} -> {file_path}".format(
            data = data,
            file_path = file_path
        ))


def _getNetQueue(dev_name):
    """ Get rx_queue and tx_queue

    Args:
        dev_name (string): net dev name
    """
    _pci_number = sysCommand("ethtool -i {}".format(dev_name),log=False)
    bus_info = re.search(r"bus-info: (.*)\n", _pci_number).group(1)
    if bus_info == '':
        return None
    queue_info = sysCommand("ls /sys/class/net/{dev_name}/queues/".format(dev_name = dev_name),log=False)
    rx_queue, tx_queue = re.findall(r"rx-\d",queue_info), re.findall(r"tx-\d",queue_info)
    return bus_info, rx_queue, tx_queue
    

def _getPCIDev():
    dev_list = sysCommand("ls /sys/class/net",log=False)

    PCI_dev_list = []
    for dev in dev_list.split("\n"):
        _path = os.path.join("/sys/class/net", dev)
        if not os.path.isdir(_path):
            continue
        try:
            _link_path = os.readlink(_path)
            if re.search(r"pci\d+", _link_path):
                if re.search(r"virtio\d", _link_path):
                    PCI_dev_list.append((re.search(r"virtio\d", _link_path).group(0), dev))
                else:
                    PCI_dev_list.append((dev,dev))
                    
        except OSError:
            continue
    logger.debug("get PCI device:{}".format(PCI_dev_list))
    return PCI_dev_list


def _getInterrupts(dev_name):
    def _getInterruptsCode(interrupts):
        result = []
        for i in interrupts:
            interrupts_id = re.search(r"^(\d+):", i).group(1)
            result.append(interrupts_id)
        return result
    
    content = sysCommand("cat /proc/interrupts",log=False)
    content = content.split('\n')
    content = [i.strip() for i in content]
    
    input_output_interrupts = [i for i in content if re.search("{dev_name}-input|{dev_name}-output".format(dev_name = dev_name),i)]
    
    if not input_output_interrupts.__len__() == 0:
        return _getInterruptsCode(input_output_interrupts)
    
    interrupts = [i for i in content if re.search("{}".format(dev_name),i)]
    return _getInterruptsCode(interrupts)


def getNetInfo():
    PCI_dev_list = _getPCIDev()

    for virtio_name, dev_name in PCI_dev_list:
        logger.debug("get net queue of dev:{}".format(dev_name))
        res = _getNetQueue(dev_name = dev_name)
        if res:
            bus_info, rx_queue, tx_queue = res
        
        interrupts_queue_id = _getInterrupts(dev_name = virtio_name)
        return dev_name, bus_info, interrupts_queue_id, rx_queue, tx_queue


def getNUMA(bus_info):
    numa_message = sysCommand("lspci -vvvs {bus_info}".format(bus_info = bus_info),log=False)
    if re.search(r"NUMA node: (\d)\n", numa_message):
        numa_node_num = re.search(r"NUMA node: (\d)\n", numa_message).group(1)
    else:
        numa_node_num = 0

    logger.debug("get numa_node_num = {}".format(numa_node_num))

    cpu_message = sysCommand("lscpu",log=False)
    if re.search(r"NUMA node{} CPU\(s\):\s*(\d+-\d+)".format(numa_node_num),cpu_message):
        numa_node_core_range = re.search(
            r"NUMA node{} CPU\(s\):\s*(\d+-\d+)".format(numa_node_num),cpu_message).group(1).split('-')
    elif re.search(r"NUMA 节点{} CPU：\s*(\d+-\d+)".format(numa_node_num),cpu_message):
        numa_node_core_range = re.search(
            r"NUMA 节点{} CPU：\s*(\d+-\d+)".format(numa_node_num),cpu_message).group(1).split('-')
    else:
        return
    
    numa_node_core_range = [int(i) for i in numa_node_core_range]
    return numa_node_core_range


def getCPUInfo():
    cpu_num   = sysCommand("cat /proc/cpuinfo| grep 'physical id'| sort| uniq| wc -l",log=False)
    processor = sysCommand("cat /proc/cpuinfo| grep 'processor'| wc -l",log=False)
    return int(cpu_num), int(processor)


def listDevice():
    devices = []
    context = pyudev.Context()
    for device in context.list_devices(subsystem="block"):
        if device.device_type == "disk" and device.attributes.get("removable", None) == b"0" and \
                (device.parent is None or \
                device.parent.subsystem in ["scsi", "virtio", "xen"]):
                    devices.append(device.sys_name)
    return devices


if __name__ == "__main__":
    dev_name, bus_info, interrupts_queue, rx_queue, tx_queue = getNetInfo()
    print("dev_name:", dev_name)
    print("bus_info:", bus_info)
    print("interrupts_queue:", interrupts_queue)
    print("rx_queue:", rx_queue)
    print("tx_queue:", tx_queue)

    numa_node_core_range = getNUMA(bus_info)
    print("numa_node_core_range: ", numa_node_core_range)

    cpu_num, processor = getCPUInfo()
    print("cpu_num:", cpu_num)
    print("processor:", processor)
