#!/bin/bash

python print_file.py exemplary_output_file.txt 0.27 &

sleep 1

python ../scripts/ECHO_plot.py --acc_file=exemplary_output_file_test.txt --freq=137.554 --realtime

if pgrep python;
then
	kill -9 $(pgrep python)
fi
