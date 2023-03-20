import os
import re  

from importlib import import_module
from collections import defaultdict  

from agent.common.pylog import logger
from agent.domain.base import BaseDomain
from agent.common.exception import unavaliableDomain, invalidDomain
from agent.common.config import Config

DOMAINOBJ = {}
DOMAINMSG = {}


def loadDomain(domain_name):
    from agent import domain

    if DOMAINOBJ.__contains__(domain_name):
        return
    
    class_name = "".join([value.capitalize() for value in domain_name.split("_")]) if "_" in domain_name else domain_name.capitalize()
    try:
        import_module('agent.domain.{}'.format(domain_name))
        domain_obj = eval('domain.{domain_name}.{class_name}()'.format(
            domain_name = domain_name,
            class_name = class_name
        ))
        if isinstance(domain_obj,BaseDomain):
            DOMAINOBJ[domain_name] = domain_obj
            DOMAINMSG[domain_name] = "ready"
            
    except Exception as e:
        logger.warning("[-] Load domain {domain_name}.{class_name} failed: {message}".format(
            domain_name = domain_name, 
            class_name = class_name,
            message = e))
        DOMAINMSG[domain_name] = "{}".format(e)


def getDomainObj(domain_name):
    loadDomain(domain_name)
    if DOMAINOBJ.__contains__(domain_name):
        return DOMAINOBJ[domain_name]
    
    if DOMAINMSG.__contains__(domain_name):
        raise unavaliableDomain(DOMAINMSG[domain_name])

    else:
        raise invalidDomain("invalid domain '{}'".format(domain_name))

def allActiveDomain():
    return list(DOMAINOBJ.keys())

def initDomain():
    logger.info("Init domain defined in config file: {}".format(Config.INIT_DOMAIN_LIST))
    for domain_name in Config.INIT_DOMAIN_LIST:
        loadDomain(domain_name)

    for domain_name, msg in DOMAINMSG.items():
        print("[DOMAIN] {} : {} ".format(domain_name,msg))