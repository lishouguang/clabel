# coding: utf-8

import logging

import numpy as np
import tensorflow as tf
from p2h.data_load import load_vocab
from p2h.data_load import load_test_string
from p2h.parameters import Parameters as P
from p2h.train import Graph


logger = logging.getLogger(__file__)

pnyn2idx, idx2pnyn, hanzi2idx, idx2hanzi = load_vocab()
logger.info('load vocab success.')


g = Graph(is_training=False)
with g.graph.as_default():
    sv = tf.train.Supervisor()
    # sess = sv.managed_session(config=tf.ConfigProto(allow_soft_placement=True))
    sess = tf.Session()
    # Restore parameters
    sv.saver.restore(sess, tf.train.latest_checkpoint(P.logdir))
    logger.info("Restored tensorflow model success.")


def p2h(pnyins):

    global g
    global sess

    x = load_test_string(pnyn2idx, pnyins)
    preds = sess.run(g.preds, {g.x: x})
    got = "".join(idx2hanzi[idx] for idx in preds[0])[:np.count_nonzero(x[0])].replace("_", "")

    return got.replace('U', '')
