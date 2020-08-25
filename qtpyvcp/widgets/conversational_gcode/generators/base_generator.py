import math

class BaseGenerator(object):
    def __init__(self):
        self.wcs = ''
        self.speed = 0.
        self.spindle_dir = 'cw'
        self.feed = 0.
        self.z_feed = 0.
        self.z_clear = 0.
        self.z_start = 0.
        self.z_end = 0.
        self.retract = 0.
        self.tool = 0
        self.coolant = ''
        self.unit = 'G20'
        self.step_down = 0.

    def start_op(self):
        output = [
            'T%i M6 G43',
            'S%.4f' % self.speed,
            'M4' if self.spindle_dir.lower() == 'ccw' else 'M3',
            'G0 X%.4f Y%.4f' % (self.x_start, self.y_start),
            self.wcs.upper()]

        if self.coolant.lower() == 'mist':
            output.append('M7')
        elif self.coolant.lower() == 'flood':
            output.append('M8')

        output.append('G0 Z%.4f' % (self.z_start + self.retract))

        return output

    def end_op(self):
        return ['G53 G0 Z%.4f' % self.z_clear]

    @property
    def z_feed_start(self):
        return self.z_start + self.retract

    def preamble(self):
        output = [
            'G90 G94 G17 G91.1',
            self.wcs,
            self.unit,
            'G53 G0 Z0',
            'T%i M6 G43' % self.tool,
            'S%.4f' % abs(self.speed)
        ]

        output.append('M4') if self.speed < 0 else output.append('M3')

        if self.coolant:
            output.append(self.coolant)

        output.append('F%.4f' % self.feed)

        return output

    def epilog(self):
        output = []
        if self.coolant:
            output.append('M9')
        output.append('G53 G0 Z0')
        output.append('M30')
        output.append('%')

        return output

    @staticmethod
    def arc(x=None, y=None, z=None, i=None, f=None, dir='cw', mode=None):
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

        return output

    def helix(self, z_start=0., z_end=0., diameter=0., angle=2, f=None, dir='cw'):
        output = []
        ramp = math.pi * diameter * math.tan(math.radians(angle))
        radius = (diameter / 2)
        depth = abs(z_end - z_start)

        next_depth = 0
        while next_depth < depth:
            next_depth += ramp
            if next_depth > depth:
                next_depth = depth
            output.extend(self.arc(z=z_start-next_depth, i=radius, f=f, dir=dir))

        return output

    def spiral(self, x=0., diameter=0., step_over=0., f=None, dir='cw'):
        output = []
        radius = (diameter / 2)
        num_steps = abs(int(math.ceil(radius / step_over)))
        step_over = radius / num_steps

        cycle = 0
        scale = 0.5
        next_step = 0
        while next_step < radius:
            cycle += 1
            next_step += step_over
            output.extend(self.arc(x=x + next_step, i=(step_over * scale), f=f, dir=dir))
            scale += 0.5
            output.extend(self.arc(x=x - next_step, i=-(step_over * scale), f=f, dir=dir))
            scale += 0.5

        output.extend(self.arc(x=x+radius, i=radius, f=f, dir=dir))

    def write_to_file(self, file_name, output, mode='w'):
        f = open(file_name, mode)
        try:
            if mode == 'w':
                f.write('\n'.join(self.preamble()))
                f.write('\n')

            f.write('\n'.join(output))
        finally:
            f.close()

    @staticmethod
    def normalize_step(size, step):
        steps = int(abs(math.ceil(size / step)))
        if steps == 0:
            return 0, steps
        return abs(size / steps), steps

