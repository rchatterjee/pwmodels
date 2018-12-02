import os
import sys

sys.path.extend([os.getcwd(), os.path.dirname(os.getcwd())])
print(sys.path)

import pwmodel

ry_leak_file = os.path.expanduser('~/passwords/rockyou-withcount.txt.gz')
phpbb_leak_file = os.path.expanduser('~/passwords/phpbb-withcount.txt.gz')
