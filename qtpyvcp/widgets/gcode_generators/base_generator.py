from qtpy.QtCore import Property

class BaseGenerator(object):
    def __init__(self):
        self.wcs_ = ''
        self.speed_ = 0.
        self.feed_ = 0.
        self.z_feed_ = 0.
        self.z_clear_ = 0.
        self.tool_ = 0
        self.coolant_ = ''
        self.unit_ = 'G20'

    @Property(str)
    def wcs(self):
        return self.wcs_

    @wcs.setter
    def wcs(self, value):
        self.wcs_ = value

    @Property(float)
    def speed(self):
        return self.speed_

    @speed.setter
    def speed(self, value):
        self.speed_ = value

    @Property(float)
    def feed(self):
        return self.feed_

    @feed.setter
    def feed(self, value):
        self.speed_ = value

    @Property(float)
    def z_feed(self):
        return self.z_feed_

    @z_feed.setter
    def z_feed(self, value):
        self.z_feed_ = value

    @Property(float)
    def z_clear(self):
        return self.z_clear_

    @z_clear.setter
    def z_clear(self, value):
        self.z_clear_ = value

    @Property(int)
    def tool(self):
        return self.tool_

    @tool.setter
    def tool(self, value):
        self.tool_ = value

    @Property(str)
    def coolant(self):
        return self.coolant_

    @coolant.setter
    def coolant(self, value):
        self.coolant_ = value

    @Property(str)
    def unit(self):
        return self.unit_

    @unit.setter
    def unit(self, value):
        self.unit_ = value

    def preamble(self):
        preamble = ['G90 G94 G17 G91.1\n',
                    '%s\n' % self.unit_,
                    'G53 G0 Z0\n',
                    'T%i M6 G43\n' % self.tool_,
                    'S%.4f\n' % abs(self.speed_)]

        if self.coolant_:
            preamble.append(self.coolant_ + '\n')

        if self.speed_ < 0:
            preamble.append("M4\n")
        else:
            preamble.append("M3\n")


        preamble.append('%s\n' % self.wcs_)
        preamble.append('F%.4f\n' % self.feed_)
        preamble.append('G0 Z%.4f\n' % self.z_clear_)

        return preamble

    def epilog(self):
        output = []
        if self.coolant_:
            output.append('M9\n')
        output.append('G53 G0 Z0\nM30\n%')
        return output
