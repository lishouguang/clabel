# coding: utf-8

import os
import jpype
from logging import config as logconfig


APP_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(APP_DIR)
RESOURCE_DIR = os.path.join(ROOT_DIR, 'zresource')
TMP_DIR = os.path.join(RESOURCE_DIR, 'tmp')

APP_RESOURCE_DIR = os.path.join(RESOURCE_DIR, os.path.basename(APP_DIR))

logconfig.fileConfig(os.path.join(ROOT_DIR, 'logging.ini'))


LM_MODEL_DIR = os.path.join(APP_RESOURCE_DIR, 'model', 'berkerley')
jars_lm = [os.path.join(LM_MODEL_DIR, 'lm.jar'), os.path.join(LM_MODEL_DIR, 'berkeleylm.jar')]

separator = ';' if sys.platform.startswith('win') else ':'
classpath = separator.join(jars_lm)
classpath_option = '-Djava.class.path=' + classpath
# -Dfile.encoding=UTF8
jpype.startJVM(jpype.getDefaultJVMPath(), classpath_option, '-Xrs', '-Xmx1024m')
