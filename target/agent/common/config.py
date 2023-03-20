import os
import re
import logging

from configparser import ConfigParser

LOGLEVEL = {
    "DEBUG"     : logging.DEBUG,
    "INFO"      : logging.INFO,
    "WARNING"   : logging.WARNING,
    "ERROR"     : logging.ERROR
}

def parseDomainList(domain_list_str):
    pass

class Config:
    conf_file_path = "/etc/keentune/target/target.conf"
    conf = ConfigParser()
    conf.read(conf_file_path)
    print("Load config from {}".format(conf_file_path))
    
    HOME                = conf['target']['HOME']                # /etc/keentune/target
    WORKSPACE           = conf['target']['WORKSPACE']           # /var/keentune/target
    SCRIPTS_PATH        = os.path.join(HOME, 'scripts')         # /etc/keentune/target/scripts
    BACKUP_PATH         = os.path.join(WORKSPACE, "backup")     # /var/keentune/target/backup
    BACKUP_PATH_ALL     = os.path.join(WORKSPACE, "backup_all") # /var/keentune/target/backup
    INIT_DOMAIN_LIST    = [re.sub(r"[\'\"]","",i) for i in re.sub("[\[\]]","",conf['target']['INIT_DOMAIN']).split(',')]
    BENCKMARK_FIlE      = "/var/keentune/bench/files"           # defined in keentune-bench

    TARGET_PORT          = conf['target']['TARGET_PORT']
    LOGFILE_PATH        = conf['log']['LOGFILE_PATH']
    CONSOLE_LEVEL       = LOGLEVEL[conf['log']['CONSOLE_LEVEL']]
    LOGFILE_LEVEL       = LOGLEVEL[conf['log']['LOGFILE_LEVEL']]
    LOGFILE_INTERVAL    = int(conf['log']['LOGFILE_INTERVAL'])
    LOGFILE_BACKUP_COUNT= int(conf['log']['LOGFILE_BACKUP_COUNT'])

    if not os.path.exists(BACKUP_PATH):
        os.makedirs(BACKUP_PATH)

    if not os.path.exists(BACKUP_PATH_ALL):
        os.makedirs(BACKUP_PATH_ALL)

    _LOG_DIR = os.path.dirname(LOGFILE_PATH)
    if not os.path.exists(_LOG_DIR):
        os.makedirs(_LOG_DIR)
        os.system("chmod 0755 {}".format(_LOG_DIR))

    print("KeenTune Home: {}".format(HOME))
    print("KeenTune Workspace: {}".format(WORKSPACE))
    print("Listening port: {}".format(TARGET_PORT))