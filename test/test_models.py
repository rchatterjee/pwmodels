from context import pwmodel as pwm 
import pytest
import os

leak_file = os.path.expanduser('~/passwords/phpbb-withcount.txt.bz2')
class TestNgramPw(object):
    def test_ngrampw(self):
        ngpw = pwm.NGramPw(n=4, pwfilename=leak_file)
        pw = 'assword12'
        print "prob of {} -- {}".format(pw, ngpw.prob(pw))
        assert False



# PCFG probabilties are wrong -- TODO - will fix it later

# class TestModel(object):
#     def test_model_prob(self):
#         modelfunc = pwm.models.pcfgtokensofw
#         w = 'password12'
#         T = pwm.buildmodel.create_model(modelfunc, listw=[(w, 12)])
#         print list(T.items())
#         assert pwm.buildmodel.prob(T, w, modelfunc) == 1.0


