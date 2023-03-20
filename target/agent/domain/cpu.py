import os
import re
import struct

from agent.domain.base import BaseDomain
from agent.plugin.common import _read_cstates_latency
from agent.common.system import sysCommand, fileAccess, fileWrite
from agent.common.pylog import logger


class Cpu(BaseDomain):
    def __init__(self):
        super().__init__(domain_name = __class__.__name__)
        
    def getAvaliableGovernor(self):
        try:
            sysCommand("which cpupower",log=False)
        except Exception as e:
            logger.warning("[CPU] Unable to find command cpupower, disable governor control:{err}".format(
                err = e))
            return

        governor_info = sysCommand("cpupower -c all frequency-info",log=False)
        cpu_governor_info_list = [i for i in re.split(r"analyzing CPU \d+:", governor_info) if i!=""]
        self.cpu_avaliable_governor = {}
        for index, cpu_governor_info in enumerate(cpu_governor_info_list):
            avaliable_governor_match = re.search(r"available cpufreq governors:(.*)",cpu_governor_info)
            if avaliable_governor_match is not None:
                avaliable_governor = [i.strip() for i in avaliable_governor_match.group(1).split(' ') if i!='' \
                                and i in ['performance', 'powersave', 'ondemand', 'userspace', 'conservative']]
                if avaliable_governor.__len__() != 0:
                    self.cpu_avaliable_governor[index] = avaliable_governor
                logger.debug("CPU{index} available cpufreq governors:{avaliable_governor}".format(
                    index = index,
                    avaliable_governor = avaliable_governor,
                ))
                    
        if self.cpu_avaliable_governor.__len__() == 0:
            logger.warning("[CPU] available cpufreq governors is none, disable [governor] setting.")
            return
        
        self.available_param.append('governor')
        logger.info("[CPU] governor setting ready, avaliable governor:{governor}".format(
            governor = self.cpu_avaliable_governor))
        
    def getAvaliableLatency(self):
        self._cpu_latency_path = "/dev/cpu_dma_latency"
        if not os.path.exists(self._cpu_latency_path):
            logger.warning("[CPU] No dma_latency avaliable, file {dma_latency_file} do not exists.".format(
                dma_latency_file = self._cpu_latency_path))
            return

        # Keep file open to setting
        self._cpu_latency_fd = open(self._cpu_latency_path, "rb+")
        
        self.cpu_avaliable_force_latency = "/sys/devices/system/cpu/cpu0/cpuidle"
        if not os.path.exists(self.cpu_avaliable_force_latency):
            logger.warning("[CPU] No cpuidle setting file avaliable in '/sys/devices/system/cpu/cpu0/cpuidle'")
            return 

        self.available_param.append('force_latency')
        logger.info("[CPU] force_latency setting ready, avaliable setting:{force_latency_file}".format(
            force_latency_file = self.cpu_avaliable_force_latency))
    
    def getAvaliablePstate(self):
        self.intel_pstate_path = "/sys/devices/system/cpu/intel_pstate"
        
        _min_perf_pct_path = os.path.join(self.intel_pstate_path, "min_perf_pct")
        if fileAccess(_min_perf_pct_path):
            self.available_param.append("min_perf_pct")
        else:
            logger.warning("config file '{path}' not exists, disable param {param}".format(
                path = _min_perf_pct_path,
                param = "min_perf_pct"
            ))

        _max_perf_pct_path = os.path.join(self.intel_pstate_path, "max_perf_pct")
        if fileAccess(_max_perf_pct_path):
            self.available_param.append("max_perf_pct")
        else:
            logger.warning("config file '{path}' not exists, disable param {param}".format(
                path = _max_perf_pct_path,
                param = "max_perf_pct"
            ))
            
        _no_turbo_path = os.path.join(self.intel_pstate_path, "no_turbo")
        if fileAccess(_no_turbo_path):
            self.available_param.append("no_turbo")
        else:
            logger.warning("config file '{path}' not exists, disable param {param}".format(
                path = _no_turbo_path,
                param = "no_turbo"
            ))
    
    def getAvaliableEnergy(self):
        try:
            sysCommand("which x86_energy_perf_policy",log=False)
        except Exception as e:
            logger.warning("[CPU] Unable to find command x86_energy_perf_policy, disable energy_perf_bias control:{}".format(e))
        else:
            self.available_param.append('energy_perf_bias')

    def _domainReady(self):
        self.available_param = []
        self.getAvaliableGovernor()  # governor
        self.getAvaliableLatency()   # force_latency
        self.getAvaliablePstate()    # min_perf_pct, max_perf_pct, no_turbo
        self.getAvaliableEnergy()    # energy_perf_bias
        logger.info("[CPU] Domain ready, avaliable parameter:{}".format(self.available_param))

    def _listAllParameters(self) -> list:
        return self.available_param
    
    def _setParam(self, param_name:str, param_value):
        logger.debug("[CPU] set param {param_name} to {param_value}".format(
            param_name = param_name,
            param_value = param_value
        ))
        if param_value is None:
            return
        
        if param_name == "governor":
            for cpu_index in self.cpu_avaliable_governor.keys():
                valid_governor = self.parseValidGovernor(param_value, self.cpu_avaliable_governor[cpu_index])
                if valid_governor is None:
                    logger.warning("invalid governor {} for cpu{}".format(param_value, cpu_index))
                    continue
                sysCommand("cpupower -c {index} frequency-set -g {param_value}".format(
                    index = cpu_index,
                    param_value = valid_governor))
        
        if param_name == "force_latency":
            latency = self._parse_latency(str(param_value))
            latency_bin = struct.pack("i",latency)
            logger.info("[CPU] write {} to {}".format(latency_bin, self._cpu_latency_path))
            self._cpu_latency_fd.write(latency_bin)

        if param_name in ['min_perf_pct', 'max_perf_pct', 'no_turbo']:
            fileWrite(file_path = os.path.join(self.intel_pstate_path,param_name), data=param_value)

        if param_name == "energy_perf_bias":
            if param_value in ['performance', 'powersave', 'normal']:
                sysCommand("x86_energy_perf_policy {param_value}".format(param_value = param_value))
            else:
                logger.warning("invalid parameter value {param_name}:{param_value}".format(
                    param_name = param_name, 
                    param_value = param_value))
        
        
    def _getParam(self, param_name:str):
        if param_name == "force_latency":
            latency_bin = self._cpu_latency_fd.read()
            logger.debug("[CPU] get latency bin:{}".format(latency_bin))
            latency = struct.unpack("i", latency_bin)[0]
            return latency

        if param_name in ['min_perf_pct', 'max_perf_pct', 'no_turbo']:
            value = sysCommand("cat {file_path}".format(
                file_path = os.path.join(self.intel_pstate_path, param_name)
            ))
            return value
        
        # if param_name == "energy_perf_bias":
        #     value = sysCommand("x86_energy_perf_policy -r").strip()
        #     if value == "":
        #         return None
        #     return value


    def parseValidGovernor(self, governor, avaliable_list):
        """ select valid governor
        
        e.g. ondemand|powersave -> powersave, if powersave in avaliable_list
        """
        governor_list = governor.split('|')
        for _gov in governor_list:
            if _gov in avaliable_list:
                return _gov
    
    def _parse_latency(self, latency_str):
        """ Tuned method, parse latency string

        """
        def _get_latency_by_cstate_id(lid):
            latency_path = os.path.join(self.cpu_avaliable_force_latency, "state{}".format(lid), "latency")
            latency = int(sysCommand("cat {}".format(latency_path)))
            return latency

        def _get_latency_by_cstate_name(name):
            cstates_latency = _read_cstates_latency()
            latency = cstates_latency.get(name,None)
            return latency

        if re.match(r"cstate.id_no_zero:\d+\|\d+", latency_str):
            lid = re.match(r"cstate.id_no_zero:(\d+)\|\d+", latency_str).group(1)
            latency = _get_latency_by_cstate_id(lid)

        elif re.match(r"cstate.id:\d+", latency_str):
            lid = re.match(r"cstate.id:(\d+)", latency_str).group(1)
            latency =  _get_latency_by_cstate_id(lid)

        elif re.match(r"cstate.id:\d+\|\d+", latency_str):
            lid = re.match(r"cstate.id:(\d+)\|\d+", latency_str).group(1)
            latency =  _get_latency_by_cstate_id(lid)

        elif re.match(r"cstate.name_no_zero:(\w+)", latency_str):
            name = re.match(r"cstate.name_no_zero:(\w+)", latency_str).group(1)
            latency =  _get_latency_by_cstate_name(name)

        elif re.match(r"cstate.name:(\w+)", latency_str):
            name = re.match(r"cstate.name:(\w+)", latency_str).group(1)
            latency =  _get_latency_by_cstate_name(latency_str)
        else:
            latency = latency_str
            
        logger.debug("[CPU] parse latency {} to {}".format(latency_str, latency))
        return int(latency)