import os

from generators.drill import Drill

from qtpy import uic
from qtpy.QtCore import Property
from qtpy.QtGui import QDoubleValidator
from qtpy.QtGui import QIntValidator
from qtpy.QtWidgets import QWidget, QComboBox, QLineEdit, QHBoxLayout

from qtpyvcp.plugins import getPlugin
from qtpyvcp.utilities.logger import getLogger
from qtpyvcp.actions.program_actions import load as loadProgram
from qtpyvcp.widgets.conversational_gcode.generators.gcode import GCode

LOG = getLogger(__name__)
TOOLTABLE = getPlugin('tooltable')


class WCSComboBox(QComboBox):
    def __init__(self, parent=None):
        super(WCSComboBox, self).__init__(parent)
        self.addItem("G54")
        self.addItem("G55")
        self.addItem("G56")
        self.addItem("G57")
        self.addItem("G58")
        self.addItem("G59")
        self.addItem("G59.1")
        self.addItem("G59.2")
        self.addItem("G59.3")

    def get_wcs(self):
        return self.currentText()


class IntLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(IntLineEdit, self).__init__(parent)
        self._default_value = 0
        self.setValidator(QIntValidator())

    @Property(int)
    def default_value(self):
        return self._default_value

    @default_value.setter
    def default_value(self, value):
        self._default_value = value

    @Property(int)
    def bottom(self):
        return self.validator().bottom()

    @bottom.setter
    def bottom(self, value):
        self.validator().setBottom(value)

    @Property(int)
    def top(self):
        return self.validator().top()

    @top.setter
    def top(self, value):
        self.validator().setTop(value)

    def focusOutEvent(self, ev):
        if self.text().strip() == '' or self.validator().validate(self.text(), 0) == QIntValidator.Invalid:
            self.setText("%i" % self._default_value)

        super(IntLineEdit, self).focusOutEvent(ev)


class FloatLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(FloatLineEdit, self).__init__(parent)
        self._default_value = 0.
        self.setValidator(QDoubleValidator())
        self.validator().setNotation(QDoubleValidator.StandardNotation)

    @Property(float)
    def default_value(self):
        return self._default_value

    @default_value.setter
    def default_value(self, value):
        self._default_value = value

    @Property(float)
    def bottom(self):
        return self.validator().bottom()

    @bottom.setter
    def bottom(self, value):
        self.validator().setBottom(value)

    @Property(float)
    def top(self):
        return self.validator().top()

    @top.setter
    def top(self, value):
        self.validator().setTop(value)

    def focusOutEvent(self, ev):
        if self.text().strip() == '':
            self.setText("%.4f" % self._default_value)

        super(FloatLineEdit, self).focusOutEvent(ev)


class SetupPanel(QWidget):
    def __init__(self, parent=None):
        super(SetupPanel, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'setup_panel.ui'), self)

        self.wcs.addItem("G54")
        self.wcs.addItem("G55")
        self.wcs.addItem("G56")
        self.wcs.addItem("G57")
        self.wcs.addItem("G58")
        self.wcs.addItem("G59")
        self.wcs.addItem("G59.1")
        self.wcs.addItem("G59.2")
        self.wcs.addItem("G59.3")

        self.program_units.addItem("IN")
        self.program_units.addItem("MM")

        self.drill_type.addItem("DRILL")
        self.drill_type.addItem("SPOT")
        self.drill_type.addItem("BREAK")
        self.drill_type.addItem("DWELL")
        self.drill_type.addItem("PECK")
        self.drill_type.addItem("TAP")
        self.drill_type.addItem("RIGID TAP")

        self.spindle_direction.addItem("CW")
        self.spindle_direction.addItem("CCW")

        self.coolant_setting.addItem("OFF")
        self.coolant_setting.addItem("MIST")
        self.coolant_setting.addItem("FLOOD")

        self._disable_buttons()
        self.drill_type_param_value.setVisible(False)
        self.drill_type_param_label.setVisible(False)

    def on_drill_type_index_changed(self, i):
        if self.drill_type.currentText() == 'DWELL':
            self.drill_type_param_label.setText("DWELL TIME (SEC.)")
            self.drill_type_param_value.setText("0.00")
            self.drill_type_param_value.setVisible(True)
            self.drill_type_param_label.setVisible(True)
        elif self.drill_type.currentText() == 'PECK':
            self.drill_type_param_label.setText("PECK DEPTH")
            self.drill_type_param_value.setText("0.0000")
            self.drill_type_param_value.setVisible(True)
            self.drill_type_param_label.setVisible(True)
        elif self.drill_type.currentText() == 'BREAK':
            self.drill_type_param_label.setText("BREAK DEPTH")
            self.drill_type_param_value.setText("0.0000")
            self.drill_type_param_value.setVisible(True)
            self.drill_type_param_label.setVisible(True)
        elif self.drill_type.currentText() in ['TAP', 'RIGID TAP']:
            self.z_feed_rate.setEnabled(False)
            self.drill_type_param_label.setText("PITCH")
            self.drill_type_param_value.setText("0.00")
            self.drill_type_param_value.setVisible(True)
            self.drill_type_param_label.setVisible(True)
        else:
            self.drill_type_param_value.setVisible(False)
            self.drill_type_param_label.setVisible(False)

    def on_tool_number_editingFinished(self):
        tool_table = TOOLTABLE.getToolTable()
        tool_number = int(self.tool_number.text())
        try:
            desc = tool_table[tool_number]["R"]
            self.tool_description.setText((desc[:45] + '...') if len(desc) > 45 else desc)
            self.tool_description.setToolTip(desc)
            if tool_number > 0:
                self._enable_buttons()
            else:
                self._disable_buttons()
        except KeyError:
            self.tool_description.setText('TOOL NOT IN TOOL TABLE')
            self.tool_description.setToolTip('TOOL NOT IN TOOL TABLE')
            self.post_to_file.setEnabled(False)

    def _enable_buttons(self):
        self.post_to_file.setEnabled(True)
        self.append_to_file.setEnabled(True)

    def _disable_buttons(self):
        self.post_to_file.setEnabled(False)
        self.append_to_file.setEnabled(False)


class CircleDrill(QWidget):
    def __init__(self, setup_panel, parent=None):
        super(CircleDrill, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'circle_drill.ui'), self)

        self._drill = Drill()
        self._setup_panel = setup_panel

    def on_post_to_file_clicked(self):
        self._setup_panel.setup_gcode(self._drill)
        self._drill.retract = float(self.retract.text())
        self._drill.z_start = float(self.hole_start.text())
        self._drill.z_end = float(self.hole_end.text())

        self._drill.bolt_hole_circle(num_holes=int(self.num_holes.text()),
                                     circle_diam=float(self.diameter.text()),
                                     circle_center=(float(self.center_x.text()), float(self.center_y.text())),
                                     start_angle=float(self.start_angle.text()))

        output = []
        if self._setup_panel.drill_type.currentText() == "DRILL":
            output.extend(self._drill.drill())

        self._drill.write_to_file('/tmp/testing.ngc', output)
        loadProgram('/tmp/testing.ngc')

    def on_append_to_file_clicked(self):
        print 'append'


class DrillGenerator(QWidget):
    def __init__(self, parent=None):
        super(DrillGenerator, self).__init__(parent)

        self.setup_panel = SetupPanel()
        self.circle_drill = CircleDrill(self.setup_panel)

        hbox = QHBoxLayout()
        hbox.addWidget(self.circle_drill)
        hbox.addWidget(self.setup_panel)
        self.setLayout(hbox)

        self.setup_panel.post_to_file.clicked.connect(self.write_program)

    def write_program(self):
        setup = self.setup_panel
        drill_setup = self.circle_drill

        gcode = GCode()
        drill = Drill()

        gcode.set_unit(setup.program_units.currentText())
        gcode.rapid(wcs='G53', z=0)
        gcode.tool_change(int(setup.tool_number.text()))
        gcode.spindle_on(float(setup.spindle_rpm.text()), setup.spindle_direction.currentText())
        gcode.set_wcs(setup.wcs.currentText())
        gcode.set_coolant(setup.coolant_setting.currentText())

        drill.zfeed = float(setup.z_feed_rate.text())
        drill.zstart = float(drill_setup.hole_start.text())
        drill.zend = float(drill_setup.hole_end.text())
        drill.retract = float(drill_setup.retract.text())

        drill.add_hole_circle(num_holes=int(drill_setup.num_holes.text()),
                              circle_diam=float(drill_setup.diameter.text()),
                              circle_center=(float(drill_setup.center_x.text()), float(drill_setup.center_y.text())),
                              start_angle=float(drill_setup.start_angle.text()))

        gcode.add(drill.drill())

        print gcode.to_string()

        gcode.write_to_file('/tmp/testing.ngc')
        loadProgram('/tmp/testing.ngc')
