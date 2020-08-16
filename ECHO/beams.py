from . import read_utils
from . import plot_utils

import healpy as hp

class Beam:
    '''The Beam class is the container object for various ECHO beams.

    A beam can be made using data from the observation object. This will likely use pyuvbeam for stuff.

    Attributes:
        beamlist (list): List of beams created with this class.
        efield (array, optional): numpy array for efield data.
        power (array, optional): numpy array for efield data.
    '''
    def __init__(self, beam_type, beamfile=None):
        '''
        Initial function for the beam class.
        '''

        self.beam = None
        self.power_beam = None
        self.beam_type = self._valid_beamtype(beam_type)
        self.hpx_beam = None
        self.hpx_rms = None
        self.hpx_counts = None

        pass

    def read_cst_beam(self,CST_txtfile, beam_type, frequency, telescope_name, feed_name, feed_version, model_name, model_version, feed_pol):
        '''Reads in a ASCII formatted CST export file and returns a beam model using pyuvbeam.

        Args:
            CST_txtfile: CST export file
            beam_type (str):
            frequency (list, Hz):
            telescope_name (str): The instrument name
            feed_name (str): The name of the feed
            feed_version (str): The version of the feed
            model_name (str): Name for the model
            model_version (str): version of the model
            feed_pol (str): polarization of the feed ('x','y','xx','yy')
        '''
        newbeam = read_utils.read_CST_puv(CST_txtfile, beam_type, frequency, telescope_name, feed_name, feed_version, model_name, model_version, feed_pol)
        if beam_type == 'efield':
            self.beam = newbeam
        elif beam_type == 'power':
            self.power_beam = newbeam
        return newbeam

    def make_power_beam(self, puvbeam):
        assert (self.beam!=None),"No efield beam found."
        pow_beam = puvbeam.efield_to_power(inplace = False)
        self.power = pow_beam
        return pow_beam

    def plot_efield(self, *args, **kwargs):
        assert (self.beam!=None),"No efield beam found."
        plot_utils.plot_efield(self.beam,*args, **kwargs)
        return
    def plot_efield_interp(self, *args, **kwargs):
        plot_utils.plot_efield_interp(self.beam,*args, **kwargs)
        return
    def plot_power(self):
        assert (self.power!=None),"No power beam found."
        plot_utils.plot_power(self.power)

        return
    def plot_power_interp(self):
        if self.power == None:
            print('No existing power beam.')
        else:
            plot_utils.plot_power_interp(self.power)
        return
    def plot_escatter(self):
        assert (self.beam!=None),"No efield beam found."
        plot_utils.plot_healpix_escatter(self.beam)
        return
    def plot_escatter_interp(self):
        assert (self.beam!=None),"No efield beam found."
        plot_utils.plot_hp_escatter_interp(self.beam)
        return
    def plot_powscatter(self):
        assert (self.power!=None),"No power beam found."
        plot_utils.plot_healpix_powscatter(self.power)
        return
    def plot_powscatter_interp(self):
        assert (self.power!=None),"No power beam found."
        plot_utils.plot_hp_powscatter_interp(self.power)
        return

    def make_hpx_beam(self, data_array, lat=None, lon=None):
        '''Read in the refined array and create a beam.

        Args:
            lat (): latitude of the receiver instrument
            lon (): longitude of the receiver instrument
        Returns:

        '''
        assert (self.beam_type == 'healpy'), "Invalid beamtype!"
        targetLat=lat
        targetLon=lon

        hpx_beam,hpx_rms,hpx_counts = plot_utils.grid_to_healpix(
            data_array[1:,1],
            data_array[1:,2],
            data_array[1:,3],
            data_array[1:,5],
            lat0 = targetLat, #self.refined_array[0,1],
            lon0 = targetLon, #self.refined_array[0,2],
            nside = 8
        )
        self.hpx_beam = hpx_beam
        self.hpx_rms = hpx_rms
        self.hpx_counts = hpx_counts
        self.power = hpx_beam
        return hpx_beam, hpx_rms, hpx_counts

    def write_beam(self, beam, rms, counts, prefix):
        '''Write the beam file out to .fits.

        Args:
            prefix (str): A string used to name and identify the output files.

        Returns:

        '''
        hp.write_map(prefix+'_beam.fits',self.hpx_beam, overwrite=True)
        hp.write_map(prefix+'_rms.fits',self.hpx_rms, overwrite=True)
        hp.write_map(prefix+'_counts.fits',self.hpx_counts, overwrite=True)

        return

    def difference_beams(self):
        '''Take the difference of healpix beams, plot. Requires multiple beams.

        '''
        pass

    def _valid_beamtype(self, beam_type):
        valid_beamtype = ['healpy', 'efield','power']
        assert (beam_type in valid_beamtype), "Invalid beamtype! Please select 'healpy', 'efield', or 'power'"
        return beam_type
