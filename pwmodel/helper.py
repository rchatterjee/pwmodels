#!/usr/bin/python

import sys
import os
import bz2
import re

# from Crypto.Random import random
import random

BASE_DIR = os.getcwd()
sys.path.append(BASE_DIR)
# from honeyvault_config import MAX_INT, DEBUG
MAX_INT = 2 ** 64 - 1
DEBUG = False

from os.path import (expanduser)
from math import sqrt
# opens file checking whether it is bz2 compressed or not.
import tarfile

home = expanduser("~")
pwd = os.path.dirname(os.path.abspath(__file__))
ROCKYOU_TOTAL_CNT = 32603388.0

def prod(L):
    x = 1
    for l in L:
        x *= l
    return x

def MILLION(n):
    return n * 10 ** 6


# returns the type of file.
def file_type(filename):
    magic_dict = {
        "\x1f\x8b\x08": "gz",
        "\x42\x5a\x68": "bz2",
        "\x50\x4b\x03\x04": "zip"
    }
    max_len = max(len(x) for x in magic_dict)
    with open(filename) as f:
        file_start = f.read(max_len)
    for magic, filetype in magic_dict.items():
        if file_start.startswith(magic):
            return filetype
    return "no match"


def open_(filename, mode='r'):
    if mode == 'w':
        type_ = filename.split('.')[-1]
    else:
        type_ = file_type(filename)
    if type_ == "bz2":
        f = bz2.BZ2File(filename, mode)
    elif type_ == "gz":
        f = tarfile.open(filename, mode)
    else:
        f = open(filename, mode);
    return f;


def get_line(file_object, lim=-1):
    for i, l in enumerate(file_object):
        if lim > 0 and lim < i:
            break
        try:
            l.decode('ascii')
            words = l.strip().split()
            c, w = int(words[0]), ' '.join(words[1:])
            if w and c > 0:
                yield w, c
        except:
            continue


regex = r'([A-Za-z_]+)|([0-9]+)|(\W+)'


def print_err(*args):
    if DEBUG == True:
        sys.stderr.write(' '.join([str(a) for a in args]) + '\n')


def tokens(w):
    T = []
    while w:
        m = re.match(regex, w)
        T.append(m.group(0))
        w = w[len(T[-1]):]
    return T


def whatchar(c):
    if c.isalpha(): return 'L';
    if c.isdigit():
        return 'D';
    else:
        return 'Y'


def mean_sd(arr):
    s = sum(arr)
    s2 = sum([x * x for x in arr])
    n = len(arr)
    m = s / float(n)
    sd = sqrt(float(s2) / n - m * m)
    return m, sd


def convert2group(t, totalC):
    return t + random.randint(0, (MAX_INT - t) / totalC) * totalC


# assumes last element in the array(A) is the sum of all elements
def getIndex(p, A):
    p %= A[-1]
    i = 0;
    for i, v in enumerate(A):
        p -= v;
        if p < 0: break
    return i
