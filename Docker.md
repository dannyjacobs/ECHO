# Docker ECHO Container Setup

Preliminaries:

1) Download and install Docker via https://docs.docker.com/engine/installation/.

2) Download the following libraries and files and place them into one directory for future use

    a) Download FTDI usb communication library (required for Signal Hound API) from

                            www.ftdichip.com/Drivers/D2xx.htm

        Download the 64-bit Linux distribution (current version 1.3.6).

    b) Download the Signal Hound API via

                https://signalhound.com/support/downloads/bb60c-bb60a-downloads/

    c) Download the FFTW (Fastest Fourier Transform in the West) C library from

                         http://www.fftw.org/download.html

        (current version 3.3.4).

3) Download get_sh_spectra.c and dislin.h from the ECHO Google Drive and place it in the same
    directory in which the files downloaded in (2) were placed.


Setting up ECHO Container:

1) Open a Docker Quickstart Terminal accessible via Applications and navigate to the
    directory where the files in the preliminaries were downloaded.

2) Pull ubuntu:14.04 official image from Docker repository by executing the command

                        docker pull ubuntu:14.04

3) Run docker container ubuntu:14.04 with the following command

            docker run -it -v downloaded-files-dir:/home/ECHO ubuntu:14.04 /bin/bash

    The flags -i tell docker to assign a terminal inside the container and make it interactive
    by grabbing the STDIN of the container.  The flag -v tells docker to create a 'data volume'
    which allows a folder on the host machine to be visible in the container.  The downloaded-
    files-dir should be the folder in which the libraries and API in the preliminaries were
    downloaded.  Upon running the above command, you should see a typical command
    prompt similar to

                        root@af8bae53bdd3:/

          Note: The ID after @ (af8bae53bdd3) is the container's ID which you can use to commit
          changes to a downloaded container.  This ID can also be viewed in a seperate Docker
          Quickstart Terminal by issuing the command

                        docker ps

          which will display all running docker containers and their corresponding container IDs.

    Navigate to /home/ECHO for future steps.

3) With the container running, execute the following commands

                        sudo apt-get update
                        sudo apt-get upgrade
                        sudo apt-get install build-essentials

    These commands will update and upgrade existing libraries/software and then install gcc
    and g++ for compilation of Signal Hound C code.  You can ensure that gcc/g++ have been
    installed by executing 'gcc --version' and 'g++ --version' on the command line.

4) Install libusb-1.0 (required for Signal Hound API) via

                        sudo apt-get install libusb-1.0-0

5) Install FTDI usb communication library (required for Signal Hound API):  
    Unzip/untar the downloaded FTDI library tarball via

                        tar -xvzf libftd2xx-x86_64-1.3.6.tgz

    Follow the instructions in the extracted README to install the FTDI library.

6) Install the Signal Hound API:
    Extract the files and follow the steps in the corresponding README to install the Signal
    Hound API.  Make sure to copy bb_api.h in include/ to /usr/local/include.  This is only
    briefly noted in the README.

7) Install the FFTW library:
    Unzip/untar downloaded FFTW library and follow the installation instructions outlined
    in INSTALL.

8) Copy dislin.h to /usr/local/include.

9) Copy get_sh_spectra.c to /home for permanent storage in the container.  Compile the code via

                     g++ get_sh_spectra.c -o get_sh_spectra -lfftw3 -lbb_api

    If the code compiles, then everything has been installed successfully and the container is built.

10) Copy the container ID and exit out of the container by issuing 'exit' on the command line.  The
    changes made can now be committed to a new container via the following command (issued
    outside the docker container on the host machine)

      docker commit -m "Commit Message" -a "Author" container-ID echoloco/ubuntu:version

    Please change the "Commit Message" to something more illuminating and place your name in
    place of "Author".  Both the commit message and author must be placed inside quotation marks.
    If a large string of numbers and letters appears after executing the above command, the changes
    have been successfully committed and the container is now ready for use.
