# BlockPy

[![Build Status](https://travis-ci.org/Edorka/blockpy.svg?branch=master)](https://travis-ci.org/Edorka/blockpy)

Minimal python implementation of a blockchain. Following the article [A blockchain in 200 lines of code](https://medium.com/@lhartikk/a-blockchain-in-200-lines-of-code-963cc1cc0e54).

# Running the tests

If you don't trust the green tag from travis-ci.org you can run tests on your own:

```
virtualenv -p python3 venv
source venv/bin/activate
python -m unittest discover tests
```
