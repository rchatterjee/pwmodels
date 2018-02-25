import heapq
import os
from collections import defaultdict
import operator
import dawg

from . import helper
from .fast_fuzzysearch import fast_fuzzysearch


def create_model(modelfunc, fname='', listw=[], outfname=''):
    """:modelfunc: is a function that takes a word and returns its
    splits.  for ngram model this function returns all the ngrams of a
    word, for PCFG it will return te split of the password.
    @modelfunc: func: string -> [list of strings]
    @fname: name of the file to read from
    @listw: list of passwords. Used passwords from both the files and
            listw if provided.
    @outfname: the file to write down the model.
    """
    pws = []
    if fname:
        pws = helper.open_get_line(fname, limit=3e6)

    def join_iterators(_pws, listw):
        for p in _pws: yield p
        for p in listw: yield p

    big_dict = defaultdict(int)
    total_f, total_e = 0, 0
    for pw, c in join_iterators(pws, listw):
        for ng in modelfunc(pw):
            big_dict[ng] += c
        if len(big_dict) % 100000 == 0:
            print(("Dictionary size: {}".format(len(big_dict))))
        total_f += c
        total_e += 1
    big_dict['__TOTAL__'] = total_e
    big_dict['__TOTALF__'] = total_f

    nDawg = dawg.IntCompletionDAWG(big_dict)
    if not outfname:
        outfname = 'tmpmodel.dawg.gz'
    elif not outfname.endswith('.gz'):
        outfname += '.gz'
    helper.save_dawg(nDawg, outfname)
    return nDawg


# def prob(nDawg, w, modelfunc):
#     t = float(nDawg.get('__TOTAL__'))
#     print '\n'.join("{} -> {}".format(ng, nDawg.get(ng, MIN_FREQ))
#                        for ng in modelfunc(w))

#     return helper.prod(nDawg.get(ng, MIN_FREQ)/t
#                        for ng in modelfunc(w))


def read_dawg(fname):
    print(("reading {fname}".format(fname=fname)))
    return helper.load_dawg(fname, dawg.IntCompletionDAWG)


def get_data_path(fname):
    data_dir = os.path.join(helper.home, '.pwmodel')
    if helper.DEBUG:
        data_dir = os.path.join(helper.thisdir, 'data')
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    return os.path.join(data_dir, fname)


class PwModel(object):
    def __init__(self, pwfilename=None, **kwargs):
        self._leak = os.path.basename(pwfilename).split('-')[0]
        freshall = kwargs.get('freshal', False)
        self.modelname = kwargs.get('modelname', 'ngram-0')
        self._modelf = get_data_path(
            '{}-{}.dawg.gz'.format(self._leak, self.modelname)
        )
        if freshall:
            os.remove(self._modelf)
        try:
            self._T = read_dawg(self._modelf)
        except IOError as ex:
            print(("I could not find the file ({}).\nHang on I "
                   "am creating the {} model for you!\nex={}"
                   .format(self._modelf, self.modelname, ex)))
            self._T = create_model(
                fname=pwfilename, outfname=self._modelf,
                modelfunc=kwargs.get('modelfunc', self.modelfunc)
            )

    def modelfunc(self, w):
        raise Exception("Not implemented")

    def prob(self, word):
        return -1

    def qth_pw(self, q):
        """
        returns the qth most probable element in the dawg.
        """
        return heapq.nlargest(q + 2, self._T.items(),
                              key=operator.itemgetter(1))[-1]

    def get(self, pw):
        return self.prob(pw)

    def __str__(self):
        return 'Pwmodel<{}-{}>'.format(self.modelname, self._leak)

    def leakname(self):
        return self._leak


################################################################################
MIN_PROB = 1e-10


class PcfgPw(PwModel):
    """Creates a pcfg model from the password in @pwfilename. 
    """

    def __init__(self, pwfilename, **kwargs):
        kwargs['modelfunc'] = self.pcfgtokensofw
        kwargs['modelname'] = 'weir-pcfg'
        super(PcfgPw, self).__init__(pwfilename=pwfilename, **kwargs)

    def pcfgtokensofw(self, word):
        """This splits the word into chunks similar to as described in Weir
        et al Oakland'14 paper.
        E.g.,
        >> ngrampw.pcfgtokensofw('password@123')
        ['password', '@', '123', '__L8__', '__Y1__', '__D3__']

        """
        tok = helper.tokens(word)

        sym = ['__{0}{1}__'.format(helper.whatchar(w), len(w))
               for w in tok]
        S = ['__S__' + ''.join(sym).replace('_', '') + '__']
        return S + sym + tok

    def tokprob(self, tok, nonT):
        """
        return P[nonT -> tok], 
        e.g., P[ W3 -> 'abc']
        """

        p = self._T.get(tok, 0) / float(self._T.get(nonT, 1))
        if not p:
            p = MIN_PROB
        return p

    def prob(self, pw):
        """
        Return the probability of pw under the Weir PCFG model.
        P[{S -> L2D1Y3, L2 -> 'ab', D1 -> '1', Y3 -> '!@#'}]
        """

        tokens = self.pcfgtokensofw(pw)
        S, tokens = tokens[0], tokens[1:]
        l = len(tokens)
        assert l % 2 == 0, "Expecting even number of tokens!. got {}".format(tokens)

        p = float(self._T.get(S, 0.0)) / sum(v for k, v in self._T.items('__S__'))
        for i, t in enumerate(tokens):
            f = self._T.get(t, 0.0)
            if f == 0:
                return 0.0
            if i < l / 2:
                p /= f
            else:
                p *= f
                # print pw, p, t, self._T.get(t)
        return p


################################################################################


class NGramPw(PwModel):
    """Create a list of ngrams from a file @fname.  NOTE: the file must be
    in password file format.  See smaple/pw.txt file for the format.
    If the file is empty string, then it will try to read the
    passwords from the @listw which is a list of tuples [(w1, f1),
    (w2, f2)...]. (It can be an iterator.)  @n is again the 'n' of
    n-gram Writes the ngrams in a file at @outfname. if outfname is
    empty string, it will print the ngrams on a file named
    'ngrams.dawg'
    :param pwfilename: a `password' file
    :param n: an integer (NOTE: you should provide a `n`.  `n` is default to 3)
    """

    def __init__(self, pwfilename, **kwargs):
        kwargs['modelfunc'] = self.ngramsofw
        kwargs['n'] = kwargs.get('n', 3)
        kwargs['modelname'] = 'ngram-{}'.format(kwargs['n'])
        self._n = kwargs.get('n', 3)
        super(NGramPw, self).__init__(pwfilename=pwfilename, **kwargs)

    @helper.memoized
    def sum_freq(self, pre):
        if not isinstance(pre, str):
            pre = str(pre)
        return float(sum(v for k, v in self._T.items(pre)))

    def cprob(self, c, history):
        """
        :param history: string
        :param c: character
        P[c | history] = f(historyc)/f(history)
        returns P[c | history]
        """
        hist = history[:]
        if len(history) >= self._n:
            history = history[-(self._n - 1):]
        if not isinstance(history, str):
            history = str(history)
        d = 0.0
        while (d == 0 or n == 0) and len(history) >= 1:
            try:
                d = self.sum_freq(history)
                if len(history) < self._n - 1:
                    n = self.sum_freq(history + c)
                else:
                    n = self._T.get(history + c, 0.0)
            except UnicodeDecodeError as e:
                print(("ERROR:", repr(history), e))
                raise e
            history = history[1:]

        # TODO - implement backoff
        assert d != 0, "ERROR: Denominator zero!\n" \
                       "d={} n={} history={!r} c={!r} ({})" \
            .format(d, n, hist, c, self._n)
        # if n==0:
        #     print "Zero n", repr(hist), repr(c)

        return n / d

    def ngramsofw(self, word):
        """Returns the @n-grams of a word @w
        """
        word = helper.START + word + helper.END
        n = self._n
        if len(word) <= n:
            return [word]

        return [word[i:i + n]
                for i in range(0, len(word) - n + 1)]

    @helper.memoized
    def prob(self, pw):
        if len(pw) < self._n:
            return 0.0
        pw = helper.START + pw  # + helper.END
        try:
            return helper.prod(self.cprob(pw[i], pw[:i])
                               for i in range(1, len(pw)))
        except Exception as e:
            print((repr(pw)))
            raise e


################################################################################

class HistPw(PwModel):
    """
    Creates a histograms from the given file. 
    Just converts the password file into  a .dawg  file.
    """

    def __init__(self, pwfilename, fuzzysearch=False, **kwargs):
        kwargs['modelfunc'] = lambda x: [x]
        kwargs['modelname'] = 'histogram'
        super(HistPw, self).__init__(pwfilename=pwfilename, **kwargs)
        self.pwfilename = pwfilename
        if fuzzysearch:
            self.ffs = fast_fuzzysearch(self._T.keys(), ed=2)
        else:
            self.ffs = None

    def similarpws(self, pw, ed=2):
        return self.ffs.query(pw, ed)

    def probsum(self, pws):
        """Sum of probs of all passwords in @pws."""

        return sum(self.prob(pw) for pw in pws)

    def prob(self, pw):
        """
        returns the probabiltiy of pw in the model.
        P[pw] = n(pw)/n(__total__)
        """
        return float(self._T.get(pw, 0)) / self._T['__TOTALF__']

    def prob_correction(self, f=1):
        """
        Corrects the probability error due to truncating the distribution.
        """
        total = {'rockyou': 32602160}
        return f * self._T['__TOTALF__'] / total.get(self._leak, self._T['__TOTALF__'])

    def iterpasswords(self, n=-1):
        return helper.open_get_line(self.pwfilename, limit=n)


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        if sys.argv[1] == '-createHpw':
            pwf = sys.argv[2]
            pwf = HistPw(pwf, freshall=True)
            print(pwf)
            print((pwf.prob('password12')))
