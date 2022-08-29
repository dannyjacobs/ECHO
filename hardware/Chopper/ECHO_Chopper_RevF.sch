EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L ECHO_PL_RevE-rescue:SN74LS08N-SN74LS08N-ECHO_PL_RevC-rescue AND_GATE1
U 1 1 600A5561
P 8300 3800
F 0 "AND_GATE1" H 8800 4065 50  0000 C CNN
F 1 "SN74LS08N" H 8800 3974 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 9150 3900 50  0001 L CNN
F 3 "http://componentsearchengine.com/Datasheets/3/SN74LS08N.pdf" H 9150 3800 50  0001 L CNN
F 4 "Quad 2i/p AND gate,SN74LS08N DIP14 25pcs" H 9150 3700 50  0001 L CNN "Description"
F 5 "5.08" H 9150 3600 50  0001 L CNN "Height"
F 6 "Texas Instruments" H 9150 3500 50  0001 L CNN "Manufacturer_Name"
F 7 "SN74LS08N" H 9150 3400 50  0001 L CNN "Manufacturer_Part_Number"
F 8 "595-SN74LS08N" H 9150 3300 50  0001 L CNN "Mouser Part Number"
F 9 "https://www.mouser.co.uk/ProductDetail/Texas-Instruments/SN74LS08N/?qs=spW5eSrOWB4y5MjcKVGhlA%3D%3D" H 9150 3200 50  0001 L CNN "Mouser Price/Stock"
F 10 "SN74LS08N" H 9150 3100 50  0001 L CNN "Arrow Part Number"
F 11 "https://www.arrow.com/en/products/sn74ls08n/texas-instruments" H 9150 3000 50  0001 L CNN "Arrow Price/Stock"
	1    8300 3800
	-1   0    0    1   
$EndComp
$Comp
L Timer:TLC555xP TIMER1
U 1 1 600A7EC2
P 8000 2300
F 0 "TIMER1" H 8000 1719 50  0000 C CNN
F 1 "TLC555xP" H 8000 1810 50  0000 C CNN
F 2 "Package_DIP:DIP-8_W7.62mm" H 8650 1900 50  0001 C CNN
F 3 "http://www.ti.com/lit/ds/symlink/tlc555.pdf" H 8850 1900 50  0001 C CNN
	1    8000 2300
	-1   0    0    1   
$EndComp
$Comp
L ECHO_PL_RevE-rescue:SN74LS04N-SN74LS04N-ECHO_PL_RevC-rescue INVERTER1
U 1 1 600AA056
P 4300 3200
F 0 "INVERTER1" H 4800 2335 50  0000 C CNN
F 1 "SN74LS04N" H 4800 2426 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 5150 3300 50  0001 L CNN
F 3 "http://www.ti.com/lit/gpn/sn74ls04" H 5150 3200 50  0001 L CNN
F 4 "Hex inverter,SN74LS04N DIP14 25pcs" H 5150 3100 50  0001 L CNN "Description"
F 5 "5.08" H 5150 3000 50  0001 L CNN "Height"
F 6 "Texas Instruments" H 5150 2900 50  0001 L CNN "Manufacturer_Name"
F 7 "SN74LS04N" H 5150 2800 50  0001 L CNN "Manufacturer_Part_Number"
F 8 "595-SN74LS04N" H 5150 2700 50  0001 L CNN "Mouser Part Number"
F 9 "https://www.mouser.co.uk/ProductDetail/Texas-Instruments/SN74LS04N/?qs=spW5eSrOWB4DgGWIHPxzvg%3D%3D" H 5150 2600 50  0001 L CNN "Mouser Price/Stock"
F 10 "SN74LS04N" H 5150 2500 50  0001 L CNN "Arrow Part Number"
F 11 "https://www.arrow.com/en/products/sn74ls04n/texas-instruments" H 5150 2400 50  0001 L CNN "Arrow Price/Stock"
	1    4300 3200
	-1   0    0    1   
$EndComp
$Comp
L Device:CP1 C1
U 1 1 600F40BE
P 1200 4700
F 0 "C1" H 1315 4738 39  0000 L CNN
F 1 "0.1uF" H 1315 4663 39  0000 L CNN
F 2 "Capacitor_THT:CP_Radial_D4.0mm_P2.00mm" H 1200 4700 50  0001 C CNN
F 3 "~" H 1200 4700 50  0001 C CNN
	1    1200 4700
	1    0    0    -1  
$EndComp
Text Label 1200 4000 0    50   ~ 0
PWM
Text Label 1200 4100 0    50   ~ 0
GND
Text Label 1200 4200 0    50   ~ 0
12V
$Comp
L Regulator_Linear:LM317_3PinPackage 5V_LINREG1
U 1 1 6009F6FD
P 1700 4550
F 0 "5V_LINREG1" H 1700 4792 50  0000 C CNN
F 1 "LM317_3PinPackage" H 1700 4701 50  0000 C CNN
F 2 "Package_TO_SOT_THT:TO-220-3_Vertical" H 1700 4800 50  0001 C CIN
F 3 "http://www.ti.com/lit/ds/symlink/lm317.pdf" H 1700 4550 50  0001 C CNN
	1    1700 4550
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R2
U 1 1 600F7605
P 1700 5000
F 0 "R2" H 1632 4962 39  0000 R CNN
F 1 "300" H 1632 5037 39  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 1740 4990 50  0001 C CNN
F 3 "~" H 1700 5000 50  0001 C CNN
	1    1700 5000
	-1   0    0    1   
$EndComp
$Comp
L Device:R_US R1
U 1 1 600F5F56
P 2000 4700
F 0 "R1" H 2068 4738 39  0000 L CNN
F 1 "100" H 2068 4663 39  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 2040 4690 50  0001 C CNN
F 3 "~" H 2000 4700 50  0001 C CNN
	1    2000 4700
	1    0    0    -1  
$EndComp
Connection ~ 1700 4850
Wire Wire Line
	1200 4850 1200 5150
Wire Wire Line
	1700 5150 2500 5150
Wire Wire Line
	2500 5150 2500 4850
Connection ~ 1700 5150
Text Label 2500 4550 0    50   ~ 0
5V
Wire Wire Line
	5800 4900 5750 4900
$Comp
L power:GND #PWR0104
U 1 1 601C380B
P 5750 4900
F 0 "#PWR0104" H 5750 4650 39  0001 C CNN
F 1 "GND" H 5755 4735 39  0000 C CNN
F 2 "" H 5750 4900 50  0001 C CNN
F 3 "" H 5750 4900 50  0001 C CNN
	1    5750 4900
	1    0    0    -1  
$EndComp
Connection ~ 5750 4900
Wire Wire Line
	5750 4900 5700 4900
NoConn ~ 5800 4300
NoConn ~ 5900 4300
Wire Wire Line
	5700 6050 5750 6050
$Comp
L Device:R_US R11
U 1 1 601CCD75
P 5850 5350
F 0 "R11" V 5669 5350 39  0000 C CNN
F 1 "20k" V 5744 5350 39  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 5890 5340 50  0001 C CNN
F 3 "~" H 5850 5350 50  0001 C CNN
	1    5850 5350
	0    1    1    0   
$EndComp
Wire Wire Line
	6100 4200 6100 4600
Wire Wire Line
	6000 4200 6100 4200
Wire Wire Line
	5700 4300 5700 4200
$Comp
L Device:R_US R10
U 1 1 601C65DB
P 5850 4200
F 0 "R10" V 5669 4200 39  0000 C CNN
F 1 "20k" V 5744 4200 39  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 5890 4190 50  0001 C CNN
F 3 "~" H 5850 4200 50  0001 C CNN
	1    5850 4200
	0    1    1    0   
$EndComp
Wire Wire Line
	5700 5450 5700 5350
Wire Wire Line
	6000 5350 6100 5350
Wire Wire Line
	6100 5350 6100 5750
$Comp
L power:GND #PWR0105
U 1 1 601D849D
P 5750 6050
F 0 "#PWR0105" H 5750 5800 39  0001 C CNN
F 1 "GND" H 5755 5885 39  0000 C CNN
F 2 "" H 5750 6050 50  0001 C CNN
F 3 "" H 5750 6050 50  0001 C CNN
	1    5750 6050
	1    0    0    -1  
$EndComp
Connection ~ 5750 6050
Wire Wire Line
	5750 6050 5800 6050
NoConn ~ 5800 5450
NoConn ~ 5900 5450
Connection ~ 5700 4200
Connection ~ 5700 5350
$Comp
L Device:LED COMP1_LED1
U 1 1 601DD499
P 6250 4900
F 0 "COMP1_LED1" H 6243 4803 50  0000 C CNN
F 1 "LED" H 6243 5026 50  0001 C CNN
F 2 "LED_THT:LED_D5.0mm" H 6250 4900 50  0001 C CNN
F 3 "~" H 6250 4900 50  0001 C CNN
	1    6250 4900
	-1   0    0    -1  
$EndComp
$Comp
L power:GND #PWR0106
U 1 1 601E43C1
P 6400 4900
F 0 "#PWR0106" H 6400 4650 39  0001 C CNN
F 1 "GND" V 6405 4772 39  0000 R CNN
F 2 "" H 6400 4900 50  0001 C CNN
F 3 "" H 6400 4900 50  0001 C CNN
	1    6400 4900
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR0107
U 1 1 601E68C6
P 6400 6050
F 0 "#PWR0107" H 6400 5800 39  0001 C CNN
F 1 "GND" V 6405 5922 39  0000 R CNN
F 2 "" H 6400 6050 50  0001 C CNN
F 3 "" H 6400 6050 50  0001 C CNN
	1    6400 6050
	0    -1   -1   0   
$EndComp
Connection ~ 6100 4600
Connection ~ 6100 5750
$Comp
L power:GND #PWR0108
U 1 1 60226779
P 7000 3200
F 0 "#PWR0108" H 7000 2950 39  0001 C CNN
F 1 "GND" V 7005 3072 39  0000 R CNN
F 2 "" H 7000 3200 50  0001 C CNN
F 3 "" H 7000 3200 50  0001 C CNN
	1    7000 3200
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR0109
U 1 1 602276E8
P 8300 3200
F 0 "#PWR0109" H 8300 2950 39  0001 C CNN
F 1 "GND" V 8305 3072 39  0000 R CNN
F 2 "" H 8300 3200 50  0001 C CNN
F 3 "" H 8300 3200 50  0001 C CNN
	1    8300 3200
	0    -1   -1   0   
$EndComp
Wire Wire Line
	7000 3600 7100 3600
Wire Wire Line
	7100 3600 7100 3050
$Comp
L Device:R_US R12
U 1 1 6023445F
P 7650 2700
F 0 "R12" V 7469 2700 39  0000 C CNN
F 1 "15k" V 7544 2700 39  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 7690 2690 50  0001 C CNN
F 3 "~" H 7650 2700 50  0001 C CNN
	1    7650 2700
	0    -1   -1   0   
$EndComp
Wire Wire Line
	8000 2700 7800 2700
NoConn ~ 8500 2300
$Comp
L Device:R_US R13
U 1 1 6023C9A9
P 7300 2300
F 0 "R13" V 7481 2300 39  0000 C CNN
F 1 "200k" V 7406 2300 39  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 7340 2290 50  0001 C CNN
F 3 "~" H 7300 2300 50  0001 C CNN
	1    7300 2300
	0    -1   -1   0   
$EndComp
$Comp
L Device:R_US R14
U 1 1 60242F97
P 7150 2150
F 0 "R14" H 7083 2112 39  0000 R CNN
F 1 "100k" H 7083 2187 39  0000 R CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 7190 2140 50  0001 C CNN
F 3 "~" H 7150 2150 50  0001 C CNN
	1    7150 2150
	1    0    0    1   
$EndComp
Wire Wire Line
	7500 2000 7500 2100
$Comp
L Device:CP1 C6
U 1 1 60248CEA
P 8650 2350
F 0 "C6" H 8535 2312 39  0000 R CNN
F 1 "1uF" H 8535 2387 39  0000 R CNN
F 2 "Capacitor_THT:CP_Radial_D4.0mm_P2.00mm" H 8650 2350 50  0001 C CNN
F 3 "~" H 8650 2350 50  0001 C CNN
	1    8650 2350
	-1   0    0    1   
$EndComp
$Comp
L power:GND #PWR0110
U 1 1 60256BD4
P 8000 1900
F 0 "#PWR0110" H 8000 1650 39  0001 C CNN
F 1 "GND" V 8005 1773 39  0000 R CNN
F 2 "" H 8000 1900 50  0001 C CNN
F 3 "" H 8000 1900 50  0001 C CNN
	1    8000 1900
	0    1    1    0   
$EndComp
Connection ~ 8000 1900
Wire Wire Line
	8500 2100 8550 2100
$Comp
L power:GND #PWR0111
U 1 1 60298F93
P 4300 2600
F 0 "#PWR0111" H 4300 2350 39  0001 C CNN
F 1 "GND" H 4305 2435 39  0000 C CNN
F 2 "" H 4300 2600 50  0001 C CNN
F 3 "" H 4300 2600 50  0001 C CNN
	1    4300 2600
	-1   0    0    1   
$EndComp
$Comp
L Connector:Conn_Coaxial RF_IN1
U 1 1 6029D1A8
P 3500 1250
F 0 "RF_IN1" H 3600 1225 50  0000 L CNN
F 1 "Valon Input" H 3600 1134 50  0000 L CNN
F 2 "Connector_Coaxial:SMA_Amphenol_132203-12_Horizontal" H 3500 1250 50  0001 C CNN
F 3 " ~" H 3500 1250 50  0001 C CNN
	1    3500 1250
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0112
U 1 1 602A35D4
P 5000 1850
F 0 "#PWR0112" H 5000 1600 50  0001 C CNN
F 1 "GND" V 5005 1744 39  0000 R CNN
F 2 "" H 5000 1850 50  0001 C CNN
F 3 "" H 5000 1850 50  0001 C CNN
	1    5000 1850
	0    -1   -1   0   
$EndComp
$Comp
L Connector:Conn_Coaxial RF_OUT1
U 1 1 602A75FD
P 5250 1250
F 0 "RF_OUT1" H 5350 1225 50  0000 L CNN
F 1 "BicoLOG Output" H 5350 1134 50  0000 L CNN
F 2 "Connector_Coaxial:SMA_Amphenol_132203-12_Horizontal" H 5250 1250 50  0001 C CNN
F 3 " ~" H 5250 1250 50  0001 C CNN
	1    5250 1250
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_Coaxial RF_TERM1
U 1 1 602AD54F
P 6500 1250
F 0 "RF_TERM1" H 6600 1225 50  0000 L CNN
F 1 "Terminated Output" H 6600 1134 50  0000 L CNN
F 2 "Connector_Coaxial:SMA_Amphenol_132203-12_Horizontal" H 6500 1250 50  0001 C CNN
F 3 " ~" H 6500 1250 50  0001 C CNN
	1    6500 1250
	1    0    0    -1  
$EndComp
$Comp
L Device:LED XOR_LED1
U 1 1 602BF5EF
P 6950 2750
F 0 "XOR_LED1" H 6943 2875 50  0000 C CNN
F 1 "LED" H 6943 2876 50  0001 C CNN
F 2 "LED_THT:LED_D5.0mm" H 6950 2750 50  0001 C CNN
F 3 "~" H 6950 2750 50  0001 C CNN
	1    6950 2750
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0113
U 1 1 602CC196
P 6800 2750
F 0 "#PWR0113" H 6800 2500 39  0001 C CNN
F 1 "GND" V 6805 2623 39  0000 R CNN
F 2 "" H 6800 2750 50  0001 C CNN
F 3 "" H 6800 2750 50  0001 C CNN
	1    6800 2750
	0    1    1    0   
$EndComp
$Comp
L Device:LED RF_OUT_LED1
U 1 1 602D025D
P 5600 2750
F 0 "RF_OUT_LED1" V 5593 2632 50  0000 R CNN
F 1 "LED" H 5593 2876 50  0001 C CNN
F 2 "LED_THT:LED_D5.0mm" H 5600 2750 50  0001 C CNN
F 3 "~" H 5600 2750 50  0001 C CNN
	1    5600 2750
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR0114
U 1 1 602D20CF
P 5600 2600
F 0 "#PWR0114" H 5600 2350 39  0001 C CNN
F 1 "GND" H 5605 2435 39  0000 C CNN
F 2 "" H 5600 2600 50  0001 C CNN
F 3 "" H 5600 2600 50  0001 C CNN
	1    5600 2600
	-1   0    0    1   
$EndComp
$Comp
L Device:LED AND_LED1
U 1 1 602D3078
P 8850 3450
F 0 "AND_LED1" V 8843 3530 50  0000 L CNN
F 1 "LED" H 8843 3576 50  0001 C CNN
F 2 "LED_THT:LED_D5.0mm" H 8850 3450 50  0001 C CNN
F 3 "~" H 8850 3450 50  0001 C CNN
	1    8850 3450
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR0115
U 1 1 602D4207
P 8850 3300
F 0 "#PWR0115" H 8850 3050 39  0001 C CNN
F 1 "GND" H 8855 3135 39  0000 C CNN
F 2 "" H 8850 3300 50  0001 C CNN
F 3 "" H 8850 3300 50  0001 C CNN
	1    8850 3300
	-1   0    0    1   
$EndComp
Text Notes 7400 7500 0    50   ~ 0
ECHO_PL_RevE\n
$Comp
L Comparator:LM311 COMPARATOR1
U 1 1 600A06E9
P 5800 4600
F 0 "COMPARATOR1" H 6144 4646 50  0000 L CNN
F 1 "LM311" H 6144 4555 50  0000 L CNN
F 2 "Package_DIP:DIP-8_W7.62mm" H 5800 4600 50  0001 C CNN
F 3 "https://www.st.com/resource/en/datasheet/lm311.pdf" H 5800 4600 50  0001 C CNN
	1    5800 4600
	1    0    0    -1  
$EndComp
$Comp
L Comparator:LM311 COMPARATOR2
U 1 1 600A1B2A
P 5800 5750
F 0 "COMPARATOR2" H 6144 5796 50  0000 L CNN
F 1 "LM311" H 6144 5705 50  0000 L CNN
F 2 "Package_DIP:DIP-8_W7.62mm" H 5800 5750 50  0001 C CNN
F 3 "https://www.st.com/resource/en/datasheet/lm311.pdf" H 5800 5750 50  0001 C CNN
	1    5800 5750
	1    0    0    -1  
$EndComp
Wire Wire Line
	1200 4200 1200 4550
$Comp
L power:GND #PWR0116
U 1 1 6031327F
P 1350 4100
F 0 "#PWR0116" H 1350 3850 39  0001 C CNN
F 1 "GND" V 1355 3972 39  0000 R CNN
F 2 "" H 1350 4100 50  0001 C CNN
F 3 "" H 1350 4100 50  0001 C CNN
	1    1350 4100
	0    -1   -1   0   
$EndComp
Text Notes 8150 7650 0    50   ~ 0
15 Feb 2021
Text Notes 10600 7650 0    50   ~ 0
D\n
$Comp
L ECHO_PL_RevE-rescue:HMC545AE-HMC545AE-ECHO_PL_RevC-rescue RF_SWITCH1
U 1 1 600ACC7A
P 5000 1950
F 0 "RF_SWITCH1" H 5500 1485 50  0000 C CNN
F 1 "HMC545AE" H 5500 1576 50  0000 C CNN
F 2 "Package_TO_SOT_SMD:SOT-23-6" H 5850 2050 50  0001 L CNN
F 3 "https://componentsearchengine.com/Datasheets/1/HMC545AE.pdf" H 5850 1950 50  0001 L CNN
F 4 "RF Switch ICs GaAs MMIC SPDT Switch, DC - 3 GHz" H 5850 1850 50  0001 L CNN "Description"
F 5 "1.45" H 5850 1750 50  0001 L CNN "Height"
F 6 "Analog Devices" H 5850 1650 50  0001 L CNN "Manufacturer_Name"
F 7 "HMC545AE" H 5850 1550 50  0001 L CNN "Manufacturer_Part_Number"
F 8 "584-HMC545AE" H 5850 1450 50  0001 L CNN "Mouser Part Number"
F 9 "https://www.mouser.co.uk/ProductDetail/Analog-Devices/HMC545AE/?qs=ILgNtqsyH20XtLk0bWE9Zg%3D%3D" H 5850 1350 50  0001 L CNN "Mouser Price/Stock"
F 10 "" H 5850 1250 50  0001 L CNN "Arrow Part Number"
F 11 "" H 5850 1150 50  0001 L CNN "Arrow Price/Stock"
	1    5000 1950
	-1   0    0    1   
$EndComp
Text Label 3000 5850 0    50   ~ 0
0.24V
Text Label 3450 5500 0    50   ~ 0
0.18V
$Comp
L power:GND #PWR0103
U 1 1 601B056C
P 4050 5750
F 0 "#PWR0103" H 4050 5500 39  0001 C CNN
F 1 "GND" V 4055 5622 39  0000 R CNN
F 2 "" H 4050 5750 50  0001 C CNN
F 3 "" H 4050 5750 50  0001 C CNN
	1    4050 5750
	0    -1   -1   0   
$EndComp
$Comp
L Device:R_US R4
U 1 1 6019F4AA
P 3000 5000
F 0 "R4" H 3068 5038 39  0000 L CNN
F 1 "47k" H 3068 4963 39  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 3040 4990 50  0001 C CNN
F 3 "~" H 3000 5000 50  0001 C CNN
	1    3000 5000
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R5
U 1 1 601A09D8
P 3000 5300
F 0 "R5" H 3068 5338 39  0000 L CNN
F 1 "22k" H 3068 5263 39  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 3040 5290 50  0001 C CNN
F 3 "~" H 3000 5300 50  0001 C CNN
	1    3000 5300
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R6
U 1 1 601A14A7
P 3000 5600
F 0 "R6" H 3068 5638 39  0000 L CNN
F 1 "5.6k" H 3068 5563 39  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 3040 5590 50  0001 C CNN
F 3 "~" H 3000 5600 50  0001 C CNN
	1    3000 5600
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R9
U 1 1 601A8407
P 3900 5750
F 0 "R9" V 4081 5750 39  0000 C CNN
F 1 "3.3k" V 4006 5750 39  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 3940 5740 50  0001 C CNN
F 3 "~" H 3900 5750 50  0001 C CNN
	1    3900 5750
	0    -1   -1   0   
$EndComp
$Comp
L Device:R_US R8
U 1 1 601A781F
P 3600 5750
F 0 "R8" V 3781 5750 39  0000 C CNN
F 1 "3.3k" V 3706 5750 39  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 3640 5740 50  0001 C CNN
F 3 "~" H 3600 5750 50  0001 C CNN
	1    3600 5750
	0    -1   -1   0   
$EndComp
$Comp
L Device:R_US R7
U 1 1 601A6AA1
P 3300 5750
F 0 "R7" V 3481 5750 39  0000 C CNN
F 1 "2.2k" V 3406 5750 39  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 3340 5740 50  0001 C CNN
F 3 "~" H 3300 5750 50  0001 C CNN
	1    3300 5750
	0    -1   -1   0   
$EndComp
$Comp
L Device:R_US R3
U 1 1 6019BF27
P 3000 4700
F 0 "R3" H 3068 4738 39  0000 L CNN
F 1 "100k" H 3068 4663 39  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 3040 4690 50  0001 C CNN
F 3 "~" H 3000 4700 50  0001 C CNN
	1    3000 4700
	1    0    0    -1  
$EndComp
$Comp
L Device:CP1 C2
U 1 1 600F9454
P 2500 4700
F 0 "C2" H 2615 4738 39  0000 L CNN
F 1 "1uF" H 2615 4663 39  0000 L CNN
F 2 "Capacitor_THT:CP_Radial_D4.0mm_P2.00mm" H 2500 4700 50  0001 C CNN
F 3 "~" H 2500 4700 50  0001 C CNN
	1    2500 4700
	1    0    0    -1  
$EndComp
Wire Wire Line
	1350 4100 1200 4100
Connection ~ 2700 3900
Wire Wire Line
	4750 3500 4750 3800
Wire Wire Line
	2700 3500 4750 3500
Wire Wire Line
	2700 3900 2700 3500
Connection ~ 2700 4100
Wire Wire Line
	2700 3900 2700 4100
Wire Wire Line
	3000 3900 2700 3900
Wire Wire Line
	2700 4200 2700 4100
Connection ~ 2700 4200
Wire Wire Line
	3000 4200 2700 4200
Wire Wire Line
	2700 4300 2700 4200
Wire Wire Line
	3000 4300 2700 4300
$Comp
L Device:CP1 C5
U 1 1 6012ADAD
P 2850 4100
F 0 "C5" V 2622 4100 39  0000 C CNN
F 1 "0.15uF" V 2697 4100 39  0000 C CNN
F 2 "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" H 2850 4100 50  0001 C CNN
F 3 "~" H 2850 4100 50  0001 C CNN
	1    2850 4100
	0    1    1    0   
$EndComp
Connection ~ 4750 3800
Connection ~ 4750 3900
Wire Wire Line
	4300 3800 4750 3800
Wire Wire Line
	4750 3900 4750 3800
Connection ~ 4750 4000
Wire Wire Line
	4750 3900 4750 4000
Wire Wire Line
	4300 4000 4750 4000
Wire Wire Line
	4750 4000 4750 4300
Wire Wire Line
	3000 3600 4400 3600
Wire Wire Line
	3000 3800 3000 3600
Wire Wire Line
	4400 3600 4400 3900
Wire Wire Line
	4400 3900 4450 3900
Connection ~ 4400 3900
Wire Wire Line
	4400 4300 4450 4300
Connection ~ 4400 4300
Wire Wire Line
	4400 4300 4400 3900
Wire Wire Line
	4300 3900 4400 3900
NoConn ~ 4300 4100
Wire Wire Line
	4300 4300 4400 4300
$Comp
L Device:CP1 C3
U 1 1 6011DEB5
P 4600 4300
F 0 "C3" V 4828 4300 39  0000 C CNN
F 1 "0.15uF" V 4753 4300 39  0000 C CNN
F 2 "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" H 4600 4300 50  0001 C CNN
F 3 "~" H 4600 4300 50  0001 C CNN
	1    4600 4300
	0    -1   -1   0   
$EndComp
$Comp
L power:GND #PWR0101
U 1 1 60122AB3
P 4750 3800
F 0 "#PWR0101" H 4750 3550 39  0001 C CNN
F 1 "GND" V 4755 3672 39  0000 R CNN
F 2 "" H 4750 3800 50  0001 C CNN
F 3 "" H 4750 3800 50  0001 C CNN
	1    4750 3800
	0    -1   -1   0   
$EndComp
$Comp
L Device:CP1 C4
U 1 1 60120E4F
P 4600 3900
F 0 "C4" V 4828 3900 39  0000 C CNN
F 1 "0.15uF" V 4753 3900 39  0000 C CNN
F 2 "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm" H 4600 3900 50  0001 C CNN
F 3 "~" H 4600 3900 50  0001 C CNN
	1    4600 3900
	0    -1   -1   0   
$EndComp
$Comp
L ECHO_PL_RevE-rescue:LTC2644CMS-L12#PBF-LTC2644CMS-L12#PBF-ECHO_PL_RevC-rescue PWM_to_V_DAC1
U 1 1 6009D7F4
P 4300 4300
F 0 "PWM_to_V_DAC1" H 4950 3535 50  0000 C CNN
F 1 "LTC2644CMS-L12#PBF" H 4950 3626 50  0000 C CNN
F 2 "Package_SO:MSOP-12-1EP_3x4mm_P0.65mm_EP1.65x2.85mm" H 5450 4400 50  0001 L CNN
F 3 "https://www.analog.com/media/en/technical-documentation/data-sheets/2644fa.pdf" H 5450 4300 50  0001 L CNN
F 4 "Digital to Analog Converters - DAC Dual 12-bit PWM to VOUT DACs with 10ppm/ C  Reference" H 5450 4200 50  0001 L CNN "Description"
F 5 "1.1" H 5450 4100 50  0001 L CNN "Height"
F 6 "Analog Devices" H 5450 4000 50  0001 L CNN "Manufacturer_Name"
F 7 "LTC2644CMS-L12#PBF" H 5450 3900 50  0001 L CNN "Manufacturer_Part_Number"
F 8 "584-C2644CMS-L12PBF" H 5450 3800 50  0001 L CNN "Mouser Part Number"
F 9 "https://www.mouser.co.uk/ProductDetail/Analog-Devices/LTC2644CMS-L12PBF?qs=hVkxg5c3xu80urzBoeNBsQ%3D%3D" H 5450 3700 50  0001 L CNN "Mouser Price/Stock"
F 10 "LTC2644CMS-L12#PBF" H 5450 3600 50  0001 L CNN "Arrow Part Number"
F 11 "https://www.arrow.com/en/products/ltc2644cms-l12pbf/analog-devices" H 5450 3500 50  0001 L CNN "Arrow Price/Stock"
	1    4300 4300
	-1   0    0    1   
$EndComp
Connection ~ 2000 4550
Wire Wire Line
	2000 4850 1700 4850
Wire Wire Line
	2000 4550 2500 4550
Wire Wire Line
	1200 5150 1700 5150
Wire Wire Line
	1200 4550 1400 4550
Connection ~ 1200 4550
$Comp
L power:GND #PWR0102
U 1 1 600FE7AC
P 1700 5150
F 0 "#PWR0102" H 1700 4900 50  0001 C CNN
F 1 "GND" H 1705 5000 39  0000 C CNN
F 2 "" H 1700 5150 50  0001 C CNN
F 3 "" H 1700 5150 50  0001 C CNN
	1    1700 5150
	1    0    0    -1  
$EndComp
Wire Wire Line
	2500 4550 3000 4550
Wire Wire Line
	4400 4550 4400 4300
Connection ~ 2500 4550
Wire Wire Line
	1200 4000 3000 4000
Connection ~ 3000 4550
Wire Wire Line
	3000 4550 4400 4550
Wire Wire Line
	3000 5750 3000 5850
Wire Wire Line
	3150 5750 3000 5750
Connection ~ 3000 5750
Wire Wire Line
	5450 4500 5450 5650
Wire Wire Line
	5450 5650 5500 5650
Connection ~ 5450 4500
Wire Wire Line
	5450 4500 5500 4500
Wire Wire Line
	3450 5750 3450 4950
Connection ~ 3450 5750
Wire Wire Line
	5000 4200 5700 4200
Wire Wire Line
	5000 5350 5700 5350
Wire Wire Line
	4400 4550 5000 4550
Connection ~ 4400 4550
Connection ~ 5000 4550
Wire Wire Line
	3450 4950 5350 4950
Wire Wire Line
	5350 4950 5350 4700
Wire Wire Line
	5350 4700 5500 4700
$Comp
L ECHO_PL_RevE-rescue:SN74LS86AN-SN74LS86AN-ECHO_PL_RevC-rescue XOR_GATE1
U 1 1 600A2AE5
P 7000 3800
F 0 "XOR_GATE1" H 7500 4065 50  0000 C CNN
F 1 "SN74LS86AN" H 7500 3974 50  0000 C CNN
F 2 "Package_DIP:DIP-14_W7.62mm" H 7850 3900 50  0001 L CNN
F 3 "http://componentsearchengine.com/Datasheets/1/SN74LS86AN.pdf" H 7850 3800 50  0001 L CNN
F 4 "QUADRUPLE 2-INPUT EXCLUSIVE-OR GATES" H 7850 3700 50  0001 L CNN "Description"
F 5 "5.08" H 7850 3600 50  0001 L CNN "Height"
F 6 "Texas Instruments" H 7850 3500 50  0001 L CNN "Manufacturer_Name"
F 7 "SN74LS86AN" H 7850 3400 50  0001 L CNN "Manufacturer_Part_Number"
F 8 "595-SN74LS86AN" H 7850 3300 50  0001 L CNN "Mouser Part Number"
F 9 "https://www.mouser.co.uk/ProductDetail/Texas-Instruments/SN74LS86AN/?qs=mTHRaKC2c7P%2FJtp1i2FCFw%3D%3D" H 7850 3200 50  0001 L CNN "Mouser Price/Stock"
F 10 "SN74LS86AN" H 7850 3100 50  0001 L CNN "Arrow Part Number"
F 11 "https://www.arrow.com/en/products/sn74ls86an/texas-instruments" H 7850 3000 50  0001 L CNN "Arrow Price/Stock"
	1    7000 3800
	-1   0    0    1   
$EndComp
Wire Wire Line
	6000 3950 6000 3800
Wire Wire Line
	7300 3950 7300 3800
Wire Wire Line
	7000 4600 7000 3800
Wire Wire Line
	6100 4600 7000 4600
Wire Wire Line
	7000 4600 8300 4600
Wire Wire Line
	8300 4600 8300 3800
Connection ~ 7000 4600
Wire Wire Line
	7050 5750 7050 3700
Wire Wire Line
	7050 3700 7000 3700
Wire Wire Line
	6100 5750 7050 5750
Wire Wire Line
	7050 5750 8350 5750
Wire Wire Line
	8350 5750 8350 3700
Wire Wire Line
	8350 3700 8300 3700
Connection ~ 7050 5750
Wire Wire Line
	5950 3050 5950 3300
Wire Wire Line
	5950 3300 6000 3300
Connection ~ 8650 2500
Wire Wire Line
	8650 2500 8500 2500
Wire Wire Line
	8650 2500 8900 2500
Wire Wire Line
	8650 2200 8650 1900
Wire Wire Line
	8650 1900 8000 1900
Wire Wire Line
	8900 2500 8900 1750
Wire Wire Line
	7500 2300 7450 2300
Wire Wire Line
	7450 2300 7450 2700
Connection ~ 7450 2300
Wire Wire Line
	7450 2700 7500 2700
Connection ~ 7150 2000
Wire Wire Line
	7150 2000 7500 2000
Wire Wire Line
	7150 2000 7150 1750
Wire Wire Line
	5000 3950 5000 4200
Connection ~ 5000 4200
Wire Wire Line
	5000 4200 5000 4550
Wire Wire Line
	5500 5850 3000 5850
Wire Wire Line
	5000 4550 5000 5350
Wire Wire Line
	4300 4200 4850 4200
Wire Wire Line
	4850 4200 4850 4500
Wire Wire Line
	4850 4500 5450 4500
Wire Wire Line
	7300 3950 6000 3950
Connection ~ 6000 3950
Wire Wire Line
	6000 3950 5000 3950
NoConn ~ 7000 3500
NoConn ~ 7000 3400
NoConn ~ 7000 3300
NoConn ~ 6000 3700
NoConn ~ 6000 3600
NoConn ~ 6000 3500
NoConn ~ 7300 3700
NoConn ~ 7300 3600
NoConn ~ 7300 3500
NoConn ~ 7300 3400
NoConn ~ 7300 3300
NoConn ~ 7300 3200
NoConn ~ 8300 3300
NoConn ~ 8300 3400
NoConn ~ 8300 3500
Wire Wire Line
	8900 1750 7150 1750
Wire Wire Line
	8550 2100 8550 2700
Wire Wire Line
	8550 2700 8000 2700
Connection ~ 8000 2700
Connection ~ 8550 2700
Wire Wire Line
	8300 3600 8550 3600
Wire Wire Line
	8550 2700 8550 3600
Wire Wire Line
	6000 3400 5900 3400
Wire Wire Line
	5900 3400 5900 2500
Wire Wire Line
	5900 2500 7500 2500
Wire Wire Line
	4000 1950 4000 2100
Wire Wire Line
	4000 2100 4500 2100
Wire Wire Line
	4300 3100 4400 3100
Wire Wire Line
	4400 2200 3900 2200
Wire Wire Line
	3900 2200 3900 1750
Wire Wire Line
	3900 1750 4000 1750
Wire Wire Line
	4300 3200 4500 3200
Wire Wire Line
	4400 2200 4400 3100
Wire Wire Line
	4500 2100 4500 3200
Connection ~ 4500 3200
NoConn ~ 4300 2700
NoConn ~ 4300 2800
NoConn ~ 4300 2900
NoConn ~ 4300 3000
NoConn ~ 3300 3100
NoConn ~ 3300 3000
NoConn ~ 3300 2900
NoConn ~ 3300 2800
NoConn ~ 3300 2700
NoConn ~ 3300 2600
Wire Wire Line
	5000 3950 5000 3350
Wire Wire Line
	5000 3350 3300 3350
Wire Wire Line
	3300 3350 3300 3200
Connection ~ 5000 3950
Wire Bus Line
	1000 1000 9000 1000
Wire Bus Line
	9000 1000 9000 6500
Wire Bus Line
	9000 6500 1000 6500
Wire Bus Line
	1000 6500 1000 1000
$Comp
L Device:R_US R17
U 1 1 608C7C36
P 8700 3600
F 0 "R17" V 8881 3600 39  0000 C CNN
F 1 "100" V 8806 3600 39  0000 C CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 8740 3590 50  0001 C CNN
F 3 "~" H 8700 3600 50  0001 C CNN
	1    8700 3600
	0    -1   -1   0   
$EndComp
$Comp
L Device:R_US R18
U 1 1 608CD088
P 7100 2900
F 0 "R18" H 7168 2938 39  0000 L CNN
F 1 "100" H 7168 2863 39  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 7140 2890 50  0001 C CNN
F 3 "~" H 7100 2900 50  0001 C CNN
	1    7100 2900
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R16
U 1 1 608CDFF1
P 6100 5900
F 0 "R16" H 6168 5938 39  0000 L CNN
F 1 "100" H 6168 5863 39  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 6140 5890 50  0001 C CNN
F 3 "~" H 6100 5900 50  0001 C CNN
	1    6100 5900
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R15
U 1 1 608CEF4E
P 6100 4750
F 0 "R15" H 6168 4788 39  0000 L CNN
F 1 "100" H 6168 4713 39  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 6140 4740 50  0001 C CNN
F 3 "~" H 6100 4750 50  0001 C CNN
	1    6100 4750
	1    0    0    -1  
$EndComp
$Comp
L Device:R_US R19
U 1 1 608D00F0
P 5600 3050
F 0 "R19" H 5668 3088 39  0000 L CNN
F 1 "100" H 5668 3013 39  0000 L CNN
F 2 "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal" V 5640 3040 50  0001 C CNN
F 3 "~" H 5600 3050 50  0001 C CNN
	1    5600 3050
	1    0    0    -1  
$EndComp
$Comp
L Device:LED COMP2_LED1
U 1 1 601DF2E3
P 6250 6050
F 0 "COMP2_LED1" H 6243 6142 50  0000 C CNN
F 1 "LED" H 6243 6176 50  0001 C CNN
F 2 "LED_THT:LED_D5.0mm" H 6250 6050 50  0001 C CNN
F 3 "~" H 6250 6050 50  0001 C CNN
	1    6250 6050
	-1   0    0    1   
$EndComp
Connection ~ 8550 3600
Wire Wire Line
	5950 3050 7100 3050
Connection ~ 7100 3050
Wire Wire Line
	4500 3200 5600 3200
Connection ~ 5600 3200
Wire Wire Line
	5600 3200 6000 3200
Wire Wire Line
	3300 1250 3300 1850
Wire Wire Line
	5050 1750 5000 1750
Wire Wire Line
	6300 1250 6300 1950
$Comp
L power:GND #PWR0117
U 1 1 602841B9
P 6500 1450
F 0 "#PWR0117" H 6500 1200 50  0001 C CNN
F 1 "GND" H 6505 1277 50  0000 C CNN
F 2 "" H 6500 1450 50  0001 C CNN
F 3 "" H 6500 1450 50  0001 C CNN
	1    6500 1450
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0119
U 1 1 602856C5
P 3500 1450
F 0 "#PWR0119" H 3500 1200 50  0001 C CNN
F 1 "GND" H 3505 1277 50  0000 C CNN
F 2 "" H 3500 1450 50  0001 C CNN
F 3 "" H 3500 1450 50  0001 C CNN
	1    3500 1450
	1    0    0    -1  
$EndComp
Wire Wire Line
	4000 1850 3600 1850
$Comp
L Device:CP1 C9
U 1 1 6026B975
P 6150 1950
F 0 "C9" V 5922 1950 39  0000 C CNN
F 1 "390pF" V 5997 1950 39  0000 C CNN
F 2 "Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder" H 6150 1950 50  0001 C CNN
F 3 "~" H 6150 1950 50  0001 C CNN
	1    6150 1950
	0    -1   1    0   
$EndComp
Wire Wire Line
	6000 1950 5000 1950
$Comp
L Device:CP1 C8
U 1 1 602819BD
P 5050 1600
F 0 "C8" H 5165 1638 39  0000 L CNN
F 1 "390pF" H 5165 1563 39  0000 L CNN
F 2 "Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder" H 5050 1600 50  0001 C CNN
F 3 "~" H 5050 1600 50  0001 C CNN
	1    5050 1600
	-1   0    0    1   
$EndComp
$Comp
L Device:CP1 C7
U 1 1 60261932
P 3450 1850
F 0 "C7" V 3583 1850 39  0000 C CNN
F 1 "390pF" V 3661 1850 39  0000 C CNN
F 2 "Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder" H 3450 1850 50  0001 C CNN
F 3 "~" H 3450 1850 50  0001 C CNN
	1    3450 1850
	0    -1   1    0   
$EndComp
Wire Wire Line
	5050 1450 5050 1250
$Comp
L power:GND #PWR0118
U 1 1 602FBF6F
P 5250 1450
F 0 "#PWR0118" H 5250 1200 50  0001 C CNN
F 1 "GND" H 5255 1277 50  0000 C CNN
F 2 "" H 5250 1450 50  0001 C CNN
F 3 "" H 5250 1450 50  0001 C CNN
	1    5250 1450
	1    0    0    -1  
$EndComp
$Comp
L Connector:Conn_01x03_Male 3PIN_CONNECTOR1
U 1 1 60300404
P 1400 4100
F 0 "3PIN_CONNECTOR1" H 1508 3819 50  0000 C CNN
F 1 "Conn_01x03_Male" H 1508 3898 50  0000 C CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Horizontal" H 1400 4100 50  0001 C CNN
F 3 "~" H 1400 4100 50  0001 C CNN
	1    1400 4100
	-1   0    0    1   
$EndComp
$EndSCHEMATC
