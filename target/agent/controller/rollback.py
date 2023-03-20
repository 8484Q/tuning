import json

from tornado.web import RequestHandler

from agent.domain import getDomainObj, allActiveDomain
from agent.common.exception import unavaliableDomain, invalidDomain
from agent.common.pylog import logger


class RollbackHandler(RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)
        logger.debug("[Request] Get rollback request:{}".format(request_data))

        if not request_data:
            rollback_domain_list, rollback_all = allActiveDomain(), False
        elif request_data['all']:
            rollback_domain_list, rollback_all = allActiveDomain(), True
        else:
            rollback_domain_list, rollback_all = request_data['domains'] if request_data['domains'].__len__() != 0 else allActiveDomain(), False

        domain_result = {}
        if rollback_all:
            logger.debug("[Request] rollback domains all parameters:{}".format(rollback_domain_list))
        else:
            logger.debug("[Request] rollback domains:{}".format(rollback_domain_list))

        for domain_name in rollback_domain_list:
            try:
                suc, res = getDomainObj(domain_name).Rollback(all = rollback_all)
                domain_result[domain_name] = {"suc": suc,"msg": res}

            except unavaliableDomain as e:
                domain_result[domain_name] = {"suc": False, "msg": "{}".format(e)}

            except invalidDomain as e:
                domain_result[domain_name] = {"suc": False, "msg": "{}".format(e)}

            except Exception as e:
                domain_result[domain_name] = {"suc": False, "msg": "{}".format(e)}
            
        logger.debug("[Request] rollback request result:{}".format(domain_result))
        self.write(json.dumps(domain_result))
        self.finish()