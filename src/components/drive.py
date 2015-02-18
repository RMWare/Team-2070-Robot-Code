import math
from wpilib import Talon
from common import util, constants
from common.syncgroup import SyncGroup


class TankDrive(object):
	def __init__(self):
		self.l_motor = SyncGroup(Talon, constants.motors.drive_left)
		self.r_motor = SyncGroup(Talon, constants.motors.drive_right)
		self.left = 0
		self.right = 0

	def move(self, left, right):
		# Applies a bit of exponential scaling to improve control at low speeds
		self.left = math.copysign(math.pow(left, 2), left)
		self.right = math.copysign(math.pow(right, 2), right)

	def update(self):
		self.l_motor.set(-self.left)
		self.r_motor.set(self.right)


class CheesyDrive(object):
	old_wheel = 0
	wheel = 0
	throttle = 0
	quickturn = False
	quickstop_accumulator = 0

	throttle_deadband = 0.02
	wheel_deadband = 0.02
	sensitivity = .75

	def __init__(self):
		self.l_motor = SyncGroup(Talon, constants.motors.drive_left)
		self.r_motor = SyncGroup(Talon, constants.motors.drive_right)

	def move(self, wheel, throttle, quickturn):
		"""
			Causes the robot to drive
			:param wheel: The speed that the robot should turn in the X direction. 1 is right [-1.0..1.0]
			:param throttle: The speed that the robot should drive in the Y direction. -1 is forward. [-1.0..1.0]
			:param quickturn: If the robot should drive arcade-drive style
		"""

		self.wheel = util.deadband(-wheel, 0.1)
		self.throttle = util.deadband(throttle, 0.1)
		self.quickturn = quickturn

	def update(self):
		wheel = util.deadband(self.wheel, self.wheel_deadband)
		throttle = util.deadband(self.throttle, self.throttle_deadband)
		neg_intertia = wheel - self.old_wheel
		self.old_wheel = wheel
		wheel = util.sin_scale(wheel, 0.5, passes=3)

		if wheel * neg_intertia > 0:
			neg_intertia_scalar = 2.5
		else:
			if abs(wheel) > .65:
				neg_intertia_scalar = 5
			else:
				neg_intertia_scalar = 3

		neg_intertia_accumulator = neg_intertia * neg_intertia_scalar

		wheel += neg_intertia_accumulator

		if self.quickturn:
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

		self.l_motor.set(-left_pwm)
		self.r_motor.set(right_pwm)
