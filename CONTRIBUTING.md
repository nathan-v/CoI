# Contributing to AWS Okta Keyman

## Code Style

This project uses Black to check for style errors. Please check your code before
submitting a PR.

    $ black ./

## Python Versions

Python 3.8.0+ is supported. As much Python version compatibility as
possible will be maintained.

## Testing

### Unit tests

Unit tests have been written using nose and should be included with every PR. If the PR
is a bug fix please include a regression test as well.

### Running Tests

The command below will run all of the unit tests for the package with lots of details
and will spit out the current code coverage numbers. Code coverage for this project is
high and the intent is that it stays that way.

    $ pytest

## Developer Setup

Dev environment setup is easy. You need a supported version of Python, git, and
virtualenv installed.

    $ git clone https://github.com/nathan-v/CoI.git
    $ cd CoI
    $ virtualenv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt
