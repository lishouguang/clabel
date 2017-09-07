# coding: utf-8

import logging
import Orange

logger = logging.getLogger(__file__)


def create(bsk_file, min_support):

    logger.info('to find frequent itemsets...')
    logging.info('min support: %f' % min_support)

    data = Orange.data.Table(bsk_file)
    logger.info('the number of transaction records is %d' % len(data))

    inducer = Orange.associate.AssociationRulesSparseInducer(support=min_support, storeExamples=True)
    itemsets = inducer.get_itemsets(data)

    frequents = []
    for itemset, tids in itemsets:
        terms = " ".join(data.domain[item].name for item in itemset)
        min_support = len(tids) / float(len(data))
        frequents.append((terms, min_support))

    frequents = sorted(frequents, key=lambda ts: ts[1], reverse=True)
    logger.info('find frequent itemsets %d' % len(frequents))

    return frequents
