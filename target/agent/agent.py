""" 
KeenTune Agent main function.  

"""
import tornado
import os

from agent.common.config import Config
from agent.domain import initDomain

from agent.controller.backup import BackupHandler
from agent.controller.configure import ConfigureHandler
from agent.controller.method import MethodHandler
from agent.controller.rollback import RollbackHandler
from agent.controller.status import StatusHandler, AvaliableDomainHandler


def main():
    initDomain()
    app = tornado.web.Application(handlers=[
        (r"/backup", BackupHandler),
        (r"/status", StatusHandler),
        (r"/rollback", RollbackHandler),
        (r"/configure", ConfigureHandler),
        (r"/method", MethodHandler),
        (r"/avaliable", AvaliableDomainHandler),
    ])
    app.listen(Config.TARGET_PORT)
    print("KeenTune-Target running...")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        os._exit(0)