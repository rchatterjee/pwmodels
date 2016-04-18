from context import pwmodel as pwm 
import pytest
import os

leak_file = os.path.expanduser('~/passwords/phpbb-withcount.txt.bz2')

@pytest.mark.parametrize('ngrampw',
                         [pwm.ngram.NGramPw(leak_file)]
)
class TestNgram(object):
    @pytest.mark.parametrize('word', ['asd', 'a'])
    def test_small_word(self, word, ngrampw):
        ngrampw._n = 6
        assert ngrampw.ngramsofw(word) == ['\x01' + word + '\x02']

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

class TestPCFG(object):
    @pytest.mark.parametrize(('word', 'res'), [('password', ['password']),
                                               ('p@123', ['p', '@', '123']),
                                               ('@12pass', ['@', '12', 'pass']),
                                               ('pass@12', ['pass', '@', '12'])
    ])
    def test_completeness(self, word, res):
        assert pwm.models.pcfgtokensofw(word) == res


