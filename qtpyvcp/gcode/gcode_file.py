class GCodeFile(object):
    def __init__(self):
        self.ops = []

        self.preamble = ['G90 G94 G17 G91.1']
        self.epilog = ['G53 G0 Z0', 'M30', '%']
        self.starting_line_number = 10
        self.line_number_stride = 10
        self._line_numbers = True

    def enable_line_numbers(self):
        self._line_numbers = True

    def disable_line_numbers(self):
        self._line_numbers = False

    def to_string(self):
        gcode = []
        gcode.extend(self.preamble)
        for op in self.ops:
            if len(op.name()) > 0:
                gcode.append('(%s)' % op.name())
            gcode.extend(op.start_op())
            gcode.extend(op.gcode())
            gcode.extend(op.end_op())
        gcode.extend(self.epilog)

        if self._line_numbers:
            line_number = self.starting_line_number
            for i in xrange(len(gcode)):
                gcode[i] = 'N%i %s' % (line_number, gcode[i])
                line_number += self.line_number_stride

        return '\n'.join(gcode)

    def write_to_file(self, filename):
        f = open(filename, 'w')
        try:
            f.write(self.to_string())
        finally:
            f.close()
