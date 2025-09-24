from __future__ import print_function

import sys
import ctypes

import numpy

from matplotlib.backend_bases import FigureCanvasBase, TimerBase
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.transforms import Bbox
from matplotlib import cbook

from xmlstore.qt_compat import QtGui,QtCore,QtWidgets,qt4_backend

if qt4_backend in ('PyQt5', 'PySide2', 'PySide6'):
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as _FigureCanvasQTAgg
    from matplotlib.backends.backend_qt5 import cursord
else:
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as _FigureCanvasQTAgg
    from matplotlib.backends.backend_qt4 import cursord

QT_API = qt4_backend

class QPainter(QtGui.QPainter):
    def eraseRect(self, rect):
        pass

class FigureCanvasQTAgg(_FigureCanvasQTAgg):

    # JB: added "afterResize" signal
    afterResize = QtCore.Signal()
    def __init__(self, figure):
        super().__init__(figure=figure)

        # JB: do NOT set QtCore.Qt.WA_OpaquePaintEvent because part of the figure is transparent.
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, False)

    def paintEvent(self, event):
        # JB: replace default painter by one that does nothing when eraseRect is called.
        # That ensures the system background that Qt has given us is not erase (see disabling of WA_OpaquePaintEvent above)
        old = QtGui.QPainter
        QtGui.QPainter = QPainter
        super().paintEvent(event)
        QtGui.QPainter = old

    # JB: emit afterResize event after resizing.
    def resizeEvent( self, e ):
        super().resizeEvent( e )
        self.afterResize.emit()
