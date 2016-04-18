from context import pwmodel as pwm 
import pytest

class TestNgram(object):
    def test_negative_n(self):
        with pytest.raises(AssertionError):
            pwm.models.ngramsofw('asdfa', -1)
            
    @pytest.mark.parametrize('word', ['asd', 'a'])
    def test_small_word(self, word):
        assert pwm.models.ngramsofw(word, n=6) == ['\x01' + word + '\x02']

    @pytest.mark.parametrize(('word', 'n'), [('password', 1),
                                             ('aaaaaaaaaa', 5)
    ])
    def test_length_all_ngrams(self, word, n):
        assert all([len(x)==n for x in pwm.models.ngramsofw(word, n)])
        assert len(pwm.models.ngramsofw(word, n)) == max(1, len(word)-n+3)

    @pytest.mark.parametrize(('word', 'n'), [('password', 1),
                                             ('asdflaksdjfa;sdf', 5),
                                             ('wjdafa893hpa9 98auadsfasdfpa fasdf;ads ac', 19)
    ])
    def test_completeness(self, word, n):
        ret = ''
        for w in pwm.models.ngramsofw(word, n):
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


