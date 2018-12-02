import os
import sys

# sys.path.extend([os.getcwd(), os.path.dirname(os.getcwd())])
# print(sys.path)

import pwmodel
from os.path import join
from pwmodel.helper import thisdir
from pwmodel.fast_fuzzysearch import Fast2FuzzySearch, lvdistance

ry_leak_file = join(thisdir, 'data', 'rockyou_2M-withcount.txt.gz')
phpbb_leak_file = join(thisdir, 'data', 'phpbb-withcount.txt.gz')
# ry_leak_file = os.path.expanduser('~/passwords/rockyou-withcount.txt.gz')
# phpbb_leak_file = os.path.expanduser('~/passwords/phpbb-withcount.txt.gz')
