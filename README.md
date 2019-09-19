# Pi-Rotate
Antenna Rotator for Raspberry Pi

Prerequisites - Hardware
  1 x Adafruit Motor DC & Stepper Motor HAT https://www.adafruit.com/product/2348
  2 x Stepper Motors 12Vdc https://www.amazon.com/gp/product/B00PNEQCLO
  1 x Raspberry Pi (3B or later)
  1 x 12Vdc Power supply for motors
  1 x 5Vdc Power supply for Pi
Prerequisites - Software
  Raspbian
  Python3
  Adafruit CircuitPython MotorKit https://github.com/adafruit/Adafruit_CircuitPython_MotorKit
  Hamlib https://github.com/Hamlib/Hamlib/wiki  
Optional - Software
  GPredict http://gpredict.oz9aec.net/ (or any other program compatible with hamlib/rotctld)
  
Setup
  Install the Pi HAT on the Pi https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi/assembly
  Install Raspbian and the other prerequisites
  Test motor operation with program stepper.py
  In a terminal, start program Pi-Rotate.py   make note of the pseudo terminal name, probably it will be: /dev/pts/0
  In another terminal, start program rotctld: rotctld -m 202 -r /dev/pts/0     (the last argument must match terminal name above)
  In another terminal, start program rotctl: 	rotctl -m 2
		use the P az el command to point the antenna North and level
		use the R x command to reset the az & el
		quit
  start gpredict
	  verify time & direction of upcoming pass
	  open Antenna Control window; choose satellite; Tolerance 0.2 deg; Engage; Track
