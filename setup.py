#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

from glob import glob
from setuptools import setup
# from distutils.core import setup
from distutils.extension import Extension

USE_CYTHON = False   # command line option, try-import, ...

ext = '.pyx' if USE_CYTHON else '.c'

extensions = [Extension("pwmodel/_fast", ["src/pwmodel/_fast"+ext])]
# data = glob('src/pwmodel/data/*')
# print(data)

if USE_CYTHON:
    from Cython.Build import cythonize
    extensions = cythonize(extensions)

setup(
    name='pwmodels',
    version='1.3.1',
    description='A simple password model generating tool',
    long_description="This module creates different useful password models, such as ngram model or PCFG mdoel.",

    url="https://github.com/rchatterjee/pwmodels.git",
    author="Rahul Chatterjee",
    author_email="rc737@cornell.edu",
    license="Apache",
    python_requires='>=3',

    # classifiers=[
    #     # How mature is this project? Common values are
    #     #   3 - Alpha
    #     #   4 - Beta
    #     #   5 - Production/Stable
    #     'Development Status :: 3 - Alpha',

    #     # Indicate who your project is intended for
    #     'Intended Audience :: Password Researchers',
    #     'Topic :: Password Modeling',

    #     # Pick your license as you wish (should match "license" above)
    #     'License :: MIT',

    #     # Specify the Python versions you support here. In particular, ensure
    #     # that you indicate whether you support Python 2, Python 3 or both.
    #     'Requires-Python: >=3',
    #     'Programming Language :: Python :: 3.6',
    # ],

    keywords="password model ngram pcfg cracking".split(),
    packages=['pwmodel'],  # find_packages(exclude(['contrib', 'docs', 'tests*'])),
    ext_modules=extensions,
    # ext_modules=cythonize("pwmodel/_fast.pyx"),
    package_dir={'': 'src'},
    include_package_data=True,
    # package_data={
    #     '': ["*.txt", "*.rst"],
    #     'src/pwmodel': data,
    # },
    dependency_links=["https://github.com/fujimotos/polyleven/archive/0.3.tar.gz"],
    setup_requires=[
        'cython'
    ],
    install_requires=[
        'dawg', 'cython', 'marisa_trie', 'polyleven',
        'python-levenshtein', 'numpy'   # for readpw
        # 'git://github.com/fujimotos/polyleven'
    ],
    scripts=['scripts/buildmodel.py']
    # data_files=[('src/pwmodel/data/', ['ngram-0-phpbb.dawg', 'ngram-3-phpbb.dawg', 'ngram-4-phpbb.dawg'])]
)
