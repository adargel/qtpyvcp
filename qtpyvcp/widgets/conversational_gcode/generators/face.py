from __future__ import division
from base_generator import BaseGenerator

from math import ceil


class GCode(object):
    def __init__(self, starting_line_number=10, stride=5):
        self.gcode = []
        self.stride = stride
        self.line_number = starting_line_number

    def append(self, value):
        self.gcode.append('N%i %s' % (self.get_next_line_number_(), value))
        return self

    def to_string(self):
        return '\n'.join(self.gcode)

    def write_to_file(self, file_name):
        f = open(file_name, 'w')
        try:
            f.write(self.to_string())
        finally:
            f.close()

    def get_next_line_number_(self):
        line_number = self.line_number
        self.line_number += self.stride
        return line_number


class Face(BaseGenerator):
    def __init__(self):
        super(Face, self).__init__()
        self.x_start = 0.
        self.y_start = 0.
        self.x_end = 0.
        self.y_end = 0.
        self.step_over = 0.
        self.step_down = 0.
        self.lead_in = 0.1
        self.lead_out = 0.1
        self.tool_diameter = 0.
        self.vertical_lead_in_radius = self.vertical_lead_out_radius = 0.2

    def face(self):
        lead_in = lead_out = self.tool_diameter * 0.1
        tool_radius = self.tool_diameter / 2

        y_dist = abs(self.y_end - self.y_start)
        num_step_overs = abs(int(ceil(y_dist / self.step_over)))
        step_over = abs(y_dist / num_step_overs)

        z_dist = abs(self.z_end - self.z_start)
        num_step_downs = abs(int(ceil(z_dist / self.step_down)))
        step_down = abs(z_dist / num_step_downs)

        x_start = self.x_start - tool_radius - lead_in
        x_end = self.x_end + tool_radius + lead_out
        y_start = self.y_start + tool_radius - step_over
        y_end = self.y_end - tool_radius + step_over
        z_start = (self.z_start + lead_in)

        gcode = GCode()
        gcode.append(self.preamble())
        gcode.append('G0 X%.3f Y%.3f' % (x_start, y_start))
        gcode.append('G0 Z%.3f' % z_start)
        gcode.append('G1 Z%.3f' % (z_start - step_down))
        gcode.append('G18 G2 X%.3f Z%.3f I0.2 K0.' % (x_start + 0.2, -step_down))

        x = self.x_end
        y = y_start
        z = -step_down
        for i in xrange(num_step_downs):
            z -= step_down
            gcode.append('G1 X%.3f F%.4f' % (x, self.feed))
            for j in xrange(num_step_overs - 1):
                y -= step_over
                if x == self.x_end:
                    gcode.append('G17 %s Y%.3f I0 J-%.4f' % ('G2' if (i % 2) == 0 else 'G3', y, step_over / 2))
                    x = self.x_start
                else:
                    gcode.append('G17 %s Y%.3f I0 J-%.4f' % ('G3' if (i % 2) == 0 else 'G2', y, step_over / 2))
                    x = self.x_end
                gcode.append('G1 X%.4f' % x)

            if i == (num_step_downs - 1):
                if x == self.x_end:
                    gcode.append('G18 G2 X%.3f Z%.3f I0 K0.2' % (self.x_end + 0.2, z + 0.2))
                else:
                    gcode.append('G18 G3 X%.3f Z%.3f I0 K0.2' % (self.x_start - 0.2, z + 0.2))
                break

            if x == self.x_end:
                gcode.append('G1 X%.4f Y%.4f' % (x_end, y_end))
                x = self.x_start
                y = y_end
            else:
                gcode.append('G1 X%.4f Y%.4f' % (x_start, y_start))
                x = self.x_end
                y = y_start

            gcode.append('G1 Z%.4f F%.4f' % (z, self.z_feed))
            step_over = -step_over

        gcode.append(self.epilog())

        return gcode

if __name__ == "__main__":
    f = Face()
    f.unit = 'G20'
    f.feed = 250
    f.speed = 1200
    f.y_start = 0
    f.y_end = -5
    f.x_start = 0
    f.x_end = 8
    f.z_clear = 1
    f.z_start = 0.
    f.z_end = -0.06
    f.z_feed = 4
    f.step_down = .04
    f.tool_diameter = 2
    f.step_over = 1.9
    f.wcs = 'G55'
    f.tool = 101

    output = f.face()
    print output.to_string()
    output.write_to_file('/tmp/face.ngc')
