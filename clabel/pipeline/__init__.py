# # coding: utf-8
#
# import os
# import logging
#
# from clabel.helper import utils
# from clabel.config import RESOURCE_DIR
# from clabel.config import FREQUENT_MIN_SUPPORT
#
# from .sample import create as create_sample
# from .clean import clean_file as clean_sample
# from .sentence_parser import pos as create_pos
# from .sentence_parser import correct_pos as correct_pos
# from .ssplit import create as create_ssplit
# from .transaction import create as create_tx
# from .frequent import create as find_frequents
#
# from .prune import run_prune
#
#
# class Pipeline(object):
#
#     def __init__(self):
#         # self.sample_file = os.path.join(RESOURCE_DIR, 'xmobile.sample')
#         # self.posed_file = os.path.join(RESOURCE_DIR, 'xmobile.sample.posed')
#         # self.ssplit_file = os.path.join(RESOURCE_DIR,'xmobile.sample.ssplited')
#         # self.tx_file = os.path.join(RESOURCE_DIR, 'xmobile.sample.tx.basket')
#
#         self.all_sample_file = os.path.join(RESOURCE_DIR, 'all.sample')
#         self.sample_file = os.path.join(RESOURCE_DIR, 'mobile.sample')
#         self.clean_file = os.path.join(RESOURCE_DIR, 'mobile.sample.clean')
#         self.posed_file = os.path.join(RESOURCE_DIR, 'mobile.sample.posed')
#         self.cposed_file = os.path.join(RESOURCE_DIR, 'mobile.sample.cposed')
#         self.ssplit_file = os.path.join(RESOURCE_DIR, 'mobile.sample.ssplited')
#         self.tx_file = os.path.join(RESOURCE_DIR, 'mobile.sample.tx.basket')
#
#     def run(self):
#         # create_sample('手机/手机', self.all_sample_file, self.sample_file)
#         # clean_sample(self.sample_file, self.clean_file)
#         # create_pos(self.clean_file, self.posed_file)
#         # correct_pos(self.posed_file, self.cposed_file)
#
#         create_ssplit(self.cposed_file, self.ssplit_file)
#         create_tx(self.ssplit_file, self.tx_file)
#
#         frequents = find_frequents(self.tx_file, min_support=FREQUENT_MIN_SUPPORT)
#         logging.info('frequent itemsets: %d', len(frequents))
#
#         utils.save_obj(frequents, os.path.join(RESOURCE_DIR, 'mobile.itemsets'))
#
#         pruned = run_prune([terms for terms, _ in frequents], self.ssplit_file, self.tx_file)
#         logging.info('frequent itemsets after pruning: %d', len(pruned))
#
#         utils.save_obj(pruned, os.path.join(RESOURCE_DIR, 'mobile.itemsets.pruned.1'))
#
#         # for terms, _ in frequents:
#         #     if terms not in pruned:
#         #         print terms
#         for x in pruned:
#             print x
