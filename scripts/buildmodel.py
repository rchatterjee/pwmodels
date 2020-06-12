#!/usr/bin/env python

import sys
import os
from pwmodel import HistPw, PcfgPw, NGramPw

# from IPython.core import ultratb
# sys.excepthook = ultratb.FormattedTB(mode='Verbose',
#                                      color_scheme='Linux', call_pdb=1)

MIN_FREQ = 0.5

if __name__ == "__main__":
    Usage = "\nUsage: \n$ {} [-hist|-ngram|-pcfg] <pwleak_file.tar.bz2> [<n>]\n" \
            "\nCreate histogram or ngram or pcfg model of the pwleak file." \
            "\nThe final output is stored in a file printed below.\n" \
            "\n<n> is the 'n' for ngram model.\n Uses only passwords with length 6 or more" \
        .format(sys.argv[0])
    d = {
        'limit': os.environ.get('LIMIT', -1),
        'dirname': os.environ.get('DIRNAME', '~/.pwmodel/')
    }
    if len(sys.argv) < 3:
        print(Usage)
        sys.exit(1)
    if sys.argv[1] == '-hist':
        hm = HistPw(sys.argv[2], **d)
        print(hm._modelf)
    elif sys.argv[1] == '-ngram':
        hm = NGramPw(sys.argv[2], n=int(sys.argv[3]) if len(sys.argv) > 3 else 3)
        print(hm._modelf)
    elif sys.argv[1] == '-pcfg':
        hm = PcfgPw(sys.argv[2])
        print(hm._modelf)
    else:
        print(Usage)
        sys.exit(1)
