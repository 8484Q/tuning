import os
import time

from collections import defaultdict

from agent.common.config import Config
from agent.common.pylog import logger
from agent.domain.base import BaseDomain
from agent.common.system import sysCommand


class MyCnf(BaseDomain):
    def __init__(self):
        super().__init__(domain_name=__class__.__name__)

    def _domainReady(self):
        self.mycnf_path = "/etc/my.cnf"
        self.backup_file = os.path.join(Config.BACKUP_PATH, "my.cnf")
        self.backup_all = os.path.join(Config.BACKUP_PATH_ALL, "my_all.cnf")
        self.get_value = "cat /etc/my.cnf |grep -w {name} | tail -n1 | awk -F'=' '{{print$2}}'"
        self.set_value = "echo {name}={value} >> /etc/my.cnf"
        self.get_flag = "cat /etc/my.cnf  |grep -w {name} | tail -n1 |wc -L |awk '{{if (sum=$(wc -L \"{name}\") && $0==$sum) print \"SET_TRUE\";else print \"SET_FALSE\"}}'"
        self.set_flag = "echo {name} >> /etc/my.cnf"
        self.init_data = "[client-server]\n!includedir /etc/my.cnf.d\n[mysqld]\n"

        if not os.path.exists(self.mycnf_path):
            raise Exception("Can not find config file: file /etc/my.cnf do not exists!")
    
    def _listAllParameters(self) -> list:
        pass

    def _getParam(self, param_name):
        try:
            if param_name in ["core-file", "skip_ssl", "skip_name_resolve"]:
                value = sysCommand(self.get_flag.format(name=param_name.strip()))
            else:
                value = sysCommand(self.get_value.format(name=param_name.strip()))
            return True, value, ""
        except Exception as err:
            return False, None, "failed to get parameter {}: {}".format(param_name, err)

    def _setParam(self, param_name, param_value):
        try:
            if param_name in ["core-file", "skip_ssl", "skip_name_resolve"]:
                if param_value == "SET_TRUE":
                    sysCommand(self.set_flag.format(name=param_name.strip()))
            else:
                sysCommand(self.set_value.format(name=param_name.strip(), value=param_value))
            return True, ""
        except Exception as err:
            return False, "failed to set parameter {}: {}".format(param_name, err)

    def SetParam(self, param_list: dict):
        with open(self.mycnf_path, "w") as f:
            f.write(self.init_data)

        param_set_result = defaultdict(dict)
        for param_name, param_info in param_list.items():
            if param_info['value'] == "":
                continue
            suc, msg = self._setParam(param_name, param_info['value'])
            param_set_result[param_name] = {"suc": suc, "msg": msg}
        return param_set_result

    def GetParam(self, param_list: dict):
        param_get_result = defaultdict(dict)
        for param_name, param_info in param_list.items():
            suc, value, msg = self._getParam(param_name)
            param_get_result[param_name] = {"suc": suc, 'value': value, "msg": msg}
        return param_get_result

    def Backup(self, param_list: dict, all=False):
        if all:
            logger.info("[{domain_name}] Backup all parameters.".format(
                domain_name = self.domain_name))
            backup_file = self.backup_all  
        else:
            logger.info("[{domain_name}] Backup somes parameters.".format(
                domain_name = self.domain_name))
            backup_file = self.backup_file
            self.Rollback(all=False)

        sysCommand("echo y | cp {} {}".format(self.mycnf_path, backup_file))
        reserved_parameters = defaultdict(dict)
        for param_name, _ in param_list.items():
            reserved_parameters[param_name]['value'] = None
        return reserved_parameters

    def Rollback(self, all=False):
        if all:
            logger.info("[{domain_name}] Rollback all parameters.".format(
                domain_name = self.domain_name))
            backup_file = self.backup_all
        else:
            logger.info("[{domain_name}] Rollback some parameters.".format(
                domain_name = self.domain_name))
            backup_file = self.backup_file
                        
        if not os.path.exists(backup_file):
            return True, "backup file {} do not exists.".format(backup_file)

        try:
            sysCommand("echo y | cp {} {}".format(backup_file, self.mycnf_path))
            if not all:
                os.remove(backup_file)
            return True, "rollback mysql conf successfully!"
        except Exception as err:
            return False, "rollback mysql conf failed: {}".format(err)