from context import pwmodel as pwm 
import pytest
import os

leak_file = os.path.expanduser('~/passwords/phpbb-withcount.txt.bz2')

@pytest.mark.parametrize('ngrampw',
                         [pwm.models.NGramPw(leak_file)]
)
class TestNgram(object):
    @pytest.mark.parametrize('word', ['asd', 'a'])
    def test_small_word(self, word, ngrampw):
        ngrampw._n = 6
        assert ngrampw.ngramsofw(word) == [u'\x01' + word + u'\x02']

    @pytest.mark.parametrize(('word', 'n'), [('password', 1),
                                             ('aaaaaaaaaa', 5)
    ])
    def test_length_all_ngrams(self, word, n, ngrampw):
        ngrampw._n = n
        assert all([len(x)==n for x in ngrampw.ngramsofw(word)])
        assert len(ngrampw.ngramsofw(word)) == max(1, len(word)-n+3)

    @pytest.mark.parametrize(('word', 'n'), [('password', 1),
                                             ('asdflaksdjfa;sdf', 5),
                                             ('wjdafa893hpa9 98auadsfasdfpa fasdf;ads ac', 19)
    ])
    def test_completeness(self, word, n, ngrampw):
        ngrampw._n = n
        ret = ''
        for w in ngrampw.ngramsofw(word):
            if not ret:
                ret = w
            else:
                ret += w[-1]
        assert ret[1:-1] == word

@pytest.mark.parametrize('pcfgpw',
                         [pwm.models.PcfgPw(leak_file)]
)
class TestPCFG(object):
    @pytest.mark.parametrize(('word', 'res'), [('password', ['__S__L8__', '__L8__', 'password']),
                                               ('p@123', ['__S__L1Y1D3__', '__L1__', '__Y1__', '__D3__', 'p', '@', '123']),
                                               ('@12pass', ['__S__Y1D2L4__', '__Y1__', '__D2__', '__L4__','@', '12', 'pass']),
                                               ('pass@12', ['__S__L4Y1D2__', '__L4__', '__Y1__', '__D2__','pass', '@', '12'])
    ])
    def test_completeness(self, word, res, pcfgpw):
        assert pcfgpw.pcfgtokensofw(word) == res

    def test_prob(self, pcfgpw):

        for pw1, pw2  in [('password12', 'assword1'),
                          ('abcd123', 'abcd1234')]:
            assert pcfgpw.prob(pw1) > pcfgpw.prob(pw2)
