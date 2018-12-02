import unittest
from pwmodel.fast_fuzzysearch import Fast2FuzzySearch, lvdistance


class TestPasswords(unittest.TestCase):
    def test_FastFuzzySearch(self):
        from pwmodel import helper
        import os
        import time
        import random
        import numpy as np
        fname = os.path.expanduser('~/passwords/rockyou-withcount.txt.gz')
        pws = list(set(
            str(pw)
            for pw, f in helper.open_get_line(fname, limit=10000000)
            if len(pw) > 10
        ))
        nidx = 10
        idxs = [random.randint(0, len(pws)) for _ in range(nidx)]
        eds = [0, 1, 2]
        # print list(ffs.ffs[1].words_with_prefix(tw)
        #            for tw in ffs.ffs[2][2].query('clover')))
        # raise AssertionError
        normalt, fastt = [], []
        print("Total words: {}".format(len(pws)))
        # d = pd.DataFrame(columns=['measure', 'mean', 'std']
        print("Approach\t\t Mean\t Std")

        for ed in eds:
            s = time.time()
            ffs = Fast2FuzzySearch(pws)
            print(("Creation time: {} microsec".format(ed, 1e6 * (time.time() - s))))
            for id_ in idxs:
                s = time.time()
                res1 = set(pw for pw in pws if lvdistance(pw, pws[id_], ed) <= ed)
                e = time.time()
                # print "\nNormal computation (ed={}) time: {:.3f} ms".format(ed, 1000*(e-s))
                normalt.append(1000 * (e - s))
                res2 = set(ffs.query(pws[id_], ed=ed))
                # print "FastFuzzy (ed={}) time: {:.3f} ms".format(ed, 1000*(time.time()-e))
                fastt.append(1000 * (time.time() - e))
                self.assertEqual(res1, res2,
                                 "Something went wrong.\nNaive-Fuzzy: {}\nFuzzy-Naive: {}"
                          .format(res1-res2, res2-res1))
            print("ed = {}".format(ed))
            print("Naive:\t\t {:.3f}\t {:.3f}".format(np.mean(normalt[-nidx:]),
                                                      np.std(normalt[-nidx:])))
            print("FuzzyFast:\t\t {:.3f}\t {:.3f}".format(np.mean(fastt[-nidx:]),
                                                          np.std(fastt[-nidx:])))

        print('=='*20)
        print("Average performance")
        print("Naive:\t\t {:.3f}\t {:.3f}".format(np.mean(normalt), np.std(normalt)))
        print("FuzzyFast:\t\t {:.3f}\t {:.3f}".format(np.mean(fastt), np.std(fastt)))
