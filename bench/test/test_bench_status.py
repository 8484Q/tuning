import json
import requests
import unittest


class TestBenchStatus(unittest.TestCase):
    def setUp(self) -> None:
        self.proxies={"http": None, "https": None}
        url = "http://{}:{}/status".format("localhost", "9874")
        re = requests.get(url, proxies=self.proxies)
        if re.status_code != 200:
            print("ERROR: Can't reach KeenTune-Bench.")
            exit()

    def tearDown(self) -> None:
        pass

    def test_bench_server_FUN_status(self):
        url = "http://{}:{}/{}".format("localhost", "9874", "status")
        result = requests.get(url, proxies=self.proxies)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.text, '{"status": "alive"}')
