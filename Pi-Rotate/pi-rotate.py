#!/usr/bin/env python
# coding: latin-1

# pi-rotate.py
# Gavin Jacobs VE7GSJ

# system library functions
import time
import threading
import socket
import sys, getopt
import os.path
import math
import logging
import datetime
import os
import subprocess
# project libraries
import axis


# helper functions
def isFloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


# listens on pseudo terminal and handles Easycomm II protocol
# test with: rotctl -m 202 -r /dev/pts/0

"""
EasyComm II implementation in hamlib/rigctl
Set Position
	Command: 	"AZ%.1f EL%.1f UP000 XXX DN000 XXX\n"
	Response:	none
Get Position
	Command:	"AZ EL \n"
	Response: 	"AZ%f EL%f\n"
Stop Rotor
	Command:	"SA SE \n"
	Response:	none
Reset
	Command:	"RESET\n"
	Response:	"RESET\n"
Park
	Command:	"PARK\n"
	Response:	"PARK\n"
Version
	Command:	"VE\n"
	Response:	"VEssssss\n"
"""
class SerialEmulator:
	def __init__(self,az,el):
		logging.debug("SerialEmulator - init")
		self.mfd, self.sfd = os.openpty()				# create pseudo terminal
		self.s_slave = str(os.ttyname(self.sfd))
		logging.info("SerialEmulator - Slave device: " + self.s_slave)
		# subprocess.run('putty -serial ' + self.s_slave, shell=True)
		self.az = az
		self.el = el
		loop = threading.Thread(target=self.loop, name='Emulator')		# prepare a new thread
		loop.daemon = True
		loop.start()                                    # and start it

	def loop(self):
		logging.debug("SerialEmulator - loop")
		# os.write(self.mfd, ("Serial - start \r\n").encode())  		# temp: announce
		while True:
			ba_rx = bytes()
			while True:
				b_rx = os.read(self.mfd, 1)								# read one character
				#print(b_rx)
				if ((b_rx == b'\n') or (b_rx == b'\r')): break			# newline or carriage return
				ba_rx += b_rx											# save each byte in buffer
			s_rx = ba_rx.decode().strip()
			logging.debug("SerialEmulator - Text received: " + s_rx)
			t_rx = s_rx.split(" ")										# split into tokens
			if(len(t_rx) == 1):
				if(t_rx[0] == 'VE'):														# "VE"
					os.write(self.mfd, (t_rx[0] + "Pi-Rotate_V0.1" + "\n").encode())		# "VExxxxxx\n"
				elif(t_rx[0] == 'RESET'):
					self.az.reset()
					self.el.reset()
					os.write(self.mfd, (t_rx[0] + "\n").encode())		# "RESET\n"
				elif (t_rx[0] == 'PARK'):
					self.az.park()
					self.el.park()
					os.write(self.mfd, (t_rx[0] + "\n").encode())		# "PARK\n"
			elif(len(t_rx) == 2):
				if(t_rx[0] == 'SA' and t_rx[1] == 'SE'):
					self.az.stop()
					self.el.stop()
					os.write(self.mfd, (t_rx[0] + " " + t_rx[1] + "\n").encode())		# "SA SE\n"
				elif(t_rx[0] == 'AZ' and t_rx[1] == 'EL'):
					os.write(self.mfd, ("AZ{:.1f} ".format(self.az.wdir) + "EL{:.1f} \n".format(self.el.wdir)).encode())
			elif(len(t_rx) == 6 and t_rx[0].startswith('AZ') and t_rx[1].startswith('EL')):
				try:
					f_az = float(t_rx[0].strip("AZ"))
					f_el = float(t_rx[1].strip("EL"))
					self.az.wdir = f_az  					# new az setpoint
					self.el.wdir = f_el  					# new el setpoint
				except ValueError:
					logging.error("SerialEmulator - Value Error: " + t_rx[0] + " " + t_rx[1])
			else:
				os.write(self.mfd, ("RX: " + t_rx[0] + "\r\n").encode())					# temp: just write it back
				t_rx.pop(0)
		# end while True
	# end loop

# class to handle CLI interface
class Cli:
	def __init__(self, az, el=None):
		logging.debug("CLI - init ")
		self.az = az
		self.el = el
		self.start_loop()

	def start_loop(self):
		loop = threading.Thread(target=self.main_loop, name='CLI')
		loop.daemon = True
		loop.start()

	def main_loop(self):
		logging.debug("CLI - loop ")
		time.sleep(0.1)
		# Loop forever
		while True:
			sdir = input("dir to move (-ve for reverse, 0 to quit): ")	# Ask the user where to move
			fdir = float(sdir)
			logging.debug("CLI - move to {:=07.3f}".format(fdir))
			self.az.set_dir(fdir)            # Move to
			self.el.set_dir(fdir)            # Move to


# main thread
# setup logging
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()

fileHandler = logging.FileHandler("pi-rotate.log")
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

# rootLogger.setLevel(logging.INFO)
rootLogger.setLevel(logging.DEBUG)
logging.info("Pi-Rotate - Started")

# initialize variables
EL_MOTOR = 1
AZ_MOTOR  = 2
EL_STEP_FWD = 1.0/30			# rotation (degrees) for one step forward
AZ_STEP_FWD = -1.0/30

# define each type of axis
el = axis.Axis_Stepper("EL", EL_MOTOR , EL_STEP_FWD, 0.0, 360.0)
az = axis.Axis_Stepper("AZ", AZ_MOTOR , AZ_STEP_FWD, 0.0, 360.0)

# instantiate the rotator emulator
emulator = SerialEmulator(az,el)

# instantiate CLI for manual control
#cli = Cli(az,el)

# mainloop
while True:
    try:
		#print ("status: AZ: W"+str(az.get_wdir())+" S%.2f E"% round(az.get_value(), 1)+ str(az.get_errors()))
		#logging.debug("Pi-Rotate - status: ")
        time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Pi-Rotate - keyboard interrupt")
        break
logging.info("Pi-Rotate - Exit ")
