
import helper

N = 3 # the 'n' of the n-gram

def ngramsofw(word, n=3):
    """Returns the @n-grams of a word @w
    """
    assert n>0, "The 'n' of ngrams must be greater than 0"
    if len(word)<=n:
        return [word]
        
    return [word[i:i+n]
            for i in xrange(0, len(word)-n+1)]


def pcfgtokensofw(word):
    """This splits the word into chunks similar to as described in Weir
    et al Oakland'14 paper.
    E.g.,
    >> ngrampw.pcfgtokensofw('password@123')
    ['password', '@', '123', '__L8__', '__Y1__', '__D3__']

    """
    tok = helper.tokens(word)
    # No need to send the symbols, at the time of final probability
    # calculation, their contribution is cacelled.

    # *Thm*: If in my model there is a constant split of a password,
    # there is no need to worry about the tree of the split, the split
    # is good enough to build the model
    
    # sym = ['__{0}{1}__'.format(helper.whatchar(w), len(w))
    # for w in tok]
    # return tok + sym
    return tok

def wholepwmodel(word):
    """This model just returns the exact password distribution induced by
    the password leak file. E.g.,
    >>> ngrampw.wholepwmodel('password12')
    ['password12']
    """
    return [wholemodel]



if __name__ == "__main__":
    w = 'passsword@123'
    print pcfgtokensofw(w)
