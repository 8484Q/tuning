import os
import logging

from configparser import ConfigParser

LOGLEVEL = {
    "DEBUG"     : logging.DEBUG,
    "INFO"      : logging.INFO,
    "WARNING"   : logging.WARNING,
    "ERROR"     : logging.ERROR
}

class Config:
    conf_file_path = "/etc/keentune/bench/bench.conf"
    conf = ConfigParser()
    conf.read(conf_file_path)

    KEENTUNE_HOME       = conf['bench']['KEENTUNE_HOME']             #/etc/keentune/bench
    KEENTUNE_WORKSPACE  = conf['bench']['KEENTUNE_WORKSPACE']        #/var/keentune/bench
    BENCH_PORT          = conf['bench']['BENCH_PORT']
    FILES_PATH          = os.path.join(KEENTUNE_WORKSPACE, "files")  #/var/keentune/bench/files

    LOGFILE_PATH        = conf['log']['LOGFILE_PATH']
    _LOG_DIR            = os.path.dirname(LOGFILE_PATH)
    CONSOLE_LEVEL       = LOGLEVEL[conf['log']['CONSOLE_LEVEL']]
    LOGFILE_LEVEL       = LOGLEVEL[conf['log']['LOGFILE_LEVEL']]
    LOGFILE_INTERVAL    = int(conf['log']['LOGFILE_INTERVAL'])
    LOGFILE_BACKUP_COUNT= int(conf['log']['LOGFILE_BACKUP_COUNT'])

    if not os.path.exists(FILES_PATH):
        os.makedirs(FILES_PATH)

    if not os.path.exists(_LOG_DIR):
        os.makedirs(_LOG_DIR)
        os.system("chmod 0755 {}".format(_LOG_DIR))

    print("KeenTune Home: {}".format(KEENTUNE_HOME))
    print("KeenTune Workspace: {}".format(KEENTUNE_WORKSPACE))