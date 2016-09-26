import json
import os
import time

from sprig import Sprig, MenuNotAvailable


def mock_sprig():
    def _request(self, key, params=None, query=None):
        path = os.path.dirname(os.path.realpath(__file__))
        content = open(os.path.join(path, "%s.json" % key)).read()
        return json.loads(content)

    Sprig._request = _request
