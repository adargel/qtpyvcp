import unittest

from qtpyvcp.gcode.drill_op import Drilling


class TestDrilling(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.sut = Drilling()
        cls.sut.tool_number = 4
        cls.sut.spindle_rpm = 1200
        cls.sut.spindle_dir = 'cw'
        cls.sut.wcs = 'G55'
        cls.sut.coolant = ''
        cls.sut.retract = 0.02
        cls.sut.z_start = 1
        cls.sut.z_end = 0.5
        cls.sut.z_feed = 4.8
        cls.sut.z_clear = 0.2

    def test_should_drill_a_hole_at_the_given_location(self):
        expected_gcode = [
            'T4 M6 G43',
            'S1200.000',
            'M3',
            'G55',
            'G0 X4.000 Y1.000',
            'G98 G81 R1.020 Z0.500 F4.800',
            'G80',
            'G0 Z0.200'
        ]

        self.sut.holes.append((4., 1.))
        op = self.sut.drill()
        self.assertEqual(op.gcode(), expected_gcode)

    def test_should_drill_multiple_holes_at_the_given_locations(self):
        expected_gcode = [
            'T4 M6 G43',
            'S1200.000',
            'M3',
            'G55',
            'G0 X4.000 Y1.000',
            'G98 G81 R1.020 Z0.500 F4.800',
            'X2.000 Y0.000',
            'X3.200 Y-10.010',
            'G80',
            'G0 Z0.200'
        ]

        self.sut.holes.append((4., 1.))
        self.sut.holes.append((2., 0.))
        self.sut.holes.append((3.2, -10.01))
        self.assertEqual(self.sut.drill().gcode(), expected_gcode)

    def test_should_set_the_coolant_to_mist_when_specified(self):
        expected_gcode = [
            'T4 M6 G43',
            'S1200.000',
            'M3',
            'G55',
            'M7',
            'G80',
            'M9',
            'G0 Z0.200'
        ]

        self.sut.coolant = 'mist'
        self.assertEqual(self.sut.drill().gcode(), expected_gcode)

    def test_should_set_the_coolant_to_flood_when_specified(self):
        expected_gcode = [
            'T4 M6 G43',
            'S1200.000',
            'M3',
            'G55',
            'M8',
            'G80',
            'M9',
            'G0 Z0.200'
        ]

        self.sut.coolant = 'flood'
        self.assertEqual(self.sut.drill().gcode(), expected_gcode)

    def test_should_set_the_spindle_to_ccw_when_specified(self):
        expected_gcode = [
            'T4 M6 G43',
            'S1200.000',
            'M4',
            'G55',
            'G80',
            'G0 Z0.200'
        ]

        self.sut.spindle_dir = 'ccw'
        self.assertEqual(self.sut.drill().gcode(), expected_gcode)

    def test_dwell_should_use_a_g82_cycle(self):
        expected_gcode = [
            'T4 M6 G43',
            'S1200.000',
            'M3',
            'G55',
            'G0 X4.000 Y1.000',
            'G98 G82 R1.020 Z0.500 P0.500 F4.800',
            'G80',
            'G0 Z0.200'
        ]

        self.sut.holes.append((4., 1.))
        self.assertEqual(self.sut.dwell(0.5).gcode(), expected_gcode)

    def test_peck_should_use_a_g83_cycle(self):
        expected_gcode = [
            'T4 M6 G43',
            'S1200.000',
            'M3',
            'G55',
            'G0 X4.000 Y1.000',
            'G98 G83 R1.020 Z0.500 Q0.100 F4.800',
            'G80',
            'G0 Z0.200'
        ]

        self.sut.holes.append((4., 1.))
        self.assertEqual(self.sut.peck(0.1).gcode(), expected_gcode)

    def test_chip_break_should_use_a_g73_cycle(self):
        expected_gcode = [
            'T4 M6 G43',
            'S1200.000',
            'M3',
            'G55',
            'G0 X4.000 Y1.000',
            'G98 G73 R1.020 Z0.500 Q0.050 F4.800',
            'G80',
            'G0 Z0.200'
        ]

        self.sut.holes.append((4., 1.))
        self.assertEqual(self.sut.chip_break(0.05).gcode(), expected_gcode)

    def test_right_hand_tap_should_use_a_g84_cycle(self):
        expected_gcode = [
            'T4 M6 G43',
            'S120.000',
            'M3',
            'G55',
            'G0 X4.000 Y1.000',
            'G98 G84 R1.020 Z0.500 F6.000 S120.000',
            'G80',
            'G0 Z0.200'
        ]

        self.sut.spindle_rpm = 120
        self.sut.holes.append((4., 1.))
        self.assertEqual(self.sut.tap(0.05).gcode(), expected_gcode)

    def test_left_hand_tap_should_use_a_g74_cycle(self):
        expected_gcode = [
            'T4 M6 G43',
            'S120.000',
            'M4',
            'G55',
            'G0 X4.000 Y1.000',
            'G98 G74 R1.020 Z0.500 F6.000 S120.000',
            'G80',
            'G0 Z0.200'
        ]

        self.sut.spindle_rpm = 120
        self.sut.spindle_dir = 'ccw'
        self.sut.holes.append((4., 1.))
        self.assertEqual(self.sut.tap(0.05).gcode(), expected_gcode)


