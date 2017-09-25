# coding: utf-8

import os
import re
import unittest

from sbd.config import RESOURCE_DIR
from sbd.config import APP_RESOURCE_DIR
from common.utils import iter_file
from common.utils import write_file
from sbd.sbd import SBDModel


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_sbd_train(self):
        self.assertTrue(True)

        model = SBDModel(os.path.join(RESOURCE_DIR, 'mobile', 'std.min.txt'))
        model._build_ctable()
        model.train()
        model.save()

    def test_sbd(self):
        self.assertTrue(True)

        model = SBDModel.load(keras_model_file=os.path.join(APP_RESOURCE_DIR, 'sbd.keras.model'))

        lines = []
        for line in iter_file(os.path.join(RESOURCE_DIR, 'tmp', 'comment.mobile.txt')):
            words = re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5]', line)
            sent = ''.join(words)
            # sequence = model.predict_sequence(sent)
            pline = model.predict_txt(sent)
            lines.append('{} -> {}'.format(line, pline))
            print('{} -> {}'.format(line, pline))

        write_file(os.path.join(RESOURCE_DIR, 'tmp', 'sbd.result.txt'), lines)


if __name__ == '__main__':
    unittest.main()
