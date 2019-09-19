# stepper.py
# Simple test for using adafruit_motorkit with a stepper motor
import time
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
print("MotorKit Example")
kit = MotorKit()                # instantiate
dt = 0.005                      # delay time
ns = 10800                      # number of steps
print("MotorKit - M1 Forward!")
for i in range(ns):
    time.sleep(dt)
    kit.stepper1.onestep(direction=stepper.FORWARD)
time.sleep(2)
print("MotorKit - M1 Reverse!")
for i in range(ns):
    time.sleep(dt)
    kit.stepper1.onestep(direction=stepper.BACKWARD)
time.sleep(2)
print("MotorKit - M2 Forward!")
for i in range(ns):
    time.sleep(dt)
    kit.stepper2.onestep(direction=stepper.FORWARD)
time.sleep(2)
print("MotorKit - M2 Reverse!")
for i in range(ns):
    time.sleep(dt)
    kit.stepper2.onestep(direction=stepper.BACKWARD)
print("MotorKit - Done")
