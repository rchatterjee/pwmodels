import heapq
import os, sys
import itertools
from collections import defaultdict
import operator
import dawg
import functools
import pathlib
import json

from . import helper
from .fast_fuzzysearch import fast_fuzzysearch

totalf_w = '\x02__TOTALF__\x03'
npws_w = '\x02__NPWS__\x03'
reserved_words = {totalf_w, npws_w}

def create_model(modelfunc, fname='', listw=[], outfname=''):
    """:modelfunc: is a function that takes a word and returns its
    splits.  for ngram model this function returns all the ngrams of a
    word, for PCFG it will return splits of the password.
    @modelfunc: func: string -> [list of strings]
    @fname: name of the file to read from
    @listw: list of passwords. Used passwords from both the files and
            listw if provided.
    @outfname: the file to write down the model.
    """

    pws = []
    if fname:
        pws = helper.open_get_line(fname, limit=3e6)

    big_dict = defaultdict(int)
    total_f, total_e = 0, 0
    for pw, c in itertools.chain(pws, listw):
        for ng in modelfunc(pw):
            big_dict[ng] += c
        if len(big_dict) % 100000 == 0:
            print(("Dictionary size: {}".format(len(big_dict))))
        total_f += c
        total_e += 1
    big_dict[npws_w] = total_e
    big_dict[totalf_w] = total_f

    nDawg = dawg.IntCompletionDAWG(big_dict)
    if not outfname:
        outfname = 'tmpmodel.dawg.gz'
    elif not outfname.endswith('.gz'):
        outfname += '.gz'
    pathlib.Path(outfname).parent.mkdir(parents=True, exist_ok=True)
    helper.save_dawg(nDawg, outfname)
    return nDawg


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
    def __init__(self, **kwargs):
        pwfilename = kwargs.get('pwfilename', '')
        self._leak = os.path.basename(pwfilename).split('-')[0]
        freshall = kwargs.get('freshal', False)
        self.modelname = kwargs.get('modelname', 'ngram-3')
        if not self._leak:
            self._leak = kwargs.get('leak', 'tmp')
            freshall = True
        self._modelf = get_data_path(
            '{}-{}.dawg.gz'.format(self._leak, self.modelname)
        )
        self._T = None
        if kwargs.get('T') != None:
            self._T = kwargs.get('T')
            return
        if freshall:
            try:
                os.remove(self._modelf)
            except OSError as e:
                print("File ({!r}) does not exist. ERROR: {}"
                      .format(self._modelf, e), file=sys.stderr)
        if self._leak != 'tmp':
            try:
                self._T = read_dawg(self._modelf)
            except IOError as ex:
                print(("ex={}\nHang on while I am creating the model {!r}!\n"
                       .format(ex, self.modelname)))
        if self._T is None:
            self._T = create_model(
                fname=pwfilename, listw=kwargs.get('listw', []),
                outfname=self._modelf,
                modelfunc=kwargs.get('modelfunc', self.modelfunc)
            )

    def modelfunc(self, w):
        raise Exception("Not implemented")

    def prob(self, word):
        raise Exception("Not implemented")

    def qth_pw(self, q):
        """
        returns the qth most probable element in the dawg.
        """
        return heapq.nlargest(q + 2, self._T.iteritems(),
                              key=operator.itemgetter(1))[-1]

    def get(self, pw):
        """Returns password probability"""
        return self.prob(pw)

    def __str__(self):
        return 'Pwmodel<{}-{}>'.format(self.modelname, self._leak)

    def npws(self):
        return self._T[npws_w]

    def totalf(self):
        return self._T[totalf_w]

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

    def __init__(self, pwfilename='', **kwargs):
        kwargs['modelfunc'] = self.ngramsofw
        kwargs['n'] = kwargs.get('n', 3)
        kwargs['modelname'] = 'ngram-{}'.format(kwargs['n'])
        self._n = kwargs.get('n', 3)
        super(NGramPw, self).__init__(pwfilename=pwfilename, **kwargs)

    @functools.lru_cache(maxsize=100000)
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
        d, n = 0.0, 0
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
        return helper.ngramsofw(word, self._n)

    def _get_next(self, history):
        """Get the next set of characters and their probabilities"""
        orig_history = history
        if not history:
            return helper.START
        history = history[-(self._n-1):]
        kv = [(k, v) for k, v in self._T.items(history)
              if k not in reserved_words]
        total = sum(v for k, v in kv)
        while total == 0 and len(history) > 0:
            history = history[1:]
            kv = [(k, v) for k, v in self._T.items(history) 
                  if k not in reserved_words]
            total = sum(v for k, v in kv)
        assert total > 0, "Sorry there is no n-gram with {!r}".format(orig_history)
        d = {}
        for k, v in kv:
            k = k[len(history)]
            d[k] = d.get(k, 0) + v/total
        return d
        
    def _gen_next(self, history):
        """Generate next character sampled from the distribution of characters next.
        """
        orig_history = history
        if not history:
            return helper.START
        history = history[-(self._n-1):]
        kv = [(k, v) for k, v in self._T.items(history)
              if k not in reserved_words]
        total = sum(v for k, v in kv)
        while total == 0 and len(history) > 0:
            history = history[1:]
            kv = [(k, v) for k, v in self._T.items(history) 
                  if k not in reserved_words]
            total = sum(v for k, v in kv)
        assert total > 0, "Sorry there is no n-gram with {!r}".format(orig_history)
        _, sampled_k = list(helper.sample_following_dist(kv, 1, total))[0]
        # print(">>>", repr(sampled_k), len(history))
        return sampled_k[len(history)]

    def sample_pw(self):
        s = helper.START
        while s[-1] != helper.END:
            s += self._gen_next(s)
        return s[1:-1]

    def generate_pws_in_order(self, n, filter_func=None, N_max=1e6):
        """
        Generates passwords in order between probability (alpha, beta]
        @N_max is the maximum size of the priority queue will be tolerated,
        so if the size of the queue is bigger than 1.5 * N_max, it will shrink the size to 0.75 * N_max
        @n is the number of password to generate. 
        **This function is expensive, and shuold be called only if necessary. Cache its call as much as possible**
        """
        # assert alpha < beta, 'alpha={} must be less than beta={}'.format(alpha, beta)
        states = [(-1.0, helper.START)]
        p_min = 1e-9 / (n**2)   # max 1 million entries in the heap 
        ret = []
        while len(ret) < n and len(states) > 0:
            p, s = heapq.heappop(states)
            if p<0: 
                p = -p
            if s[-1] == helper.END:
                s = s[1:-1]
                if filter_func is None or filter_func(s):
                    ret.append((s, p))
            else:
                for c, f in self._get_next(s).items():
                    if f*p < p_min: continue
                    heapq.heappush(states, (-f*p, s+c))
            if len(states) > N_max * 3 / 2:
                print("The size of states={}.  Still need={} pws. Truncating"
                      .format(len(states), n - len(ret)))
                states = heapq.nsmallest(int(N_max * 3/4), states)
                print("Done")
        return ret



    @functools.lru_cache(maxsize=100000)
    def prob(self, pw):
        if len(pw) < self._n:
            return 0.0
        pw = helper.START + pw + helper.END
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
        return float(self._T.get(pw, 0)) / self._T[totalf_w]

    def prob_correction(self, f=1):
        """
        Corrects the probability error due to truncating the distribution.
        """
        total = {'rockyou': 32602160}
        return f * self._T[totalf_w] / total.get(self._leak, self._T[totalf_w])

    def iterpasswords(self, n=-1):
        return helper.open_get_line(self.pwfilename, limit=n)


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        if sys.argv[1] == '-createHpw':
            pwf = sys.argv[2]
            pwm = HistPw(pwf, freshall=True)
            print(pwm)
            print((pwm.prob('password12')))
        elif sys.argv[1] == '-ngramGen':
            pwf = sys.argv[2]
            pwm = NGramPw(pwfilename=pwf)
            # print(pwm.sample_pw())
            print(json.dumps(pwm.generate_pws_in_order(1000, filter_func=lambda x: len(x)>6), indent=4))
