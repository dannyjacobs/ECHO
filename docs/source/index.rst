.. ECHO documentation master file, created by
   sphinx-quickstart on Mon Jul 13 10:42:31 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ECHO's documentation!
================================
The External Calibrator for Hydrogen Observatories (ECHO) is a system for calibrating wide-field radio frequency arrays using a radio transmitter mounted on a drone. Primarily targeting (but not exclusively limited to) arrays operating in the sub-GHz band targeting highly redshifted 21cm radiation from the early universe.

This repository contains software used to generate flight plans, program the calibrator, collect and reduce resulting data.

You can read about the first demonstration of ECHO(Jacobs et al. 2017) here_


.. _here: https://ui.adsabs.harvard.edu/abs/2017PASP..129c5002J/abstract

ECHO setup
------------

.. image:: ../images/ECHO_setup.png
    :width: 700px
    :align: center
    :height: 400px
    :alt: LWA-SV '19 setup



Flight Path
-----------------
.. image:: ../images/flightpath.png
    :width: 300px
    :align: center
    :height: 200px
    :alt: flight path



.. toctree::
   :caption: Contents:


   Installation <installation>
   Tutorial <tutorial>
   API Reference <api>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
