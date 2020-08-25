from drill_circle import *
from qtpyvcp.widgets.qtdesigner import _DesignerPlugin

class IntLineEditPlugin(_DesignerPlugin):
    def pluginClass(self):
        return IntLineEdit

class FloatLineEditPlugin(_DesignerPlugin):
    def pluginClass(self):
        return FloatLineEdit

class DrillGeneratorPlugin(_DesignerPlugin):
    def pluginClass(self):
        return DrillGenerator
