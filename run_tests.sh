#!/usr/bin/env bash
set -e

mkdir -p reports

echo "PEP8 tests>>>"
# place your tests here
pep8 --max-line-length=120 ./aws_helper/ | tee ./reports/pep8.out;
echo "<<<PEP8 tests"

echo "Pylint tests>>>"
pylint --rcfile=.pylintrc ./aws_helper/ | tee ./reports/pylint.out; result=$(( ${PIPESTATUS[0]} & 3 ))
if [[ ${result} -ne 0 ]]; then exit 1; fi;
echo "<<Pylint tests"

echo "Nose tests>>>"
nosetests --config .noserc | tee ./reports/nose.out; result=$(( ${PIPESTATUS[0]} & 3 ))
if [[ ${result} -ne 0 ]]; then exit 1; fi;

echo "<<Nose tests"
