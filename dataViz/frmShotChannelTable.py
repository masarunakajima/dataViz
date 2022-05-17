
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QShortcut



from PyQt5.QtCore import QObject, pyqtSignal


import os,sys

from os import path
dirname = path.dirname(__file__)
fname = "frmShotChannelTable.ui"
fpath = path.join(dirname, fname)

# path =os.getcwd()
# while len(path)>5:
    # path = os.path.dirname(path)
    # dirs = next(os.walk(path))[1]
    # if path not in sys.path:
        # sys.path.append(path)
    # for Dir in dirs:
        # if Dir not in sys.path:
            # sys.path.append(os.path.join(path,Dir))

from dataGuiBaseClasses import *




class frmShotChannelTable(QtWidgets.QFrame, dataGuiBaseClass):
    sigChannelListDoubleClicked  = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        uic.loadUi(fpath, self)

        self.tblAvailableChannel.itemSelectionChanged.connect(self.updateSelection)
        self.tblAvailableChannel.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.selectedChannelIDs = []

    def updateChannelOptions(self, paramDf):
        if len(paramDf)==0:
            return

        df = paramDf.reset_index(drop=True)
        if len(df.columns)==0:
            df = self.params.reset_index(drop=True)
        data = {}

        types = []
        array = []
        for i in range(len(df)):
            array.append(tuple(df.ix[i]))
        for i in range(len(df.columns)):
            types.append((df.columns[i],df[df.columns[i]].dtype))
        data = np.array(array,dtype=types)

        self.tblAvailableChannel.setData(data)

    def updateSelection(self):
      print ("updating channel selection")
      self.selectedChannelIDs = []
      if self.tblAvailableChannel.rowCount()==0 or self.tblAvailableChannel.columnCount()==0 :
          return

      channelIdColumnIndex = -1
      for i in range(self.tblAvailableChannel.columnCount()):
          if self.tblAvailableChannel.horizontalHeaderItem(i).text()==self.channelIdKey:
              channelIdColumnIndex = i

      if channelIdColumnIndex == -1:
          return

      l=[]
      for index in self.tblAvailableChannel.selectedIndexes():
          l.append(self.tblAvailableChannel.item(index.row(),channelIdColumnIndex).text())

      self.selectedChannelIDs = list(np.unique(l))

    def listChannel(self):
        self.updateChannelOptions(self.params)

    def listLoadedShots(self):
        self.updateChannelOptions(self.params)





if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    frame = frmShotChannelTable()
    
    # app.aboutToQuit.connect(app.deleteLater)
    # Frame = QtWidgets.QFrame()
    # ui = frmLoadData()
    # ui.setupUi(Frame)
    frame.show()
    app.exec_()



