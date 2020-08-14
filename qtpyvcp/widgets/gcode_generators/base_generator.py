class BaseGenerator(object):
    def __init__(self):
        self.wcs = ''
        self.speed = 0.
        self.feed = 0.
        self.z_feed = 0.
        self.z_clear = 0.
        self.z_start = 0.
        self.z_end = 0.
        self.tool = 0
        self.coolant = ''
        self.unit = 'G20'

    def preamble(self):
        preamble = ['G90 G94 G17 G91.1\n',
                    '%s\n' % self.unit,
                    'G53 G0 Z0\n',
                    'T%i M6 G43\n' % self.tool,
                    'S%.4f\n' % abs(self.speed)]

        preamble.append('M4\n') if self.speed < 0 else preamble.append('M3\n')

        if self.coolant:
            preamble.append(self.coolant + '\n')

        preamble.append('%s\n' % self.wcs)
        preamble.append('F%.4f\n' % self.feed)
        preamble.append('G0 Z%.4f\n' % self.z_clear)

        return preamble

    def epilog(self):
        output = []
        if self.coolant:
            output.append('M9\n')
        output.append('G53 G0 Z0\nM30\n%')
        return output
