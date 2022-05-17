
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QShortcut



from PyQt5.QtCore import QObject, pyqtSignal


import os,sys

from os import path
dirname = path.dirname(__file__)
fname = "dlgXyView.ui"
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



class dlgXyView(QtWidgets.QDialog,dataGuiBaseClass):
    def __init__(self):
        super().__init__()
        uic.loadUi(fpath, self)

        self.listCbxChannel = [getattr(self, n) for n in dir(self) if 'cbxChannel' in n]
        self.listCbxShotNum = [getattr(self, n) for n in dir(self) if 'cbxShotNum' in n]
        
        #initiate the combo boxes
        for i in range(len(self.listCbxShotNum)):
            self.listCbxShotNum[i].currentIndexChanged.connect(functools.partial(self.updateAfterShotNumSelection,i))
            self.listCbxShotNum[i].selected = False
        for i in range(len(self.listCbxChannel)):
            self.listCbxChannel[i].currentIndexChanged.connect(functools.partial(self.updateAfterChannelSelection,i))            
            self.listCbxChannel[i].selected = False

        if len(self.params)!=0:
            for cbxShotNum in self.listCbxShotNum:
                cbxShotNum.addItems(['']+list(np.unique(self.params[shotNumKey]).astype(str)))
                
        #connect button
        self.btnPlot.clicked.connect(self.accept)
        
        
        
    def updateAfterShotNumSelection(self,i):

        self.listCbxChannel[i].clear()
        shotNum = self.listCbxShotNum[i].currentText()
        if shotNum == '':
            self.listCbxChannel[i].addItems([''])
            self.listCbxShotNum[i].selected = False
            
        else:
            self.listCbxShotNum[i].selected = True
            tempParam = self.params[self.params[shotNumKey]==int(shotNum)]
            self.listCbxChannel[i].addItems(['']+list(np.unique(tempParam[channelDescriptionKey]).astype(str)))
        
    def updateAfterChannelSelection (self,i):

        if self.listCbxChannel[i].currentText() =='':
            self.listCbxChannel[i].selected = False

        else:
            
            self.listCbxChannel[i].selected = True


    @staticmethod
    def getXY():

        # dialog = QtWidgets.QDialog()
        ui = dlgXyView()
        # ui.setupUi(dialog)
        result = ui.exec_()

        if not all (x.selected for x in ui.listCbxChannel) or not all (x.selected for x in ui.listCbxShotNum):
            return pd.DataFrame()
        if result != QtWidgets.QDialog.Accepted:
            return pd.DataFrame()
        
        shotNumX, channelX = ui.cbxShotNumX.currentText(), ui.cbxChannelX.currentText()
        shotNumY, channelY = ui.cbxShotNumY.currentText(), ui.cbxChannelY.currentText()
        mask1,mask2 = ui.params[shotNumKey]==int(shotNumX), ui.params[channelDescriptionKey]==str(channelX)
        dataParamX = ui.params[mask1&mask2].reset_index(drop=True)
        dataParamX = dataParamX[dataParamX.index==0]
        mask1,mask2 = ui.params[shotNumKey]==int(shotNumY), ui.params[channelDescriptionKey]==str(channelY)
        dataParamY = ui.params[mask1&mask2].reset_index(drop=True)
        dataParamY = dataParamY[dataParamY.index==0]   
        
        dataParam = dataParamX.append(dataParamY).reset_index(drop=True)
        return dataParam



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    frame = dlgXyView()
    
    # app.aboutToQuit.connect(app.deleteLater)
    # Frame = QtWidgets.QFrame()
    # ui = frmLoadData()
    # ui.setupUi(Frame)
    frame.show()
    app.exec_()



