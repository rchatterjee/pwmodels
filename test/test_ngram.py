from context import pwmodel as pwm 
import pytest

class TestNgram(object):
    def test_negative_n(self):
        with pytest.raises(AssertionError):
            pwm.models.ngramsofw('asdfa', -1)
            
    @pytest.mark.parametrize('word', ['asdfa', 'a'])
    def test_small_word(self, word):
        assert pwm.models.ngramsofw(word, n=6) == [word]

    @pytest.mark.parametrize(('word', 'n'), [('password', 1),
                                             ('aaaaaaaaaa', 5)
    ])
    def test_length_all_ngrams(self, word, n):
        assert all([len(x)==n for x in pwm.models.ngramsofw(word, n)])
        assert len(pwm.models.ngramsofw(word, n)) == max(1, len(word)-n+1)

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
        assert ret == word

class TestPCFG(object):
    @pytest.mark.parametrize(('word', 'res'), [('password', ['password']),
                                               ('p@123', ['p', '@', '123']),
                                               ('@12pass', ['@', '12', 'pass']),
                                               ('pass@12', ['pass', '@', '12'])
    ])
    def test_completeness(self, word, res):
        assert pwm.models.pcfgtokensofw(word) == res


class TestModel(object):
    def test_model_prob(self):
        modelfunc = pwm.models.pcfgtokensofw
        w = 'password12'
        T = pwm.buildmodel.create_model(modelfunc, listw=[(w, 12)])
        print list(T.items())
        assert pwm.buildmodel.prob(T, w, modelfunc) == 1.0
