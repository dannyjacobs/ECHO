from __future__ import absolute_import
from . import read_utils
from . import plot_utils
from . import position_utils
from . import time_utils
from . import server_utils

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdate

import ECHO.read_utils as rd
import ECHO.time_utils
import ECHO.position_utils as pos


class Observation:
    
    '''
    An observation will consist of multiple sorties.
    It will be able to start from log/data files and output a beam map.
    Sorties will be added by a function using log files.
    The sorties will be combined, calibrated, then converted to a beam map.
    
    '''
    
    def __init__(self):
        self.sortie_list = []
        self.num_sorties = 0
        
    def addSortie(self, tlog, ulog, data):
        #add a sortie to this observation
        self.num_sorties+=1
        self.sortie_list.append(self.Sortie(tlog, ulog, data, sortie_num=self.num_sorties))
        
    def read_sorties(self):
        for sortie in self.sortie_list:
            sortie.read()
    
    def flagSorties(self):
        '''
        Flag the global data in each sortie
        return flagged data, mission data
        '''
        for sortie in self.sortie_list:
            print(sortie["name"])
            #flag start/stop
            sortie.flag_endpoints()
            #flag waypoints
            sortie.flag_waypoints()
            #flag yaws
            sortie.flag_yaws
            
    def combine_sorties():
        #combine multiple sorties into a dataproduct
        #Customize fields?
        
        #sort by time first
        pass

    class Sortie:
        '''
        A sortie is created by three files: a ulog, a tlog, and an LWA data file.
        The data from these files is read and compiled into arrays.
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
            sortie_tlog = read_utils.read_tlog_txt(self.tlog)
            sortie_ulog = read_utils.read_ulog(self.ulog,messages="vehicle_global_position,vehicle_local_position,vehicle_gps_position")
            self.t_dict={"log_type":"t","waypoint_t":sortie_tlog[0],"global_t":sortie_tlog[1],"local_t":sortie_tlog[2],"gps_t":sortie_tlog[3]}
            self.u_dict={"log_type":"u",'global_position_u':sortie_ulog[0],'local_position_u':sortie_ulog[1],'gps_position_u':sortie_ulog[2]}

        def flag_waypoints(self):
            # flag based on mission waypoints
            pass

        def flag_endpoints(self):
            # flag based on mission waypoints
            self.flagged_data, self.mission_data = read_utils.mission_endpoint_flagging(self.t_dict["global_t"], self.t_dict["waypoint_t"])

        def flag_yaws(self):
            # flag based on mission waypoints
            pass
        
        ### Plotting Functions
        
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
            
            