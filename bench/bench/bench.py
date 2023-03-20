import tornado
import os

from bench.controller.sendfile import SendfileHandler
from bench.controller.benchmark import BenchmarkHandler
from bench.controller.status import StatusHandler, AvaliableDomainHandler

from bench.common.config import Config


""" 
KeenTune-bench main function.  

KeenTune-bench running in an auxiliary environment distinguished from tunning target environment.

This environment is used for running benchmark script to target environment to calculate the performance score of target environment with specified parameter configuration
"""


def main():
    app = tornado.web.Application(handlers=[
        (r"/sendfile", SendfileHandler),
        (r"/benchmark", BenchmarkHandler),
        (r"/status", StatusHandler),
        (r"/avaliable", AvaliableDomainHandler)
    ])
    app.listen(Config.BENCH_PORT)
    print("KeenTune bench running at port {}...".format(Config.BENCH_PORT))
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        os._exit(0)