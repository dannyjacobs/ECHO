from __future__ import absolute_import
from . import read_utils
from . import plot_utils
from . import position_utils
from . import time_utils
from . import server_utils

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import pandas as pd
import h5py 
from astropy.time import Time
import healpy as hp


class Observation:
    '''
    The class object for making observations.
    '''
    
    def __init__(self, lat, lon, frequency=None, description=None):
        '''
        Create an observation for a particular target antenna.
        Input
            lat: float, latitude of receiving antenna (degrees)
            lon: float, longitude of receiving antenna (degrees)
            frequency: the reference frequency of the transmitter (MHz)
            channel: int, The reference channel of the transmitter 
            description: str, text string with information about observation

        Output
            Creates an object that contains multiple sorties, as  well as methods to analyze them.

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
        #add a sortie to this observation
        #def __init__(self, sortie_tlog, sortie_ulog, sortie_data, sortie_num, sortie_name=None, sortie_title=None)
        self.num_sorties+=1
        self.sortie_list.append(self.Sortie(sortie_tlog=tlog, sortie_ulog=ulog, sortie_data=data, sortie_name=sortie_name, sortie_title=sortie_title, sortie_num=self.num_sorties, ref_f=self.ref_frequency ))
        
        return
        
    def read_sorties(self):
        for sortie in self.sortie_list:
            sortie.read()
            sortie.get_freq_chans()
        return
    
    def flagSorties(self):
        '''
        Flag the global data in each sortie.
        
        Output: flagged data, mission data
        
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
        '''
        At any point we may need to sort the list of sorties by time. 
        It's preferable to do this rather than sort the data arrays after combining.
        
        Sort our current list of sorties by time, using the first entry in each.
        
        Output:
            s: Sortie object
        '''
        #get list of sorties
        sorties = self.sortie_list
        #check first time in each sortie
        #order sorties by first time
        s = sorted(sorties, key = lambda sortie:sortie.t_dict['global_t'][0,0])
        
        return s
    
    def combine_sorties(self):
        '''
        Combine sorties. Sorts currently added sorties by timestamp, then aggregates into a single array
        
        Output: 
            Array containing: 'Epoch Time(s), Lat(deg), Lon(deg), Alt(m from ground), Yaw(deg)' for every sortie
            
        '''

        #combine multiple sorties into a dataproduct
        
        #TODO: rewrite using sort_sorties()
        
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
        '''
        Takes position-times of the drone and uses them to interpolate the receiver 
        data to the same dimensions as position data.
        
        Input:
            frequency: float, the frequency of the reference channel in Mhz
            channel: int, the reference channel
            obsNum: int, the number of the observation to use
            tuning: int, the number of the tuning to use
            pol: str, which polarization to use ('XX', 'YY', 'YX', 'XY')
        
        
        Output: 
            Array with columns: 'Epoch Time(s), Lat(deg), Lon(deg), Alt(m from ground), Yaw(deg), Radio Spectra'
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
            freqchan=sortie.freq_chan
                
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
        '''
        Read in the refined array and create a beam.
        Input:
        Output:

        '''
        if not lat:
            targetLat=self.lat
        else:
            targetLat=lat
        if not lon:
            targetLon=self.lon
        else:
            targetLon=lon
        
        hpx_beam,hpx_rms,hpx_counts = plot_utils.grid_to_healpix(
            self.refined_array[1:,1],
            self.refined_array[1:,2],
            self.refined_array[1:,3],
            self.refined_array[1:,5],
            lat0 = targetLat, #self.refined_array[0,1],
            lon0 = targetLon, #self.refined_array[0,2], 
            nside = 8
        )

        self.hpx_beam = hpx_beam
        self.hpx_rms = hpx_rms
        self.hpx_counts = hpx_counts
        
        return
        
    def write_beam(self,prefix):
        '''
        Write the beam file out to .fits.
        Input:
            prefix (str): A string used to name and identify the output files.
        Output:
            
        '''
        hp.write_map(prefix+'_beam.fits',self.hpx_beam, overwrite=True)
        hp.write_map(prefix+'_rms.fits',self.hpx_rms, overwrite=True)
        hp.write_map(prefix+'_counts.fits',self.hpx_counts, overwrite=True)
        
        return
    
    def diffrence_beams():
        '''
        Take the difference of healpix beams, plot.
        '''
        pass
    
    def plot_beam(self, fits=False,beamfile=None,countsfile=None):
        '''        
        Plot the healpix beam from our observation object. Optionally plot beams read in from beam files.
        
        Input
            fits (bool):
            beamfile (str):
            countsfile (str):
        Output:
            
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
    
    def plot_slices(self):
        '''
        Plot E and H plane slices of the beam
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
        
        plt.figure()
        plt.plot(alt*180/np.pi,slice_E,'-k',lw=2)
        plt.grid()
        plt.xlabel('$\\theta$ (deg)')
        plt.ylabel('E plane\n [dB V/m]')
        plt.figure()
        plt.plot(alt*180/np.pi,slice_H,'-k',lw=2)
        plt.grid()
        plt.xlabel('$\\theta$ (deg)')
        plt.ylabel('H plane\n [dB V/m]')
        
        return
    
    def plot_polar(self):
        '''
        Plot polar diagrams of the received beam.
        
        '''
        radPhi=np.pi
        az=np.linspace(-radPhi, radPhi)
        alt=np.zeros_like(az)
        alt[:]=np.pi/2

        M = np.ma.array(self.hpx_beam,fill_value=hp.UNSEEN)
        M = np.ma.masked_where(hp.UNSEEN==M,M)
        M.fill_value = hp.UNSEEN
        beam_map = M
        beam_map -= beam_map.max()
        
        pol_slice = plot_utils.get_interp_val(beam_map,alt,az)
        
        ax=plt.subplot(111, projection='polar')
        ax.plot((az+np.pi)*180/np.pi, pol_slice)
        ax.set_rmax(5)
        ax.set_rmin(-10)
        ax.grid(True)
        
        return

    class Sortie:
        '''
        A sortie is created by three files: a ulog, a tlog, and an LWA data file.
        The data from these files is read and compiled into arrays.
        
        Input:
        
        Output:
        
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
            '''
             Uses the GPS time to calculate the time at drone boot.
             
             Output: 
                 bootstart (int): 
            '''
            bootstart = self.u_dict["gps_position_u"][0][1] - self.u_dict["gps_position_u"][0][0]
            
            return bootstart

        def apply_bootstart(self):
            '''
            Puts drone data on absolute GPS-based time scale. Uses GPS messages in 
            on-board ulog to calibrate times of positions logged on ground station.
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
            frequency=self.ref_frequency
            obs='Observation1'
            tun='Tuning1'
            target_data = self.data_dict
            center_freq = frequency*1e6 #into Hz
            freq_arr = target_data[obs][tun]['freq']
            get_ind = np.where(freq_arr<=center_freq)[0][-1]
            return get_ind
        
        def read(self):
            '''
            Read in the sortie from associated data files. The stored tlog, ulog, and 
            receiver datafiles are opened and copied into dictionaries.
            
            Output:
                t_dict: A dictionary containing info from the sortie tlog
                u_dict: A dictionary containing info from the sortie ulog
                data_dict: A dictionary containing info from the sortie receiver datafile
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
            '''
            Flag data arrays based on waypoint data.
            
            Output:
            
            '''
            # flag based on mission waypoints
            pass

        def flag_endpoints(self):
            '''
            Flag data arrays based on mission start/end. Reads in "global_t" and 
            "waypoint_t" from the tlog data dictionary.
            
            "global_t" contains continuous position data from drone telemetry during the entire sortie.
            "waypoint_t" contains the position data for each navigational waypoint used to maneuver the drone.
            
            Output:
                flagged_data:
                mission_data:
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
        
        #flesh this out, lower priority
        #plot waterfalls, channels
        
        def plot(self):
            '''
            Creates multiple plots showing position data for sortie.
            
            Output:
                Tlog X/Y Position
                ULog X/Y Position
                X Position / Time
                Y Position / Time
                Z Position / Time
            
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
            #plt.xticks(rotation=15)
            ax1.axes.get_yaxis().set_visible(False)
            #ax1.xaxis.set_major_formatter(date_formatter)
            
            ax2 = fig2.add_subplot(312)
            ax2.plot(self.t_dict['global_t'][:,0],self.t_dict['global_t'][:,2],'b-')
            ax2.plot(self.u_dict['global_position_u'][:,0],self.u_dict['global_position_u'][:,2],'r-',alpha=0.5)
            ax2.title.set_text('Global Y')
            #plt.xticks(rotation=15)
            ax2.axes.get_yaxis().set_visible(False)
            #ax2.xaxis.set_major_formatter(date_formatter)
            
            ax3 = fig2.add_subplot(313)
            ax3.plot(self.t_dict['global_t'][:,0],self.t_dict['global_t'][:,3],'b-')
            ax3.plot(self.u_dict['global_position_u'][:,0],self.u_dict['global_position_u'][:,3],'r-',alpha=0.5)
            ax3.title.set_text('Global Z')
            #plt.xticks(rotation=15)
            ax3.axes.get_yaxis().set_visible(False)
            #ax3.xaxis.set_major_formatter(date_formatter)
            
            #plt.legend(['Tlogs','Ulogs'],bbox_to_anchor=(1.25,7.5))
            #fig.tight_layout()
            #alt
            
            #position
            
            return
            
        def plot_flags():
            
            pass
    class Beam:
        '''
        
        The Beam class is the container object for various ECHO beams.
        a beam can be made using data from the observation object.
        
        
        This will likely use pyuvbeam for stuff.
        '''
        def __init__():
            pass
        
        pass

class Model:
    '''
    Model to simulate link budget, this is mostly structural for now
    Requires:
        Drone Position (XYZ)
        Drone Attitude (Roll Pitch Yaw)
        Drone Beam
        RX Beam
        
    '''
    
    def __init__():
        
        pass
    
    def get_distance():
        
        pass
    
    def link_budget():
        
        pass
    
    
    class drone:
        '''
        Model of our drone, includes positions, attitudes, beam
        
        '''
        def __init(self):
            
            pass
    
    class antenna:
        '''
        Model of our antenna, includes position, beam
        
        '''
        def __init__(self):
            pass
    
    #define RX center
    #define drone position
    
    