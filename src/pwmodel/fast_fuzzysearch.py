"""
Use dawg to speed up fuzzy search
"""
import itertools

import dawg
from Levenshtein import distance
from polyleven import levenshtein as lvdistance


def fast_fuzzysearch(words, ed):
    if ed == 1:
        return Fast1FuzzySearch(words)
    elif ed == 2:
        return Fast2FuzzySearch(words)
    else:
        raise ValueError("Currently only supports edit distance up to 2")


class Fast2FuzzySearch(object):
    """
    Fuzzy sttring matching for arbitrary edit distance. (ed<=4) is useful.
    After that distance is faster. 
    """
    _ed = 2

    def __init__(self, words):
        self.ffs = {
            1: Fast1FuzzySearch(words)
        }
        modified_words = list(zip(*[
            #    wL          wR           rmL     rmF
            (w[:len(w) // 2], w[len(w) // 2:], w[:-1], w[1:])
            for w in words
        ]))
        self.ffs[2] = [Fast1FuzzySearch(ws) for ws in modified_words]

    def query(self, w, ed=2):
        assert ed <= self._ed
        w = str(w)
        n = len(w)
        res_iter_list = []
        if ed <= 1:
            return self.ffs[1].query(w, ed)

        # 0 error on prefix, 2 no suffix
        res_iter_list.append(self.ffs[1].words_with_prefix(w[:n // 2]))
        # 1 error on left 
        res_iter_list.extend(
            self.ffs[1].words_with_prefix(tw)
            for tw in self.ffs[2][0].query(w[:n // 2])
        )
        # 1 error on right
        res_iter_list.extend(
            self.ffs[1].words_with_suffix(tw)
            for tw in self.ffs[2][1].query(w[n // 2:])
        )
        # first character deleted or replaced
        res_iter_list.extend(
            self.ffs[1].words_with_prefix(tw)
            for tw in self.ffs[2][2].query(w[1:])
        )
        # Last character deleted or replaced
        res_iter_list.extend(
            self.ffs[1].words_with_suffix(tw)
            for tw in self.ffs[2][2].query(w[:-1])
        )
        # 2 error on prefix, 0 on suffix
        res_iter_list.append(self.ffs[1].words_with_suffix(w[n // 2:]))

        all_options = set(w for iter_ in res_iter_list for w in iter_)
        # print "Len options to explore: {}".format(len(all_options))
        return [
            _w
            for _w in all_options
            if abs(len(_w) - len(w)) <= self._ed and 
            lvdistance(_w, w, self._ed) <= self._ed
        ]


class Fast1FuzzySearch(object):
    """This is an implementation of fuzzy string matching using dawgs.
    Good for only edit distance 1.  Idea is for the query take word
    and look at words with similar prifix, or the ones with simlar
    suffix. We are looking for words at distance 1, so, the edit must
    be either on the first half of the word, or on the last half, and
    we can safely check that using prefix, and suffix match.
    """
    _ed = 1

    def __init__(self, words):
        # good for 1 edit distance
        self._L, self._R = self._process_list(list(set(words)))

    def _process_list(self, words):
        rev_words = [w[::-1] for w in words]
        norm_dawg = dawg.CompletionDAWG(words)
        rev_dawg = dawg.CompletionDAWG(rev_words)
        return norm_dawg, rev_dawg

    def words_with_prefix(self, prefix):
        return self._L.iterkeys(str(prefix))

    def words_with_suffix(self, suffix):
        return (w[::-1] for w in self._R.iterkeys(str(suffix[::-1])))

    def query(self, w, ed=1):  # Can only handle ed=1
        """
        Finds the fuzzy matches (within edit distance 1) of w from words 
        """
        assert ed <= self._ed
        if ed == 0:
            return [w] if w in self._L else ['']
        w = str(w)
        n = len(w)
        prefix, suffix = w[:n // 2], w[n // 2:][::-1]
        options_w_prefix = self._L.keys(prefix)
        options_w_suffix = [x[::-1] for x in self._R.iterkeys(suffix)]
        return [
            _w
            for _w in set(itertools.chain(options_w_prefix, options_w_suffix))
            if abs(len(_w) - len(w)) <= 1 and lvdistance(str(_w), str(w), 1) <= 1
        ]


if __name__ == "__main__":
    test_FastFuzzySearch()
