#!/bin/sh
if [ -z $1 ]
then
    TEST="runalltests.py"
else
    TEST=$1
fi
cd ../ && sudo ./setup.py install && cd tests && ./$TEST