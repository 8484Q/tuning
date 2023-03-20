import json
import requests
import unittest


class TestBenchBenchmark(unittest.TestCase):
    def setUp(self) -> None:
        self.proxies={"http": None, "https": None}
        url = "http://{}:{}/status".format("localhost", "9874")
        re = requests.get(url, proxies=self.proxies)
        if re.status_code != 200:
            print("ERROR: Can't reach KeenTune-Bench.")
            exit()
            
        url = "http://{}:{}/{}".format("localhost", "9874", "sendfile")
        data = {
            "file_name":"demo.sh",
            "encode_type":"utf-8",
            "body":"echo a=1"
            }

        headers = {"Content-Type": "application/json"}
        
        result = requests.post(url, data=json.dumps(data), headers=headers, proxies=self.proxies)
        self.assertEqual(result.status_code, 200)
        self.assertIn('"suc": true', result.text)
 
    def tearDown(self) -> None:
        pass

    def test_bench_server_FUN_benchmark(self):
        url = "http://{}:{}/{}".format("localhost", "9874", "benchmark")
        data = {
            "bench_id": 1,
            "resp_ip": "localhost",
            "resp_port": "9871",
            "benchmark_cmd":"bash demo.sh",
            "round": 1
        }

        headers = {"Content-Type": "application/json"}
        
        result = requests.post(url, data=json.dumps(data), headers=headers, proxies=self.proxies)
        self.assertEqual(result.status_code, 200)
        self.assertIn('"suc": true', result.text)
