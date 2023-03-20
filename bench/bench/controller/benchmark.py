import os
import json

from tornado.web import RequestHandler

from bench.modules import benchmark
from bench.common.config import Config
from bench.common.system import httpResponse


class BenchmarkHandler(RequestHandler):
    def _runBenchmark(self, bench_cmd: str, round: int = 1):
        benchcmd_list = bench_cmd.split()
        benchcmd_list[1] = os.path.join(Config.FILES_PATH, benchcmd_list[1])
        bench_cmd_local = " ".join(benchcmd_list)
        return benchmark.runBenchmark(bench_cmd_local, round)

    def post(self):
        request_data = json.loads(self.request.body)
        self.write(json.dumps({"suc" : True, "msg": "Benchmark is Runing"}))
        self.finish()
        
        suc, res = self._runBenchmark(
                bench_cmd = request_data['benchmark_cmd'], 
                round     = request_data['round'])
        
        response_data = {
            "suc": suc, 
            "result": res, 
            "msg": res, 
            "bench_id": request_data['bench_id']}

        httpResponse(response_data, request_data['resp_ip'], request_data['resp_port'])