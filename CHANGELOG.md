# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.3] - 2020-10-08
### Added
- Documentation and Tutorial for usage

## [0.0.2] - 2020-8-20
### Added
- ReadTheDocs support, can now be read at: https://external-calibrator-for-hydrogen-arrays-echo.readthedocs.io
- Initial RtD tutorial added
- Added list of drone iterations with build logs and solid model files. Table in hardware/echo_hardware_summary.rst
- Class created for Beams, allows reading and writing of both drone and instrument beams
- Requirements.txt created, all modules now referenced there during setup
- Additional plotting functions for beams: orthview, E and H slices, polar plots, mollview
- Preliminary files for CircleCI

### Changed
- Observations and Beam functions split into separate files (observations.py, beams.py)
- Beam functions now check for appropriate beam types
- Bugfixes for beam functions
- Editing to docstrings, placed in Google format (https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

### Removed
- Python 2.7 support and testing (not compatible with astropy)


## [0.0.1] - 2020-02-03
### Added
- Changelog
- Test subfolders and empty test files
- keep/ directory for scripts, will move when finalized
- basic test CI infrastructure and GitHub action

### Changed
- testing/ directory renamed to tests/
- edited setup.py to include dependencies and tests

### Removed
- Drone RFI report
- ECHO Reduction
