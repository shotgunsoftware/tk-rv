from PySide.QtCore import QFile
from PySide.QtGui import QDoubleSpinBox, QDial, QCheckBox
from PySide.QtUiTools import QUiLoader
import types
import os
import math
import rv
import rv.qtutils

import sg_test # need to get at the module itself

class PySideDockTest(rv.rvtypes.MinorMode):
    "A python mode example that uses PySide"

    def checkBoxPressed(self, checkbox, prop):
        def F():
            try:
                if checkbox.isChecked():
                    if self.rvSessionQObject is not None:
                        self.rvSessionQObject.setWindowOpacity(1.0)
                    rv.commands.setIntProperty(prop, [1], True)
                else:
                    if self.rvSessionQObject is not None:
                        self.rvSessionQObject.setWindowOpacity(0.5)
                    rv.commands.setIntProperty(prop, [0], True)
            except:
                pass
        return F


    def dialChanged(self, index, last, spins, prop):
        def F(value):
            diff = float(value - last[index])
            if diff < -180:
                diff = value - last[index] + 360  
            elif diff > 180:
                diff = value - last[index] - 360  
            diff /= 360.0
            last[index] = float(value)
            try:
                p = rv.commands.getFloatProperty(prop, 0, 1231231)
                p[0] += diff
                if p[0] > spins[index].maximum() :
                    p[0] = spins[index].maximum()
                if p[0] <  spins[index].minimum()  :
                    p[0] = spins[index].minimum()
                spins[index].setValue(p[0])
                rv.commands.setFloatProperty(prop, p, True)
            except:
                pass
        return F

    def spinChanged(self, index, spins, prop):
        def F(value):
            try:
                rv.commands.setFloatProperty(prop, [p], True)
            except:
                pass

        def F():
            try:
                p = spins[index].value()
                rv.commands.setFloatProperty(prop, [p], True)
            except:
                pass

        return F

    def findSet(self, typeObj, names):
        array = []
        for n in names:
            array.append(self.dialog.findChild(typeObj, n))
            if array[-1] == None:
                print "Can't find", n
        return array

    def hookup(self, checkbox, spins, dials, prop, last):
        checkbox.released.connect(self.checkBoxPressed(checkbox, "%s.node.active"%prop))
        for i in range(0,3):
            dial = dials[i]
            spin = spins[i]
            propName = "%s.warp.k%d" % (prop,i+1)
            dial.valueChanged.connect(self.dialChanged(i, last, spins, propName))
            spin.valueChanged.connect(self.spinChanged(i, spins, propName))
            last[i] = dial.value()


    def __init__(self):
        rv.rvtypes.MinorMode.__init__(self)
        self.init("pyside_example", None, None)

        self.loader = QUiLoader()
        #uifile = QFile(os.path.join(self.supportPath(pyside_example, "pyside_example"), "control.ui"))
        uifile = QFile('/Users/stewartb/git/tk-rv/python/tk_rv/sg-test.ui')
        uifile.open(QFile.ReadOnly)
        self.dialog = self.loader.load(uifile)
        uifile.close()

        #self.enableCheckBox  = self.dialog.findChild(QCheckBox, "enableCheckBox")

        #
        # To retrieve the current RV session window and
        # use it as a Qt QMainWindow, we do the following:
        self.rvSessionQObject = rv.qtutils.sessionWindow()

        # have to hold refs here so they don't get deleted
        #self.radialDistortDials = self.findSet(QDial, ["k1Dial", "k2Dial", "k3Dial"])

        #self.radialDistortSpins = self.findSet(QDoubleSpinBox, ["k1SpinBox", "k2SpinBox", "k3SpinBox"])

        #self.lastRadialDistort = [0,0,0]

        #self.hookup(self.enableCheckBox, self.radialDistortSpins, self.radialDistortDials, "#RVLensWarp", self.lastRadialDistort)


    def activate(self):
        rv.rvtypes.MinorMode.activate(self)
        self.dialog.show()

    def deactivate(self):
        rv.rvtypes.MinorMode.deactivate(self)
        self.dialog.hide()

def createMode():
    "Required to initialize the module. RV will call this function to create your mode."
    return PySideDockTest()
