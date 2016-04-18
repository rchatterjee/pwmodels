import os
from buildmodel import create_model, read_dawg
import helper


class NGramPw(object):
    """Create a list of ngrams from a file @fname.  NOTE: the file must be
    in password file format.  See smaple/pw.txt file for the format.
    If the file is empty string, then it will try to read the
    passwords from the @listw which is a list of tuples [(w1, f1),
    (w2, f2)...]. (It can be an iterator.)  @n is again the 'n' of
    n-gram Writes the ngrams in a file at @outfname. if outfname is
    empty string, it will print the ngrams on a file named
    'ngrams.dawg'

    """

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
                                       modelfunc=self.ngramsofw)

    def cprob(self, c, history):
        """
        :param history: string
        :param c: character
        P[c | history] = f(historyc)/f(history)
        returns P[c | history]
        """
        if len(history)>=self._n:
            history = history[-(self._n-1):]
        d = float(sum(v for k,v in self._T.iteritems(unicode(history))))
        n = sum(v for k,v in self._T.iteritems(unicode(history+c)))  # TODO - implement backoff
        assert d!=0, "Denominator zero: {} {} ({})".format(c, history, self._n)
        print "{}+{} --> {}".format(history, c, n/d)
        return n/d
    
    def ngramsofw(self, word):
        """Returns the @n-grams of a word @w
        """
        word = helper.START + word + helper.END
        n = self._n
        if len(word)<=n:
            return [word]
        
        return [word[i:i+n]
                for i in xrange(0, len(word)-n+1)]

    def prob(self, pw):
        pw = helper.START + pw + helper.END
        return helper.prod(self.cprob(pw[i], pw[:i])
                    for i in xrange(self._n-1, len(pw)))

