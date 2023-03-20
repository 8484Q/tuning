import json

from tornado.web import RequestHandler
from bench.common.system import checkAddressAvaliable


class StatusHandler(RequestHandler):
    def get(self):
        back_json = {"status": "alive"}
        self.write(json.dumps(back_json))
        self.finish()


class AvaliableDomainHandler(RequestHandler):
    def post(self):
        """ Check if ip address is touchable
        
        request data : 
        {
            'agent_address':['address1','address2']
        }
        or 
                {
            'agent_address':'address1'
        }
        
        response data:
        {
            'address1':True,
            'address2':False
        }
        """
        request_data = json.loads(self.request.body)
        agent_address = request_data['agent_address']
        if not isinstance(agent_address, list):
            agent_address = [agent_address]
        result = checkAddressAvaliable(agent_address)
        self.write(json.dumps(result))
        self.finish()