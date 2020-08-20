from __future__ import division
import math

from math import ceil
from base_generator import BaseGenerator
from gcode import GCode, Drill


class Pocket(BaseGenerator):
    def __init__(self):
        super(Pocket, self).__init__()
        self.x_center = 0.
        self.y_center = 0.
        self.step_down = 0.
        self.step_over = 0.
        self.tool_diameter = 0.

    def circle(self, center_xy, diameter):
        pocket_radius = diameter / 2
        tool_radius = self.tool_diameter / 2
        cut_radius = pocket_radius - tool_radius
        step_over = self.tool_diameter * self.step_over / 100

        step_over, num_step_overs = self.num_steps(pocket_radius - tool_radius, step_over)
        step_down, num_step_downs = self.num_steps(self.z_end - self.z_start, self.step_down)
        ramp, num_ramps = self.num_steps(step_down, (self.tool_diameter * 0.94) * math.tan(math.radians(4)))

        gcode = []
        gcode.append('G0 X%.4f Y%.4f' % center_xy)
        gcode.append('G0 Z%.4f' % self.z_start)

        if self.tool_diameter > diameter:
            print 'tool too large'
            exit(-1)
        elif self.tool_diameter == diameter:
            gcode.append('G98 G83 R%.4f Z%.4f Q%.4f F%.4f' % (self.z_start, self.z_end, 0.1, self.z_feed))
            return gcode
        elif pocket_radius <= 2 * self.tool_diameter:
            return self.bore(center_xy, diameter)

        z = self.z_start
        for i in xrange(num_step_downs):
            for _ in range(num_ramps):
                if self.tool_diameter < diameter:
                    print pocket_radius / 2
                    gcode.append('G91 G3 Z%.4f I%.4f' % (-ramp, min(0.95 * tool_radius, (0.95 * (cut_radius / 2)))))
                else:
                    exit(-1)
            scale = 1
            cycle = 1
            gcode.append('G90 G1 Z%4f' % (z - (num_ramps * ramp)))
            gcode.append('G3 X%.4f I%.4f' % (center_xy[0] + step_over, step_over / 2))
            z -= step_down
            while cycle < num_step_overs:
                gcode.append('G3 X%.4f I-%.4f' % (center_xy[0] - (cycle * step_over), (scale * step_over)))
                cycle += 1
                scale += 0.5
                gcode.append('G3 X%.4f I%.4f' % (center_xy[0] + (cycle * step_over), (scale * step_over)))
                scale += 0.5
#
            gcode.append('G3 I-%.4f' % (scale * step_over))
            gcode.append('G0 X%.4f Y%4f' % center_xy)

        return gcode

    def bore(self, center_xy, bore_diameter, ramp_angle=2):
        bore_radius = bore_diameter / 2
        tool_radius = self.tool_diameter / 2
        bore_depth = self.z_end - self.z_start
        ramp = self.tool_diameter * math.tan(math.radians(2 * ramp_angle))
        ramp, num_ramps = self.num_steps(bore_depth, ramp)

        gcode = []
        gcode.append('G0 X%.4f Y%.4f' % center_xy)
        gcode.append('G0 Z%.4f' % self.z_start)
        gcode.append('G1 X%.4f' % (center_xy[0] - bore_radius))

        for i in xrange(1, num_ramps + 1):
            gcode.append('G3 Z-%.4f I%.4f F%.4f' % (ramp * i, bore_radius - tool_radius, self.z_feed))

        return gcode


class Pocketing:
    def __init__(self, gcode):
        self.gcode = gcode
        self.zstart = 0.
        self.zend = 0.
        self.step_over = 0.
        self.step_down = 0.
        self.zfeed = 0.
        self.zclear = 0.
        self.retract = 0.

    def circle(self, center_xy=(0., 0.), pocket_diameter=0., tool_diameter=0.):
        zstart = self.zstart + self.retract
        step_down = self.step_down + self.retract

        self.gcode.rapid(x=center_xy[0], y=center_xy[1])
        self.gcode.rapid(z=zstart)

        if tool_diameter > pocket_diameter:
            raise ValueError('The tool is too large to create a pocket. Tool diameter %.2f, Pocket Diameter % .2f' %
                             (tool_diameter, pocket_diameter))

        if tool_diameter == pocket_diameter:
            Drill(self.gcode).peck(z=self.zend, r=zstart, f=self.zfeed, q=0.1)
        elif tool_diameter < pocket_diameter <= 2 * tool_diameter:
            self.gcode.helix(z_start=zstart, z_end=self.zend, diameter=pocket_diameter - tool_diameter)
        else:
            prev_z = curr_z = zstart
            while curr_z > self.zend:
                curr_z -= step_down
                if curr_z < self.zend:
                    curr_z = self.zend
                self.gcode.helix(z_start=prev_z, z_end=curr_z, diameter=self.step_over)
                self.gcode.spiral(x=center_xy[0], diameter=pocket_diameter - tool_diameter, step_over=self.step_over)
                self.gcode.rapid(z=self.zclear)
                self.gcode.rapid(x=center_xy[0], y=center_xy[1])
                prev_z = curr_z + self.retract
                self.gcode.linear(z=prev_z)

if __name__ == "__main__":
    gcode = GCode()
    gcode.set_wcs('G55')
    gcode.tool_change(4)
    gcode.set_feed(60)
    gcode.spindle_on(12000)
    gcode.rapid(z=0, wcs='G53')
    gcode.rapid(x=0, y=0)
    gcode.rapid(z=0.1)
    pocket = Pocketing(gcode)
    pocket.zstart = 0.0
    pocket.zend = -0.25
    pocket.zclear = 0.1
    pocket.retract = 0.02
    pocket.step_over = 0.125
    pocket.step_down = 0.125
    pocket.zfeed = 13
    pocket.circle(center_xy=(0, 0), pocket_diameter=0.5, tool_diameter=0.25)

    print gcode.to_string()
    gcode.write_to_file('/tmp/pocket.ngc')
