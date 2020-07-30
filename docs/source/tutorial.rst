.. ECHO documentation master file, created by
   sphinx-quickstart on Mon Jul 13 10:42:31 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. highlight:: python

Tutorial
================================
ECHO is used to inspect and combine drone data and receiver data from any telescope and radio receiver.

Data in ECHO consists of log files from the drone as well as efield or power data from the receiving instrument.

To begin with, we make an Observation Object, passing in the latitude, longitude, our reference frequency, and a short description.::

    import ECHO
    datadir = '/LWA_October_2019/data/'


    NS_Obs = ECHO.Observation(lat=34.3486, lon=-106.8857, frequency=70, description='LWA Observation')


Working with sorties
--------------------
Any data used is organized into sorties. Sorties are the associated data from the drone flight and the received data during that flight.::

    NS_Obs.addSortie(
        tlog=datadir+"tlog_data/NSMap_MiddleSortie.txt",
        ulog=datadir+"ulog_data/NSMap_MiddleSortie.ulg",
        data=datadir+"LWA_spectra/NS_Sorties/01_NSmap_MidSortie_waterfall.hdf5",
        sortie_title="NS Mid"
        )

    NS_Obs.read_sorties()

The data is placed in dicts within the object.::

    print(NS_Obs.sortie_list[0].t_dict.keys())
    print(NS_Obs.sortie_list[0].u_dict.keys())


Additional sorties can be added to a single observation.::

    #add two additional sorties
    NS_Obs.addSortie(
        tlog=datadir+"tlog_data/NSMap_TopSortie_Repeat.txt",
        ulog=datadir+"ulog_data/NSMap_TopSortie_Repeat.ulg",
        data=datadir+"LWA_spectra/NS_Sorties/03_NSmap_TopSortie_waterfall.hdf5"
        )
    NS_Obs.addSortie(
        tlog=datadir+"tlog_data/NSMap_BottomSortie.txt",
        ulog=datadir+"ulog_data/NSMap_BottomSortie.ulg",
        data=datadir+"LWA_spectra/NS_Sorties/02_NSmap_BotSortie_waterfall.hdf5"
        )
    #read in all of the current sorties, apply bootstart correction, and flag the start/endpoints
    for sortie in NS_Obs.sortie_list:
        sortie.read() #Note that this replaces all previous reads
        sortie.apply_bootstart()
        sortie.flag_endpoints()

    #takes the data from all sorties, sorts them by time, and combines them into a single array
    NS_Obs.combine_sorties()

    #combine the drone position data with the instrument receiver data
    NS_Obs.interpolate_rx(1,1,'XX')

Making beams
----------------
To further investigate an instrument's response during a sortie, it is helpful to look at the beam pattern of the instrument. ::

    Obs_beam = NS_Obs.make_beam()

    NS_Obs.plot_mollview()

    NS_Obs.plot_grid()

    NS_Obs.plot_slices(figsize=(10,10))

    NS_Obs.plot_polar(altitude=0)
