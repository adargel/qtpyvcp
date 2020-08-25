from __future__ import division
import math

class GCode(object):
    def __init__(self, starting_line_number=10, stride=5):
        self.output = []
        self.stride = stride
        self.line_number = starting_line_number
        self.preamble = ['G90 G94 G17 G91.1']
        self.epilog = ['G53 G0 Z0', 'M30', '%']

    def set_wcs(self, value):
        self.add([value.upper()])

    def set_unit(self, value):
        self.add('G20' if value.lower() == 'in' else 'G21')

    def set_feed(self, value):
        self.add('F%.4f' % value)

    def tool_change(self, value):
        self.add('T%i M6 G43' % value)

    def set_coolant(self, value):
        if value.lower() == 'mist':
            self.coolant_mist_on()
        elif value.lower() == 'flood':
            self.coolant_flood_on()

    def spindle_on(self, rpm, dir='cw'):
        self.add('S%.4f' % abs(rpm))
        self.add('M3' if dir.lower() == 'cw' else 'M4')

    def spindle_off(self):
        self.add('M5')

    def coolant_mist_on(self):
        self.add('M7')

    def coolant_flood_on(self):
        self.add('M8')

    def coolant_off(self):
        self.add('M9')

    def linear(self, x=None, y=None, z=None, f=None, wcs=None):
        self.move_(x, y, z, f, wcs, motion='G0')

    def rapid(self, x=None, y=None, z=None, f=None, wcs=None):
        self.move_(x, y, z, f, wcs, motion='G0')

    def arc(self, x=None, y=None, z=None, i=None, f=None, dir='cw', mode=None):
        output = []
        if mode:
            output.append(mode)

        output.append('G2' if dir.lower() == 'cw' else 'G3')

        if x is not None:
            output.append('X%.4f' % x)
        if y is not None:
            output.append('Y%.4f' % y)
        if z is not None:
            output.append('Z%.4f' % z)
        if i is not None:
            output.append('I%.4f' % i)
        if f is not None:
            output.append('F%.4f' % f)

        self.add(' '.join(output))

    def helix(self, z_start=0., z_end=0., diameter=0., angle=2, f=None, dir='cw'):
        ramp = math.pi * diameter * math.tan(math.radians(angle))
        radius = (diameter / 2)
        depth = abs(z_end - z_start)

        next_depth = 0
        while next_depth < depth:
            next_depth += ramp
            if next_depth > depth:
                next_depth = depth
            self.arc(z=z_start-next_depth, i=radius, f=f, dir=dir)

    def spiral(self, x=0., diameter=0., step_over=0., f=None, dir='cw'):
        radius = (diameter / 2)
        num_steps = abs(int(math.ceil(radius / step_over)))
        step_over = radius / num_steps

        cycle = 0
        scale = 0.5
        next_step = 0
        while next_step < radius:
            cycle += 1
            next_step += step_over
            self.arc(x=x + next_step, i=(step_over * scale), f=f, dir=dir)
            scale += 0.5
            self.arc(x=x - next_step, i=-(step_over * scale), f=f, dir=dir)
            scale += 0.5

        self.arc(x=x+radius, i=radius, f=f, dir=dir)

    def add(self, value):
        if isinstance(value, str):
            self.output.append(value)
        else:
            self.output.extend(value)

    def to_string(self):
        output = []
        output.extend(self.preamble)
        output.extend(self.output)
        output.extend(self.epilog)

        numbered_output = []
        for line in output:
            numbered_output.append('N%i %s' % (self.get_next_line_number_(), line))

        return '\n'.join(numbered_output)

    def write_to_file(self, file_name):
        f = open(file_name, 'w')
        try:
            f.write(self.to_string())
        finally:
            f.close()

    def move_(self, x=None, y=None, z=None, f=None, wcs=None, motion='G1'):
        output = [motion]
        if wcs is not None:
            output.append(wcs)
        if x is not None:
            output.append('X%.4f' % x)
        if y is not None:
            output.append('Y%.4f' % y)
        if z is not None:
            output.append('Z%.4f' % z)
        if f is not None:
            output.append('F%.4f' % f)

        self.add(' '.join(output))

    def get_next_line_number_(self):
        line_number = self.line_number
        self.line_number += self.stride
        return line_number


class Drill(object):
    def __init__(self, gcode):
        self.gcode = gcode
        self.holes = []
        self.zstart = 0.
        self.zend = 0.
        self.retract = 0.
        self.zfeed = 0.

    def drill(self):
        self._build_gcode('G98 G81 R%.4f Z%.4f F%.4f' % (self.zstart + self.retract, self.zend, self.zfeed))

    def dwell(self, p=0.1):
        self._build_gcode('G98 G82 R%.4f Z%.4f P%.4f F%.4f' % (self.zstart + self.retract, self.zend, p, self.zfeed))

    def peck(self, q=0.1):
        self._build_gcode('G98 G83 R%.4f Z%.4f Q%.4f F%.4f' % (self.zstart + self.retract, self.zend, q, self.zfeed))

    def chip_break(self, q=0.1):
        self._build_gcode('G98 G73 R%.4f Z%.4f Q%.4f F%.4f' % (self.zstart + self.retract, self.zend, q, self.zfeed))

    def tap(self, pitch=0., speed=0., dir='cw'):
        feed = abs(speed * pitch)
        self.gcode.add('S%.4f' % speed)
        cycle = 'G74' if dir == 'ccw' else 'G84'

        self._build_gcode('G98 %s R%.4f Z%.4f F%.4f' % (cycle, self.zstart + self.retract, self.zend, feed))

    def rigid_tap(self, pitch=0.):
        self._build_gcode('G33.1 Z%.4f K%.4f F%.4f' % (self.zend, pitch, self.zfeed))

    def add_hole(self, x=None, y=None):
        self.holes.append((x, y))

    def add_hole_circle(self, num_holes, circle_diam, circle_center, start_angle=0):
        curr_angle = start_angle
        angle_step = (360. / num_holes)

        for _ in range(0, num_holes):
            x = math.cos(math.radians(curr_angle)) * (circle_diam / 2.)
            y = math.sin(math.radians(curr_angle)) * (circle_diam / 2.)
            x += circle_center[0]
            y += circle_center[1]
            curr_angle += angle_step

            self.add_hole(x=x, y=y)

    def _build_gcode(self, cycle):
        self.gcode.rapid(x=self.holes[0][0], y=self.holes[0][1])
        self.gcode.rapid(z=self.zstart + self.retract)
        self.gcode.add(cycle)
        for hole in self.holes[1:]:
            self.gcode.add('X%.4f Y%.4f' % (hole[0], hole[1]))
        self.gcode.add('G80')


if __name__ == "__main__":
    gcode = GCode()
    gcode.set_wcs('G55')
    gcode.rapid(z=0, wcs='G53')
    gcode.tool_change(4)
    gcode.coolant_mist_on()
    gcode.set_feed(60)
    gcode.spindle_on(12000)
    gcode.rapid(x=3, y=3)
    gcode.rapid(z=0.1)
    gcode.helix(z_start=0.1, z_end=-0.25, diameter=0.4)
    gcode.spiral(x=3, diameter=2, step_over=0.3)
    gcode.rapid(z=1)
    gcode.rapid(x=3, y=3)
    gcode.rapid(z=-0.20)
    gcode.helix(z_start=-0.20, z_end=-0.5, diameter=0.4)
    gcode.spiral(x=3, diameter=2, step_over=0.3)
    print gcode.to_string()
    gcode.write_to_file('/tmp/ramp.ngc')
