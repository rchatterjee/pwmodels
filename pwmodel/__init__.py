from .models import *
from .buildmodel import create_model, prob, read_dawg

import os

class NGramPw(object):
    def __init__(self, pwfilename, n=3):
        leak = os.path.basename(pwfilename).split('-')[0]
        ngrampwf = '{}/data/ngram-{}-{}.dawg'\
                   .format(os.path.dirname(__file__), n, leak)
        self._n = n
        try:
            self._T = read_dawg(ngrampwf)
        except IOError:
            print "I could not find the file ({}).\nHang on I "\
                "am creating the ngram model for you!"\
                .format(ngrampwf)
            with open(ngrampwf, 'wb') as f:
                self._T = create_model(fname=pwfilename, outfname=ngrampwf,
                                       modelfunc=self.modelfunc)
    def modelfunc(self, pw):
        return ngramsofw(pw, n=self._n)

    def prob(self, pw):
        return prob(self._T, pw, self.modelfunc)

