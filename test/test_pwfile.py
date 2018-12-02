import unittest
from pwmodel.readpw import Passwords
from pwmodel import helper
import os
from .context import phpbb_leak_file

class TestPasswords(unittest.TestCase):
    def test_pw2freq(self):
        passwords = Passwords(phpbb_leak_file)
        for pw, f in list({'michelle': 38, 'george': 39,
                           'familia': 2, 'honeybunny': 2,
                           'asdfasdf2wg': 0, '  234  adsf': 0}.items()):
            pw = str(pw)
            self.assertEqual(passwords.pw2freq(pw), f, "Frequency mismatch for"
                             "{}, expected {}, got {}"\
                             .format(pw, f, passwords.pw2freq(pw)))

    def test_getallgroups(self):
        for inp, res in [([1, 2, 3],
                          set([(1,), (2,), (3,), (1, 2), (2, 3), (1, 3), (1, 2, 3)]))]:
            res1 = set(helper.getallgroups(inp))
            self.assertEqual(res1, res, "Expecting: {}, got: {}".format(res, res1))
