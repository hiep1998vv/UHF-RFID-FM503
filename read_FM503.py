import serial
import os
import sys
import time
import string
import datetime
import csv
####WARNING!!!! The RFID Module MUST be connected through the non power USB port####
#serial_port = '/dev/ttyUSB0' #this should be correct, but if not working use $ python -m serial.tools.miniterm
serial_port = '/dev/ttyAMA0'
ser = serial.Serial(port=serial_port,baudrate = 38400,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS,timeout=1)

Stall_Time = 60               #Time to consider that the tag has completely left the reader area
Last_Tag = "initialise value" #just need a value that isn't an RFID tag
Last_Time = time.time() - Stall_Time  #set the time value to effectively 0 (for use in loop later)

#start set_up_the_reader()
def set_up_the_reader():
	#set the power level and report back the value
	power_level = '02'			 #Reader power level from -2 ~ 25dB
	ser.write(b'\nN1,{power_level}\r')

	#set up the region - this is the frequency of operation - uncomment correct line
	ser.write(b'\nN5,01\r')                 #Region 01: US  902~928MHz
	#ser.write(b'\nN5,03\r')                 #Region 02: TW  922~928MHz
	#ser.write(b'\nN5,03\r')                  #Region 03: CN  920~925MHz
	#ser.write(b'\nN5,03\r')                 #Region 04: CN2 840~845MHz
	#ser.write(b'\nN5,03\r')                 #Region 05: EU  865~868MHz
	#ser.write(b'\nN5,03\r')                 #Region 06: JP  916~921MH
#end set_up_the_reader()

#start write_to_csv()
def write_to_csv(RFID_Tag,RFID_Time):
	data = [RFID_Tag[1:34], RFID_Time.strftime('%Y-%m-%d'), RFID_Time.strftime('%H:%M:%S.%f')]
	with open('test.csv', 'a+') as read_file:
		writer = csv.writer(read_file)
		read_file.seek(0)
		writer.writerow(data)
#end write_to_csv()

#start send_command()
def send_command():
	reader_command = '\nU\r'                 #uncomment if you want to only see EPC
	#reader_command = '\nR2,0,6\r'		 #uncomment to see TID copy/paste to www.gs1.org/services/tid-decoder '806' is NXP
	ser.write(reader_command.encode())
	time.sleep(0.1)
#end send_command()

#start read_buffer()
def read_buffer():
	RFID_Tag = ser.read(ser.inWaiting()).decode("utf-8").replace('U', '')    #read the buffer (ser.read) for specific byte length (inWaiting)
	RFID_Time = datetime.datetime.now()    #record the time the tag was read
	return RFID_Tag, RFID_Time
#end read_buffer()

#main()
set_up_the_reader()

while True:
	send_command()
	RFID = read_buffer()
	RFID_Tag = RFID[0]
	RFID_Time = RFID[1]
	time.sleep(0.1)
	

        
	if len(RFID_Tag) > 15:                               #this should be about 15 normally
		if RFID_Tag != Last_Tag:                     #compare last read to this read to see if it is the same
			print (RFID_Tag)                     #only display the tag id part of the value
			print (RFID_Time)                    #display the time the tag was read at (yes its delayed but close enough)
			write_to_csv(RFID_Tag,RFID_Time)     #
			Last_Tag = RFID_Tag                  #gives something to compare for next run through loop
			Last_Time = time.time()              #gives seconds since /whatever/ so can check if 60 seconds has passed for next part of loop
		elif time.time() - Last_Time > Stall_Time:   #this part of the loop checks if a /time/ has passed before recording the RFID again, this could be several minutes really
			print (RFID_Tag)                     #do the same stuff as first loop
			print (RFID_Time)                    #
			write_to_csv(RFID_Tag,RFID_Time)     #
			Last_Tag = RFID_Tag                  #
			Last_Time = time.time()		     #