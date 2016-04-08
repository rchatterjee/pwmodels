
from collections import defaultdict
import helper

N = 3 # the 'n' of the n-gram
MIN_PROB = 1e-6

def ngramsofw(word, n=3):
    """Returns the @n-grams of a word @w
    """
    if len(word)<n:
        return [word]
        
    return [word[i:i+n]
            for i in xrange(0, len(word)-n)]

def createNgrams(fname='', listw=[], n=3, outfname=''):
    """Create a list of ngrams from a file @fname.  NOTE: the file must be in
    password file format.  See smaple/pw.txt file for the format.  If the file
    is empty string, then it will try to read the passwords from the @listw which
    is a list of tuples [(w1, f1), (w2, f2)...]. (It can be an iterator.)
    @n is again the 'n' of n-gram
    Writes the ngrams in a file at @outfname. if outfname is empty string, it will
    print the ngrams on a file named 'ngrams.dawg' 
    """
    assert n>0, "The 'n' of ngrams must be greater than 0"
    
    if fname:
        pws = helper.open_get_file(fname)
    def join_iterators(pws, listw):
        for p in pws: yield p
        for p in listw: yield p
    big_dict = defaultdict(int)
    for pw, c in join_iterators(pws, listw):
        for ng in ngramsofw(word, n):
            big_dict[unicode(ng)] += c
    big_dict['__TOTAL__'] = sum(big_dict.values())
    nDawg= dawg.IntCompletionDAWG(big_dict)
    if not outfname:
        outfname = 'ngrams.dawg'
    T.save(outfname)
    return nDawg

def readNgrams(fname):
    nDawg= dawg.IntCompletionDAWG(fname)
    nDawg.load(fname)
    return nDawg

def prob(w, nDawg):
    t = float(nDawg.get('__TOTAL__'))
    return helper.prod(nDawg.get(ng, MIN_PROB)/t
                       for ng in ngramsofw(w))
    
