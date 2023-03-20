import os
import unittest

from test_bench_sendfile import TestBenchSendfile
from test_bench_benchmark import TestBenchBenchmark
from test_bench_status import TestBenchStatus
from test_bench_available import TestBenchAvailable


def RunModelCase():
    suite = unittest.TestSuite()
    suite.addTest(TestBenchSendfile('test_bench_server_FUN_sendfile'))
    suite.addTest(TestBenchBenchmark('test_bench_server_FUN_benchmark'))
    suite.addTest(TestBenchStatus('test_bench_server_FUN_status'))
    suite.addTest(TestBenchAvailable('test_bench_server_FUN_available'))
    return suite


if __name__ == '__main__':
    print("--------------- start to run test cases ---------------")
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(RunModelCase())
    print("--------------- run test cases end ---------------")
