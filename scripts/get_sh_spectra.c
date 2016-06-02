/**

Reads from SignalHound, live plotting tool + saves raw data.

Authors:
Hamdi, Jay & Michael 2/13/2015

Compile
g++ get_sh_spectra.c -o get_sh_spectra -lbb_api -lfftw3

**/

#include <cstdio>
#include <iostream>
#include <time.h>
#include <unistd.h>
#include <cmath>
#include <vector>
#include <fftw3.h>
#include <signal.h>
#include "bb_api.h"

extern "C"
{
    #include "dislin.h"
};

/////////////////////////////////////////////////////////////////
//			Defined Variables		       //
/////////////////////////////////////////////////////////////////

#define pi 3.141592
#define Fs 80 	  // sampling rate [MSample / second] limited by SH API
#define Ns 299008 // 3.7376 mS of data
#define n_zoom 103

/////////////////////////////////////////////////////////////////
// 		          User Settings                        //
/////////////////////////////////////////////////////////////////


// Integration time in [mS] must be multiple of 3.7376 mS
#define tau 40007.2704 //20003.6352 // 3737.6 //10001.8176 //5000.9088
#define Nfft 4096 //131072 (2^17)
// number of fft points power of 2

float times[Ns]; 		 			// Time Vector
float f [Nfft / 2 ];  //remove DC 		 	// Frequency Vector [MHz]
float f_zoom [n_zoom ];
float fft_output[(Nfft / 2 )]; 	// Frequency Domain Data , remove 0 DC
float avg[(Nfft/2) ]; // average fft_out
float avg_zoom [n_zoom];
float maxmax;
float maxfreq;
time_t timestamp;
// Sweep Parameters (in MHz)
#define fcenter 137e6 // Center Frequency in H
#define fspan 20e6

#define y1min 0.600
#define y1max 4.20
#define y1step 0.400

#define y2min 2.800
#define y2max 4.20
#define y2step 0.20

// Detector Mode Settings: "average" or "min-max"
#define detect_mode "BB_AVERAGE"
#define scale "BB_LOG_SCALE"
#define reflvl 0

// Attenuation Mode
#define gain_level 0
#define rbw_val 10e3
#define vbw_val 10e3

/////////////////////////////////////////////////////////////////
//		   Signal Hound Functions		       //
/////////////////////////////////////////////////////////////////

std::vector<double> maxList;
std::vector<double> bufList;
std::vector<double> triggerList;

// Signal Hound parameters
int devID;
unsigned int traceSize;
double binSize, startFreq;
double *min, *max;
//float *buf, *triggers;
//float *samples = new float[Ns]; // 3.7376 mS of Data.

//struct rec ;

//sig_atomic_t volatile run = 'T' ;

// Iterators
int i, j, k;

// Define pointers to (fftw) complex arrays
// which will serve as input and output to the Fourier transforms
//fftw_complex *in, *out ; //, *in_win1 , *in_win2, *out_win1 , *out_win2;
//fftw_plan p; //, p1, p2;



static bool keepRunning = true;

void intHandler(int dummy=0) {
    keepRunning = false;
}
// Initialize, open and configure device.
void sh_calibration()
{

	bbOpenDevice( &devID );
		printf("#Signal Hound Device #: %i\n",devID);

	bbConfigureAcquisition(
		devID,
		BB_AVERAGE,
		BB_LOG_SCALE  // Log scaled results
		);


	bbConfigureCenterSpan(
		devID,
		fcenter,    // 915 MHz center
		fspan // 20 Mhz span is default for raw-pipe mode
		);

	bbConfigureLevel(
		devID,
		0, // not applicable if gain selected
		BB_AUTO_ATTEN   // atten dB, a set attenuation may produce a non-flat noise floor.
		);

	bbConfigureGain(
                devID,
                BB_AUTO_GAIN //BB_AUTO_GAIN //1 // 0// low gain
                );

	bbConfigureSweepCoupling(
		devID,
		rbw_val, // 10 kHz
		vbw_val, // 1 kHz
		0.10,    // 1 second
		BB_NATIVE_RBW, // Use native rbw
		BB_NO_SPUR_REJECT  // No software spur rejection
		);

	bbConfigureWindow(
		devID,
		BB_HAMMING // Hamming windowing functionb
		);

	bbConfigureProcUnits(
		devID,
		BB_POWER  //
		);

}

//I broke up these calls b/c when taking samples it is not necessary to recalibrate, only reinitiate

void sh_init()
{

	bbInitiate(
		devID,
		BB_SWEEPING,
		0
		);

	bbQueryTraceInfo(
		devID,
		&traceSize, // Get trace size, our case power
		&binSize,   // Get freq per returned sample, difference in frequency between values
		&startFreq  // Get accurate start frequency
		);
	min = new double[traceSize];
	max = new double[traceSize];

// To determine the frequency at any point, use the following function
// Frequency of n'th sample point in return sweep=startfreq+n*binsize



	bbFetchTrace(
		devID,
		traceSize,
		min,
		max
		);

}

//compute frequency table
//freq = np.linspace(fcenter-(fspan/2),fcenter+(fspan/2),len(spec['max']))
//peak_power = np.max(spec['max'])
//peak_freq = freq[list(spec['max']).index(float(peak_power))]

/**

void sh_get_samples()
{

	for ( i = 0; i < 10; i++ )
	{
	sh_init();
	bbFetchTrace(
	devID,
	traceSize,
	min,
	max);
		for (j=1; j < 10; j++)
		{
			if(max[i] < max[j])
			{
				max[0]=max[j];
				maxList.push_back(max[i]);
			}
		}20.00
	//Delay(1000);		//time delay of 1000ms, 1 sec. for now takes data for 10 seconds
	for( std::vector<double>::const_iterator i = maxList.begin(); i != maxList.end(); ++i)
    		std::cout << *i << ",  ";
	};


	while( streamingData = TRUE ) {
		bbFetchRaw(
		devID,
		buf,     // spectrum
		triggers // triggers
		);

	// Extract just the trigger positions into a vector
	int i = 0;
	while(buf[i]) {
		bufList.push_back(buf[i]);
		i++;
	}

	//doSomethingWithData( buf, triggerList ); // Save/process/display

}


**/

//the first for loop fetches a trace each second for 10 sec
//the second for loop looks at the max array(peak power) and checks each element to see which is
//larger. It starts with 0,1 and stores the larger value in max[0], then checks the new max[0]
//against max[2] and so forth until the largest element is stored in max[0]


////////////////////////////////////////////////////////////////////////

/**

void s_save()
{
	FILE *fp;

	fp=fopen("/home/SHdata1","w");
	fwrite('%f %f %f \n',traceSize,min,max);
	fclose(fp);
}

**/

void sh_terminate()
{
	printf("#Disconnecting Instrument ...\n");
	bbCloseDevice(devID);
	//printf("Saving remaining data ...\n");

}







/////////////////////////////////////////////////////////////////////////
//	interupt handler
/////////////////////////////////////////////////////////////////////////

/**

class GracefulInterruptHandler(object):

    def __init__(self, sig=signal.SIGINT):
        self.sig = sig

    def __enter__(self):

        self.interrupted = False
        self.released = False

        self.original_handler = signal.getsignal(self.sig)

        def handler(signum, frame):
            self.release()
            self.interrupted = True

        signal.signal(self.sig, handler)

        return self

    def __exit__(self, type, value, tb):
        self.release()

    def release(self):

        if self.released:
            return False

        signal.signal(self.sig, self.original_handler)

        self.released = True


**/

/////////////////////////////////////////////////////////////////
//			Main Method			       //
/////////////////////////////////////////////////////////////////



int main()
{
	min = NULL;
	max = NULL;
	signal(SIGINT, intHandler);
	sh_calibration();
	sh_init();
	timestamp = time(NULL);
   //timestamp = gmtime(&timestamp);
	printf("%ld",timestamp);
	// print the frequencies to the top of a text file here
	for (i = 0; i<traceSize; i++)
	{
		printf(",%6.3f ",(i*binSize+startFreq)/1e6);
	}
	printf("\n");
	//start inifinit loop

	while (keepRunning){
		bbQueryTraceInfo(
			devID,
			&traceSize, // Get trace size, our case power
			&binSize,   // Get freq per returned sample, difference in frequency between values
			&startFreq  // Get accurate start frequency
		);

		//min = new double[traceSize];
		//max = new double[traceSize];

		bbFetchTrace(
			devID,
			traceSize,
			min,
			max
			);
		//get the spectrum
		timestamp = time(NULL); //get the time in secomends since 1970

		//print the time and the spectrum
		printf("%ld",timestamp);
		for (i = 0; i<traceSize; i++)
		{
			printf(",%6.3f", min[i]);
		}
		printf("\n");
		//printf("#binsize = %6.2f, startFreq = %6.3f  bandwidth=%6.2f\n",binSize/1e3,startFreq/1e6,binSize*traceSize/1e6);
		//printf("%i %f %f \n",traceSize,*min,*max);


		/**
		//Find the max
		maxmax=-1000;
		maxfreq = 0;
		for (i = 0; i<traceSize; i++)
		{
			if (max[i]>maxmax)
			{
				maxmax = max[i];
				maxfreq = i*binSize+startFreq;
			}
		}
		printf("max = %6.3f, freq = %6.3f \n",maxmax,maxfreq);
		**/
		sleep(2);
	} //end of the while
	sh_terminate();
	if (min != NULL) delete min;
	if (max != NULL) delete max;

}


//bbFetchRawSweep(devID,*samples); //spectrum is an array with an entry for each channels. 	   This needs to be defined at the top based on your setup. **I believe spectrum will be the 	  samples array

/** Jay/Michael

Don't do the below stuff something in the FFTW usage is messed up. Instead lets use the bbFetchRawSweep function see above.

        in[0][0]=0;//this is causing the program to exit (wihtout any error) Our current compile command is:  g++ SHtest1.c -o SHtest1 -lbbapi -lfftw3 -lm && sudo ./SHtest1
	printf("Running our test_func...\n");
	test_func();
        printf("getting samples...\n");
	sh_get_samples();
	//printf("in[0][0]: %f\n", in[0][0]);
	**/


//Both sweep and raw sweep mode takes a stream of data at 20 Mhz bandwidth
//the difference is that sweep takes continuous data, while raw sweep takes steps with n samples at
//each step of the 20Mhz stream. Raw data mode does the same, only returns 32-bit floats rather
//than the signed shorts of what raw sweep returns




/*

dont need this code




void sig_handler(int signum)
{
  if (signum == SIGINT)
    run = 'F' ;
}

void sh_get_samples()
{
    for ( i = 0; i < Ns; i++ )
    {
          samples[i] = 0 ;
    }
    //printf("fetchingRaw");
    bbFetchRaw(
           devID,
           samples, // spectrum
           NULL // triggers
           );
    for ( i = 0; i < Ns; i++ )
    {
        in[i][0]  =  samples[i];
    }

}

void do_fft(fftw_complex *in,fftw_complex *out)
{
    // Execute the FFTW plan
	fftw_execute(p);
	int k = 0 ;
	for ( i = 1; i < ( Nfft /2 +1)  ; i++ )
	{
		fft_output[k] =  out[i][0] * out[i][0] ; // remove DC component
		k = k + 1 ;
	}
}







	// Setup the 1D Complex FFTW (FFTW ver 3.3 )
    	// Allocate memory using the fftw specific malloc
    	in  = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * Ns);
    	out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * Nfft);
    	p = fftw_plan_dft_1d(Nfft, in, out, FFTW_FORWARD, FFTW_ESTIMATE);

    	in[i][1] = 0 ; // 0 Imaginary Part

        // Number of Averaged spectra
	//int navg =tau/3.7376 ;
	int navg = floor((tau/3.7376)+0.5);
	printf("Number of Integrated Spectra = %d \n", navg);


    	for ( i = 0; i < Ns; i++ )
   	{
	times [i] =  i * 1E3  / Fs   ; // unit : Nano second
    	}
	// Build the Frequency Vector
	for ( i = 0; i < (Nfft/2)  ; i++ )
	{
	f[i] = (1425 - 20) + ( i * ( ( Fs  * 1E6  )  /( Nfft)) ) / 1000000  ;// unit : MHz
	//printf("%f \n",f[i]) ;
	}

	k= 0;
	for ( i = 717; i < 717 + n_zoom; i++ )
	{
       	f_zoom[k] =f[i];
       	//printf("%f \n",f_zoom[k]) ;
        k=k+1 ;
        }


	sh_calibration();

	signal(SIGINT, &sig_handler);
	while( run = 'T')
	{
	    for (j = 0 ; j < navg+1 ; j++)
	    {
            sh_get_samples() ;
	    //printf("%f %f \n",f[i],in[i][0]);
	    do_fft(in,out) ;
	    for (i = 0 ; i < Nfft/2   ; i++)
            {
                avg[i] = avg[i] + (fft_output[i] )/ 2  ;
            }

	if (run == 'F' )
	    {
	    break;
	    }
        }
        if (run == 'F' )
        {
	    break;
        }

    	k = 0 ;
    	for ( int z = 717; z < 717 + n_zoom; z++ )
    	{
        avg_zoom[k]=avg[z] ;
	//printf("%f %f \n",f_zoom[k],avg_zoom[k]);
	//printf("%f %f \n",f[i],samples[i]);
        k=k+1 ;
   	}

	//printf("%f %f \n",f[i],samples[i]) ;
	printf (" Disconnecting Instrument ...\n");
	sh_terminate();
	printf (" Saving Data ...\n");
    	s_save();
	printf (" Cleaning up ...\n");
    	fftw_destroy_plan(p);
    	fftw_free(in); fftw_free(out);




*/
