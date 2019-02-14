import unittest
from pwmodel.readpw import Passwords
from pwmodel import helper
import os
from .context import phpbb_leak_file, test_file
import io
import tempfile

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

    def test_pwfile_parsing_anyspaceseperated(self):
        # tf = tempfile.NamedTemporaryFile(mode='w+')
        # tf.write(" 1234 password\n33   123456\n00234\t password1\n")
        # pws = {w:c for w,c in helper.open_get_line(tf.name)}
        pws = Passwords(test_file, freshall=True)
        for pw, f in [('password', 35), ('123456', 344)]:
            self.assertEqual(pws.pw2freq(pw), f, "Frequency mismatch for"
                             "{}, expected {}, got {}"\
                             .format(pw, f, pws.pw2freq(pw)))

    def test_pwfile_parsing_tabseperated(self):
        # tf = tempfile.NamedTemporaryFile(mode='w+')
        # tf.write(" 1234\tpassword\n33  \t123456\n00234\t password\n")
        # pws = {w:c for w,c in helper.open_get_line(tf.name, sep='\t')}
        pws = Passwords(test_file, sep='\t', freshall=True)
        for pw, f in [('password', 1234), ('123456', 344), (' password', 35)]:
            self.assertEqual(pws.pw2freq(pw), f, "Frequency mismatch for"
                             "{}, expected {}, got {}"\
                             .format(pw, f, pws.pw2freq(pw)))

        
    def test_getallgroups(self):
        for inp, res in [([1, 2, 3],
                          set([(1,), (2,), (3,), (1, 2), (2, 3), (1, 3), (1, 2, 3)]))]:
            res1 = set(helper.getallgroups(inp))
            self.assertEqual(res1, res, "Expecting: {}, got: {}".format(res, res1))
