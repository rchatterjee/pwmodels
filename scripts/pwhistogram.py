#!/usr/bin/env python

import sys, os
from pwmodel import readpw 

if __name__ == "__main__":
    Usage = "\nUsage:  \n$ {} <pwfile> <dirname> <limit> <pwlist>\n"\
            "This will generate the a .trie and .npz file in the @dirname "\
            "folder, that will very useful Password library, see readpw.py file."\
            "n=-1 will read the whole file, so be patient if the file is really "\
            "large"\
            .format(sys.argv[0])
    if len(sys.argv) < 5:
        print(Usage)
        sys.exit(1)
    fname, dirname, limit = sys.argv[1:4]
    pwm = readpw.Passwords(fname, dirname=dirname, limit=int(limit))
    pws = sys.argv[4:]
    ranks = pwm.guessranks(pws)
    for pw, r in zip(pws, ranks):
        print("{} --> {}".format(pw, r))
