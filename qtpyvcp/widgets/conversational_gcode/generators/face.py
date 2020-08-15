from __future__ import division
from base_generator import BaseGenerator

from math import ceil


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

    def face(self):
        tool_radius = self.tool_diameter / 2

        part_width = abs(self.y_end - self.y_start)
        num_y_steps = (abs(int(ceil(part_width / self.step_over))))
        step_over = part_width / num_y_steps

        part_depth = abs(self.z_end - self.z_start)
        num_z_steps = (abs(int(ceil(part_depth / self.step_down))))
        step_down = part_depth / num_z_steps

        x_start = self.x_start - tool_radius - self.lead_in
        x_end = self.x_end + tool_radius + self.lead_out
        y_start = self.y_start + tool_radius - step_over
        z_start = self.z_start - step_down

        output = [
            self.preamble(),
            'G0 X%.4f Y%.4f' % (x_start, y_start),
            'G0 Z%.4f' % self.z_clear,
        ]
#
        x = x_end
        y = y_start
        z = z_start
        for i in range(num_z_steps):
            output.append('G1 Z%.4f' % z)
            output.append('G1 X%.4f' % x)
            x = x_start if x == x_end else x_end
            for j in range(0, num_y_steps - 1):
                y -= step_over
                output.append('G1 Y%.4f' % y)
                output.append('G1 X%.4f' % x)
                x = x_start if x == x_end else x_end
            z -= step_down
            step_over = -step_over

        output.append(self.epilog())
        return '\n'.join(output)


if __name__ == "__main__":
    def write_to_file(file_name, data):
        f = open(file_name, 'w')
        try:
            f.write(data)
        finally:
            f.close()

    f = Face()
    f.feed = 400
    f.speed = 240
    f.y_start = 0
    f.y_end = -2
    f.x_start = 0
    f.x_end = 3
    f.step_over = 0.25
    f.z_clear = 0.1
    f.z_start = 0.
    f.z_end = -0.4
    f.step_down = 0.1
    f.tool_diameter = 0.5
    f.wcs = 'G55'
    f.tool = 7
    print f.face()
    write_to_file('/tmp/face.ngc', f.face())
