import json

from tornado.web import RequestHandler

from agent.domain import getDomainObj
from agent.common.exception import unavaliableDomain, invalidDomain
from agent.common.pylog import logger


class BackupHandler(RequestHandler):
    def post(self):
        """ Backup parameters value to backup file
        
        """
        request_data = json.loads(self.request.body)
        logger.debug("[Request] Get backup request:{}".format(request_data))

        domain_result = {}
        for domain_name, param_list in request_data.items():
            try:
                domain_obj = getDomainObj(domain_name)
                domain_result[domain_name] = domain_obj.Backup(param_list, all = False)
            except unavaliableDomain as e:
                domain_result[domain_name] = "unvaliable domain '{domain_name}': {message}".format(
                    domain_name = domain_name,
                    message = "{}".format(e))
            except invalidDomain as e:
                domain_result[domain_name] = "invalid domain '{domain_name}': {message}".format(
                    domain_name = domain_name,
                    message = "{}".format(e))
            except Exception as e:
                domain_result[domain_name] = "Backup failed '{domain_name}': {message}".format(
                    domain_name = domain_name,
                    message = "{}".format(e))

        logger.debug("[Request] backup request result:{}".format(domain_result))
        self.write(json.dumps(domain_result))
        self.finish()