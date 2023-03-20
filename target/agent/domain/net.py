import os 

from agent.common.tools import adaptiveCall
from agent.common.system import sysCommand
from agent.common.system import getNUMA, getNetInfo, getCPUInfo
from agent.domain.base import BaseDomain
from agent.common.pylog import logger
from agent.common.config import Config

class ERDMA():
    def hasERDMA():
        script_path = os.path.join(Config.SCRIPTS_PATH, "erdma.sh")
        try:
            sysCommand("{} hasERDMA".format(script_path))
        except Exception as e:
            return False
        return True

    def toggleERDMA(target):
        script_path = os.path.join(Config.SCRIPTS_PATH, "erdma.sh")
        sysCommand("{} toggleERDMA {}".format(script_path, target))

    def isERDMA():
        script_path = os.path.join(Config.SCRIPTS_PATH, "erdma.sh")
        try:
            sysCommand("{} isERDMA".format(script_path))
        except Exception as e:
            return "off"
        return "on"

class Net(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)

    def _domainReady(self):
        self.available_param = []

        self.dev_name, \
        self.bus_info, \
        self.interrupts_queue, \
        self.rx_queue, \
        self.tx_queue = getNetInfo()

        logger.info("[Net] dev_name = {dev_name}, bus_info = {bus_info},interrupts_queue = {interrupts_queue}, rx_queue = {rx_queue}, tx_queue = {tx_queue}".format(
            dev_name = self.dev_name,
            bus_info = self.bus_info,
            interrupts_queue = self.interrupts_queue,
            rx_queue = self.rx_queue,
            tx_queue = self.tx_queue))
            
        if self.rx_queue is not None and self.rx_queue.__len__()>0:
            self.available_param.append("RPS")

        if self.tx_queue is not None and self.tx_queue.__len__()>0:
            self.available_param.append("XPS")
        
        self.numa_node_core_range = getNUMA(self.bus_info)
        if self.numa_node_core_range is not None:
            self.available_param.append("smp_affinity")
        logger.debug("[Net] numa_node_core_range: {}".format(self.numa_node_core_range))

        if ERDMA.hasERDMA():
            self.available_param.append("eRDMA")

        _, self.processor = getCPUInfo()
        # self.tx_queue = self.tx_queue[:min(len(self.tx_queue), self.processor)]
        # self.rx_queue = self.rx_queue[:min(len(self.rx_queue), self.processor)]

        self.hashsize_path = "/sys/module/nf_conntrack/parameters/hashsize"
        if os.path.exists(self.hashsize_path):
            self.available_param.append("nf_conntrack_hashsize")
        else:
            logger.warning("config file '{path}' not exists, disable param '{param}'".format(
                path = self.hashsize_path,
                param = "nf_conntrack_hashsize"
            ))

    def _listAllParameters(self) -> list:
        return self.available_param


    def _setParam(self, param_name:str, param_value):
        if param_name.lower() == "xps":
            self._setPacketSteering(param_value, xps = True)
                
        elif param_name.lower() == "rps":
            self._setPacketSteering(param_value, xps = False)

        elif param_name.lower() == "smp_affinity":
            self._setSmpAffinity(param_value)
        
        elif param_name.lower().strip() == "nf_conntrack_hashsize":
            sysCommand("echo {param_value} > {path}".format(
                param_value = param_value,
                path = self.hashsize_path
            ))
    
        elif param_name.lower() == "erdma":
            ERDMA.toggleERDMA(param_value)
    
    def _getParam(self, param_name:str):
        if param_name.lower() == "xps":
            values = []
            for queue_id in self.tx_queue:
                _value = sysCommand("cat /sys/class/net/{dev_name}/queues/{queue_id}/xps_cpus".format(
                        dev_name = self.dev_name,
                        queue_id = queue_id),log=False)
                values.append(_value)
            return values
        
        elif param_name.lower() == "rps":
            values = []
            for queue_id in self.rx_queue:
                _value = sysCommand("cat /sys/class/net/{dev_name}/queues/{queue_id}/rps_cpus".format(
                        dev_name = self.dev_name,
                        queue_id = queue_id),log=False)
                values.append(_value)
            return values
        
        elif param_name.lower() == "smp_affinity":
            values = []
            for queue_id in self.interrupts_queue:
                _value = sysCommand("cat /proc/irq/{queue_id}/smp_affinity_list".format(
                            queue_id = queue_id),log=False)
                values.append(_value)
            return values
        
        elif param_name.lower().strip() == "nf_conntrack_hashsize":
            return sysCommand("cat {path}".format(
                path = self.hashsize_path
            ))

        elif param_name.lower() == "erdma":
            return ERDMA.isERDMA()

    def _setPacketSteering(self, param_value, xps=True):
        def setXPS(queue_id, core_code):
            sysCommand("echo {core_code} > /sys/class/net/{dev_name}/queues/{queue_id}/xps_cpus".format(
                core_code = core_code,
                dev_name  = self.dev_name,
                queue_id  = queue_id))
        def setRPS(queue_id, core_code):
            sysCommand("echo {core_code} > /sys/class/net/{dev_name}/queues/{queue_id}/rps_cpus".format(
                core_code = core_code,
                dev_name  = self.dev_name,
                queue_id  = queue_id))
        
        queue = self.tx_queue if xps else self.rx_queue
        set_method = setXPS if xps else setRPS
        
        if param_value == "off":
            param_value = "0"
        
        if param_value == "different":
            param_value  = []
            cpu_core_num = self.processor
            queue_size   = len(queue)

            for queue_index in range(queue_size):
                code = hex(int("".join(['1' if ci%queue_size == queue_index%cpu_core_num else '0' for ci in range(cpu_core_num)][::-1]),2))[2:]
                param_value.append(code)
                
        adaptiveCall(queue, param_value, set_method)


    def _setSmpAffinity(self, param_value):
        def setSmpAffinity(queue_id, core_code):
            sysCommand("echo {core_code} > /proc/irq/{queue_id}/smp_affinity_list".format(
                core_code = core_code,
                queue_id = queue_id))
        
        if param_value == "dedicated":
            param_value = self.numa_node_core_range[0]
        if param_value == "different":
            param_value = []
            for i in range(len(self.interrupts_queue)):
                _code = self.numa_node_core_range[0] + i%(
                        self.numa_node_core_range[1] - self.numa_node_core_range[0])
                param_value.append(_code)
        if param_value == "off":
            param_value = "{}-{}".format(self.numa_node_core_range[0], self.numa_node_core_range[1])
        
        adaptiveCall(self.interrupts_queue, param_value, setSmpAffinity)