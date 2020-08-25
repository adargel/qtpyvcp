import unittest

from qtpyvcp.gcode.gcode_file import GCodeFile


class FakeOp:
    def __init__(self):
        self.test_gcode = ''
        self.test_name = ''
        self.test_start_op = []
        self.test_end_op = []

    def name(self):
        return self.test_name

    def start_op(self):
        return self.test_start_op

    def end_op(self):
        return self.test_end_op

    def gcode(self):
        return self.test_gcode


class TestGCodeFile(unittest.TestCase):
    @classmethod
    def setUp(cls):
        cls.sut = GCodeFile()
        cls.sut.disable_line_numbers()

    def test_should_output_line_numbers_and_increment_by_stride_for_each_line(self):
        self.sut.enable_line_numbers()
        expected_output = [
            'N10 G90 G94 G17 G91.1',
            'N20 G53 G0 Z0',
            'N30 M30',
            'N40 %',
        ]

        self.assertEqual(self.sut.to_string(), '\n'.join(expected_output))

    def test_should_not_add_line_numbers_when_not_enabled(self):
        expected_output = [
            'G90 G94 G17 G91.1',
            'G53 G0 Z0',
            'M30',
            '%',
        ]

        self.assertEqual(self.sut.to_string(), '\n'.join(expected_output))

    def test_should_add_the_op_name_as_comment_before_the_op(self):
        expected_output = [
            'G90 G94 G17 G91.1',
            '(a simple op)',
            'G53 G0 Z0',
            'M30',
            '%',
        ]

        op = FakeOp()
        op.test_name = 'a simple op'
        self.sut.ops.append(op)

        self.assertEqual(self.sut.to_string(), '\n'.join(expected_output))

    def test_should_add_a_single_op(self):
        expected_output = [
            'G90 G94 G17 G91.1',
            '(a simple op)',
            'some gcode',
            'G53 G0 Z0',
            'M30',
            '%',
        ]

        op = FakeOp()
        op.test_name = 'a simple op'
        op.test_gcode = ['some gcode']
        self.sut.ops.append(op)

        self.assertEqual(self.sut.to_string(), '\n'.join(expected_output))

    def test_should_add_multiple_ops(self):
        expected_output = [
            'G90 G94 G17 G91.1',
            '(a simple op)',
            'some gcode',
            '(another simple op)',
            'some more gcode',
            '(yet another simple op)',
            'and some more gcode',
            'G53 G0 Z0',
            'M30',
            '%',
        ]

        op1 = FakeOp()
        op1.test_name = 'a simple op'
        op1.test_gcode = ['some gcode']
        self.sut.ops.append(op1)

        op2 = FakeOp()
        op2.test_name = 'another simple op'
        op2.test_gcode = ['some more gcode']
        self.sut.ops.append(op2)

        op3 = FakeOp()
        op3.test_name = 'yet another simple op'
        op3.test_gcode = ['and some more gcode']
        self.sut.ops.append(op3)

        self.assertEqual(self.sut.to_string(), '\n'.join(expected_output))

    def test_should_not_add_name_as_comment_when_not_present(self):
        expected_output = [
            'G90 G94 G17 G91.1',
            'G53 G0 Z0',
            'M30',
            '%',
        ]

        op = FakeOp()
        self.sut.ops.append(op)

        self.assertEqual(self.sut.to_string(), '\n'.join(expected_output))

    def test_should_add_op_start_and_end_gcode_when_present(self):
        expected_output = [
            'G90 G94 G17 G91.1',
            'some', 'start', 'gcode',
            'some', 'op', 'gcode',
            'some', 'end', 'gcode',
            'G53 G0 Z0',
            'M30',
            '%',
        ]

        op = FakeOp()
        op.test_start_op = ['some', 'start', 'gcode']
        op.test_gcode = ['some', 'op', 'gcode']
        op.test_end_op = ['some', 'end', 'gcode']
        self.sut.ops.append(op)

        self.assertEqual(self.sut.to_string(), '\n'.join(expected_output))


if __name__ == '__main__':
    unittest.main()
