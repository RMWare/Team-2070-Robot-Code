import logging
import math
from wpilib import Talon, Gyro, Encoder, Timer
from common import util, constants, quickdebug
from common.syncgroup import SyncGroup
from . import Component


log = logging.getLogger("drivetrain")


class Drive(Component):
	left_pwm = 0
	right_pwm = 0

	# Cheesy Drive Stuff
	quickstop_accumulator = 0
	old_wheel = 0
	sensitivity = 1.5

	# Gyro & encoder stuff
	gyro_timer = Timer()

	gyro_goal = 0
	gyro_tolerance = 1  # Degrees

	encoder_goal = 0
	encoder_tolerance = 1  # Inches

	def __init__(self):
		super().__init__()

		self.l_motor = SyncGroup(Talon, constants.motor_drive_l)
		self.r_motor = SyncGroup(Talon, constants.motor_drive_r)

		self.l_encoder = Encoder(*constants.encoder_drive_l)
		self.r_encoder = Encoder(*constants.encoder_drive_r)

		DISTANCE_PER_REV = 4 * math.pi
		TICKS_PER_REV = 128
		REDUCTION = 30 / 36

		self.l_encoder.setDistancePerPulse((DISTANCE_PER_REV * REDUCTION) / TICKS_PER_REV)
		self.r_encoder.setDistancePerPulse((DISTANCE_PER_REV * REDUCTION) / TICKS_PER_REV)

		self.gyro = Gyro(constants.gyro)
		quickdebug.add_printables(self, [
			('gyro angle', self.gyro.getAngle),
			('left encoder', self.l_encoder.getDistance),
			('right encoder', self.r_encoder.getDistance),
		    'left_pwm', 'right_pwm', 'encoder_goal'
		])

	def update(self):
		self.l_motor.set(self.left_pwm)
		self.r_motor.set(-self.right_pwm)

	def stop(self):
		"""Disables EVERYTHING. Only use in case of critical failure."""
		self.l_motor.set(0)
		self.r_motor.set(0)

	def reset_gyro(self):
		pass
		# self.gyro.reset_encoder()

	def cheesy_drive(self, wheel, throttle, quickturn):
		"""
			Poofs!
			:param wheel: The speed that the robot should turn in the X direction. 1 is right [-1.0..1.0]
			:param throttle: The speed that the robot should drive in the Y direction. -1 is forward. [-1.0..1.0]
			:param quickturn: If the robot should drive arcade-drive style
		"""

		neg_inertia = wheel - self.old_wheel
		self.old_wheel = wheel
		wheel = util.sin_scale(wheel, 0.8, passes=3)

		if wheel * neg_inertia > 0:
			neg_inertia_scalar = 2.5
		else:
			if abs(wheel) > .65:
				neg_inertia_scalar = 5
			else:
				neg_inertia_scalar = 3

		neg_inertia_accumulator = neg_inertia * neg_inertia_scalar

		wheel += neg_inertia_accumulator

		if quickturn:
			if abs(throttle) < 0.2:
				alpha = .1
				self.quickstop_accumulator = (1 - alpha) * self.quickstop_accumulator + alpha * util.limit(wheel, 1.0) * 5
			over_power = 1
			angular_power = wheel
		else:
			over_power = 0
			angular_power = abs(throttle) * wheel * self.sensitivity - self.quickstop_accumulator
			self.quickstop_accumulator = util.wrap_accumulator(self.quickstop_accumulator)

		right_pwm = left_pwm = throttle

		left_pwm += angular_power
		right_pwm -= angular_power

		if left_pwm > 1:
			right_pwm -= over_power * (left_pwm - 1)
			left_pwm = 1
		elif right_pwm > 1:
			left_pwm -= over_power * (right_pwm - 1)
			right_pwm = 1
		elif left_pwm < -1:
			right_pwm += over_power * (-1 - left_pwm)
			left_pwm = -1
		elif right_pwm < -1:
			left_pwm += over_power * (-1 - right_pwm)
			right_pwm = -1
		self.left_pwm = left_pwm
		self.right_pwm = right_pwm

	def tank_drive(self, left, right):
		# Applies a bit of exponential scaling to improve control at low speeds
		self.left_pwm = math.copysign(math.pow(left, 2), left)
		self.right_pwm = math.copysign(math.pow(right, 2), right)

	# Stuff for encoder driving
	def set_encoder_goal(self, goal):
		self.l_encoder.reset()
		self.r_encoder.reset()
		self.encoder_goal = goal

	def drive_encoder(self):
		l_error = self.encoder_goal - self.l_encoder.getDistance()
		r_error = self.encoder_goal - self.r_encoder.getDistance()

		self.left_pwm =  util.limit(l_error, 0.5)
		self.right_pwm = util.limit(r_error, 0.5)

	def at_encoder_goal(self):
		l_error = self.encoder_goal - self.l_encoder.getDistance()
		r_error = self.encoder_goal - self.r_encoder.getDistance()
		return abs(l_error) < self.encoder_tolerance and abs(r_error) < self.encoder_tolerance

	# Stuff for Gyro driving
	def set_gyro_goal(self, goal):
		self.gyro_timer.stop()
		self.gyro_timer.reset()
		self.gyro_goal = goal

	def turn_gyro(self):
		result = self.gyro_error() * 0.05

		self.left_pwm = result
		self.right_pwm = -result

	def at_gyro_goal(self):
		on = abs(self.gyro_error()) < self.gyro_tolerance
		if False and on:
			if not self.gyro_timer.running:
				self.gyro_timer.start()
			if self.gyro_timer.hasPeriodPassed(.3):
					return True
		return False

	def gyro_error(self):
		"""
		Returns gyro error wrapped from -180 to 180
		:return:
		"""
		raw_error = self.gyro_goal - self.gyro.getAngle()
		wrapped_error = raw_error - 360 * round(raw_error / 360)
		return wrapped_error