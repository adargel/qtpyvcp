from __future__ import division
import math

from base_generator import BaseGenerator
from gcode import GCode


class Bore(BaseGenerator):
    def __init__(self):
        super(Bore, self).__init__()
        self.x_center = 0.
        self.y_center = 0.
        self.bore_diameter = 0.
        self.tool_diameter = 0.
        self.step_down = 0.
        self.step_over = 0.

    def bore(self, center_xy, bore_diameter, ramp_angle=2):
        bore_radius = bore_diameter / 2
        tool_radius = self.tool_diameter / 2
        bore_depth = self.z_end - self.z_start
        ramp = self.tool_diameter * math.tan(math.radians(2 * ramp_angle))
        ramp, num_ramps = self.num_steps(bore_depth, ramp)

        gcode = GCode()
        gcode.append(self.preamble())
        gcode.append('G0 X%.4f Y%.4f' % center_xy)
        gcode.append('G0 Z%.4f' % self.z_start)

        gcode.append('G1 X%.4f' % (center_xy[0] - bore_radius))
        for i in xrange(1, num_ramps + 1):
            gcode.append('G3 Z-%.4f I%.4f F%.4f' % (ramp * i, bore_radius - tool_radius, self.z_feed))

        gcode.append(self.epilog())

        return gcode



if __name__ == "__main__":
    def write_to_file(file_name, data):
        f = open(file_name, 'w')
        try:
            f.write(data)
        finally:
            f.close()


    f = Bore()
    f.unit = 'G20'
    f.wcs = 'G55'
    f.tool = 4
    f.feed = 60
    f.speed = 240
    f.z_clear = 1
    f.z_start = 0.
    f.z_end = -0.25
    f.z_feed = 4
    f.step_down = 0.1
    f.step_over = 52
    f.tool_diameter = 0.25
    f.x_center = 2.5
    f.y_center = 2.5
    f.bore_diameter = 1
    gcode = f.bore()
    print gcode
    write_to_file('/tmp/bore.ngc', gcode)
