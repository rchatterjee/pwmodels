import pwmodel
import sys
pwm = pwmodel.NGramPw('/home/rahul/passwords/rockyou-withcount.txt.gz', limit=1000000)
pws = pwm.generate_pws_in_order(int(sys.argv[1]), filter_func=lambda x: 6 <= len(x) <= 30)
print('\n'.join(str(x) for x in pws))
print("Total generated: {}".format(len(pws)))
print("Total Prob: {}".format(sum(v for k, v in pws)))
print("p(123456)={}".format(pwm.prob('123456')))
