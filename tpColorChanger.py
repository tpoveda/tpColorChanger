#! /usr/bin/python

"""
    File name: tpColorChanger.py
    Author: Tomas Poveda
    Description: Tool to change color of curve controls quickly
"""

try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance

import os
from functools import partial
import random

import maya.OpenMayaUI as OpenMayaUI
import maya.cmds as cmds

# ==== Control Colors
cControlColors = []
cControlColors.append((.467, .467, .467))
cControlColors.append((.000, .000, .000))
cControlColors.append((.247, .247, .247))
cControlColors.append((.498, .498, .498))
cControlColors.append((0.608, 0, 0.157))
cControlColors.append((0, 0.016, 0.373))
cControlColors.append((0, 0, 1))
cControlColors.append((0, 0.275, 0.094))
cControlColors.append((0.145, 0, 0.263))
cControlColors.append((0.78, 0, 0.78))
cControlColors.append((0.537, 0.278, 0.2))
cControlColors.append((0.243, 0.133, 0.122))
cControlColors.append((0.6, 0.145, 0))
cControlColors.append((1, 0, 0))
cControlColors.append((0, 1, 0))
cControlColors.append((0, 0.255, 0.6))
cControlColors.append((1, 1, 1))
cControlColors.append((1, 1, 0))
cControlColors.append((0.388, 0.863, 1))
cControlColors.append((0.263, 1, 0.635))
cControlColors.append((1, 0.686, 0.686))
cControlColors.append((0.89, 0.675, 0.475))
cControlColors.append((1, 1, 0.384))
cControlColors.append((0, 0.6, 0.325))
cControlColors.append((0.627, 0.412, 0.188))
cControlColors.append((0.62, 0.627, 0.188))
cControlColors.append((0.408, 0.627, 0.188))
cControlColors.append((0.188, 0.627, 0.365))
cControlColors.append((0.188, 0.627, 0.627))
cControlColors.append((0.188, 0.404, 0.627))
cControlColors.append((0.435, 0.188, 0.627))
cControlColors.append((0.627, 0.188, 0.404))

def _getMayaWindow():
    
    """
    Return the Maya main window widget as a Python object
    :return: Maya Window
    """

    ptr = OpenMayaUI.MQtUtil.mainWindow ()
    if ptr is not None:
        return wrapInstance (long (ptr), QMainWindow)

def tpUndo(fn):

    """
    tpRigLib simple undo wrapper. Use @tpUndo above the function to wrap it.
    @param fn: function to wrap
    @return wrapped function
    """

    def wrapper(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        try:
            ret = fn(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=True)
        return ret
    return wrapper
    
# -------------------------------------------------------------------------------------------------

class tpSplitter (QWidget, object):
    def __init__(self, text=None, shadow=True, color=(150, 150, 150)):

        """
        Basic standard splitter with optional text
        :param str text: Optional text to include as title in the splitter
        :param bool shadow: True if you want a shadow above the splitter
        :param tuple(int) color: Color of the slitter's text
        """

        super (tpSplitter, self).__init__ ()

        self.setMinimumHeight (2)
        self.setLayout (QHBoxLayout ())
        self.layout ().setContentsMargins (0, 0, 0, 0)
        self.layout ().setSpacing (0)
        self.layout ().setAlignment (Qt.AlignVCenter)

        firstLine = QFrame ()
        firstLine.setFrameStyle (QFrame.HLine)
        self.layout ().addWidget (firstLine)

        mainColor = 'rgba(%s, %s, %s, 255)' % color
        shadowColor = 'rgba(45, 45, 45, 255)'

        bottomBorder = ''
        if shadow:
            bottomBorder = 'border-bottom:1px solid %s;' % shadowColor

        styleSheet = "border:0px solid rgba(0,0,0,0); \
                      background-color: %s; \
                      max-height: 1px; \
                      %s" % (mainColor, bottomBorder)

        firstLine.setStyleSheet (styleSheet)

        if text is None:
            return

        firstLine.setMaximumWidth (5)

        font = QFont ()
        font.setBold (True)

        textWidth = QFontMetrics (font)
        width = textWidth.width (text) + 6

        label = QLabel ()
        label.setText (text)
        label.setFont (font)
        label.setMaximumWidth (width)
        label.setAlignment (Qt.AlignCenter | Qt.AlignVCenter)

        self.layout ().addWidget (label)

        secondLine = QFrame ()
        secondLine.setFrameStyle (QFrame.HLine)
        secondLine.setStyleSheet (styleSheet)

        self.layout ().addWidget (secondLine)
        
class tpSplitterLayout (QHBoxLayout, object):
    
    def __init__(self):

        """
        Basic splitter to separate layouts
        """

        super(tpSplitterLayout, self).__init__()

        self.setContentsMargins(40, 2, 40, 2)

        splitter = tpSplitter(shadow=False, color=(60, 60, 60))
        splitter.setFixedHeight(2)

        self.addWidget(splitter)
        
# -------------------------------------------------------------------------------------------------

class tpColorChanger(QDialog, object):
    def __init__(self):
        super(tpColorChanger, self).__init__(parent=_getMayaWindow())
        
        winName = 'tpColorChangerDialog'
        
        # Check if this UI is already open. If it is then delete it before  creating it anew
        if cmds.window (winName, exists=True):
            cmds.deleteUI (winName, window=True)
        elif cmds.windowPref (winName, exists=True):
            cmds.windowPref (winName, remove=True)

        # Set the dialog object name, window title and size
        self.setObjectName(winName)
        self.setWindowTitle('tpColorChanger')
        self.setMinimumSize(245, 245)
        self.setFixedSize(QSize(245, 245))
        
        self.customUI()
        
        self.show()


    def customUI(self):

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.layout().setSpacing(2)
        self.layout().setAlignment(Qt.AlignTop)

        self.layout().addWidget(tpSplitter('Pick Color'))

        gridLayout = QGridLayout()
        self.layout().addLayout(gridLayout)

        # Fill grid with Maya index available colors
        cIndex = 0
        cButtons = []
        for i in range(0, 4):
            for j in range(0, 8):
                cButton = QPushButton()
                cButtons.append(cButton)
                cButton.setStyleSheet(" background-color:rgb(%s,%s,%s);" % (
                cControlColors[cIndex][0] * 255, cControlColors[cIndex][1] * 255,
                cControlColors[cIndex][2] * 255))
                gridLayout.addWidget(cButton, i, j)
                cIndex += 1

        # Add selected color icon
        self.layout().addWidget(tpSplitter('Selected Color'))

        selectedColorLayout = QHBoxLayout()
        self.layout().addLayout(selectedColorLayout)

        self.colorLabel = QLabel()
        self.colorLabel.setStyleSheet("border: 1px solid black; background-color:rgb(0, 0, 0);")
        self.colorLabel.setMinimumWidth(45)
        self.colorSlider = QSlider(Qt.Horizontal)
        self.colorSlider.setMinimum(0)
        self.colorSlider.setMaximum(31)
        self.colorSlider.setValue(2)
        self.colorSlider.setStyleSheet(
            "QSlider::groove:horizontal {border: 1px solid #999999;height: 8px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);margin: 2px 0;}QSlider::handle:horizontal {background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);border: 1px solid #5c5c5c;width: 10px;margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */border-radius: 1px;}");

        selectedColorLayout.addWidget(self.colorLabel)
        selectedColorLayout.addWidget(self.colorSlider)

        self.layout().addLayout(tpSplitterLayout())

        typeLayout = QHBoxLayout()
        typeBox = QGroupBox()
        typeBox.setTitle('Override color: ')
        typeBox.setLayout(typeLayout)
        self.layout().addWidget(typeBox)

        self.transformTypeCbx = QCheckBox('Transforms')
        self.shapeTypeCbx = QCheckBox('Shapes')
        self.shapeTypeCbx.setChecked(True)

        typeLayout.addWidget(self.transformTypeCbx)
        typeLayout.addWidget(self.shapeTypeCbx)

        self.layout().addLayout(tpSplitterLayout())

        changeColorLayout = QHBoxLayout()
        changeColorLayout.setAlignment(Qt.AlignCenter)
        self.layout().addLayout(changeColorLayout)
        self.changeColorBtn = QPushButton('Change color')
        changeColorLayout.addWidget(self.changeColorBtn)

        # ==== SIGNALS ==== #

        for i, btn in enumerate(cButtons):
            btn.clicked.connect(partial(self._setColor, i))
        self.colorSlider.valueChanged.connect(self._setSlider)
        self.changeColorBtn.clicked.connect(self.setColor)
        self.shapeTypeCbx.stateChanged.connect(self._updateState)
        self.transformTypeCbx.stateChanged.connect(self._updateState)

    def _setColor(self, index):

        """
        Sets the color of the color icon
        :param index: int, Index of the color
        """

        self.colorLabel.setStyleSheet("border: 1px solid black; background-color:rgb(%s, %s, %s);" % (
        cControlColors[index][0] * 255, cControlColors[index][1] * 255,
        cControlColors[index][2] * 255))
        self.colorSlider.setValue(index)

    def _setSlider(self, index):

        """
        Sets the color using the slider
        :param index: int, Index of the color
        :return:
        """

        self._setColor(index)

    def _updateState(self):

        """
        Updates the state of the tool UI
        """

        self.changeColorBtn.setEnabled(self.transformTypeCbx.isChecked() or self.shapeTypeCbx.isChecked())

    @tpUndo
    def setColor(self):

        """
        Sets the color of the selected controls
        """

        sel = cmds.ls(selection=True, type=['shape', 'transform'])
        if len(sel) > 0:
            for obj in sel:
                if cmds.nodeType(obj) == 'transform':
                    shapes = cmds.listRelatives(obj, type='shape')
                    if len(shapes) > 0 and self.shapeTypeCbx.isChecked():
                        for shape in shapes:
                            if cmds.attributeQuery('overrideEnabled', node=shape, exists=True):
                                cmds.setAttr(shape + '.overrideEnabled', True)
                                if cmds.attributeQuery('overrideColor', node=shape, exists=True):
                                    cmds.setAttr(shape + '.overrideColor', self.colorSlider.value())
                if self.transformTypeCbx.isChecked():
                    if cmds.attributeQuery('overrideEnabled', node=obj, exists=True):
                        cmds.setAttr(obj + '.overrideEnabled', True)
                        if cmds.attributeQuery('overrideColor', node=obj, exists=True):
                            cmds.setAttr(obj + '.overrideColor', self.colorSlider.value())

def initUI():
    tpColorChanger()
    
initUI()