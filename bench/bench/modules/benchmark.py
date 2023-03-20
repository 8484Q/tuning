from statistics import mean
from collections import defaultdict

from bench.common.system import sysCommand
from bench.common.pylog import logger


def _parseBenchmarkResult(benchmark_result: str):
    benchmark_result_dict = {}
    for equation in benchmark_result.split(","):
        name  = equation.split("=")[0].strip()
        value = equation.split("=")[1].strip()
        benchmark_result_dict[name] = float(value)

    return benchmark_result_dict


def runBenchmark(benchmark_cmd: str, round: int):
    """ run benchmark script.

    Args:
        benchmark_cmd (str): run benchmark command.

    Returns:
        str: benchmark result or error message.
    """
    logger.info("Benchmark cmd = {}".format(benchmark_cmd))
    benchmark_result = defaultdict(list)
    for i in range(round):
        try:
            suc, res = sysCommand(benchmark_cmd)
            if not suc:
                return "Execute the Benchmark script {} failed:{}".format(benchmark_cmd, res)
            
            _result = _parseBenchmarkResult(res)
            logger.info("Run Benchmark in round {}/{}: {}".format(i+1, round, _result))

        except IndexError:
            return False, "invalid output data of benchmark script! :'{}'".format(res)

        except Exception as e:
            return False, "An unknown error occurred! :{}".format(e)

        else:
            for k in _result.keys():
                benchmark_result[k].append(_result[k])
    
    for k in benchmark_result.keys():
        benchmark_result[k] = mean(benchmark_result[k])
    logger.info("Average benchmark result : {}".format(benchmark_result))
    return True, benchmark_result
