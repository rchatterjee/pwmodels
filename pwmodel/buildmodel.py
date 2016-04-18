from collections import defaultdict
import helper
import dawg

import models

MIN_FREQ = 0.5


def create_ngram_model(fname='', listw=[], outfname='', n=3):

    return create_model(fname=fame, listw=listw, outfname=outfname,
                        modelfunc=lambda w: models.ngramsofw(w, n=3))

if __name__ == "__main__":
    import sys
    w = 'password@123'
    T = create_model(fname=sys.argv[1], listw=[], outfname='',
                 modelfunc=models.pcfgtokensofw)
    print prob(T, w, modelfunc=models.pcfgtokensofw)


