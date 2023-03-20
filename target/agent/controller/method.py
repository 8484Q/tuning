import json

from agent.common.pylog import logger
from agent.plugin import methods
from tornado.web import RequestHandler


MethodList = {
    "check_net_queue_count":methods.check_net_queue_count,
    "cpulist_invert": methods.cpulist_invert,
    "cpulist_online": methods.cpulist_online,
    "cpulist_unpack": methods.cpulist_unpack,
    "cpulist2hex_invert":methods.cpulist2hex_invert,
    "cpulist2hex":methods.cpulist2hex,
    "exec":methods.execute,
    "regex_search_ternary":methods.regex_search_ternary,
    "strip":methods.strip,
    "cpu_core":methods.cpu_core,
    "mem_total":methods.mem_total,
    "mem_free":methods.mem_free,
    "uname_arch":methods.uname_arch,
    "thunderx_cpu_info":methods.thunderx_cpu_info,
    "amd_cpu_model":methods.amd_cpu_model,
    "os_release":methods.os_release,
    "virt":methods.virt,
    "system":methods.system   
}


class MethodHandler(RequestHandler):
    def methodExec(self, method_name, method_args):
        actual_method_args = []
        for arg in method_args:
            if isinstance(arg, dict) and arg.__contains__('method_name'):
                actual_arg = self.methodExec(
                    method_name = arg['method_name'], 
                    method_args = arg['method_args'])
                actual_method_args.append(actual_arg)
            else:
                actual_method_args.append(arg)
                
        logger.info("execute method {method_name}: {method_args}".format(
                    method_name = method_name,
                    method_args = actual_method_args))
        result = MethodList[method_name](args = actual_method_args)
        if isinstance(result, str):
            result = result.strip()
        
        logger.info("return method {method_name}: {result}".format(
                    method_name = method_name,
                    result = result))
        
        return result
    
    def post(self):
        """ Backup parameters value to backup file
        """
        request_data = json.loads(self.request.body)
        logger.debug("[Request] Get method request:{}".format(request_data))

        methods_result = []
        for funcobj in request_data:
            try:
                result = self.methodExec(
                    method_name = funcobj['method_name'], 
                    method_args = funcobj['method_args'])
                
            except Exception as e:
                methods_result.append({
                    "suc": False,
                    "res": "{}".format(e)
                })

            else:
                methods_result.append({
                    "suc": True,
                    "res": result
                })

        logger.debug("[Request] method request result:{}".format(methods_result))
        self.write(json.dumps(methods_result))
        self.finish()