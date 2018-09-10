#!/usr/bin/python

from setuptools import setup
from Cython.Build import cythonize

setup(
    name='pwmodels',
    version='1.2',
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

    keywords="password model ngram pcfg cracking",
    packages=['pwmodel'],  # find_packages(exclude(['contrib', 'docs', 'tests*'])),
    ext_modules = cythonize("pwmodel/_fast.pyx"),
    package_dir={'pwmodel': 'pwmodel'},
    package_data={'pwmodel': ['data/*.dawg']},
    install_requires=[
        'dawg', 'cython'
    ],
    scripts=['scripts/buildmodel.py']
    # data_files=[('pwmodel/data/', ['ngram-0-phpbb.dawg', 'ngram-3-phpbb.dawg', 'ngram-4-phpbb.dawg'])]
)
