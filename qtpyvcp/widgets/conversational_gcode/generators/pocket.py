from __future__ import division

from math import ceil
from base_generator import BaseGenerator


class Pocket(BaseGenerator):
    def __init__(self):
        super(Pocket, self).__init__()
        self.pocket_diameter = 0.
        self.x_center = 0.
        self.y_center = 0.
        self.step_down = 0.
        self.step_over = 0.
        self.tool_diameter = 0.

    def spiral(self):
        pocket_radius = self.pocket_diameter / 2
        tool_radius = self.tool_diameter / 2
        step_over = self.tool_diameter * self.step_over / 100

        num_circles = int(abs(ceil((pocket_radius - tool_radius) / step_over)))
        step_over = (pocket_radius - tool_radius) / num_circles

        z_depth = abs(self.z_end - self.z_start)
        num_z_steps = int(abs(ceil(z_depth / self.step_down)))
        step_down = z_depth / num_z_steps

        gcode = [
            self.preamble(),
            'G0 X%.4f Y%.4f' % (self.x_center, self.y_center),
            'G0 Z%.4f' % self.z_start
        ]

        z = self.z_start
        x = self.x_center
        for i in xrange(num_z_steps):
            spiral_step = step_down / 8
            z_spiral = z - spiral_step
            z -= step_down
            for _ in range(8):
                gcode.append('G3 X%.4f Z%.4f I%.4f' % (self.x_center, z_spiral, (tool_radius * 0.95 / 2)))
                z_spiral -= spiral_step
            scale = 1
            cycle = 1
            gcode.append('G3 X%.4f I%.4f' % (self.x_center + step_over, step_over / 2))
            while cycle < num_circles:
                gcode.append('G3 X%.4f I-%.4f' % (self.x_center - (cycle * step_over), (scale * step_over)))
                cycle += 1
                scale += 0.5
                gcode.append('G3 X%.4f I%.4f' % (self.x_center + (cycle * step_over), (scale * step_over)))
                scale += 0.5

            gcode.append('G3 I-%.4f' % (scale * step_over))

            gcode.append('G0 Z%4f' % self.z_start)
            gcode.append('G0 X%.4f Y%4f' % (self.x_center, self.y_center))

        gcode.append(self.epilog())
        return '\n'.join(gcode)


if __name__ == "__main__":
    def write_to_file(file_name, data):
        f = open(file_name, 'w')
        try:
            f.write(data)
        finally:
            f.close()

    f = Pocket()
    f.unit = 'G20'
    f.feed = 40
    f.speed = 240
    f.y_start = 4
    f.y_end = 0
    f.x_start = 0
    f.x_end = 8
    f.step_over = 95
    f.z_clear = 1
    f.z_start = 0.
    f.z_end = -0.25
    f.z_feed = 4
    f.step_down = .125
    f.tool_diameter = 0.25
    f.wcs = 'G55'
    f.tool = 4
    f.pocket_diameter = 2
    f.x_center = 0
    f.y_center = 0
    gcode = f.spiral()
    print gcode
    write_to_file('/tmp/pocket.ngc', gcode)

