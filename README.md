# Pwmodels [![Build Status](https://travis-ci.org/rchatterjee/pwmodels.svg?branch=master)](https://travis-ci.org/rchatterjee/pwmodels) 
Password research often requires modelling password distributions from a
password leak. (I have to rewrite similar code for at least four times for
different projects.) Hence, this module!

In this module I plan to add different password models, such as n-gram and PCFG.
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
See `tests/` for more usage information.


## `Passwords` module  
In `src/pwmodel/readpw.py` file, there is a `Passwords` class. This class makes
it much easier to read password files; especially the ones created using `uniq
-c` command. This will convert a single password file into two files: (1) a
marisa-trie `.trie` file that contains all the password in a prefix trie format,
and (2) a numpy array in `.npz` format that contains the frequencies of the
passwords. This is significantly better in space (on disk and memory) and speed
for doing many operations, such as sampling passwords according to the
distribution, finding guess ranks of a list of passwords, or getting
frequency/probability of a passowrd. Every password `w` is assigned a unique id `i`,
and the frequency of that password is at the `i`-th location in the array. 

```ipython
>>> from pwmodel import readpw
>>> pwm = readpw.Passwords(fname, dirname=dirname, limit=int(limit))
>>> pwm.pw2id('password12')
367412281
>>> pwm.sample_pws(10)
<generator object Passwords.sample_pws.<locals>.<genexpr> at 0x7f3d5adf8518>
>>> l = list(pwm.sample_pws(10))
>>> l
['qwertasdfg',
 'jamez9',
 'sadigojy',
 'kastorka89055082696',
 '062766',
 '14geno',
 'love80384',
 'jessica13',
 '0550135855',
 'estevan12']
>>> pwm.guessranks(l)
array([     5873,   8763930, 103938240, 103938240,   1836406,  10060962,
       103938240,      6713, 103938240,   1113414])
```


## Version 1.3

## TODO
* ~Add a function to enable the models to churn out passwords in decreasing
  order of their probability~
* Add better pcfg model, especially updated with keyboard sequence, and
  repeating characters, more natural way of spliting the password than just
  based on continuous sequence of letters, digits and symbols.
* `n`-gram model is pretty slow now, because it has to comppute the sum of
  frequency of all the passwords that start with `START` (which is a lot).


## Changelog
1. Added `readpw.py`, ann utility to read password leak data. 
