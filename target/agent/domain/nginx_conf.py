import re  
import os

from pynginxconfig import NginxConfig
from collections import defaultdict

from agent.common.config import Config
from agent.common.system import sysCommand
from agent.domain.base import BaseDomain
from agent.common.pylog import logger


class NginxConf(BaseDomain):
    def __init__(self):
        super().__init__(domain_name=__class__.__name__)
    
    def _domainReady(self):
        self.nginx_config_path = "/etc/nginx/nginx.conf"
        self.backup_file = os.path.join(Config.BACKUP_PATH, "nginx_backup.conf")
        self.backup_all = os.path.join(Config.BACKUP_PATH_ALL, "nginx_backup_all.conf")
        self.nginx_conf = NginxConfig()
        self._restart()

    def _listAllParameters(self) -> list:
        pass
    
    def _persistenceSetting(self):
        pass

    def _restart(self):
        """ Restart nginx service

        Returns:
            bool: whether success to restart nginx service.
            str : fail message.
        """
        sysCommand("systemctl restart nginx")
        return "restart nginx successfully!"
        
    def _getParam(self, param_name):
        """ Read value of a parameter in nginx.conf
        Args:
            param_name (string): parameter name.
        Returns:
            bool: whether success to read parameter value.
            str : parameter value or fail message.
        """
        try:
            if param_name in ["worker_processes", "worker_rlimit_nofile", "worker_cpu_affinity"]:
                res = self.nginx_conf.get(param_name)
            elif param_name in ["worker_connections", "multi_accept"]:
                res = self.nginx_conf.get([('events',), param_name])
            else:
                res = self.nginx_conf.get([('http',), param_name])

            if res is None:
                return False, None, ""
            else:
                param_value = res[1]
                return True, param_value, ""
        except Exception as err:
            return False, None, "failed to get parameter {}: {}".format(param_name, err)

    def _appendParam(self, param, item):
        """ Append a parameter and value to nginx.conf
        Args:
            param (str) : main module of nginx.conf
            item (tuple): the name and value of the parameter.
        Returns:
            bool: whether success to append parameter and value.
            str : fail message.
        """
        try:
            position_dict = {"events": 1, "http": 7}
            position = position_dict[param]
            for index, element in enumerate(self.nginx_conf.data):
                if isinstance(element, dict) and element["name"] == param:
                    self.nginx_conf.data[index]["value"].insert(position, item)
        except Exception as err:
            return False, "append parameter failed, error is:{}".format(err)
        return True, ""
    
    def _setParam(self, param_name, param_value):
        """ Set value of a parameter in nginx.conf
        Args:
            param_name (str) : parameter name.
            param_value (str): parameter value to set.
        Returns:
            bool: whether success to set parameter value.
            str : fail message.
        """
        if param_name == '' or param_value == '':
            return True, ""
        try:
            param_value = "{}".format(param_value).strip()
            if param_name in ["worker_processes", "worker_rlimit_nofile", "worker_cpu_affinity"]:
                if self.nginx_conf.get(param_name):
                    self.nginx_conf.set(param_name, param_value)
                else:
                    self.nginx_conf.append(
                        (param_name, param_value), position=4)
            elif param_name in ["worker_connections", "multi_accept"]:
                if self.nginx_conf.get([("events",), param_name]):
                    self.nginx_conf.set([("events",), param_name], param_value)
                else:
                    self._appendParam("events", (param_name, param_value))
            else:
                if self.nginx_conf.get([("http",), param_name]):
                    self.nginx_conf.set([("http",), param_name], param_value)
                else:
                    self._appendParam("http", (param_name, param_value))
            return True, ""
        except Exception as err:
            return False, "failed to set parameter {}: {}".format(param_name, err) 

    def SetParam(self, param_list: dict) -> dict:
        """ Set value of parameters.
        if success to set parameters, restart nginx service.
        Args:
            param_list (dict): parameters list.
        Returns:
            bool: whether success to set parameters value.
            obj : result dictionary or error message
        """
        self.nginx_conf.loadf(self.nginx_config_path)
        log_value = """main  '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"'"""
        if self.nginx_conf.get([("http",), "log_format"]):
            self.nginx_conf.set([("http",), "log_format"], log_value)
        if self.nginx_conf.get([("http",), "access_log"]):
            self.nginx_conf.set([("http",), "access_log"], "off")

        param_set_result = defaultdict(dict)
        for param_name, param_info in param_list.items():
            suc, msg = self._setParam(param_name, param_info["value"])
            param_set_result[param_name] = {"suc": suc, "msg": msg}

        self.nginx_conf.savef(self.nginx_config_path)
        self._restart()
        return param_set_result
    
    def GetParam(self, param_list: dict) -> dict:
        """ Read value of parameters.
        Args:
            param_list (dict): parameters list.
        Returns:
            bool: whether success to get parameters value.
            obj : result dictionary or error message
        """
        self.nginx_conf.loadf(self.nginx_config_path)

        param_get_result = defaultdict(dict)
        for param_name in param_list.keys():
            suc, param_value, msg = self._getParam(param_name)
            param_get_result[param_name] = {
                "value": str(param_value).replace("\t", " "), 
                "suc": suc, "msg": msg
                }
        return param_get_result

    def Backup(self, param_list: dict, all=False) -> dict:
        """ Backup parameter values in nginx.conf to backup files.
        Copy parameter values from nginx.conf to backup file as .conf
        Returns:
            bool: whether success to backup.
            str : fail message.
        """
        if all:
            logger.info("[{domain_name}] Backup all parameters.".format(
                domain_name=self.domain_name))
            backup_file = self.backup_all
            
        else:
            logger.info("[{domain_name}] Backup somes parameters.".format(
                domain_name=self.domain_name))
            backup_file = self.backup_file
            self.Rollback(all=False)

        sysCommand("echo y | cp {} {}".format(self.nginx_config_path, backup_file))
        reserved_parameters = defaultdict(dict)
        for param_name, _ in param_list.items():
            reserved_parameters[param_name]['value'] = None
        return reserved_parameters
    
    def Rollback(self, all=False):
        """ rollback parameter values in nginx.conf.
        1. Copy parameter values from backup file to nginx.conf
        2. restart nginx service if success to rollback nginx.conf. 
        Returns:
            bool: whether success to rollback.
            str : fail message.
        """
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
            sysCommand("echo y | cp {} {}".format(backup_file, self.nginx_config_path))
            self._restart()
            if not all:
                os.remove(backup_file)
            return True, "rollback nginx conf successfully!"
        except Exception as err:
            return False, "rollback nginx conf failed: {}".format(err)
