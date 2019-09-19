# axis.py
# axis classes


import time
import threading
import logging
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper


# Axis base class
class Axis:
	def __init__(self, axname, min: float = 0.0, max: float = 360.0):
		self.axname = axname
		logging.debug("Axis - init: " + self.axname)
		self.min = min
		self.max = max
		self.wdir = 0.0			# target direction; 0 - 360 degrees
		self.pdir = 0.0			# previous direction
		self.status = 'init'

	def get_dir(self):
		return self.wdir

	def set_dir(self, value):
		new_val = max(value, self.min)
		new_val = min(new_val, self.max)
		self.wdir = new_val
		return

	def park(self):
		logging.debug("Axis - park: " + self.axname)
		self.wdir = 0.0			# new target is home position
		return

	def reset(self):
		logging.debug("Axis - reset: " + self.axname)
		self.wdir = 0.0			# new target
		self.pdir = 0.0			# matches target
		self.status = 'idle'
		return

	def stop(self):
		logging.debug("Axis - stop: " + self.axname)
		self.wdir = self.pdir		# wherever we are, that's far enough
		self.status = 'idle'
		return


# axis controller with fake hardware
class Axis_Fake(Axis):
	pass


# axis controller with stepper motor
class Axis_Stepper(Axis):
	dt = 0.01									# delay time (seconds)
	#step_size = 1.0/30							# axis rotation (degrees) for one motor step
	def __init__(self, axname, nmotor, step_fwd, min: float = 0.0, max: float = 360.0):
		Axis.__init__(self, axname, min, max)	# base class constructor
		self.status = 'unknown'
		self.kit = MotorKit()					# instantiate a stepper motor
		if(nmotor == 1): self.stepper = self.kit.stepper1
		if(nmotor == 2): self.stepper = self.kit.stepper2
		self.step_fwd = step_fwd
		loop = threading.Thread(target=self.loop, name="AxWork" + self.axname)  # prepare a new thread
		loop.daemon = True						# exit automatically when main program exits
		loop.start()  							# and start it

	def loop(self):
		logging.debug("AxisWork - loop")
		while True:
			delta = self.wdir - self.pdir		# calculate deviation (error) from setpoint
			mag = abs(delta)
			if (mag >= abs(self.step_fwd)):		# do we need at least one step?
				self.status = 'move'
				logging.debug("AxisWork - step from {:=07.3f} towards {:=07.3f}".format(self.pdir, self.wdir))
				if ((mag > 180.0) and (self.max == 360.0) and (self.min == 0.0)): delta *= -1.0		# go other direction
				if ((delta > 0) and (self.step_fwd > 0)) or ((delta < 0) and (self.step_fwd < 0)):
					drot = stepper.FORWARD
					self.pdir += self.step_fwd  				# track position
				else:
					drot = stepper.BACKWARD
					self.pdir -= self.step_fwd  				# track position
				self.stepper.onestep(direction=drot)			# take a step
				if (self.pdir > 360.0): self.pdir -= 360.0
				if (self.pdir < 0.0): 	self.pdir += 360.0
			else:
				self.status = 'idle'
			time.sleep(self.dt)


#	def get_dir(self):
#		return self.wdir

def set_dir(self, value):
	new_val = max(value, self.min)
	new_val = min(new_val, self.max)
	self.wdir = value					# leave it for worker thread to handle
	return
