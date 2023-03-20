import json

from tornado.web import RequestHandler

from agent.domain import getDomainObj
from agent.common.pylog import logger
from agent.common.system import httpResponse
from agent.common.exception import unavaliableDomain, invalidDomain


class ConfigureHandler(RequestHandler):
    def _configureImpl(self, param_domain_dict:dict, readonly:bool):
        domain_result = {}
        for domain_name, param_list in param_domain_dict.items():
            try:
                domain_obj = getDomainObj(domain_name)
                domain_result[domain_name] = dict(domain_obj.GetParam(param_list) if readonly \
                                            else domain_obj.SetParam(param_list))

            except unavaliableDomain as e:
                domain_result[domain_name] = "unvaliable domain '{domain_name}': {message}".format(
                    domain_name = domain_name,
                    message = "{}".format(e))

            except invalidDomain as e:
                domain_result[domain_name] = "invalid domain '{domain_name}': {message}".format(
                    domain_name = domain_name,
                    message = "{}".format(e))

            except Exception as e:
                domain_result[domain_name] = "Configure failed '{domain_name}': {message}".format(
                    domain_name = domain_name,
                    message = "{}".format(e))

        return domain_result

    def post(self):
        request_data = json.loads(self.request.body)
        self.write(json.dumps({"suc" : True, "msg" : ""}))
        self.finish()
        
        logger.debug("[Request] Get configure request:{}".format(request_data))
        res = self._configureImpl(request_data['data'], request_data['readonly'])

        response_data = {
            "data"      : res,
            "target_id" : request_data['target_id'], 
        }
        logger.debug("[Request] configure request result: {}".format(response_data))
        httpResponse(response_data, request_data['resp_ip'], request_data['resp_port'])
