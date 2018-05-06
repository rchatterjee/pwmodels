from collections import defaultdict
import itertools

import helper
import dawg

import models

MIN_PROB = 1e-6


def prob(nDawg, w, modelfunc):
    t = float(nDawg.get('__TOTAL__'))
    return helper.prod(nDawg.get(ng, MIN_PROB) / t
                       for ng in modelfunc(w))


def read_dawg(fname):
    nDawg = dawg.IntCompletionDAWG(fname)
    nDawg.load(fname)
    return nDawg


def create_ngram_model(fname='', listw=[], outfname='', n=3):
    """Create a list of ngrams from a file @fname.  NOTE: the file must be
    in password file format.  See smaple/pw.txt file for the format.
    If the file is empty string, then it will try to read the
    passwords from the @listw which is a list of tuples [(w1, f1),
    (w2, f2)...]. (It can be an iterator.)  @n is again the 'n' of
    n-gram Writes the ngrams in a file at @outfname. if outfname is
    empty string, it will print the ngrams on a file named
    'ngrams.dawg'

    """

    return create_model(fname=fname, listw=listw, outfname=outfname,
                        modelfunc=lambda w: models.ngramsofw(n=3))


if __name__ == "__main__":
    import sys

    w = 'password@123'
    T = create_model(fname=sys.argv[1], listw=[], outfname='',
                     modelfunc=models.pcfgtokensofw)
    print(prob(T, w, modelfunc=models.pcfgtokensofw))
