#!/usr/bin/env bash
set -e

mkdir -p reports

echo "PEP8 tests>>>"
# place your tests here
pep8 --max-line-length=120 . | tee ./reports/pep8.out; exit \${PIPESTATUS[0]}
echo "<<<PEP8 tests"

echo "Pylint tests>>>"
dpylint --rcfile=.pylintrc ./ | tee ./reports/pylint.out; exit \$(( \${PIPESTATUS[0]} & 3 ))
echo "<<Pylint tests"

echo "Nose tests>>>"
nosetests --config .noserc | tee ./reports/nose.out; exit \$(( \${PIPESTATUS[0]} & 3 ))
echo "<<Nose tests"
