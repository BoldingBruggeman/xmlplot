from __future__ import print_function

import sys
import traceback

from xmlstore.qt_compat import QtCore,QtGui,QtWidgets

class ErrorReceiver(QtCore.QObject):
    """Objects of this class accept an ErrorEvent (contained), takes the contained error message
    and passes it to ErrorDialog for showing the error in the GUI. Errors can be posted from
    any thread (not necessarily the GUI thread) using QtWidgets.QApplication.postEvent.
    """
    def __init__(self):
        QtCore.QObject.__init__(self)
    
    class ErrorEvent(QtCore.QEvent):
        """Custom class derived from QEvent, used only to contain a string (error message).
        """
        def __init__(self,error):
            QtCore.QEvent.__init__(self,QtCore.QEvent.User)
            self.error = error

    def event(self,ev):
        """Ignores all event except those of type QtCore.QEvent.User. Events of this type must
        be objects of class ErrorEvent. Their contained string is passed to the ErrorDialog for
        display.
        """
        if ev.type()==QtCore.QEvent.User:
            ErrorDialog.postError(ev.error)
            return True
        return QtWidgets.QWidget.event(self,ev)
        
# The one and only errorreceiver object, responsible for receiving posted errors from all threads.
# Posted errors will be passed to an ErrorDialog.
errorreceiver = ErrorReceiver()

def redirect_stderr(appname, errortext):
    """Redirects all text written to stderr to a contained class that posts the error
    message to the one and only errorreceiver object. The posting mechanism allows the
    error message to be passed between threads.
    """
    ErrorDialog.appname = appname
    ErrorDialog.errortext = errortext
    def hook(type, value, tb):
        text = ''.join(traceback.format_exception(type, value, tb))
        QtWidgets.QApplication.postEvent(errorreceiver,ErrorReceiver.ErrorEvent(text))
    sys.excepthook = hook

class ErrorDialog(QtWidgets.QWidget):
    errdlg = None
    errortext = None
    appname = None

    @staticmethod
    def postError(string):
        """Creates the one and only ErrorDialog if it does not exist yet, then shows the
        provided error message in the dialog.
        """
        if ErrorDialog.errdlg is None:
            ErrorDialog.errdlg = ErrorDialog()
        ErrorDialog.errdlg.write(string)
        ErrorDialog.errdlg.show()
    
    def __init__(self,parent=None):
        if parent is None: parent = QtWidgets.QApplication.activeWindow()
        QtWidgets.QWidget.__init__(self,parent,QtCore.Qt.Tool)

        self.labelStart = QtWidgets.QLabel('Errors occurred during execution of %s:' % ErrorDialog.appname,self)
        self.labelStart.setWordWrap(True)
        self.labelStop = QtWidgets.QLabel(ErrorDialog.errortext,self)
        self.labelStop.setOpenExternalLinks(True)
        self.labelStop.setWordWrap(True)

        self.textedit = QtWidgets.QTextEdit(self)
        self.textedit.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.textedit.setReadOnly(True)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.labelStart)
        layout.addWidget(self.textedit)
        layout.addWidget(self.labelStop)
        self.setLayout(layout)
        
        self.setWindowTitle('Errors occurred')
        self.resize(600, 200)

        if parent is not None:
            self.setAttribute(QtCore.Qt.WA_QuitOnClose,False)
            
    def write(self,string):
        cur = self.textedit.textCursor()
        cur.movePosition(QtGui.QTextCursor.End)
        cur.insertText(string)