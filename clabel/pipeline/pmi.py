# coding: utf-8

import logging
import math

import requests

from clabel.config import PMI_SEARCH_URL
from . import db

logger = logging.getLogger(__file__)


def get_polar(word):

    context, opinion = '', ''

    words = word.split('_')
    if len(words) == 1:
        opinion = words[0]
    else:
        context, opinion = '_'.join(words[:-1]), words[-1]

    polar = db.query(context, opinion)

    if polar is None:
        good_hits, poor_hits = search_single()
        logger.debug('good_hits: %d, poor_hits: %d' % (good_hits, poor_hits))

        phrase_good_hits, phrase_poor_hits = search_join(word)
        logger.debug('word: %s, phrase_good_hits: %d, phrase_poor_hits: %d' % (word, phrase_good_hits, phrase_poor_hits))

        if phrase_poor_hits == 0 or phrase_good_hits == 0:
            polar = 'x'
        else:
            pmi = calc_pmi(good_hits, poor_hits, phrase_good_hits, phrase_poor_hits)
            polar = '+' if pmi > 0 else '-'

        db.insertOrUpdate(context, opinion, polar)

    return polar


def search_single():
    if GOOD_HITS is not None and POOR_HITS is not None:
        return GOOD_HITS, POOR_HITS
    else:
        response = requests.post(PMI_SEARCH_URL % 'single').json()
        good, poor = response['good'], response['poor']
        return good, poor


def search_join(word):
    response = requests.post(PMI_SEARCH_URL % 'join', data={'q': word}).json()
    good, poor = response['good'], response['poor']
    return good, poor


def calc_pmi(good_hits, poor_hits, phrase_good_hits, phrase_poor_hits):
    return math.log((1.0 * phrase_good_hits * poor_hits) / (phrase_poor_hits * good_hits), 2)


GOOD_HITS = None
POOR_HITS = None
