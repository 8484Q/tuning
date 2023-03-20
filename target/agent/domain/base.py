import os  
import re
import json 

from collections import defaultdict

from abc import ABCMeta, abstractmethod
from agent.common.config import Config
from agent.common.pylog import logger
from agent.common.exception import ParamSettingWarning, ParamSettingError

class BaseDomain(metaclass=ABCMeta):
    def __init__(self, domain_name):
        self.domain_name = domain_name
        self.backup_file = os.path.join(Config.BACKUP_PATH, "{}.json".format(domain_name))
        self.backup_all  = os.path.join(Config.BACKUP_PATH_ALL, "{}_all.json".format(domain_name))
        try:
            self._domainReady()
        except Exception as e:
            logger.warning("{domain_name} is not supported in this environment: {message}".format(
                domain_name = domain_name,
                message = e
            ))
            raise
        logger.info("[{domain_name}] backup all parameters".format(domain_name=domain_name))
        self.Backup({},all=True)

    @abstractmethod
    def _domainReady(self) -> str:
        pass
    
    @abstractmethod
    def _listAllParameters(self) -> list:
        """
        List all avaliable parameters
        
        This function will be called repeatly, do not perform time-consuming operations
        """
        pass  
    
    @abstractmethod
    def _setParam(self, param_name:str, param_value):
        pass
    
    @abstractmethod
    def _getParam(self, param_name:str):
        pass

    def _settingPrepare(self):
        pass 

    def _persistenceSetting(self):
        """ Make parameter settings take effect in persistence after calling _setParam()
        
            e.g. restart service or enable source file.
            
            It can also be used for post-setting-processing processes
        """
        pass
    
    def SetParam(self, param_list: dict) -> dict:
        logger.debug("[{domain_name}] setting prepare.".format(domain_name = self.domain_name))
        self._settingPrepare()
        
        param_set_result = defaultdict(dict)
        for param_name, param_info in param_list.items():

            if param_name.strip() not in self._listAllParameters():
                logger.warning("[{domain_name}] Find unvalid paramters {param_name}".format(
                        param_name = param_name,
                        domain_name = self.domain_name
                ))
                param_set_result[param_name] = {"suc":False,"msg":"Unsupported parameter"}
                continue
            
            try:
                self._setParam(param_name = param_name, param_value = param_info['value'])
                logger.info("[{domain_name}] Set parameter '{param_name}' to {value}".format(
                        domain_name = self.domain_name,
                        param_name = param_name,
                        value = param_info['value']
                ))
                param_set_result[param_name] = {"suc":True,"msg":""}
            
            except ParamSettingWarning as e:
                logger.warning("[{domain_name}] Setting param {param_name} warning:{err}".format(
                    param_name = param_name,
                    domain_name = self.domain_name,
                    err = e))
                param_set_result[param_name] = {"suc":True,"msg":"{}".format(e)}

            except ParamSettingError as e:
                logger.error("[{domain_name}] Setting param {param_name} error:{err}".format(
                    param_name = param_name,
                    domain_name = self.domain_name,
                    err = e))
                param_set_result[param_name] = {"suc":False,"msg":"{}".format(e)}

            except Exception as e:
                logger.error("[{domain_name}] unknown Setting param {param_name} error:{err}".format(
                    param_name = param_name,
                    domain_name = self.domain_name,
                    err = e))
                param_set_result[param_name] = {"suc":False,"msg":"{}".format(e)}
        
        try:
            logger.debug("[{domain_name}] persistence setting".format(
                domain_name = self.domain_name))
            self._persistenceSetting()
        except Exception as e:
            logger.error("[{domain_name}] persistence setting failed: {error}".format(
                domain_name = self.domain_name,
                error = e))
            return "{}".format(e)
        else:
            return param_set_result
    
    def GetParam(self, param_list: dict) -> dict:
        param_get_result = defaultdict(dict)
        for param_name, _ in param_list.items():
            if param_name.strip() not in self._listAllParameters():
                logger.warning("[{domain_name}] Invalid paramters {param_name}".format(
                    param_name = param_name,
                    domain_name = self.domain_name
                ))
                param_get_result[param_name] = {'value':None, "suc":False, "msg":"Unsupported parameter"}
                continue
            
            try:
                value = self._getParam(param_name = param_name)
                param_get_result[param_name] = {'value':value, "suc":True,"msg":""}
                
            except Exception as e:
                param_get_result[param_name] = {
                    'value': None, "suc":False,"msg":"failed to get parameter:{}".format(e)}
                
        return param_get_result

    def Backup(self, param_list:dict, all = False) -> dict:
        if all:
            '''
            rollback all and backup all is disable in this version.
            '''
            logger.warning("backup all is disable in this version.")
            return defaultdict(dict)
            # backup_file = self.backup_all
            # param_name_list = self._listAllParameters()
            # logger.debug("[{domain_name}] Backup parameters {param_list} to {file}".format(
            #     param_list = param_name_list,
            #     file = backup_file,
            #     domain_name = self.domain_name))
            
        else:
            backup_file = self.backup_file
            param_name_list = [param for param in param_list.keys() if param in self._listAllParameters()]
            logger.debug("[{domain_name}] Backup parameters {param_list} to {file}".format(
                param_list = param_name_list,
                file = backup_file,
                domain_name = self.domain_name))
            self.Rollback(all = False)
            
        reserved_parameters = defaultdict(dict)
        for param_name in param_name_list:
            try:
                value = self._getParam(param_name = param_name)
                logger.debug("[{domain_name}] read param value {param_name} = {value}".format(
                    domain_name = self.domain_name,
                    param_name = param_name,
                    value = value))
                
            except Exception as e:
                logger.error("[{domain_name}] failed to read parameter {param_name} value:{message}".format(
                        domain_name = self.domain_name,
                        param_name = param_name,
                        message = e
                ))
                continue
            else:
                reserved_parameters[param_name] = value

        if reserved_parameters.keys().__len__() == 0:
            logger.warning("[{domain_name}] Nothing to backup.".format(
                domain_name = self.domain_name
            ))
        
        else:
            logger.debug("[{domain_name}] Save backup file in {path}".format(
                domain_name = self.domain_name,
                path = backup_file
            ))
            with open(backup_file, "w") as f:
                f.write(json.dumps(reserved_parameters))
        return reserved_parameters
          
    def Rollback(self, all = False):
        rollback_success, rollback_msg = True, {}
        if all:
            '''
            rollback all and backup all is disable in this version.
            '''
            logger.warning("rollback all is disable in this version.")
            return True, "rollback all is disable in this version."
            # logger.debug("[{domain_name}] Rollback all parameters.".format(
            #     domain_name = self.domain_name))
            # backup_file = self.backup_all
        else:
            logger.debug("[{domain_name}] Rollback parameters.".format(
                domain_name = self.domain_name))
            backup_file = self.backup_file
                        
        if not os.path.exists(backup_file):
            return True, "backup file {} do not exists.".format(backup_file)
        
        try:
            reserved_parameters = json.load(open(backup_file))
        except Exception as e:
            logger.error("Load backup file '{file_path}' failed:'{error}'".format(
                file_path = backup_file,
                error = e
            ))
            return False, "{}".format(e)
        
        self._settingPrepare()
        for param_name, value in reserved_parameters.items():
            try:
                self._setParam(param_name = param_name, param_value = value)
                logger.debug("[{domain_name}] Set parameter {param_name} to {value}".format(
                    domain_name = self.domain_name,
                    param_name = param_name,
                    value = value
                ))
            except ParamSettingWarning as e:
                logger.warning("[{domain_name}] Rollback parameter {param_name} warning: {message}".format(
                    domain_name = self.domain_name,
                    param_name = param_name,
                    message = e
                ))
                rollback_success = True
                rollback_msg[param_name] = "warning: {}".format(e)
                continue

            except ParamSettingError as e:
                logger.error("[{domain_name}] Rollback parameter {param_name} failed: {message}".format(
                    domain_name = self.domain_name,
                    param_name = param_name,
                    message = e
                ))
                rollback_success = False
                rollback_msg[param_name] = "error: {}".format(e)
                continue

            except Exception as e:
                logger.error("[{domain_name}] Rollback parameter {param_name} failed: {message}".format(
                    domain_name = self.domain_name,
                    param_name = param_name,
                    message = e
                ))
                rollback_success = False
                rollback_msg[param_name] = "error: {}".format(e)
                continue
        
        self._persistenceSetting()
        
        if rollback_success and not all:
            os.remove(backup_file)

        return rollback_success, rollback_msg


class BaseBenchmark(BaseDomain):
    def __init__(self, domain_name):
        super().__init__(domain_name = domain_name)

    def _domainReady(self):
        if not os.path.exists("/etc/keentune/bench"):
            raise Exception("keentune-bench is not installed in this env.")
        
        if not os.path.exists("/var/keentune/bench/files"):
            raise Exception("The version of keentune-bench is not match with agent.")

        # try:
        #     sysCommand(self.cmd)
        # except Exception as e:
        #     raise Exception("{} is not installed in this env:{}".format(self.cmd,e))

        self.param_value = self.default_param
    
    def _listAllParameters(self):
        return self.parameters_list

    def _setParam(self, param_name:str, param_value):
        if param_value != None:
            self.param_value[param_name] = param_value
    
    def _getParam(self, param_name:str):
        if self.param_value.__contains__(param_name):
            return self.param_value[param_name]
    
    def _persistenceSetting(self):
        args = " ".join(["-{}={}".format(k, v) for k,v in self.param_value.items()])
        with open(self.script_path, "r") as f:
            data = f.read()
            data = re.sub(r'DEFAULT = "[a-zA-Z0-9\-=\s]*"', 'DEFAULT = "{}"'.format(args), data)

        with open(self.script_path, "w") as f:
            f.write(data)
        self.param_value = self.default_param