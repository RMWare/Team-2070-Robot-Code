from wpilib import Solenoid, Talon, DigitalInput
from common import constants
from . import Component


class Intake(Component):
    def __init__(self):
        super().__init__()

        self._l_motor = Talon(constants.motor_intake_l)
        self._r_motor = Talon(constants.motor_intake_r)
        self._intake_piston = Solenoid(constants.solenoid_intake)
        self._photosensor = DigitalInput(constants.far_photosensor)

        self._left_pwm = 0
        self._right_pwm = 0
        self._open = False

    def update(self):
        self._l_motor.set(self._left_pwm)
        self._r_motor.set(self._right_pwm)

        self._intake_piston.set(not self._open)

    def spin(self, power, same_direction=False):
        self._left_pwm = power
        self._right_pwm = power * (1 if same_direction else -1)

    def intake_tote(self):
        power = .3 if not self._photosensor.get() else .75
        self.spin(power)

    def intake_bin(self):
        power = .3 if not self._photosensor.get() else .65
        self.spin(power)

    def open(self):
        self._open = True

    def close(self):
        self._open = False

    def stop(self):
        """Disables EVERYTHING. Only use in case of critical failure"""
        self._l_motor.set(0)
        self._r_motor.set(0)
