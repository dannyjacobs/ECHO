 #!/bin/bash


SESSION=ECHO
BAUDRATE=57600
FREQ=137.500
APM_PATH="/Applications/APM\ Planner\ 2.0.app/"
HOST="10.1.1.1"
ARGS=$@

START_DATE=$(date +"%m-%d-%y")
START_TIME=$(date +"%H-%M-%S")
GPS_FILE="gps_"$START_DATE"_"$START_TIME".txt"
SPEC_FILE="spec_"$START_DATE"_"$START_TIME".txt"
ACC_FILE="acc_"$START_DATE"_"$START_TIME".txt"

for i in ${ARGS}
do
   case $i in
      --ground)
      GROUND=1
      shift
      ;;
      --accum)
      ACCUM=1
      shift
      ;;
      --trans=*)
      TRANS="${i#*=}"
      shift
      ;;
      --dt=*)
      DT="${i#*=}"
      shift
      ;;
      --host=*)
      HOST="${i#*=}"
      shift
      ;;
      --lat0=*)
      LAT0="${i#*=}"
      shift
      ;;
      --lon0=*)
      LON0="${i#*=}"
      shift
      ;;
#      --realtime)
#      REALTIME=1
#      shift
#      ;;
      --freq=*)
      FREQ="${i#*=}"
      shift
      ;;
      --nsides=*)
      NSIDES="${i#*=}"
      shift
      ;;
      *) #unrecognized value
      ;;
      # Add more parameters here
   esac
done


# Create tmux window
tmux new-session -d -s $SESSION
tmux new-window -t $SESSION
tmux split-window -v

# Modify tmux window
tmux select-pane -t 0
tmux split-window -h
tmux select-pane -t 2
tmux split-window -h

if [ $GROUND ]; then
   # Check if 3DR telem radio plugged in
   if [ $(ls /dev/tty.usb*) ]; then
      RADIO_LOC=$(ls /dev/tty.usb*)
   else
      tmux kill-session -t $SESSION
      echo "No valid 3DR telemetry radio found"
      echo "Exiting..."
      exit
   fi

   ECHO_PATH="/Users/echo_loco/ECHO"
   TLOG_PATH="/Users/echo_loco/apmplanner2/tlogs/octocopter"
   TLOG=$(ls -t ${TLOG_PATH} | head -1)

   # Open APM Planner
   tmux select-pane -t 0
   tmux send-keys "open /Applications/APM\ Planner\ 2.0.app/" C-m
#  tmux send-keys "mavproxy.py --master=${RADIO_LOC} --baudrate=${BAUDRATE} --out=udp:127.0.0.1:14550" C-m
   tmux send-keys "mavproxy.py --master=${RADIO_LOC} --baudrate=${BAUDRATE} --out=tcp:127.0.0.1:5760" C-m


   # Get GPS data from drone once UDP comm up
   tmux select-pane -t 1
   tmux send-keys "sleep 5" C-m
#   if [ $TRANS ]; then
#      tmux send-keys "python ${ECHO_PATH}/scripts/ECHO_get_gps.py --gps_file=$GPS_FILE --trans=$TRANS" C-m
#   else
#      tmux send-keys "python ${ECHO_PATH}/scripts/ECHO_get_gps.py --gps_file=$GPS_FILE" C-m
#   fi
    if [ $TRANS ]; then
       tmux send-keys "python ${ECHO_PATH}/scripts/ECHO_get_gps.py --gps_file=${GPS_FILE} --tlog=\"${TLOG_PATH}/${TLOG}\" --trans=${TRANS}" C-m
    else
       tmux send-keys "python ${ECHO_PATH}/scripts/ECHO_get_gps.py --gps_file=${GPS_FILE} --tlog=\"${TLOG_PATH}/${TLOG}\"" C-m
    fi



   tmux select-pane -t 2
   tmux send-keys "sleep 10" C-m
   if [ $DT ]; then
      tmux send-keys "python ${ECHO_PATH}/scripts/ECHO_server.py --gps_file=${GPS_FILE} --dt=${DT} --host=${HOST}" C-m
   else
      tmux send-keys "python ${ECHO_PATH}/scripts/ECHO_server.py --gps_file=${GPS_FILE} --host=${HOST}" C-m
   fi

   tmux select-pane -t 3
   tmux send-keys "sleep 10" C-m
   tmux send-keys "tail -f ${GPS_FILE}" C-m

   tmux attach-session -t ${SESSION}


elif [ ${ACCUM} ]; then

   ECHO_PATH="/home/echo/ECHO"
   # Run get_sh_spectra script for radio spectrum from Signal Hound
   tmux select-pane -t 0
   tmux send-keys "You have 20s to enter the password" C-m
   tmux send-keys "sudo ${ECHO_PATH}/scripts/get_sh_spectra_137 > ${SPEC_FILE}" C-m

   # Assume realtime and make another script for non realtime???
   #   if [ $REALTIME ]; then
   # Run ECHO_accumulate.py with potential options
   tmux select-pane -t 1
   tmux send-keys "sleep 20" C-m
   if [ ${HOST} ]; then
      if [ ${LAT0} -a ${LON0} ]; then
         tmux send-keys "python ${ECHO_PATH}/scripts/ECHO_accumulate.py --realtime --gps_file=${GPS_FILE} --spec_file=${SPEC_FILE} --acc_file=${ACC_FILE} --freq=${FREQ} --host=${HOST} --lat0=${LAT0} --lon0=${LON0}" C-m
      else # No LAT0 or LON0, still HOST
         tmux send-keys "python ${ECHO_PATH}/scripts/ECHO_accumulate.py --realtime --gps_file=${GPS_FILE} --spec_file=${SPEC_FILE} --acc_file=${ACC_FILE} --freq=${FREQ} --host=${HOST}" C-m
      fi
   else # No HOST
      if [ ${LAT0} -a ${LON0} ]; then
         tmux send-keys "python ${ECHO_PATH}/scripts/ECHO_accumulate.py --realtime --gps_file=${GPS_FILE} --spec_file=${SPEC_FILE} --acc_file=${ACC_FILE} --freq=${FREQ} --lat0=${LAT0} --lon0=${LON0}" C-m
      else # No HOST, LAT0, or LON0
      tmux send-keys "python ${ECHO_PATH}/scripts/ECHO_accumulate.py --realtime --gps_file=${GPS_FILE} --spec_file=${SPEC_FILE} --acc_file=${ACC_FILE} --freq=${FREQ}" C-m
      fi
   fi

   # Monitor accumulated file
   tmux select-pane -t 2
   tmux send-keys "sleep 25" C-m
   tmux send-keys "tail -f ${ACC_FILE}" C-m

   # Run ECHO_plot.py with realtime + other options
   tmux select-pane -t 3
   tmux send-keys "sleep 30" C-m
   if [ ${NSIDES} ]; then
      if [ ${LAT0} -a ${LON0} ]; then
         tmux send-keys "python ${ECHO_PATH}/scripts/ECHO_plot.py --realtime --acc_file=${ACC_FILE} --freq=${FREQ} --lat0=${LAT0} --lon0=${LON0} --nsides=${NSIDES}" C-m
      else # No LAT0 or LON0, still NSIDES
         tmux send-keys "python ${ECHO_PATH}/scripts/ECHO_plot.py --realtime --acc_file=${ACC_FILE} --freq=${FREQ} --nsides=${NSIDES}" C-m
      fi
   else # No NSIDES
      if [ ${LAT0} -a ${LON0} ]; then
         tmux send-keys "python ${ECHO_PATH}/scripts/ECHO_plot.py --realtime --acc_file=${ACC_FILE} --freq=${FREQ} --lat0=${LAT0} --lon0=${LON0}" C-m
      else # No LAT0 or LON0, still NSIDES
         tmux send-keys "python ${ECHO_PATH}/scripts/ECHO_plot.py --realtime --acc_file=${ACC_FILE} --freq=${FREQ}" C-m
      fi
   fi

   tmux select-pane -t 0
   tmux attach-session -t ${SESSION}

#   fi # END IF REALTIME

else
   echo "Please specify --ground or --accum"
   exit
fi
