from . import read_utils
from . import plot_utils
from . import position_utils
from . import time_utils
from . import server_utils
from . import beams

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import h5py
from astropy.time import Time
import healpy as hp

class Observation:
    '''
    The class object for making observations.

    Args:
            lat (float):, latitude of receiving antenna (degrees)
            lon (float), longitude of receiving antenna (degrees)
            frequency (int): the reference frequency of the transmitter (MHz)
            channel (int), The reference channel of the transmitter
            description (str):, text string with information about observation
    '''

    def __init__(self, lat, lon, frequency=None, description=None):
        '''Create an observation for a particular target antenna.

        '''

        self.sortie_list = []
        self.num_sorties = 0
        self.isFlagged = False
        self.lat = float(lat)
        self.lon = float(lon)
        if frequency: self.ref_frequency = float(frequency)
        if description: self.description = description

        return

    def addSortie(self, tlog, ulog, data, sortie_name=None, sortie_title=None):
        '''Add a sortie to the current observation class.

        Args:
            tlog (file): txt file for the tlog data
            ulog (file): txt file for the ulog data
            data (file): txt file for the receiver data
            sortie_name (str): unique name for this sortie
            sortie_title (str): display title for this sortie

        '''

        self.num_sorties+=1
        self.sortie_list.append(self.Sortie(sortie_tlog=tlog, sortie_ulog=ulog, sortie_data=data, sortie_name=sortie_name, sortie_title=sortie_title, sortie_num=self.num_sorties, ref_f=self.ref_frequency ))

        return

    def read_sorties(self):
        '''Reads in the data files for a given sortie.

        '''
        for sortie in self.sortie_list:
            sortie.read()
            sortie.get_freq_chans()


        return

    def flagSorties(self):
        '''Flag the sortie for start and endpoints, as well as waypoints.

        '''
        for sortie in self.sortie_list:
            print(sortie["name"])
            #flag start/stop
            sortie.flag_endpoints()
            #flag waypoints
            sortie.flag_waypoints()
            #flag yaws
            #sortie.flag_yaws()

        return

    def sort_sorties(self):
        '''Sort our current list of sorties by time, using the first entry in each.

        At any point we may need to sort the list of sorties by time.
        It's preferable to do this rather than sort the data arrays after combining.


        Returns:
            s: Sortie object
        '''
        #get list of sorties
        sorties = self.sortie_list
        #check first time in each sortie
        #order sorties by first time
        s = sorted(sorties, key = lambda sortie:sortie.t_dict['global_t'][0,0])

        return s

    def combine_sorties(self):
        '''Combine our current list of sorties to create a data object for position.

        Sorts currently added sorties by timestamp, then aggregates into a single array

        Returns:
            dataproduct (array): 'Epoch Time(s), Lat(deg), Lon(deg), Alt(m from ground), Yaw(deg)' for every sortie

        '''

        if 'mission_data' in dir(self.sortie_list[0]):
            combined_arr = self.sortie_list[0].mission_data
            for sortie in self.sortie_list[1:]:
                if 'mission_data' not in dir(self.sortie_list[0]):
                    print("Unable to combine: " +sortie.name + " mission data not flagged")
                    break
                combined_arr = np.vstack((combined_arr, sortie.mission_data))
            self.dataproduct = np.sort(combined_arr, axis=0)  #remove after rewrite
        else:
            print("Unable to combine: " +self.sortie_list[0].name + " mission data not flagged")

        return

    def interpolate_rx(self, obsNum, tuning, polarization):
        '''Takes position-times of the drone and interpolate the receiver data to the same dimensions as position data.

        Args:
            obsNum (int): the number of the observation to use
            tuning (int): the number of the tuning to use, 1 or 2
            pol (str): which polarization to use ('XX', 'YY', 'YX', 'XY')


        Returns:
            refined_array (array): 'Epoch Time(s), Lat(deg), Lon(deg), Alt(m from ground), Yaw(deg), Radio Spectra'
        '''


        obs='Observation'+str(obsNum)

        tun='Tuning'+str(tuning)
        pol = polarization

        sorties = self.sort_sorties()
        rx_data = []
        t_rx = []
        pos_times = []
        for i,sortie in enumerate(sorties):
            #get frequency channel of sortie

            #target_data = h5py.File(sortie.data,'r')
            target_data = sortie.data_dict
            freqchan = sortie.freq_chan
            start_time, end_time = sortie.mission_data[0,0], sortie.mission_data[-1,0]
            pos_times.append(list(sortie.mission_data[:,0]))

            rx_times = target_data[obs]['time'][()]
            indices = np.nonzero(np.logical_and(rx_times >= start_time , rx_times <= end_time))
            times = target_data[obs]['time'][list(indices[0])]
            t_rx.append(Time(times,scale='utc',format='unix'))
            rx_data.append(
                read_utils.dB(
                    target_data[obs][tun][pol][indices[0],freqchan] #freqchan, 512]
                )
            )

        rx = np.concatenate(rx_data)
        t_rx = np.concatenate(t_rx)
        pos_times = np.concatenate(pos_times)
        postimes = Time(pos_times, format = 'unix')
        time_info =  Time(t_rx,scale='utc')
        interp_rx = read_utils.interp_rx(postimes, time_info, rx)

        for i,sortie in enumerate(sorties):
            if i == 0:
                sortie_full_mission = sortie.mission_data
            else:
                sortie_full_mission = np.vstack((sortie_full_mission, sortie.mission_data))

        interp_arr = np.zeros((interp_rx.shape[0],1))
        for i, interp in enumerate(interp_rx):
            interp_arr[i,0] = interp

        refined_array = np.hstack((sortie_full_mission, interp_arr))
        self.refined_array=refined_array[~np.isnan(refined_array).any(axis=1)]
        self.rx_full = rx
        self.t_rx_full = time_info

        return

    def make_beam(self, lat=None, lon=None):
        '''Read in the refined array and create a beam.

        Args:
            lat (): latitude of the receiver instrument
            lon (): longitude of the receiver instrument
        Returns:

        '''
        if not lat:
            targetLat=self.lat
        else:
            targetLat=lat
        if not lon:
            targetLon=self.lon
        else:
            targetLon=lon

        newBeam = beams.Beam(beam_type='healpy')
        hpx_beam,hpx_rms,hpx_counts = newBeam.make_hpx_beam(self.refined_array, targetLat, targetLon)

        self.hpx_beam = hpx_beam
        self.hpx_rms = hpx_rms
        self.hpx_counts = hpx_counts

        return newBeam

    def write_beam(self,prefix):
        '''Write the beam file out to .fits.

        Args:
            prefix (str): A string used to name and identify the output files.

        Returns:

        '''
        hp.write_map(prefix+'_beam.fits',self.hpx_beam, overwrite=True)
        hp.write_map(prefix+'_rms.fits',self.hpx_rms, overwrite=True)
        hp.write_map(prefix+'_counts.fits',self.hpx_counts, overwrite=True)

        return

    def diffrence_beams():
        '''Take the difference of healpix beams, plot. Requires multiple beams.

        '''
        pass

    def plot_mollview(self, *args, **kwargs):
        '''Plot a mollview of the beam using

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        '''
        beam=self.hpx_beam
        plot_utils.mollview(beam, 'Target Beam', *args, **kwargs)

        return


    def plot_grid(self, *args, **kwargs):
        '''Plot a grid view of the beam.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        '''
        M = np.ma.array(self.hpx_beam,fill_value=hp.UNSEEN)
        M = np.ma.masked_where(hp.UNSEEN==M,M)
        M.fill_value = hp.UNSEEN

        M -= M.max()

        beams=[M]
        plot_utils.healpix_grid(beams, 'Target Directivity', '1', 1, 1,*args, **kwargs)

        return

    def plot_beam(self, fits=False,beamfile=None,countsfile=None):
        '''Plot the healpix beam from our observation object.

        Optionally plot beams read in from beam files.

        Args:
            fits (bool):
            beamfile (str):
            countsfile (str):

        Returns:

        '''

        if fits==True:
            counts = read_utils.read_map(countsfile)
            beam = read_utils.read_map(beamfile)
        else:
            M = np.ma.array(self.hpx_beam,fill_value=hp.UNSEEN)
            M = np.ma.masked_where(hp.UNSEEN==M,M)
            M.fill_value = hp.UNSEEN

            counts = self.hpx_counts
            beam = M

        beam -= beam.max()

        THETA,PHI,IM = plot_utils.project_healpix(beam)
        X,Y = np.meshgrid(
            np.linspace(-1,1,num=THETA.shape[0]),
            np.linspace(-1,1,num=THETA.shape[1])
            )

        hp.mollview(beam)

        plt.figure()
        ax1 = plt.subplot(111)
        ax1.axis('equal')
        beamcoll = plot_utils.make_polycoll(beam,cmap=matplotlib.cm.jet)
        beamcoll.set_clim(-2.3,0)
        ax1.add_collection(beamcoll)
        CS = ax1.contour(X,Y,THETA*180/np.pi,[20,40,60],colors='k')
        CS.levels = [plot_utils.nf(val) for val in CS.levels]
        plt.clabel(CS, inline=1, fontsize=10,fmt=plot_utils.fmt)
        ax1.autoscale_view()
        ax1.set_yticklabels([])
        ax1.set_xticklabels([])
        ax1.set_title('Gridded power')
        cb = plt.colorbar(beamcoll, ax=ax1,orientation='horizontal')
        tick_locator = matplotlib.ticker.MaxNLocator(nbins=5)
        cb.locator = tick_locator
        cb.update_ticks()
        cb.set_label('dB')

        return

    def plot_slices(self, figsize=None, *args, **kwargs):
        '''Plot E and H plane slices of the beam

        Args:
            figsize (tuple): figure size for plot
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:

        '''
        radTheta=np.pi/2
        alt=np.linspace(-radTheta, radTheta)
        az=np.zeros_like(alt)

        M = np.ma.array(self.hpx_beam,fill_value=hp.UNSEEN)
        M = np.ma.masked_where(hp.UNSEEN==M,M)
        M.fill_value = hp.UNSEEN
        beam_map = M
        beam_map -= beam_map.max()

        slice_E = plot_utils.get_interp_val(beam_map,alt,az)
        slice_H = plot_utils.get_interp_val(beam_map,alt,az+np.pi/2)

        plt.figure(figsize=figsize)
        plt.plot(alt*180/np.pi,slice_E,'-k',lw=2, *args, **kwargs)
        plt.grid()
        plt.xlabel('$\\theta$ (deg)')
        plt.ylabel('E plane\n [dB V/m]')
        plt.figure(figsize=figsize)
        plt.plot(alt*180/np.pi,slice_H,'-k',lw=2, *args, **kwargs)
        plt.grid()
        plt.xlabel('$\\theta$ (deg)')
        plt.ylabel('H plane\n [dB V/m]')

        return

    def plot_polar(self,altitude, *args, **kwargs):
        '''Plot polar diagrams of the received beam.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        '''
        radPhi=np.pi
        az=np.linspace(0, 2*radPhi,360)
        alt=np.zeros_like(az)
        alt[:]=altitude*np.pi/2

        M = np.ma.array(self.hpx_beam,fill_value=hp.UNSEEN)
        M = np.ma.masked_where(hp.UNSEEN==M,M)
        M.fill_value = hp.UNSEEN
        beam_map = M
        beam_map -= beam_map.max()

        pol_slice = plot_utils.get_interp_val(beam_map,alt,az)

        plt.figure(figsize=(8,8))
        ax=plt.subplot(111, projection='polar', *args, **kwargs)
        ax.plot(az, pol_slice)
        ax.set_theta_zero_location('N')
        ax.set_theta_direction('clockwise')
        ax.set_rmax(5)
        ax.set_rmin(-10)
        ax.grid(True)
        plt.show()
        plt.close()
        return

    def plot_isometric(self, figsize=(5,5), *args, **kwargs):
        '''Plot polar diagrams of the received beam.

        Args:
            figsize (tuple): figure size for plot
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        '''
        xs=self.refined_array[:,1]
        ys=self.refined_array[:,2]
        zs=self.refined_array[:,3]
        fig = plot_utils.plot_position_3d(xs, ys, zs, figsize, *args, **kwargs)

        #fig = plt.figure()
        #ax = fig.add_subplot(111, projection='3d')
        #ax.plot(xs, ys, zs=0, zdir='z')
        fig.axes[0].set_xlabel('Latitude')
        fig.axes[0].set_ylabel('Longitude')
        fig.axes[0].set_zlabel('Altitude')

        return

    class Sortie:
        '''
        A sortie is created by three files: a ulog, a tlog, and an LWA data file.
        The data from these files is read and compiled into arrays.

        '''
        def __init__(self, sortie_tlog, sortie_ulog, sortie_data, sortie_num, ref_f, sortie_name=None, sortie_title=None):
            self.ulog = sortie_ulog
            self.tlog = sortie_tlog
            self.data = sortie_data
            self.sortie_num=sortie_num
            self.title=sortie_title
            self.ref_frequency=ref_f
            if not sortie_name:
                #self.name = "sortie"+f"{sortie_num:02d}"
                self.name = "sortie%(sortienum)02d"%{'sortienum':sortie_num}
            flag_mask = []

            return

        def get_bootstart(self):
            '''Uses the GPS time to calculate the time at drone boot.

            '''
            bootstart = self.u_dict["gps_position_u"][0][1] - self.u_dict["gps_position_u"][0][0]

            return bootstart

        def apply_bootstart(self):
            '''Puts drone data on absolute GPS-based time scale.

            Uses GPS messages in on-board ulog to calibrate times of positions logged on ground station.

            '''
            bootstart = self.u_dict["gps_position_u"][0][1] - self.u_dict["gps_position_u"][0][0]
            for key,data in self.t_dict.items():
                if key!="log_type":
                    if key!='waypoint_t':
                        data[:,0] = data[:,1]+bootstart
                        data = np.delete(data, 1, 1)
                        self.t_dict[key]=data
            for key,data in self.u_dict.items():
                if key!="log_type":
                    data[:,0] = data[:,0]+bootstart
                    if key!="global_position_u":
                        data = np.delete(data, 1, 1)
                    self.u_dict[key]=data

            return

        def get_freq_chans(self):
            '''Find the channel for our reference frequency.

            Args:

            Returns:

            '''
            frequency=self.ref_frequency
            obs='Observation1'
            tun= 'Tuning1'
            target_data = self.data_dict
            center_freq = frequency*1e6 #into Hz
            freq_arr = target_data[obs][tun]['freq']
            get_ind = np.where(freq_arr<=center_freq)[0][-1]
            return get_ind

        def read(self):
            '''Read in the sortie from associated data files.

            The stored tlog, ulog, and receiver datafiles are opened and copied into dictionaries.

            Returns:
                t_dict (dict): A dictionary containing info from the sortie tlog
                u_dict (dict): A dictionary containing info from the sortie ulog
                data_dict (dict): A dictionary containing info from the sortie receiver datafile
            '''
            sortie_tlog = read_utils.read_tlog_txt(self.tlog)
            sortie_ulog = read_utils.read_ulog(
                self.ulog,
                messages="vehicle_global_position,vehicle_local_position,vehicle_gps_position"
            )
            self.t_dict={
                "log_type":"t",
                "waypoint_t":sortie_tlog[0],
                "global_t":sortie_tlog[1],
                "local_t":sortie_tlog[2],
                "gps_t":sortie_tlog[3]
            }
            self.u_dict={
                "log_type":"u",
                'global_position_u':sortie_ulog[0],
                'local_position_u':sortie_ulog[1],
                'gps_position_u':sortie_ulog[2]
            }
            #TODO: Add data read instead of reading in interpolate_rx
            self.data_dict = read_utils.read_h5(self.data)
            self.freq_chan = self.get_freq_chans()
           


            return

        #function to adjust gain?

        def flag_waypoints(self):
            '''Flag data arrays based on waypoint data.

            Args:

            '''
            # flag based on mission waypoints
            pass

        def flag_endpoints(self):
            '''Flag data arrays based on mission start/end.

            Reads in "global_t" and "waypoint_t" from the tlog data dictionary.

            "global_t" contains continuous position data from drone telemetry during the entire sortie.
            "waypoint_t" contains the position data for each navigational waypoint used to maneuver the drone.

            Updates flagged_data and mission_data properties for a sortie

            '''

            self.flagged_data, self.mission_data = read_utils.mission_endpoint_flagging(
                self.t_dict["global_t"],
                self.t_dict["waypoint_t"]
            )

            return

        def flag_yaws(self):
            # flag based on yaw position
            pass

        ### Plotting Functions

        def plot(self):
            '''Creates multiple plots showing position data for sortie.

            Tlog X/Y Position, ULog X/Y Position, X Position / Time, Y Position / Time, Z Position / Time:

            Return:
                Tlog X/Y Position:
                ULog X/Y Position:
                X Position / Time:
                Y Position / Time:
                Z Position / Time:

            '''



            fig1 = plt.figure()
            plt.plot(self.t_dict['global_t'][:,1],self.t_dict['global_t'][:,2],'b.')
            plt.plot(self.u_dict['global_position_u'][:,1],self.u_dict['global_position_u'][:,2],'r.', alpha=0.25)
            plt.xlabel('Latitude (deg)')
            plt.xticks(rotation=45)
            plt.ylabel('Longitude (deg)')
            plt.title(self.title + 'Global Position')
            plt.axis('square')
            plt.grid()
            plt.legend(['Tlogs','Ulogs'],bbox_to_anchor=(1.35,1))
            plt.ticklabel_format(useOffset=False)

            fig2 = plt.figure(figsize=(5,5))

            date_fmt = '%m-%d %H:%M:%S'
            date_formatter = mdate.DateFormatter(date_fmt)

            ax1 = fig2.add_subplot(311)
            ax1.plot(self.t_dict['global_t'][:,0],self.t_dict['global_t'][:,1],'b-')
            ax1.plot(self.u_dict['global_position_u'][:,0],self.u_dict['global_position_u'][:,1],'r-',alpha=0.5)
            ax1.title.set_text('Global X')
            ax1.set_ylabel('Latitude in deg')
            #plt.xticks(rotation=15)
            ax1.axes.get_yaxis().set_visible(False)
            #ax1.xaxis.set_major_formatter(date_formatter)

            ax2 = fig2.add_subplot(312)
            ax2.plot(self.t_dict['global_t'][:,0],self.t_dict['global_t'][:,2],'b-')
            ax2.plot(self.u_dict['global_position_u'][:,0],self.u_dict['global_position_u'][:,2],'r-',alpha=0.5)
            ax2.title.set_text('Global Y')
            ax2.set_ylabel('Longitude in deg')
            #plt.xticks(rotation=15)
            ax2.axes.get_yaxis().set_visible(False)
            #ax2.xaxis.set_major_formatter(date_formatter)

            ax3 = fig2.add_subplot(313)
            ax3.plot(self.t_dict['global_t'][:,0],self.t_dict['global_t'][:,3],'b-')
            ax3.plot(self.u_dict['global_position_u'][:,0],self.u_dict['global_position_u'][:,3],'r-',alpha=0.5)
            ax3.title.set_text('Global Z')
            ax3.set_ylabel('Alt in m')
            #plt.xticks(rotation=15)
            ax3.axes.get_yaxis().set_visible(False)
            #ax3.xaxis.set_major_formatter(date_formatter)

            #plt.legend(['Tlogs','Ulogs'],bbox_to_anchor=(1.25,7.5))
            #fig2.tight_layout()
            #alt

            #position

            return

        def plot_flags():
            '''Creates a plot showing flagged positions for sortie.

            Return:

            '''
            pass
