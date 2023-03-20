import json
import requests
import unittest


class TestBenchAvailable(unittest.TestCase):
    def setUp(self) -> None:
        self.proxies={"http": None, "https": None}
        url = "http://{}:{}/status".format("localhost", "9874")
        re = requests.get(url, proxies=self.proxies)
        if re.status_code != 200:
            print("ERROR: Can't reach KeenTune-Bench.")
            exit()

    def tearDown(self) -> None:
        pass

    def test_bench_server_FUN_available(self):
        url = "http://{}:{}/{}".format("localhost", "9874", "avaliable")
        data = {
            "agent_address": "localhost"
        }

        headers = {"Content-Type": "application/json"}
        result = requests.post(url, data=json.dumps(data), headers=headers, proxies=self.proxies)
        self.assertEqual(result.status_code, 200)
        self.assertIn('{"localhost": true}', result.text)
