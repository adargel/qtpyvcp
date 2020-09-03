from __future__ import division

import math
import unittest

from qtpyvcp.widgets.conversational.ops.base_op import BaseGenerator


class Facing(BaseGenerator):
    def __init__(self):
        super(Facing, self).__init__()
        self.tool_diameter = 0.
        self.step_over = 0.
        self.step_down = 0.
        self.lead_in = self.lead_out = 0.1
        self.x_start = self.x_end = 0.
        self.y_start = self.y_end = 0.

    def face(self):
        width = abs(self.y_end - self.y_start)
        depth = abs(self.z_end - self.z_start)

        num_step_down = abs(int(math.ceil(depth / self.step_down)))
        num_step_over = abs(int(math.ceil(width / self.step_over)))

        step_over = width / num_step_over
        step_down = depth / num_step_down

        tool_radius = self.tool_diameter / 2
        ramp_radius = self.retract + step_down

        x_start = self.x_start - tool_radius - ramp_radius
        y_start = self.y_start + tool_radius - step_over
        z_start = self.z_start

        z = z_start
        gcode = self._start_op()
        step_over = - step_over
        for i in xrange(num_step_down):
            x = self.x_end
            y = y_start
            gcode.append('G0 X%.4f Y%.4f' % (x_start, y_start))
            gcode.append('G0 Z%.4f' % (z + self.retract))
            gcode.append('G18 G2 X%.4f Z%.4f I%.4f' %
                         (x_start + ramp_radius, z + self.retract - ramp_radius, ramp_radius))

            z -= step_down

            gcode.append('G1 X%.4f' % x)
            for _ in xrange(num_step_over - 1):
                y += step_over
                if x == self.x_end:
                    gcode.append('G17 G2 Y%.4f J%.4f' % (y, step_over / 2))
                    x = self.x_start
                else:
                    gcode.append('G17 G3 Y%.4f J%.4f' % (y, step_over / 2))
                    x = self.x_end

                gcode.append('G1 X%.4f' % x)

            if x == self.x_start:
                gcode.append('G18 G3 X%.4f Z%.4f K%.4f' % (x - ramp_radius, z + ramp_radius, ramp_radius))
            else:
                gcode.append('G18 G2 X%.4f Z%.4f K%.4f' % (x + ramp_radius, z + ramp_radius, ramp_radius))

            if i < (num_step_down - 1):
                gcode.append('G0 Z%.4f' % self.z_clear)

        gcode.extend(self._end_op())

        return gcode


class TestFacing(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.sut = Facing()
        cls.sut.tool_number = 4
        cls.sut.spindle_rpm = 1200
        cls.sut.spindle_dir = 'cw'
        cls.sut.wcs = 'G55'
        cls.sut.coolant = ''
        cls.sut.retract = 0.02
        cls.sut.z_start = 1
        cls.sut.z_end = 0.5
        cls.sut.z_feed = 4.8
        cls.sut.z_clear = 1.2
        cls.sut.x_start = 1
        cls.sut.y_start = 1
        cls.sut.x_end = 6
        cls.sut.y_end = -2
        cls.sut.lead_in = cls.sut.lead_out = 0.1
        cls.sut.tool_diameter = 2
        cls.sut.step_over = 1
        cls.sut.step_down = 0.125
        cls.sut.xy_feed = 60

    def test_should_face_in_one_pass_when_possible(self):
        expected_gcode = [
            'T4 M6 G43',
            'S1200.0000',
            'M3',
            'G55',
            'F60.0000',
            'G0 X-0.1450 Y1.0000',
            'G0 Z1.0200',
            'G18 G2 X0.0000 Z0.8750 I0.1450',
            'G1 X6.0000',
            'G18 G2 X6.1450 Z1.0200 K0.1450',
            'G0 Z1.2000',
        ]

        self.sut.y_end = 0
        self.sut.z_end = 0.875
        self.assertEqual(expected_gcode, self.sut.face())

    def test_should_face_with_multiple_step_overs(self):
        expected_gcode = [
            'T4 M6 G43',
            'S1200.0000',
            'M3',
            'G55',
            'F60.0000',
            'G0 X-0.1450 Y1.0000',
            'G0 Z1.0200',
            'G18 G2 X0.0000 Z0.8750 I0.1450',
            'G1 X6.0000',
            'G17 G2 Y0.0000 J-0.5000',
            'G1 X1.0000',
            'G18 G3 X0.8550 Z1.0200 K0.1450',
            'G0 Z1.2000',
        ]

        self.sut.y_end = -1
        self.sut.z_end = 0.875
        self.assertEqual(expected_gcode, self.sut.face())

    def test_should_face_with_odd_number_of_steps_overs(self):
        expected_gcode = [
            'T4 M6 G43',
            'S1200.0000',
            'M3',
            'G55',
            'F60.0000',
            'G0 X-0.1450 Y1.0000',
            'G0 Z1.0200',
            'G18 G2 X0.0000 Z0.8750 I0.1450',
            'G1 X6.0000',
            'G17 G2 Y0.0000 J-0.5000',
            'G1 X1.0000',
            'G17 G3 Y-1.0000 J-0.5000',
            'G1 X6.0000',
            'G18 G2 X6.1450 Z1.0200 K0.1450',
            'G0 Z1.2000',
        ]

        self.sut.y_end = -2
        self.sut.z_end = 0.875
        self.assertEqual(expected_gcode, self.sut.face())

    def test_should_face_with_multiple_step_downs(self):
        expected_gcode = [
            'T4 M6 G43',
            'S1200.0000',
            'M3',
            'G55',
            'F60.0000',
            'G0 X-0.1450 Y1.0000',
            'G0 Z1.0200',
            'G18 G2 X0.0000 Z0.8750 I0.1450',
            'G1 X6.0000',
            'G18 G2 X6.1450 Z1.0200 K0.1450',
            'G0 Z1.2000',
            'G0 X-0.1450 Y1.0000',
            'G0 Z0.8950',
            'G18 G2 X0.0000 Z0.7500 I0.1450',
            'G1 X6.0000',
            'G18 G2 X6.1450 Z0.8950 K0.1450',
            'G0 Z1.2000',
        ]

        self.sut.y_end = 0
        self.sut.z_end = 0.750
        self.assertEqual(expected_gcode, self.sut.face())

    def test_should_face_with_multiple_step_downs_and_step_overs(self):
        expected_gcode = [
            'T4 M6 G43',
            'S1200.0000',
            'M3',
            'G55',
            'F60.0000',
            'G0 X-0.1450 Y1.0000',
            'G0 Z1.0200',
            'G18 G2 X0.0000 Z0.8750 I0.1450',
            'G1 X6.0000',
            'G17 G2 Y0.0000 J-0.5000',
            'G1 X1.0000',
            'G17 G3 Y-1.0000 J-0.5000',
            'G1 X6.0000',
            'G18 G2 X6.1450 Z1.0200 K0.1450',
            'G0 Z1.2000',
            'G0 X-0.1450 Y1.0000',
            'G0 Z0.8950',
            'G18 G2 X0.0000 Z0.7500 I0.1450',
            'G1 X6.0000',
            'G17 G2 Y0.0000 J-0.5000',
            'G1 X1.0000',
            'G17 G3 Y-1.0000 J-0.5000',
            'G1 X6.0000',
            'G18 G2 X6.1450 Z0.8950 K0.1450',
            'G0 Z1.2000',
        ]

        self.sut.y_end = -2
        self.sut.z_end = 0.750
        self.assertEqual(expected_gcode, self.sut.face())

    def test_should_adjust_the_step_over_to_use_even_step_over(self):
        expected_gcode = [
            'T4 M6 G43',
            'S1200.0000',
            'M3',
            'G55',
            'F60.0000',
            'G0 X-0.1450 Y0.5000',
            'G0 Z1.0200',
            'G18 G2 X0.0000 Z0.8750 I0.1450',
            'G1 X6.0000',
            'G17 G2 Y-1.0000 J-0.7500',
            'G1 X1.0000',
            'G18 G3 X0.8550 Z1.0200 K0.1450',
            'G0 Z1.2000',
        ]

        self.sut.step_over = 2
        self.sut.y_end = -2
        self.sut.z_end = 0.875
        self.assertEqual(expected_gcode, self.sut.face())

    def test_should_adjust_the_step_down_to_use_even_step_down(self):
        expected_gcode = [
            'T4 M6 G43',
            'S1200.0000',
            'M3',
            'G55',
            'F60.0000',
            'G0 X-1.5200 Y1.0000',
            'G0 Z1.0200',
            'G18 G2 X0.0000 Z-0.5000 I1.5200',
            'G1 X6.0000',
            'G18 G2 X7.5200 Z1.0200 K1.5200',
            'G0 Z1.2000',
            'G0 X-1.5200 Y1.0000',
            'G0 Z-0.4800',
            'G18 G2 X0.0000 Z-2.0000 I1.5200',
            'G1 X6.0000',
            'G18 G2 X7.5200 Z-0.4800 K1.5200',
            'G0 Z1.2000',
        ]

        self.sut.y_end = 0
        self.sut.step_down = 2
        self.sut.z_end = -2
        self.assertEqual(expected_gcode, self.sut.face())
