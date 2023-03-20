import os
import json

from tornado.web import RequestHandler

from bench.common.config import Config
from bench.common.pylog import functionLog


class SendfileHandler(RequestHandler):
    def post(self):
        request_data = json.loads(self.request.body)

        try:
            file_name = request_data["file_name"]
            file_encode = request_data["encode_type"]
            file_content = request_data["body"]

        except KeyError as error_key:
            self.write(json.dumps({
                "suc": False,
                "msg": "can not find key: {}".format(error_key)

            }))
            self.finish()

        else:
            suc, send_file_result = _sendFileImpl(
                file_path=file_name,
                file_encode=file_encode,
                file_content=file_content
            )

            self.write(json.dumps({
                "suc": suc,
                "msg": "{}".format(send_file_result)
            }))
            self.finish()


@functionLog
def _sendFileImpl(file_content, file_encode, file_path):
    """ Save file content to KeenTune work dir

    Args:
        file_content (str): file content to save.
        file_encode (str): file encode format.
        file_path (str): file save name.

    Returns:
        res: error msg
    """
    file_sub_path, file_name = os.path.split(file_path)

    file_local_folder = os.path.join(Config.FILES_PATH, file_sub_path)
    if not os.path.exists(file_local_folder):
        os.makedirs(file_local_folder)
    file_local_path = os.path.join(file_local_folder, file_name)

    with open(file_local_path, 'w', encoding=file_encode) as f:
        f.write(str(file_content))

    return True, file_local_path
