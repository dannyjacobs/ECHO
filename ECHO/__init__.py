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
    An observation will consist of multiple sorties.
    It will be able to start from log/data files and output a beam map.
    Sorties will be added by a function using log files.
    The sorties will be combined, calibrated, then converted to a beam map.
    
    '''
    
    def __init__(self, lat, lon, frequency=None, channel=None, description=None):
        self.sortie_list = []
        self.num_sorties = 0
        self.isFlagged = False
        self.lat = lat
        self.lon = lon
        self.ref_frequency = frequency
        self.ref_channel = channel
        if description is not None:
            self.description = description
        
    def addSortie(self, tlog, ulog, data):
        #add a sortie to this observation
        self.num_sorties+=1
        self.sortie_list.append(self.Sortie(tlog, ulog, data, sortie_num=self.num_sorties))
        
    def read_sorties(self):
        for sortie in self.sortie_list:
            sortie.read()
    
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
        Combine sorties.
        
        Output:
            
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

        #sort by time first
    def interpolate_rx(self, obsNum, tuning, polarization, frequency=None, channel=None):
        '''
        Takes position-times of the drone and uses them to create RX information of the same dimensions as position data.
        Input:
            frequency: float, the frequency of the reference channel in Mhz
            channel: int, the reference channel
            obsNum: int, the number of the observation to use
            tuning: int, the number of the tuning to use
            pol: str, which polarization to use ('XX', 'YY', 'YX', 'XY')
        
        
        Output: 
            Array with columns: 'Epoch Time(s), Lat(deg), Lon(deg), Alt(m from ground), Yaw(deg), Radio Spectra'
        '''
        
        #add ability to select frequency channel
        
        
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
            if channel:
                freqchan=channel
            else: 
                if not frequency:
                    frequency=self.ref_frequency 
                #get channel
                center_freq=frequency*1e6 #into Hz
                target_data = sortie.data_dict
                freq_arr=target_data[obs][tun]['freq']
                get_ind=np.where(freq_arr<center_freq)[0][-1]
                freqchan=get_ind
                
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

        self.refined_array = np.hstack((sortie_full_mission, interp_arr))
        self.rx_full = rx
        self.t_rx_full = time_info
        
        pass
    
    def make_beam(self, lat=None, lon=None, fits=False):
        '''
        RENAME TO MAKE BEAM
        Read in the refined array and create a beam file (FITS).
        
        Output:
        
        lat0 = 34.3486      #mru: 34.3482865
        lon0 = -106.8857    #mru:-106.886013
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
            lat0 = targetlat, #self.refined_array[0,1],
            lon0 = targetlon, #self.refined_array[0,2], 
            nside = 8
        )
        
        if fits==True:
            hp.write_map('./NS_corrected_beam.fits',hpx_beam)
            hp.write_map('./NS_corrected_rms.fits',hpx_rms)
            hp.write_map('./NS_corrected_counts.fits',hpx_counts)
        
        self.hpx_beam = hpx_beam
        self.hpx_rms = hpx_rms
        self.hpx_counts = hpx_counts
        
    
    def plot_beam(self, fits=None):
        '''        
        
        
        '''
        
        if fits:
            countsfile = './NS_corrected_counts.fits'
            beamfile = './NS_corrected_beam.fits'
            counts = read_utils.read_map(countsfile)
            beam = read_utils.read_map(beamfile)
        else:
            counts = self.hpx_counts
            beam = self.hpx_beam
        
        beam -= beam.max()

        THETA,PHI,IM = plot_utils.project_healpix(beam)
        X,Y = np.meshgrid(
            np.linspace(-1,1,num=THETA.shape[0]),
            np.linspace(-1,1,num=THETA.shape[1])
            )

        hp.mollview(beam)

        plt.figure()
        ax1 = plt.subplot(111)
        plt.axis('equal')
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

    class Sortie:
        '''
        A sortie is created by three files: a ulog, a tlog, and an LWA data file.
        The data from these files is read and compiled into arrays.
        
        Input:
        
        Output:
        
        '''
        def __init__(self, sortie_tlog, sortie_ulog, sortie_data, sortie_num, sortie_name=None):
            self.ulog = sortie_ulog
            self.tlog = sortie_tlog
            self.data = sortie_data
            self.sortie_num=sortie_num
            if not sortie_name:
                self.name = "sortie"+f"{sortie_num:02d}"
            flag_mask = []

        def get_bootstart(self):
            bootstart = self.u_dict["gps_position_u"][0][1] - self.u_dict["gps_position_u"][0][0]
            return bootstart

        def apply_bootstart(self):
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

        def read(self):
            '''
            Read in the sortie from associated data files.
            
            Output:
            
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
            
            
        def flag_waypoints(self):
            '''
            Flag data arrays based on waypoint data.
            
            Output:
            
            '''
            # flag based on mission waypoints
            pass

        def flag_endpoints(self):
            '''
            Flag data arrays based on mission start/end.
            
            Output:
            
            '''
            # flag based on mission waypoints
            self.flagged_data, self.mission_data = read_utils.mission_endpoint_flagging(
                self.t_dict["global_t"], 
                self.t_dict["waypoint_t"]
            )

        def flag_yaws(self):
            # flag based on yaw position
            pass
        
        ### Plotting Functions
        
        #flesh this out, lower priority
        #plot waterfalls, channels
        
        def plot(self):
            #This makes a plot of various views of the drone data.
            
            
            
            fig1 = plt.figure()
            plt.plot(self.t_dict['global_t'][:,1],self.t_dict['global_t'][:,2],'b.')
            plt.plot(self.u_dict['global_position_u'][:,1],self.u_dict['global_position_u'][:,2],'r.', alpha=0.25)
            plt.xlabel('Latitude (deg)')
            plt.xticks(rotation=45)
            plt.ylabel('Longitude (deg)')
            plt.title('NS Mid GLOBAL Position')
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
            ax3.title.set_text('NS Mid Global Z')
            #plt.xticks(rotation=15)
            ax3.axes.get_yaxis().set_visible(False)
            #ax3.xaxis.set_major_formatter(date_formatter)
            
            #plt.legend(['Tlogs','Ulogs'],bbox_to_anchor=(1.25,7.5))
            #fig.tight_layout()
            #alt
            
            #position
            
        def plot_flags():
            
            pass