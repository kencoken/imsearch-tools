import os
import sys

file_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(file_dir, '..', '..', 'imsearch-tools'))
from imsearchtools import query as image_query

import requests
import re

class TestBingAPI(object):

    def setup(self):
        self._gws = image_query.BingAPISearchV5(False)
        self._q = 'polka dots'

    def test_query(self):
        res = self._gws.query(self._q, num_results=10)
        print res

    def test_images_returned(self):
        res = self._gws.query(self._q, num_results=100)
        assert len(res) == 100

test = TestBingAPI()
test.setup()
test.test_images_returned()

