# pwmodels
Password research often requires modelling password distributions from a password leak. (I have to rewrite similar code for at least four times for different projects.) Hence, this module!

In this module I plan to add those models, such as n-gram and PCFG.
In current version it supports, 
* `n`-gram or Markovian password model 
* [Weir et al. PCFG](http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=5207658), and 
* simple histogram of the passwords.

## Install
```bash
$ pip install git+https://github.com/rchatterjee/pwmodels.git
```

## Usage
```python
from pwmodel import NGramPw, PcfgPw, HistPw
pwm = NGramPw(pwfilename='/Users/badger/passwords/myspace-withcount.tar.bz2', n=4)
print pwm.prob('passwords123')
```

## Version
1.0.0

## TODO
* Add a function to enable the models to churn out passwords in decreasing order of their probability
* Add better pcfg model, especially updated with keyboard sequence, and repeating characters, more natural way of spliting the password than just based on continuous sequence of letters, digits and symbols. 
* `n`-gram model is pretty slow now, because it has to comppute the sum of frequency of all the passwords that start with `START` (which is all). 
