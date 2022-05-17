
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QShortcut



from PyQt5.QtCore import QObject, pyqtSignal


import os,sys
from os import path
dirname = path.dirname(__file__)
fname = "frmAction1.ui"
fpath = path.join(dirname, fname)

path =os.getcwd()
# while len(path)>5:
    # path = os.path.dirname(path)
    # dirs = next(os.walk(path))[1]
    # if path not in sys.path:
        # sys.path.append(path)
    # for Dir in dirs:
        # if Dir not in sys.path:
            # sys.path.append(os.path.join(path,Dir))

from dataGuiBaseClasses import *
from constants import *

from popFrmArithmetics import popFrmArithmetics


class frmAction1(QtWidgets.QFrame,dataGuiBaseClass):
    sigNewWindowOpened = QtCore.pyqtSignal()
    
    sigBtnPlotPressed = QtCore.pyqtSignal()
    sigBtnPsdPressed = QtCore.pyqtSignal()
    sigBtnLinkXPressed = QtCore.pyqtSignal()
    sigBtnLinkYPressed = QtCore.pyqtSignal()
    sigBtnLinkXYPressed = QtCore.pyqtSignal()
    sigBtnLinkRegionPressed = QtCore.pyqtSignal()
    sigBtnCsdPressed = QtCore.pyqtSignal()
    sigIvDataAdded = QtCore.pyqtSignal()

    sigDataAdded = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        uic.loadUi(fpath, self)

        #create shortcut for deselecting for all the lists
        self.lstWidgetList = [getattr(self, n) for n in dir(self) if 'lst' in n]
        for lst in self.lstWidgetList:
            QShortcut(QKeySequence(QtCore.Qt.Key_Escape), lst,  lst.clearSelection,context=QtCore.Qt.WidgetShortcut)
        

        self.btnPlot.clicked.connect(self.sigBtnPlotPressed.emit)
        self.btnPsd.clicked.connect(self.sigBtnPsdPressed.emit)
        self.btnLinkX.clicked.connect(self.sigBtnLinkXPressed.emit)
        self.btnLinkY.clicked.connect(self.sigBtnLinkYPressed)
        self.btnLinkXY.clicked.connect(self.sigBtnLinkXYPressed.emit)
        self.btnLinkRegion.clicked.connect(self.sigBtnLinkRegionPressed.emit)
        self.btnCsd.clicked.connect(self.sigBtnCsdPressed.emit) 
        self.btnProcIvCharacteristics.clicked.connect(self.IvCharacteristics)
        self.btnProcArithmetics.clicked.connect(self.arithmetics)
        

        
        
    def arithmetics(self):
        self.popFrmArithmetics = popFrmArithmetics()
        self.popFrmArithmetics.sigNewDataAdded.connect(self.sigArithmeticsAdded)
        self.popFrmArithmetics.show() 
        
    

    def sigArithmeticsAdded(self):
        self.sigDataAdded.emit()
        
    def IvCharacteristics(self):



        self.frame = QtGui.QFrame()
        self.ui = Ui_popFrmIvCharacteristics()
        self.ui.setupUi(self.frame)
        self.ui.sigIvDataAdded.connect(self.ivDataAdded)
        self.frame.show()


        
    def ivDataAdded (self):
        self.sigIvDataAdded.emit()
        'frmAction1: emit'
        
        
        
    def getProcessParams(self):
        # get parameters

            
        nperseg = self.cmbNperseg.currentText()
        if nperseg =='-':
            nperseg = 512
        elif not nperseg.isdigit(): 
            nperseg = 512
        else:
            nperseg = int (nperseg)
            
            
        npersegSpectrogram = self.cmbNpersegSpectrogram.currentText()
        if npersegSpectrogram =='-':
            npersegSpectrogram = 2*nperseg
        elif not npersegSpectrogram.isdigit(): 
            npersegSpectrogram = 2*nperseg
        elif int(npersegSpectrogram)<2*nperseg:
            npersegSpectrogram = 2*nperseg
        else:
            npersegSpectrogram = int(npersegSpectrogram)
            
        overlap = self.sbxOverlap.value()
        if overlap ==0:
            overlap = 50
        else:
            overlap = int(overlap)
            
        overlapSpectrogram = self.sbxOverlapSpectrogram.value()
        if overlapSpectrogram ==0:
            overlapSpectrogram = 50
        else:
            overlapSpectrogram = int(overlapSpectrogram)
        
            

            
  
        processParams = {isSmoothKey:self.cbxSmooth.isChecked(),
                        nSmoothKey: self.ledNSmooth.text(),
                        isDcCancelHeadKey: self.rbtDcCancelHead.isChecked(), 
                        nDcCancelHeadKey: self.ledNDcCancelHead.text(),
                        isDcCancelTailKey: self.rbtDcCancelTail.isChecked(),
                        nDcCancelTailKey: self.ledNDcCancelTail.text(),
                        isDetrendKey: self.cbxDetrend.isChecked(),
                        nDetrendKey: self.ledNDetrend.text(),
                        isAbsolutePhaseKey: self.cbxAbsolutePhase.isChecked(),
                        npersegKey:nperseg,
                        isUncalibratedSignalKey:self.cbxUncalibratedSignal.isChecked(),
                        isNormalizePsdKey:self.cbxNormalizePsd.isChecked(),
                        overlapKey:overlap,
                        overlapSpectrogramKey:overlapSpectrogram,
                        npersegSpectrogramKey: npersegSpectrogram,
                        processCountKey:0,
                        isErrorBarKey:self.cbxErrorBar.isChecked()
                        }


        return processParams
        

        


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    frame = frmAction1()
    
    frame.show()
    app.exec_()

