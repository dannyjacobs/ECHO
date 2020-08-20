# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- ReadTheDocs support, can now be read at: https://external-calibrator-for-hydrogen-arrays-echo.readthedocs.io
- RtD tutorial fleshed out
- Hardware RST files and logs
- Class created for Beams, allows reading and writing of both drone and instrument beams
- Requirements.txt created, all modules now referenced there during setup
- Additional plotting functions for beams: orthview, E and H slices, polar plots, mollview
- Preliminary files for CircleCI

### Changed
- Observations and Beam functions split into separate files (observations.py, beams.py)
- Beam functions now check for appropriate beam types
- Bugfixes for beam functions
- Massive editing to docstrings, placed in Google format

### Removed
- Python 2.7 no longer tested or supported


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
