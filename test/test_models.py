from context import pwmodel as pwm 
import pytest
import os

leak_file = os.path.expanduser('~/passwords/phpbb-withcount.txt.bz2')
class TestNgramPw(object):
    def test_ngrampw(self):
        ngpw = pwm.NGramPw(n=4, pwfilename=leak_file)
        for (pw1, pw2) in [('password12', 'assword12'),
                           ('1234567', '123456789'),
                           ('password', 'pasword')]:
            assert ngpw.prob(pw1)>ngpw.prob(pw2)



# PCFG probabilties are wrong -- TODO - will fix it later

class TestModel(object):
    def test_model_prob(self):
        pcfgpw = pwm.PcfgPw(leak_file)
        w = 'password12'
        assert pcfgpw.prob(w) > pcfgpw.prob(w[1:])

def test_qth_pw():
    hm = pwm.HistModel(leak_file)
    L = [hm.qth_pw(q)
         for q in xrange(100, 110, 1)]
    assert all(x>y for x,y in zip(L, L[1:]))
