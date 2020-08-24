from drill_circle import DrillCircle, WCSComboBox, DrillTypeComboBox, SpindleDirectionComboBox, CoolantComboBox, \
    ToolNumberLineEdit

from qtpyvcp.widgets.qtdesigner import _DesignerPlugin

class DrillCirclePlugin(_DesignerPlugin):
    def pluginClass(self):
        return DrillCircle

class WCSComboBoxPlugin(_DesignerPlugin):
    def pluginClass(self):
        return WCSComboBox

class DrillTypeComboBoxPlugin(_DesignerPlugin):
    def pluginClass(self):
        return DrillTypeComboBox

class CoolantComboBoxPlugin(_DesignerPlugin):
    def pluginClass(self):
        return CoolantComboBox

class SpindleDirectionComboBoxPlugin(_DesignerPlugin):
    def pluginClass(self):
        return SpindleDirectionComboBox

class ToolNumberLineEditPlugin(_DesignerPlugin):
    def pluginClass(self):
        return ToolNumberLineEdit
