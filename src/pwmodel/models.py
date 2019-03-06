import heapq
import os
import sys
import itertools
from collections import defaultdict
import operator
import dawg
import functools
import pathlib
import json
import string

from . import helper
from .fast_fuzzysearch import fast_fuzzysearch

TOTALF_W = '\x02__TOTALF__\x03'
NPWS_W = '\x02__NPWS__\x03'
reserved_words = {TOTALF_W, NPWS_W}
# Valid characters for passwords
# string.digits + string.ascii_letters + string.punctuation
VALID_CHARS = set(string.printable[:-6] + helper.START + helper.END)
N_VALID_CHARS = len(VALID_CHARS)


def create_model(modelfunc, fname='', listw=[], outfname='',
                 limit=int(3e6), min_pwlen=6, topk=10000, sep=r'\s+'):
    """:modelfunc: is a function that takes a word and returns its
    splits.  for ngram model this function returns all the ngrams of a
    word, for PCFG it will return splits of the password.
    @modelfunc: func: string -> [list of strings]
    @fname: name of the file to read from
    @listw: list of passwords. Used passwords from both the files and
            listw if provided.
    @outfname: the file to write down the model.
    """

    def length_filter(pw):
        pw = ''.join(c for c in pw if c in VALID_CHARS)
        return len(pw) >= min_pwlen

    pws = []
    if fname:
        pws = helper.open_get_line(fname, limit=limit, pw_filter=length_filter, sep=sep)

    big_dict = defaultdict(int)
    total_f, total_e = 0, 0
    # Add topk passwords from the input dataset to the list
    topk_pws = []
    for pw, c in itertools.chain(pws, listw):
        for ng in modelfunc(pw):
            big_dict[ng] += c
        total_f += c
        total_e += 1
        if len(big_dict) % 100000 == 0:
            print(("Dictionary size: {} (Total_freq: {}; Total_pws: {}"\
                   .format(len(big_dict), total_f, total_e)))
        if len(topk_pws) >= topk:
            heapq.heappushpop(topk_pws, (c, pw))
        else:
            heapq.heappush(topk_pws, (c, pw))
    # Adding topk password to deal with probability reduction of popular
    # passwords. Mostly effective for n-gram models
    print("topk={}".format(topk))
    if topk > 0:
        for c, pw in topk_pws:
            tpw = helper.START + pw + helper.END
            big_dict[tpw] += c
            total_f += c
            total_e += 1

    big_dict[NPWS_W] = total_e
    big_dict[TOTALF_W] = total_f

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
        freshall = kwargs.get('freshall', False)
        self.modelname = kwargs.get('modelname', 'ngram-3')
        if not self._leak:
            self._leak = kwargs.get('leak', 'tmp')
            freshall = True
        self._modelf = get_data_path(
            '{}-{}.dawg.gz'.format(self._leak, self.modelname)
        )
        self._T = None
        if kwargs.get('T') is not None:
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
                modelfunc=kwargs.get('modelfunc', self.modelfunc),
                limit=int(kwargs.get('limit', 3e6)),
                topk=kwargs.get('topk', -1),
                sep=kwargs.get('sep', r'\s+')
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
        return self._T[NPWS_W]

    def totalf(self):
        return self._T[TOTALF_W]

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
        kwargs['topk'] = 10000
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
        self._n = kwargs.get('n', 3)
        kwargs['modelname'] = 'ngram-{}'.format(self._n)
        kwargs['topk'] = -1
        super(NGramPw, self).__init__(pwfilename=pwfilename, **kwargs)
        self._leet = self._T.compile_replaces(helper.L33T)

    @functools.lru_cache(maxsize=100000)
    def sum_freq(self, pre):
        if not isinstance(pre, str):
            pre = str(pre)
        return float(sum(v for k, v in self._T.iteritems(pre)))

    @functools.lru_cache(maxsize=100000)
    def get_freq(self, x):
        """get freq of x  with or without L33t transformations """
        # This is causing problem with ngram-probabilities.
        # > pwm.prob('s@f@r!')
        # > 1.441957095339684

        # keys = self._T.similar_keys(x, self._leet)
        return self._T.get(x, 0.0)
        # # print("get_freq: {!r} -> {!r}".format(x, keys))
        # if len(keys) > 0:
        #     return self._T[keys[0]]
        # else:
        #     return 0.0

    def cprob(self, c, history):
        """
        :param history: string
        :param c: character
        P[c | history] = (f(history+c) + 1)/(f(history) + |V|-1)
        Implement add-1 smoothing with backoff for simplicty.
        TODO: Does it make sense
        returns P[c | history]
        """
        if not history:
            return 1
        hist = history[:]
        if len(history) >= self._n:
            history = history[-(self._n-1):]
        if not isinstance(history, str):
            history = str(history)
        d, n = 0.0, 0.0
        while (d == 0.0) and len(history) >= 1:
            try:
                d = self.get_freq(history)
                n = self.get_freq(history + c)
            except UnicodeDecodeError as e:
                print(("ERROR:", repr(history), e))
                raise e
            history = history[1:]

        assert d != 0, "ERROR: Denominator zero!\n" \
                       "d={} n={} history={!r} c={!r} ({})" \
            .format(d, n, hist, c, self._n)

        return (n + 1) / (d + N_VALID_CHARS-1)

    def ngramsofw(self, word):
        return helper.ngramsofw(word, 1, self._n)

    def _get_next(self, history):
        """Get the next set of characters and their probabilities"""
        orig_history = history
        if not history:
            return helper.START
        history = history[-(self._n-1):]
        while history and not self._T.get(history):
            history = history[1:]
        kv = [(k, v) for k, v in self._T.items(history)
              if not (k in reserved_words or k == history)]
        total = sum(v for k, v in kv)
        while total == 0 and len(history) > 0:
            history = history[1:]
            kv = [(k, v) for k, v in self._T.items(history)
                  if not (k in reserved_words or k == history)]
            total = sum(v for k, v in kv)
        assert total > 0, "Sorry there is no n-gram with {!r}".format(orig_history)
        d = defaultdict(float)
        total = self._T.get(history)
        for k, v in kv:
            k = k[len(history):]
            d[k] += (v+1)/(total + N_VALID_CHARS-1)
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
        Generates passwords in order between upto N_max
        @N_max is the maximum size of the priority queue will be tolerated,
        so if the size of the queue is bigger than 1.5 * N_max, it will shrink
        the size to 0.75 * N_max
        @n is the number of password to generate.
        **This function is expensive, and shuold be called only if necessary.
        Cache its call as much as possible**
        # TODO: Need to recheck how to make sure this is working.
        """
        # assert alpha < beta, 'alpha={} must be less than beta={}'.format(alpha, beta)
        states = [(-1.0, helper.START)]
        # get the topk first
        p_min = 1e-9 / (n**2)   # max 1 million entries in the heap 
        ret = []
        done = set()
        already_added_in_heap = set()
        while len(ret) < n and len(states) > 0:
        # while n > 0 and len(states) > 0:
            p, s = heapq.heappop(states)
            if p < 0:
                p = -p
            if s in done: continue
            assert s[0] == helper.START, "Broken s: {!r}".format(s)
            if s[-1] == helper.END:
                done.add(s)
                clean_s = s[1:-1]
                if filter_func is None or filter_func(clean_s):
                    ret.append((clean_s, p))
                    # n -= 1
                    # yield (clean_s, p)
            else:
                for c, f in self._get_next(s).items():
                    if (f*p < p_min or (s+c) in done or
                        (s+c) in already_added_in_heap):
                        continue
                    already_added_in_heap.add(s+c)
                    heapq.heappush(states, (-f*p, s+c))
            if len(states) > N_max * 3 / 2:
                print("Heap size: {}. ret={}. (expected: {}) s={!r}"
                      .format(len(states), len(ret), n, s))
                print("The size of states={}.  Still need={} pws. Truncating"
                      .format(len(states), n - len(ret)))
                states = heapq.nsmallest(int(N_max * 3/4), states)
                print("Done")
        return ret

    def _get_largest_prefix(self, pw):
        s = self._T.prefixes(pw)
        if not s or len(s[-1]) <= self._n:
            return ('', 0.0), pw
        pre = s[-1]
        rest = pw[len(pre):]
        pre_prob = self._T.get(pre)/self.totalf()
        return (pre, pre_prob), rest

    def _prob(self, pw, given=''):
        p = 1.0
        while pw:
            (pre, pre_prob), rest_pw = self._get_largest_prefix(pw)
            # print("pw={!r} given={!r} p={}".format(pw, given, p))
            if pre_prob > 0.0:
                p *= pre_prob
                pw, given = rest_pw, pre
            else:
                try:
                    p *= self.cprob(pw[0], given)
                    pw, given = pw[1:], given+pw[0]
                except Exception as e:
                    print((repr(pw)))
                    raise e
        return p

    @functools.lru_cache(maxsize=100000)
    def prob(self, pw):
        new_pw = helper.START + pw + helper.END
        return self._prob(new_pw)


def normalize(pw):
    """ Lower case, and change the symbols to closest characters"""
    pw_lower = pw.lower()
    return ''.join(helper.L33T.get(c, c) for c in pw_lower)


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
        self.sep = kwargs.get('sep', r'\s+')
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
        return float(self._T.get(pw, 0)) / self._T[TOTALF_W]

    def prob_correction(self, f=1):
        """
        Corrects the probability error due to truncating the distribution.
        """
        total = {'rockyou': 32602160}
        return f * self._T[TOTALF_W] / total.get(self._leak, self._T[TOTALF_W])

    def iterpasswords(self, n=-1):
        return helper.open_get_line(self.pwfilename, limit=n, sep=self.sep)


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
