import common_func as helper
import gzip
import marisa_trie


class Passwords(object):
    """
    Its a class to efficiently store and read large password
    file.
    """

    def __init__(self, pass_file):
        fbansename = os.path.basename(pass_file).split('.', 1)[0]
        # self.e_pass_file_dawg = os.path.join('data/', fbansename+'.dawg')
        self.e_pass_file_trie = os.path.join('data/', fbansename + '.trie')
        self.e_pass_file_freq = os.path.join('data/', fbansename + '.freq.gz')
        if os.path.exists(self.e_pass_file_trie) and os.path.exists(self.e_pass_file_freq):
            self.load_data()
        else:
            self.create_data_structure(pass_file)

    def create_data_structure(self, pass_file):
        passwords = {}
        for w, c in helper.open_get_line(pass_file):
            passwords[str(w)] = c
        self.T = marisa_trie.Trie(list(passwords.keys()))
        self.freq_list = [0 for _ in passwords]
        for k in list(self.T.keys()):
            self.freq_list[self.T.key_id(k)] = passwords[k]
        with open(self.e_pass_file_trie, 'wb') as f:
            self.T.write(f)
        with gzip.open(self.e_pass_file_freq, 'w') as f:
            for n in self.freq_list:
                f.write('%d\n' % n)

    def load_data(self):
        self.T = marisa_trie.Trie()
        self.T.load(self.e_pass_file_trie)
        with gzip.open(self.e_pass_file_freq, 'r') as f:
            self.freq_list = [int(n) for n in f]

    def pw2id(self, pw):
        try:
            return self.T.key_id(pw)
        except KeyError:
            return -1

    def pw2freq(self, pw):
        try:
            return self.freq_list[self.T.key_id(pw)]
        except KeyError:
            return 0

    def id2pw(self, _id):
        try:
            return self.T.restore_key(_id)
        except KeyError:
            return ''

    def id2freq(self, _id):
        try:
            return self.freq_list[_id]
        except ValueError:
            return 0


import unittest


class TestPasswords(unittest.TestCase):
    def test_pw2freq(self):
        passwords = Passwords(os.path.expanduser('~/passwords/rockyou-withcount.txt.bz2'))
        for pw, f in list({'michelle': 12714, 'george': 4749,
                           'familia': 1975, 'honeybunny': 242,
                           'asdfasdf2wg': 0, '  234  adsf': 0}.items()):
            pw = str(pw)
            self.assertEqual(passwords.pw2freq(pw), f, "Frequency mismatch" \
                                                       " for {}, expected {}, got {}".format(pw, f,
                                                                                             passwords.pw2freq(pw)))

    def test_getallgroups(self):
        for inp, res in [([1, 2, 3], set([(1,), (2,), (3,), (1, 2), (2, 3), (1, 3)]))]:
            res1 = set(getallgroups(inp))
            self.assertEqual(res1, res, "Expecting: {}, got: {}".format(res, res1))
