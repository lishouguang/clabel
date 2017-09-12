# coding: utf-8

import os
import unittest

from avro import schema
from avro.io import DatumReader
from avro.io import DatumWriter
from avro.datafile import DataFileReader
from avro.datafile import DataFileWriter

from clabel.config import TMP_DIR


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    data_schema = {
        "namespace": "clable.bi.meizu.com",
        "name": "User",
        "type": "record",
        "fields": [{
            "name": "name",
            "type": "string"
        }, {
            "name": "age",
            "type": "int"
        }]
    }

    def test_avro_write(self):
        self.assertTrue(True)

        schema_file = os.path.join(TMP_DIR, 'user.avsc')
        data_file = os.path.join(TMP_DIR, 'user.avro')
        with open(schema_file, 'rb') as sf, open(data_file, 'wb') as df:
            data_schema = schema.parse(sf.read())

            writer = DataFileWriter(df, DatumWriter(), data_schema)
            writer.append({'name': 'lisg', 'age': 30})
            writer.append({'name': 'zhangsan', 'age': 28})

            writer.close()

    def test_avro_read(self):
        self.assertTrue(True)

        data_file = os.path.join(TMP_DIR, 'user.avro')

        with open(data_file, 'rb') as df:
            reader = DataFileReader(df, DatumReader())
            for user in reader:
                print(user)
            reader.close()

    def test_x(self):
        self.assertTrue(True)

        from clabel.pipeline import sentence_parser
        from clabel.config import RESOURCE_DIR

        clean_file = os.path.join(RESOURCE_DIR, 'clean', 'mobile.sample.clean.min')
        relation_file = os.path.join(RESOURCE_DIR, 'relation', 'sents.min.avro')
        sentence_parser.parse(clean_file, relation_file)

    def test_y(self):
        self.assertTrue(True)

        from fastavro import reader as avro_reader

        from clabel.pipeline import sentence_parser
        from clabel.config import RESOURCE_DIR

        i = 0
        relation_file = os.path.join(RESOURCE_DIR, 'relation', 'sents.min.avro')
        with open(relation_file, 'rb') as df:
            for pinglun in avro_reader(df):
                # txt = pinglun['txt']
                for sent in pinglun['sents']:
                    i += 1
                    # if i < 1000:
                    print(sent['sent'])
                    print(sent['relations'])

if __name__ == '__main__':
    unittest.main()
