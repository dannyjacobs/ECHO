---
layout: single
header:
   image: /assets/images/ECHO_page_header4.png
toc: true
toc_label: "On this page"
toc_icon: "gear"
toc_sticky: true
sidebar:
   nav: "links"
---
# About
The aim of the ECHO project is high precision calibration of wide-field radio instruments. A transmitter mounted to a drone provides a known signal at a known location.  The goal for 21cm experiments is to make full sky maps of antenna beams accurate to 1% across the instrument bandwidth.

The method paper answers many frequently asked questions. (Jacobs et al 2017, [journal](https://ui.adsabs.harvard.edu/abs/2017PASP..129c5002J/abstract), [arxiv preprint](https://arxiv.org/abs/1610.02607))
{: .notice--info}

# Open Source project
A secondary goal is to build a community resource for drone-based radio calibration.

## Project organization
Organized by [Professor Daniel Jacobs](https://danielcjacobs.com) in the [Low frequency Cosmology Lab](https://loco.lab.asu.edu) at Arizona State University.

 * We have an active "Slack Connect" channel, accessible to anyone with a Slack account. To be invited, email Danny
 * [Analysis code on github](https://github.com/dannyjacobs/echo)
 * [Hardware also on github](https://github.com/dannyjacobs/echo)
 * Code documentation on [ReadTheDocs](https://external-calibrator-for-hydrogen-arrays-echo.readthedocs.io/)
 * A [mailing list](https://groups.google.com/d/forum/astro_echo) exists.

# ECHO @ ASU Notes
 * The project began in 2012 at Arizona State University as a student powered instrumentation development. It has been supported by the National Science Foundation (AST-1407646, AST-1711179)
 * We have used both Commercial drones and custom builds. The current Mark 7 platform (ca 2019) is a custom build using kit parts. (build log in memo 51)
 * Antenna: [Aaronia Bicolog 5070](https://aaronia.com/antennas/bicolog-series-biconical)
 * Max Drone Height: 400ft (FAA limit)
 * Mount: 3d printed, fixed beneath
 * Battery posture: top mounted (I think this somewhat novel for a battery of the size we're using, but despite seeming dreadfully unstable it works fine)
 * Frequency Coverage: 50-250MHz (not all at once)
 * Position Accuracy: 8cm rms using RTK GPS and base station*
 * Transmitters:  TX V1 used dual tone Valon 5009 VCO (23 - 6GHz) on an independent battery. TX V2 will add chopping. TX V3 will add 20MHz band limited noise
 * Safety: Part 107 certified pilot with 7 years experience, 45 hours, 100+ flights
 * Kit Contents: 3 spare drones (essential!), 2 spare antennas, SAS542 folding bicone + stand for auxiliary receiver.
 * Flight time: 45min hover, 30 minute mapping sorties
 * Drone built cost: ~$1200

# Presentations
Presentations etc
 * “External Calibration of Hydrogen Arrays” M. Gopalkrishna, URSI-NRSM
 * “Drone-based Beam Mapping of the LWA.”, D. Jacobs, University of New Mexico, LWA Users Meeting, July 2020 ([pptx](http://danielcjacobs.com/uploads/ECHO_LWAUM_2020.pptx))
 * “The Airborne External Calibration for Precision Low Frequency Instrumentation”, D. Jacobs, Caltech, March 2019 ([pdf](http://danielcjacobs.com/uploads/ECHO_March2019_small.pdf))
 * “The External Calibrator for Hydrogen Observatories”, D. Jacobs, URSI Boulder, January, 2016 (slides lost to ravages of time etc etc)
