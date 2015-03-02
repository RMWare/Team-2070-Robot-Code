import wpilib


class XboxController(object):
	"""
		Allows usage of an Xbox controller, with sensible names for xbox
		specific buttons and axes.

	"""

	def __init__(self, port):
		"""
		:param port: The port on the driver station that the controller is
			plugged into.
		:type  port: int
		"""

		self.joy = wpilib.Joystick(port)

	def left_x(self):
		"""Get the left stick X axis

		:returns: -1 to 1
		:rtype: float
		"""
		return self.joy.getRawAxis(0)

	def left_y(self):
		"""Get the left stick Y axis

		:returns: -1 to 1
		:rtype: float
		"""
		return self.joy.getRawAxis(1)

	getX = left_x
	getY = left_y

	def left_pressed(self):
		"""Determines if the left stick is pressed

		:returns: True if pressed, False otherwise
		:rtype: bool
		"""
		return self.joy.getRawButton(9)

	def pov(self):
		"""Get the state of a POV on the joystick.

		:param pov: which POV (default is 0)
		:type  pov: int
		:returns: The angle of the POV in degrees, or -1 if the POV is not
				  pressed.
		:rtype: float
		"""
		return self.joy.getPOV(0)

	def right_x(self):
		"""Get the right stick X axis

		:returns: -1 to 1
		:rtype: float
		"""
		return self.joy.getRawAxis(4)

	def right_y(self):
		"""Get the right stick Y axis

		:returns: -1 to 1
		:rtype: float
		"""
		return self.joy.getRawAxis(5)

	def right_pressed(self):
		"""Determines if the right stick is pressed

		:returns: True if pressed, False otherwise
		:rtype: bool
		"""
		return self.joy.getRawButton(10)

	def a(self):
		"""Gets whether the A button is pressed

		:returns: True if pressed, False otherwise
		:rtype: bool
		"""
		return self.joy.getRawButton(1)

	def b(self):
		"""Gets whether the B button is pressed

		:returns: True if pressed, False otherwise
		:rtype: bool
		"""
		return self.joy.getRawButton(2)

	def x(self):
		"""Gets whether the X button is pressed

		:returns: True if pressed, False otherwise
		:rtype: bool
		"""
		return self.joy.getRawButton(3)

	def y(self):
		"""Gets whether the X button is pressed

		:returns: True if pressed, False otherwise
		:rtype: bool
		"""
		return self.joy.getRawButton(4)

	def start(self):
		"""Gets whether the Start button is pressed

		:returns: True if pressed, False otherwise
		:rtype: bool
		"""
		return self.joy.getRawButton(8)

	def back(self):
		"""Gets whether the Back button is pressed

		:returns: True if pressed, False otherwise
		:rtype: bool
		"""
		return self.joy.getRawButton(7)

	def left_bumper(self):
		"""Gets whether the left bumper is pressed

		:returns: True if pressed, False otherwise
		:rtype: bool
		"""
		return self.joy.getRawButton(5)

	def right_bumper(self):
		"""Gets whether the right bumper is pressed

		:returns: True if pressed, False otherwise
		:rtype: bool
		"""
		return self.joy.getRawButton(6)

	def left_trigger(self):
		"""Gets whether the left trigger is pressed

		:returns: True if pressed, False otherwise
		:rtype: bool
		"""
		return self.joy.getRawAxis(2) > 0

	def right_trigger(self):
		"""Gets whether the right trigger is pressed

		:returns: True if pressed, False otherwise
		:rtype: bool
		"""
		return self.joy.getRawAxis(3) > 0

	def rumble(self, left=None, right=None):
		"""Sets the rumble amount on one/both side(s) of the controller"""
		if left is not None:
			self.joy.setRumble(wpilib.Joystick.RumbleType.kLeftRumble_val, left)
		if right is not None:
			self.joy.setRumble(wpilib.Joystick.RumbleType.kRightRumble_val, right)