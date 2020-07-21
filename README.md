![](https://github.com/dannyjacobs/ECHO/workflows/Run%20Tests/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/external-calibrator-for-hydrogen-arrays-echo/badge/?version=latest)](https://external-calibrator-for-hydrogen-arrays-echo.readthedocs.io/en/latest/?badge=latest)


The External Calibrator for Hydrogen Arrays (ECHO) is a system for calibrating wide-field radio frequency arrays using a radio transmitter mounted on a drone.
Primarily targeting (but not exclusively limited to) arrays operating in the sub-GHz band targeting highly redshifted
21cm radiation from the early universe.

This repository contains software used to operate drone mounted calibrator sources and then collect and reduce the
resulting data.

ECHO is an open source project. Use and reuse is encouraged.  If you use this code in published work please reference the github repo.
http://github.com/dannyjacobs/ECHO and cite [our 2017 paper](http://adsabs.harvard.edu/abs/2017PASP..129c5002J).

* Mailing list:   https://groups.google.com/d/forum/astro_echo
* ASU team blog:  http://danielcjacobs.com/ECHO
* Documentation:  http://dannyjacobs.github.io/ECHO/

## Installation
Install prerequisites. We recommend the anaconda package manager
* healpy (note that as of Jan 2020 healpy is not available for Windows)
* matplotlib
* numpy
* scipy

Get this repo
`git clone https:github.com/dannyjacobs/ECHO`

Install using pip
```
cd ECHO
pip install .
```


## Organization
The code is organized into a few modules. The beam mapping pipeline steps are
1. Read and down-select drone telemetry
2. Read and down-select radio telescope data (varies per telescope, usually spectra vs time)
3. Match up drone positions and telescope measurements. (Sometimes referred to as zippering.)
4. Grid beam (including power map, sample counts and standard deviation)
5. Analyze results. Example analysis steps include:
  1. subtract transmitter model
  2. plot beam maps
  3. plot slices
  4. plot drone events and dynamics  
  5. difference beams
### Modules
NB: If a function is not mentioned here, it is because I don't think it matters any more. Such things will probably be culled in a future cleanup.
 #### `plot_utils.py`
 Functions for plotting, but also all functions relating to healpix gridding
 and manipulation including gridding.
  * `grid_to_healpix` :  grids aligned RF power vs XYZ position
 into a healpix map
  * `make_beam` :  downselects desired spectral channel, converts from latlon to XYZ and calls `grid_to_healpix`
  * `project_healpix` :  flattens from spherical healpix map to 2d gnomic projection
  * `rotate_hpm` :  rotates a healpix map about the polar axis. useful for plotting
  * Other functions, most of whom are deprecated.
 #### `read_utils.py`
 Functions for reading and writing drone and beam data. Drone log file formats
 are not well documented and change all the time.
  * `read_map` : replacement for healpy read function that respects nans
  * `write_map`: replacement for healpy write function that respect nans
  * `apm_version`: tries to determine the version of ardupilot that wrote a log file.
  * `read_apm_log_A_B_C` : reads an ardupilot log of version A_B_C
    * returns position_times, positions,
    * attitude_times, attitudes,
    * waypoint_times, waypoint_numbers
  * `read_echo_spectrum` : reads a spectrum data file output by the ECHO spectrum logger ca 2017 (signalhound + get_sh_spectra)
  * `read_orbcomm_spectrum` : reads a spectrum data file output by the Bradley orbcomm system (ca 2017)
  * `channel_select` : given a spectrum, list of frequencies, and desired frequency returns closest frequency and spectrum amplitude
  * `interp_rx`: interpolates received power onto the measured position time grid
  * `flag_angles` : flags outlier yaws input times,yaw_angles return matching flag array
  * `flag_waypoints` : flags a range of time around a list of waypoints
  * `apply_flagtimes` : Given a list of bad times, a buffer size and a time array, generate a flag table.
#### `position_utils.py`
 * `latlon2xy` : about what you think
 * `to_spherical` : xyz to spherical
#### `time_utils.py`
Most of these are of dubious necessity.
 * `unix_to_gps` : thin wrapper around astropy.Time
 * `gps_to_HMS` : convert GPS time to Hours Minutes Seconds, thin wrapper around
#### `server_utils.py`
Stuff developed to support real-time operations. This never worked very well with mavlink.
### Scripts
#### Jacobs 2017
Scripts used in the 2017 paper are all run in [one master shell script](https://github.com/dannyjacobs/ECHO_paper1/blob/master/scripts/make_plots.sh)
 * plot_yaw.py
 * plot_GB_pos_power_interp.py
 * ECHO_zipper.py
 * ECHO_mk_beam.py
 * plot_ECHO_GB_power_rms_counts.py
 * plot_ECHO_GB_maps.py
 * plot_GB_slices.py
 * ECHO_sub_tx_beam.py
 * plot_ECHO_GB_ratios.py
 * plot_GB_avg_slices.py
 * plot_MWAtile_slices.py
 * MWATilemodel2hpm.py
 * combine_MWAtile_maps.py

 #### Utility Scripts
  * valon_readwrite.py : program the valon transmitter
  * gen_spherical_flight_path.py : generate waypoints in a healpix pattern
  * CST_to_healpix.py : convert the beam file from CST Microwave studio to a healpix map. Note that this should eventually be replaced with [pyuvbeam](https://github.com/RadioAstronomySoftwareGroup/pyuvdata/blob/master/pyuvdata/uvbeam.py).
