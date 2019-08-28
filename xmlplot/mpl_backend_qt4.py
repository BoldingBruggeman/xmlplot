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
    from matplotlib.backends.backend_qt5 import TimerQT, FigureCanvasQT as FigureCanvasQT
else:
    from matplotlib.backends.backend_qt4 import TimerQT, FigureCanvasQT as FigureCanvasQT

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
        """Copy the image from the Agg canvas to the qt.drawable.

        In Qt, all drawing should be done inside of here when a widget is
        shown onscreen.
        """
        if self._update_dpi():
            # The dpi update triggered its own paintEvent.
            return
        self._draw_idle()  # Only does something if a draw is pending.

        # if the canvas does not have a renderer, then give up and wait for
        # FigureCanvasAgg.draw(self) to be called
        if not hasattr(self, 'renderer'):
            return

        painter = QtGui.QPainter(self)

        # JB do not erase widget background, we'll paint on top
        #if self._erase_before_paint:
        #    painter.eraseRect(self.rect())
        #    self._erase_before_paint = False

        rect = event.rect()
        left = rect.left()
        top = rect.top()
        width = rect.width()
        height = rect.height()
        # See documentation of QRect: bottom() and right() are off by 1, so use
        # left() + width() and top() + height().
        bbox = Bbox(
            [[left, self.renderer.height - (top + height * self._dpi_ratio)],
             [left + width * self._dpi_ratio, self.renderer.height - top]])
        reg = self.copy_from_bbox(bbox)
        buf = cbook._unmultiplied_rgba8888_to_premultiplied_argb32(
            memoryview(reg))
        qimage = QtGui.QImage(buf, buf.shape[1], buf.shape[0],
                              QtGui.QImage.Format_ARGB32_Premultiplied)
        if hasattr(qimage, 'setDevicePixelRatio'):
            # Not available on Qt4 or some older Qt5.
            qimage.setDevicePixelRatio(self._dpi_ratio)
        origin = QtCore.QPoint(left, top)
        painter.drawImage(origin / self._dpi_ratio, qimage)
        # Adjust the buf reference count to work around a memory
        # leak bug in QImage under PySide on Python 3.
        if QT_API in ('PySide', 'PySide2'):
            ctypes.c_long.from_address(id(buf)).value = 1

        self._draw_rect_callback(painter)

        painter.end()


    # JB: emit afterResize event after resizing.
    def resizeEvent( self, e ):
        FigureCanvasQT.resizeEvent( self, e )
        self.afterResize.emit()

    def drawRectangle(self, rect):
        # Draw the zoom rectangle to the QPainter.  _draw_rect_callback needs
        # to be called at the end of paintEvent.
        if rect is not None:
            def _draw_rect_callback(painter):
                # JB draw dashed white line on solid black to get contrast
                painter.setPen( QtGui.QPen( QtCore.Qt.black, 1. / self._dpi_ratio, QtCore.Qt.SolidLine ) )
                painter.drawRect(*(pt / self._dpi_ratio for pt in rect))

                painter.setPen( QtGui.QPen( QtCore.Qt.white, 1. / self._dpi_ratio, QtCore.Qt.DotLine ) )
                painter.drawRect(*(pt / self._dpi_ratio for pt in rect))
        else:
            def _draw_rect_callback(painter):
                return
        self._draw_rect_callback = _draw_rect_callback
        self.update()
