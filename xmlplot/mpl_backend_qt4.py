from __future__ import print_function

import sys
import ctypes

import numpy

from matplotlib.backend_bases import FigureCanvasBase, TimerBase
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.transforms import Bbox
from matplotlib import cbook

from xmlstore.qt_compat import QtGui,QtCore,QtWidgets,qt4_backend

if qt4_backend in ('PyQt5', 'PySide2'):
    from matplotlib.backends.backend_qt5 import TimerQT, FigureCanvasQT as FigureCanvasQT, cursord
else:
    from matplotlib.backends.backend_qt4 import TimerQT, FigureCanvasQT as FigureCanvasQT, cursord

QT_API = qt4_backend

class FigureCanvasQTAgg(FigureCanvasAgg, FigureCanvasQT):

    # JB: added "afterResize" signal
    afterResize = QtCore.Signal()
    def __init__(self, figure):
        FigureCanvasQT.__init__( self, figure )
        FigureCanvasAgg.__init__( self, figure )

        # JB: do NOT set QtCore.Qt.WA_OpaquePaintEvent because part of the figure is transparent.
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent, False)

        # JB: added "animating" flag.
        self.animating = False


    def paintEvent(self, event):
        """
        Copy the image from the Agg canvas to the qt.drawable.

        In Qt, all drawing should be done inside of here when a widget is
        shown onscreen.
        """
        if self._update_dpi():
            # The dpi update triggered its own paintEvent.
            return
        self._draw_idle()  # Only does something if a draw is pending.

        # If the canvas does not have a renderer, then give up and wait for
        # FigureCanvasAgg.draw(self) to be called.
        if not hasattr(self, 'renderer'):
            return

        painter = QtGui.QPainter(self)
        try:
            # See documentation of QRect: bottom() and right() are off
            # by 1, so use left() + width() and top() + height().
            rect = event.rect()
            # scale rect dimensions using the screen dpi ratio to get
            # correct values for the Figure coordinates (rather than
            # QT5's coords)
            width = rect.width() * self._dpi_ratio
            height = rect.height() * self._dpi_ratio
            left, top = self.mouseEventCoords(rect.topLeft())
            # shift the "top" by the height of the image to get the
            # correct corner for our coordinate system
            bottom = top - height
            # same with the right side of the image
            right = left + width
            # create a buffer using the image bounding box
            bbox = Bbox([[left, bottom], [right, top]])
            reg = self.copy_from_bbox(bbox)
            buf = cbook._unmultiplied_rgba8888_to_premultiplied_argb32(
                memoryview(reg))

            # JB do not erase widget background, we'll paint on top
            # clear the widget canvas
            #painter.eraseRect(rect)

            qimage = QtGui.QImage(buf, buf.shape[1], buf.shape[0],
                                  QtGui.QImage.Format_ARGB32_Premultiplied)
            if hasattr(qimage, 'setDevicePixelRatioF'):
                # Not available on Qt<5.6
                qimage.setDevicePixelRatioF(self._dpi_ratio)
            elif hasattr(qimage, 'setDevicePixelRatio'):
                # Not available on Qt4 or some older Qt5.
                qimage.setDevicePixelRatio(self._dpi_ratio)
            # set origin using original QT coordinates
            origin = QtCore.QPoint(rect.left(), rect.top())
            painter.drawImage(origin, qimage)
            # Adjust the buf reference count to work around a memory
            # leak bug in QImage under PySide on Python 3.
            if QT_API in ('PySide', 'PySide2'):
                ctypes.c_long.from_address(id(buf)).value = 1

            self._draw_rect_callback(painter)
        finally:
            painter.end()


    # JB: emit afterResize event after resizing.
    def resizeEvent( self, e ):
        FigureCanvasQT.resizeEvent( self, e )
        self.afterResize.emit()
