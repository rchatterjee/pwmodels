import os

import pytest
from .context import pwmodel as pwm
from .context import phpbb_leak_file

leak_file = phpbb_leak_file

@pytest.mark.parametrize(
    'ngrampw',
    [pwm.models.NGramPw(pwfilename=leak_file)]
)
class TestNgram(object):
    @pytest.mark.parametrize('word', ['asd', 'a'])
    def test_small_word(self, word, ngrampw):
        ngrampw._n = 1
        assert ngrampw.ngramsofw(word) == ['\x02', *word, '\x03']

    @pytest.mark.parametrize(('word', 'n'), [('password', 1),
                                             ('aaaaaaaaaa', 5)
                                             ])
    def test_length_all_ngrams(self, word, n, ngrampw):
        ngrampw._n = n
        assert all([len(x) <= n for x in ngrampw.ngramsofw(word)])
        # maximum length of a ngram min(len(word)+2, n)
        # k = max size of an n-gram
        # sum_{i=1}^k (len(word)-i+3) = k*(len(word) + 3) - k(k+1)/2
        k_max = min(len(word) + 2, n)
        n_ngrams = k_max * (len(word) + 3 - (k_max + 1) / 2)
        assert len(ngrampw.ngramsofw(word)) == n_ngrams

    @pytest.mark.parametrize(
        ('word', 'n'),
        [('password', 1),
         ('asdflaksdjfa;sdf', 5),
         ('wjdafa893hpa9 98auadsfasdfpa fasdf;ads ac', 19)]
    )
    def test_completeness(self, word, n, ngrampw):
        ngrampw._n = n
        ret = ['' for _ in range(n)]
        for w in ngrampw.ngramsofw(word):
            i = len(w) - 1
            if not ret[i]:
                ret[i] = w
            else:
                ret[i] += w[-1]
        for i in range(n):
            assert not ret[i] or ret[i][1:-1] == word


@pytest.mark.parametrize(
    'pcfgpw',
    [pwm.models.PcfgPw(leak_file)]
)
class TestPCFG(object):
    @pytest.mark.parametrize(
        ('word', 'res'),
        [('password', ['__S__L8__', '__L8__', 'password']),
         ('p@123',
          ['__S__L1Y1D3__', '__L1__', '__Y1__', '__D3__', 'p', '@', '123']),
         ('@12pass',
          ['__S__Y1D2L4__', '__Y1__', '__D2__', '__L4__', '@', '12', 'pass']),
         ('pass@12',
          ['__S__L4Y1D2__', '__L4__', '__Y1__', '__D2__', 'pass', '@', '12'])])
    def test_completeness(self, word, res, pcfgpw):
        assert pcfgpw.pcfgtokensofw(word) == res

    def test_prob(self, pcfgpw):
        for pw1, pw2 in [('password12', 'assword1'),
                         ('abcd123', 'abcd1234')]:
            assert pcfgpw.prob(pw1) > pcfgpw.prob(pw2)
