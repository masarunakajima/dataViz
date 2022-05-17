# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'frmShotChannel.ui'
#
# Created: Wed Jun 15 10:56:51 2016
#      by: PyQt5 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QShortcut



from PyQt5.QtCore import QObject, pyqtSignal


import os,sys
from os import path
dirname = path.dirname(__file__)
fname = "frmWindowLayout.ui"
fpath = path.join(dirname, fname)

from os import path
dirname = path.dirname(__file__)
fname = "frmShotChannel.ui"
fpath = path.join(dirname, fname)


path =os.getcwd()

from dataGuiBaseClasses import *
from constants import * 



class frmShotChannel(QtWidgets.QFrame,dataGuiBaseClass):
    sigChannelListDoubleClicked  = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        uic.loadUi(fpath, self)


        #create shortcut for deselecting for all the lists
        self.lstWidgetList = [getattr(self, n) for n in dir(self) if 'lst' in n]
        for lst in self.lstWidgetList:
            QShortcut(QKeySequence(QtCore.Qt.Key_Escape), lst,  lst.clearSelection,context=QtCore.Qt.WidgetShortcut)


        #create ListboxItem instances

        self.ListboxItemLoadedShot = ListboxItem(self.lstLoadedShot)
        self.ListboxItemChannel = ListboxItem (self.lstChannel)

        self.selectedShots = []
        self.selectedChannels = []
        self.selectedChannelIDs = []


        #Connect

        self.lstLoadedShot.doubleClicked.connect(self.listChannel)

        self.lstLoadedShot.doubleClicked.connect(self.plotBasic)


        self.lstLoadedShot.itemSelectionChanged.connect(self.updateAvailShot)
        self.lstChannel.itemSelectionChanged.connect(self.updateAvailChannel)
        self.lstChannel.doubleClicked.connect(self.plotBasic)

    def listLoadedShots(self):
        if len(self.params)==0:
            return

        selectedShots = [x.text() for x in self.lstLoadedShot.selectedItems()]
        self.selectedShots=selectedShots
        l = list(self.params[shotNumKey].unique())

        if len(l) == self.lstLoadedShot.count():
            currentList = [self.lstLoadedShot.item(i).text() for i in range(self.lstLoadedShot.count())]
            if all([l[i]==currentList[i] for i in range(self.lstLoadedShot.count())]):
                return
        self.ListboxItemLoadedShot.nameList = l
        self.ListboxItemLoadedShot.itemList = l
        self.ListboxItemLoadedShot.listInBox()
        for shot in selectedShots:
            items = self.lstLoadedShot.findItems(shot,QtCore.Qt.MatchExactly)
            if len(items)>0:
                item = items[0]
                item.setSelected(True)



    def listChannel (self):
        if len(self.params)==0:
            return
        selectedChannels = [x.text() for x in self.lstChannel.selectedItems()]
        self.selectedChannels=selectedChannels
        l = list(self.params[channelDescriptionKey].unique())
        l = [str(x) for x in l if X_ValueKey not in str(x)]
        if len(l) == self.lstChannel.count():
            currentList = [self.lstChannel.item(i).text() for i in range(self.lstChannel.count())]
            if all([l[i]==currentList[i] for i in range(self.lstChannel.count())]):
                return
        self.ListboxItemChannel.nameList = l
        self.ListboxItemChannel.itemList = l
        self.ListboxItemChannel.listInBox()
        for channel in selectedChannels:
            items = self.lstChannel.findItems(channel,QtCore.Qt.MatchExactly)
            if len(items)>0:
                item = items[0]
                item.setSelected(True)

    def updateAvailChannel(self):
      #print("number of selected channels: ", len(self.lstChannel.selectedItems()))
      for item in [self.lstChannel.item(i) for i in range(self.lstChannel.count())]:
          item.setFlags(item.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
          item.setBackground(listBgColor)

      if len(self.lstLoadedShot.selectedItems())==0:
        #print ("no shot selected")
        return

      shotNums = [x.text() for x in self.lstLoadedShot.selectedItems()]
      # print (shotNums)
      # print(len(self.lstChannel.selectedItems()))
      for item in [self.lstChannel.item(i) for i in range(self.lstChannel.count())]:
          count = 0
          for shotNum in shotNums:
              tempParam = self.params[self.params[shotNumKey]==int(shotNum)].copy()
              if item.text() in list(tempParam[channelDescriptionKey]):
                  count +=1

          if count == 0: #if the channel cannot be found in any shots selected
              item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable & ~QtCore.Qt.ItemIsEnabled)
          elif count < len(shotNums):#only some but not all the shots selected have the channel
              item.setBackground(listIncompleteMatchBgColor)

      self.updateSelection()


    def updateAvailShot (self):
      for item in [self.lstLoadedShot.item(i) for i in range(self.lstLoadedShot.count())]:
          item.setFlags(item.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
          #item.setBackground(self.listBgColor)

      if len(self.lstChannel.selectedItems())==0:
          return

      channels = [x.text() for x in self.lstChannel.selectedItems()]

      for item in [self.lstLoadedShot.item(i) for i in range(self.lstLoadedShot.count())]:
          count = 0
          for channel in channels:
              tempParam = self.params[self.params[channelDescriptionKey]==channel].copy()
              if int(item.text()) in list(tempParam[shotNumKey]):
                  count +=1

          if count == 0: #if the channel cannot be found in any shots selected
              item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable & ~QtCore.Qt.ItemIsEnabled)
          elif count < len(channels):#only some but not all the shots selected have the channel
              item.setBackground(self.listIncompleteMatchBgColor)

      self.updateSelection()

    def plotBasic (self):
        self.sigChannelListDoubleClicked.emit()

    def updateSelection(self):
        self.selectedChannels=[x.text() for x in self.lstChannel.selectedItems()]
        self.selectedShots=[x.text() for x in self.lstLoadedShot.selectedItems()]
        self.selectedChannelIDs=[]
        l=[]

        for shot in self.selectedShots:
            df = self.params.copy()
            df = df[df[shotNumKey].isin([int(shot)])]
            # print ("shot", shot)
            # print("param length after shot selection", len(df))
            # df = df[df[self.shotNumKey].isin(np.array([shot]).astype(df[self.shotNumKey].dtype))]
            for channel in self.selectedChannels:

              # df1 = df[df[self.channelDescriptionKey].isin(np.array([channel]).astype(df[self.channelDescriptionKey].dtype))]

              #print (df[self.channelDescriptionKey])
              df1 = df[df[channelDescriptionKey].isin([str(channel)])]

              l+=list(df1[channelIdKey])

        self.selectedChannelIDs = list(np.unique(l))
        # print("selected channels", len(self.selectedChannelIDs))

    def updateChannelOptions(self,paramDf):
        self.listLoadedShots()
        self.listChannel()
        self.updateAvailShot()
        self.updateAvailChannel()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    frame = frmShotChannel()
    
    # app.aboutToQuit.connect(app.deleteLater)
    # Frame = QtWidgets.QFrame()
    # ui = frmLoadData()
    # ui.setupUi(Frame)
    frame.show()
    app.exec_()
