# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'frmLoadData.ui'
#
# Created: Tue Jun 14 21:56:47 2016
#      by: PyQt5 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from constants import *
from PyQt5.QtCore import QObject, pyqtSignal
from glob import glob
import os,sys
from os import path

dirname = path.dirname(__file__)
fname = "frmLoadData.ui"
fpath = path.join(dirname, fname)

path =os.getcwd()
while len(path)>5:
    path = os.path.dirname(path)
    dirs = next(os.walk(path))[1]
    if path not in sys.path:
        sys.path.append(path)
    for Dir in dirs:
        if Dir not in sys.path:
            sys.path.append(os.path.join(path,Dir))


from dataGuiBaseClasses import *





class frmLoadData(QtWidgets.QFrame, dataGuiBaseClass):
    sigLoaded = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        uic.loadUi(fpath, self)

        #create shortcut for deselecting for all the lists
        self.lstWidgetList = [getattr(self, n) for n in dir(self) if 'lst' in n]
        for lst in self.lstWidgetList:
            QShortcut(QKeySequence(QtCore.Qt.Key_Escape), lst,  lst.clearSelection,context=QtCore.Qt.WidgetShortcut)

        #create ListboxItem instances
        self.ListboxItemYear = ListboxItem(self.lstYear)
        self.ListboxItemMonth = ListboxItem(self.lstMonth)
        self.ListboxItemDate = ListboxItem(self.lstDate)
        self.ListboxItemShot = ListboxItem(self.lstShot)

        #Connect
        self.lstYear.doubleClicked.connect(self.doubleYear)
        self.lstMonth.doubleClicked.connect(self.doubleMonth)
        self.lstDate.doubleClicked.connect(self.doubleDate)
        self.lstShot.doubleClicked.connect(self.doubleShot)
        self.btnBrowse.clicked.connect(self.searchMasterData)
        self.btnSearch.clicked.connect(self.specificSearch)
        self.btnLoad.clicked.connect(self.loadShotDaqs)
        self.btnLoadAll.clicked.connect(self.loadAll)
        self.btnRefresh.clicked.connect(self.refresh)

        #set attributes

        self.ws = []
        self.ps = []
        self.ds = []

        self.catPathList = []

        self.xRegionGroups=[]
        self.loadedShots = []



        self.catRefresh()


    def catRefresh(self):

        if not os.path.isdir(catalystDir):
            return
        self.catPathList = glob(self.catalystDir+'/*')
        self.catPathList = [x for x in self.catPathList if len(os.path.basename(x))>6 and '.' in os.path.basename(x)]

    def doubleYear(self,event):
        if not self.ListboxItemYear.listbox.selectedIndexes():
            return
        index = [x.row() for x in self.ListboxItemYear.listbox.selectedIndexes()][0]
        self.listMonths(self.ListboxItemYear.itemList[index])

    def doubleMonth(self,event):
        if not self.ListboxItemMonth.listbox.selectedIndexes():
            return
        index = [x.row() for x in self.ListboxItemMonth.listbox.selectedIndexes()][0]
        self.listDates(self.ListboxItemMonth.itemList[index])

    def doubleDate(self,event):
        if not self.ListboxItemDate.listbox.selectedIndexes():
            return
        index = [x.row() for x in self.ListboxItemDate.listbox.selectedIndexes()][0]
        self.listShots(self.ListboxItemDate.itemList[index])

    def doubleShot (self,event):
        global INDEX
        INDEX=self.ListboxItemShot.listbox.selectedIndexes()
        if not self.ListboxItemShot.listbox.selectedIndexes():
            return
        index = [x.row() for x in self.ListboxItemShot.listbox.selectedIndexes()][0]

        self.loadShotDaq(index)



        self.sigLoaded.emit()


    def loadAll (self):
        count = self.lstShot.count()
        for i in range (count):
            self.loadShotDaq(i)


        self.sigLoaded.emit()



    def loadShotDaqs(self):
        if not self.ListboxItemShot.listbox.selectedIndexes():
            return
        indexs = [x.row() for x in self.ListboxItemShot.listbox.selectedIndexes()]
        for index in indexs:
            self.loadShotDaq(index)

        self.sigLoaded.emit()


    def searchMasterData(self):
      dirfilename = "default_dir.txt"
      # dirPath = QtWidgets.QFileDialog.getExistingDirectory(None,'Select a "data" directory',\
      # os.path.expanduser("~"),QtWidgets.QFileDialog.ShowDirsOnly)
      home = os.getenv("HOME")
      default_path = os.path.dirname(dirname)
      if os.path.exists(dirfilename):
        default_path = open(dirfilename).readline()

      dirPath =\
      QtWidgets.QFileDialog.getExistingDirectory(None, "Open a folder",
                                             default_path,
                                             QtWidgets.QFileDialog.ShowDirsOnly)

      if not dirPath:
        return


      dirName = os.path.basename(str(dirPath))
      savedir = os.path.dirname(os.path.abspath(dirPath))
      f = open(dirfilename, 'w')
      f.write(os.path.dirname(dirPath))
      f.close()
      #Test if the path is for 'data' directory
      global DIRNAME
      DIRNAME = dirName
      #Test if the path is for 'year' directory
      if len(dirName)==4 and dirName.isdigit():
          if int(dirName)>2000: #data since 2000
              self.listMonths(str(dirPath))

      elif dirName[:2].isdigit() and dirName[2]=='_':
          self.listDates(str(dirPath))

      elif all([x.isdigit() for  x in dirName.split('_')]):
          self.listShots(str(dirPath))

      else:
          self.listYears(str(dirPath))
    def specificSearch(self):

        self.lstYear.clear()
        self.lstMonth.clear()
        self.lstDate.clear()
        def_path = os.path.join(os.path.dirname(dirname),
                "sample_data/2016/01_January")
        pathfilename = "shot_dir.txt"
        if os.path.exists(pathfilename):
            temp_path = open(pathfilename).readline()
            if os.path.exists(temp_path):
                def_path = temp_path
        dirPath = QtWidgets.QFileDialog.getExistingDirectory(None,'Select a "data" directory',\
        def_path, QtWidgets.QFileDialog.ShowDirsOnly)
        global DIRPATH
        DIRPATH = dirPath
        if not dirPath:
            return
        self.listShots(str(dirPath))
        with open(pathfilename, 'w') as f:
            f.write(os.path.dirname(dirPath))


    def listYears (self,path):
        allDirNames = next(os.walk(path))[1]
        self.ListboxItemYear.nameList = [x for x in allDirNames if len(x)==4 and x.isdigit()]
        self.ListboxItemYear.itemList = [os.path.join(path,x) for x in self.ListboxItemYear.nameList]
        self.ListboxItemYear.listInBox()
        self.lblYearParent.setText(path)

    def listMonths(self,path):
        allDirNames = next(os.walk(path))[1]
        self.ListboxItemMonth.nameList = [x for x in allDirNames if x[:2].isdigit() and x[2]=='_']
        self.ListboxItemMonth.itemList = [os.path.join(path,x) for x in self.ListboxItemMonth.nameList]
        self.ListboxItemMonth.listInBox()
        self.lblMonthParent.setText(os.path.basename(path))

    def listDates(self,path):
        allDirNames = next(os.walk(path))[1]
        self.ListboxItemDate.nameList = [x for x in allDirNames if all([y.isdigit() for y in x.split('_')])]
        self.ListboxItemDate.itemList = [os.path.join(path,x) for x in self.ListboxItemDate.nameList]
        self.ListboxItemDate.listInBox()
        self.lblDateParent.setText(os.path.basename(path))


    def listShots(self, path):
        allFileNames = next(os.walk(path))[2]
        shotList = [x for x in allFileNames if x[-6:].isdigit()]
        global SHOTLIST, ALLFILENAMES
        SHOTLIST, ALLFILENAMES = shotList, allFileNames
        nameList = []
        itemList = []

        while len(shotList)!=0:
            f = shotList.pop(0)
            item=[f]
            nameList.append(f[-6:])
            shotListCopy=shotList[:]
            for File in shotListCopy:
                if File[-6:]==f[-6:]:
                    item.append(File)
                    shotList.remove(File)
            itemList.append(item)


        self.ListboxItemShot.nameList = nameList[:]
        self.ListboxItemShot.itemList=itemList[:]

        self.ListboxItemShot.listInBox()
        self.ListboxItemShot.path=path
        self.lblShotParent.setText(os.path.basename(path))

    def refresh (self):
        if not hasattr(self.ListboxItemShot, 'path'):
            return
        path = self.ListboxItemShot.path
        self.listShots(path)

    def loadShotDaq (self, index):

        dirPath = self.ListboxItemShot.path
        shotNum = self.ListboxItemShot.nameList[index]
        shotDaq = ShotDaq(shotNum)
        digitizerNameList = self.ListboxItemShot.itemList[index]
        param=pd.DataFrame()
        catPath = [x for x in self.catPathList if os.path.basename(x).split('.')[-2][-3:]+os.path.basename(x).split('.')[-1]==shotNum]


        for digitizerName in digitizerNameList:
            digitizerData = getDigitizerData(os.path.join(dirPath,digitizerName),**keys)
            param = param.append(digitizerData.info).reset_index(drop=True)
            shotDaq.digitizerDataList.append(digitizerData.data)

        if not catPath:
            catPath = False
        else:
            catPath = catPath[0]
            catData = catalyst_reader(catPath,param,**self.keys)
            param = param.append(catData.info).reset_index(drop=True)
            shotDaq.digitizerDataList.append(catData.data)


        if self.cbxTimeShift_2.isChecked():
            if self.ledTimeShift_2.text() != '' and self.ledTimeShift_2.text().replace('-','').replace('.','').isdigit():
                param[self.X0Key]=param[self.X0Key].astype(float)+float(self.ledTimeShift_2.text())*0.001


        if shotNum not in self.loadedShots:

            dataGuiBaseClass.params = dataGuiBaseClass.params.append(param)
            data = {shotNumKey:shotNum, dfKey:pd.concat(shotDaq.digitizerDataList, axis=1), dfErrKey:pd.DataFrame()}
            dataGuiBaseClass.dataList.append(data)

        else:
            mask = dataGuiBaseClass.params[shotNumKey].astype(str)!=shotNum
            dataGuiBaseClass.params = dataGuiBaseClass.params[mask]
            dataGuiBaseClass.params = dataGuiBaseClass.params.append(param)
            index = [x for x in range(len(dataGuiBaseClass.dataList)) if dataGuiBaseClass.dataList[x][shotNumKey]==shotNum][0]
            data = {shotNumKey:shotNum, dfKey:pd.concat(shotDaq.digitizerDataList, axis=1), dfErrKey:pd.DataFrame()}
            #dataGuiBaseClass.params.sort(self.shotNumKey,inplace=True).dataList[index]=data
            dataGuiBaseClass.dataList[index]=data

        dataGuiBaseClass.params.sort_values(by=[shotNumKey], inplace=True)
        self.loadedShots.append(shotNum)











if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    frame = frmLoadData()
    
    # app.aboutToQuit.connect(app.deleteLater)
    # Frame = QtWidgets.QFrame()
    # ui = frmLoadData()
    # ui.setupUi(Frame)
    frame.show()
    app.exec_()
