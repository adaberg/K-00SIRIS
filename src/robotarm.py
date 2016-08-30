import math

import time

from kinematics import Kinematics, KinematicsError, WorldCoordinateSystem


class Robotarm:
    """
    Main controller-class for the 00SIRIS Robotarm
    """

    # TODO: Integrate Hedgehog and get this going
    """
    Hedgehog information:
    2000 Steps per Servo
    """

    def __init__(self, client, links, base_offset, min_angles, max_angles, min_servo_pos, max_servo_pos):
        """
        Constructor - used for initialization

        :param links: the lengths of all links in an array
        :param base_offset: the distance in between the center of the base axis and the first joint
        """

        # Params
        self.client = client
        self.links = links
        self.base_offset = base_offset
        self.min_angles = min_angles
        self.max_angles = max_angles
        self.min_servo_pos = min_servo_pos
        self.max_servo_pos = max_servo_pos

        # Base, axis 1, axis 2, axis 3, axis 4, grabber
        self.joint_pos = [0.0, 1.51, -1.51, 0.0, 0.0, 0.0]

        self.kinematics = Kinematics(self.links, self.base_offset)

    def move_to_pos(self, pos, joint):
        self.client.set_servo(joint, True, pos)
        self.joint_pos[joint] = pos

    def move_to_angle(self, angle, joint):
        """
        Moves a joint to a certain angle
        :param angle: the angle
        :param joint: the joint
        """
        pos = self.angle_to_step(angle, joint)

        self.move_to_pos(pos, joint)

    def angle_to_step(self, angle, joint):
        """
        Calculates the step value of the given angle for the given joint.
        Servos have 2048 steps and this maps the angle to those
        :param angle: the angle in radiant representation
        :param joint: the joint that should be used
        :return: the servo-position in steps
        """
        if self.min_angles[joint] < angle < self.max_angles[joint]:
            raise OutOfReachError

        total_steps = (self.max_servo_pos[joint] - self.min_servo_pos[joint])

        pos = (total_steps / (2 * math.pi)) * angle + self.min_servo_pos[joint]

        # TODO test properly

        return pos

    def step_to_angle(self, step, joint):
        # TODO
        angle = step    # Placeholder
        return angle

    def move_to_cartesian(self, x, y, z, fixed_joint, fj_angle):
        """
        Moves the robotarm to the given cartesian coordinates.

        :param x: the x-coordinate
        :param y: the y-coordinate
        :param z: the z-coordinate
        """

        try:
            angles = self.kinematics.inverse(x, y, z, fixed_joint, fj_angle)
            self.move_to_config(angles)
        except KinematicsError as ke:
            print("Position cannot be reached: " + ke.message)

        except OutOfReachError as oore:
            print("The kinematics module was able to calculate a position, but the servos are not able to reach it: " +
                  oore.message)

    def move_to_cartesian_aligned(self, x, y, z, alignment):
        """
        Moves the robotarm to the given cartesian coordinates.
        This one takes the alignment of the grabber towards the x-axis and uses it as the fixed joint.

        :param x: the x-coordinate
        :param y: the y-coordinate
        :param z: the z-coordinate
        """

        try:
            angles = self.kinematics.inverse_aligned(x, y, z, alignment)
            self.move_to_config(angles)
        except KinematicsError as ke:
            print("Position cannot be reached: " + ke.message)

        except OutOfReachError as oore:
            print("The kinematics module was able to calculate a position, but the servos are not able to reach it: " +
                  oore.message)

    def move_to_config(self, angles):
        """
        Move the robotarm to the given configuration.

        :param angles: the angles of all joints
        """

        if self.validate_configuration(angles):
            for index, angle in angles:
                self.move_to_angle(index, angles[index])
        else:
            raise OutOfReachError("The given configuration cannot be reached!")

    def validate_configuration(self, angles):
        """
        Validates whether the given configuration is reachable.

        :param angles: the angles of all joints
        :return: True if the given configuration is reachable, else: False
        """
        # TODO test properly

        if len(angles) != 6:
            return False

        # Check whether the angles on all joints can be reached
        for joint, angle in enumerate(angles):
            if not self.validate_angle(angle, joint):
                return False

        return True

    def validate_angle(self, angle, joint):
        """
        Validates whether the given angle is reachable with the given joint.

        :param angle: the angle that should be validated
        :param joint: the joint that the angle should be validated for
        :return: True if the given angle is reachable with the given joint, else: False
        """
        return self.min_angles[joint] < angle < self.max_angles[joint]

    def move_servo_over_time(self, pos, joint, duration):
        # TODO
        pass

    def get_tool_cs(self):
        angles = []
        for joint, pos in enumerate(self.joint_pos):
            angles[joint] = self.step_to_angle(pos, joint)

        x, y, z, theta_x, theta_y, theta_z = self.kinematics.direct(angles)
        return WorldCoordinateSystem(x, y, z, theta_x, theta_y, theta_z)

    def close(self):
        self.client.close()


class Joint:
    def __init__(self, ):
        pass


class RobotarmError(Exception):
    """
    Is thrown when an error occurs within the Robotarm module
    """

    def __init__(self, message):
        """
        Initializes the exception
        :param message: explanation of the error
        """

        self.message = message


class OutOfReachError(RobotarmError):
    pass
