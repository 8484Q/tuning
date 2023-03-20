import json
import requests
import unittest


class TestTargetAvailable(unittest.TestCase):
    def setUp(self) -> None:
        self.proxies={"http": None, "https": None}
        url = "http://{}:{}/status".format("localhost", "9873")
        re = requests.get(url, proxies=self.proxies)
        if re.status_code != 200:
            print("ERROR: Can't reach KeenTune-Target.")
            exit()

    def tearDown(self) -> None:
        pass

    def test_target_server_FUN_available(self):
        url = "http://{}:{}/{}".format("localhost", "9873", "avaliable")
        result = requests.get(url, proxies=self.proxies)
        self.assertEqual(result.status_code, 200)
        self.assertIn('{"result": ["sysctl"', result.text)
