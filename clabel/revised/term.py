# coding: utf-8

from common import utils


class RevisedTerm(object):

    def __init__(self, f):
        lines = utils.read_file(f)

        self._clusters = {}

        for line in lines:
            if line.startswith('='):
                continue

            terms = [f for f in line.split(' ') if f.strip() != '']
            self._clusters[terms[0]] = set(terms)

        self._terms = set()
        for head in self._clusters:
            for feature in self._clusters[head]:
                self._terms.add(feature)

    def get_head(self, term):
        for head in self._clusters:
            if term in self._clusters[head]:
                return head
        return None

    def get_heads(self):
        return list(self._clusters.keys())

    def is_term(self, t):
        return t in self._terms
