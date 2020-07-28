.. ECHO documentation master file, created by
   sphinx-quickstart on Mon Jul 13 10:42:31 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ECHO's documentation!
================================
The External Calibrator for Hydrogen Arrays (ECHO) is a system for calibrating wide-field radio frequency arrays using a radio transmitter mounted on a drone. Primarily targeting (but not exclusively limited to) arrays operating in the sub-GHz band targeting highly redshifted 21cm radiation from the early universe.

This repository contains software used to operate drone mounted calibrator sources and then collect and reduce the resulting data.

.. csv-table:: ECHO_Summary3
   :header: "Version", "Source", "Frame", "Name", "Mount (STL"), "Transmitter (datasheet)", "Antenna", "Flight Software"
   :widths: auto

   "1", "A new zealand company?", "Octo", "Brain", " ", " ", "BicoLOG 5070", " "
   "6", "looking for off-the-shelf, long flighttime", "Steadidrone Vader X8", "Vader", "Vader_Mount (3 parts + Generic_BicoLOG_Mount)", "Blackbox", "BicoLOG 5070", "PX4"