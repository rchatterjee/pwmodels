from collections import defaultdict
import helper
import dawg
from models import HistModel, PwModel, NGramPw
import models

MIN_FREQ = 0.5

if __name__ == "__main__":
    import sys
    Usage = "\nUsage: \n$ {} [-hist|-ngram|-pcfg] <pwleak_file.tar.bz2>\n"\
        "\nCreate histogram or ngram or pcfg model of the pwleak file."\
        "\nThe final output is stored in a file printed below.\n"\
            .format(sys.argv[0])
    if len(sys.argv) != 3:
        print Usage
        sys.exit(1)
    if sys.argv[1] == '-hist':
        hm = HistModel(sys.argv[2])
        print hm._modelf
    elif sys.argv[1] == '-ngram':
        hm = NGramPw(sys.argv[2])
        print hm._modelf
    elif sys.argv[1] == '-hist':
        hm = PcfgPw(sys.argv[2])
        print hm._modelf
    else:
        print Usage
        sys.exit(1)
