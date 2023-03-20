import json

from tornado.web import RequestHandler
from agent.domain import allActiveDomain
from agent.common.pylog import logger


class StatusHandler(RequestHandler):
    """ Alive check.

    """
    def get(self):
        back_json = {"status": "alive"}
        self.write(json.dumps(back_json))
        self.finish()


class AvaliableDomainHandler(RequestHandler):
    """ Get avaliable domain list

    """
    def get(self):
        avaliable_domain = allActiveDomain()
        logger.debug("[Request] Get avaliable request, return: {}".format(avaliable_domain))
        self.write(json.dumps({"result":avaliable_domain}))
        self.finish()