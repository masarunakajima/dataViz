
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QShortcut



from PyQt5.QtCore import QObject, pyqtSignal


import os,sys



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




class frmParameterFilter(QtWidgets.QFrame,dataGuiBaseClass):
    sigFilterChanged = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        uic.loadUi('frmParameterFilter.ui', self)

    
        self.lstWidgetList = [getattr(self, n) for n in dir(self) if 'lst' in n]
        for lst in self.lstWidgetList:
            QShortcut(QKeySequence(QtCore.Qt.Key_Escape), lst,  lst.clearSelection,context=QtCore.Qt.WidgetShortcut)
        
        
        #Create listboxitem
        self.paramListboxItem = ListboxItem(self.lstParams)
        self.selectedParamListboxItem = ListboxItem(self.lstSelectedParams)
        
        #define attributes
        self.paramFilterCount = 0
        self.paramFilterItems = []        
        self.filteredParams = []
        self.selectedParams = []

        self.filteredParamDf = pd.DataFrame()   
        
        #connect
        self.btnSelect.clicked.connect(self.select)
        self.btnAdd.clicked.connect(self.add)
        self.btnClear.clicked.connect(self.clear)
        self.btnApplyAllFilters.clicked.connect(self.applyAllFilters)
        self.btnClearAllFilters.clicked.connect(self.clearAllFilters)
        
        
        
    def select (self):
        if not self.lstParams.selectedItems():
            return
        self.deleteAllParamFilterItems()
        names = [x.text() for x in self.lstParams.selectedItems()]
        self.addParams(names)
        self.update()
        
    def add(self):
        if not self.lstParams.selectedItems():
            return
        names = [x.text() for x in self.lstParams.selectedItems()]
        names = [x for x in names if x not in self.selectedParams]
        self.addParams(names)
        self.update()
        
        
    def clear(self):
        self.deleteAllParamFilterItems()
        self.update()
        

        
    def addParams (self,paramNames):
        for name in paramNames:
            self.addParam(name)
            
                 
        

    def addParam (self, paramName):
        #add to paraListbox
        self.selectedParams.append(paramName)
        filterItem = paramFilterItem(paramName, np.unique(self.params[paramName]))
        self.paramFilterItems.append(filterItem)
        self.gloParamFilterItems.addWidget(filterItem.label, 0,self.paramFilterCount,1,1)
        self.gloParamFilterItems.addWidget(filterItem.listbox, 1,self.paramFilterCount,1,1)
        self.gloParamFilterItems.addWidget(filterItem.btnApplyFilter, 2,self.paramFilterCount,1,1)
        self.gloParamFilterItems.addWidget(filterItem.btnClearFilter, 3,self.paramFilterCount,1,1)
        self.paramFilterCount +=1
        
        #connect signals
        filterItem.sigApplyFilter.connect(self.update)
        filterItem.sigClearFilter.connect(self.update)       
        
        
        
    def deleteAllParamFilterItems(self):
        for item in self.paramFilterItems:
            self.deleteParamFilterItem(item)
        self.filteredParams=[]
        self.selectedParams=[]
        self.paramFilterItems = []


        
    def deleteParamFilterItem (self, paramFilterItem):
        
        self.gloParamFilterItems.removeWidget(paramFilterItem.label)
        self.gloParamFilterItems.removeWidget(paramFilterItem.listbox)
        self.gloParamFilterItems.removeWidget(paramFilterItem.btnApplyFilter)
        self.gloParamFilterItems.removeWidget(paramFilterItem.btnClearFilter)
        
        paramFilterItem.label.deleteLater()
        paramFilterItem.listbox.deleteLater()
        paramFilterItem.btnApplyFilter.deleteLater()
        paramFilterItem.btnClearFilter.deleteLater()
        
        paramFilterItem.label = None
        paramFilterItem.listbox = None
        paramFilterItem.btnApplyFilter = None
        paramFilterItem.btnClearFilter = None

        self.paramFilterCount -= 1
    
        
    def applyAllFilters(self):
        for item in self.paramFilterItems:
            item.sigApplyFilter.disconnect(self.update)
            item.applyFilter()
            item.sigApplyFilter.connect(self.update)
        self.update()
        
        
        
        
    def clearAllFilters(self):
        for item in self.paramFilterItems:
            item.sigClearFilter.disconnect(self.update)
            item.clearFilter()
            item.sigClearFilter.connect(self.update)
        self.update()
        

 
        
    def update(self):
        
        self.selectedParamListboxItem.itemList = self.selectedParams
        self.selectedParamListboxItem.nameList = self.selectedParams
        self.selectedParamListboxItem.listInBox()
               
        df = self.params
        for item in self.paramFilterItems:
            df = df[df[item.paramName].isin(np.array(item.selectedValues).astype(df[item.paramName].dtype))]
            if item.isFiltered and item.paramName not in self.filteredParams:
                self.filteredParams.append(item.paramName)
            elif not item.isFiltered and item.paramName in self.filteredParams:
                self.filteredParams.remove(item.paramName)
                
        filterParam = list(np.unique(self.selectedParams+[self.channelIdKey]))
        
        self.filteredParamDf = df[filterParam].reset_index(drop=True)
                
        for item in [self.lstSelectedParams.item(i) for i in range(self.lstSelectedParams.count())]:
            if item.text() in self.filteredParams:
                item.setBackgroundColor(pg.mkColor('y'))
            else:
                item.setBackgroundColor(pg.mkColor('w'))
                
        
        
       
        self.sigFilterChanged.emit()
        
    def updateParamList(self):

        selectedParams = [x.text() for x in self.lstParams.selectedItems()]
        l = list(self.params.columns)
        if len(l) == self.lstParams.count():
            currentList = [self.lstParams.item(i).text() for i in range(self.lstParams.count())]
            if all (l[i]==currentList[i] for i in range(self.lstParams.count())):
                return
        self.paramListboxItem.nameList = l
        self.paramListboxItem.itemList = l
        self.paramListboxItem.listInBox()
        for param in selectedParams:
            items = self.lstParams.findItems(param,QtCore.Qt.MatchExactly)
            if len(items)>0:
                item = items[0]
                item.setSelected(True)
                
                
class paramFilterItem(QObject,dataGuiBaseClass):
    
    #signals
    sigApplyFilter = QtCore.pyqtSignal()
    sigClearFilter = QtCore.pyqtSignal()
    sigUpdateParamValues = QtCore.pyqtSignal()
    def __init__(self, paramName,paramValues):
        """
        paramName: string showing the name of the parameter
        paramValues: list of values for the parameter
        """
        QObject.__init__(self)
    
        #create items
        lbl = QtGui.QLabel()
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        
        lst = QtGui.QListWidget()
        lst.setMinimumSize(QtCore.QSize(100, 50))
        lst.setMaximumSize(QtCore.QSize(200, 16777215))
        lst.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        lst.setAutoScroll(True)
        lst.setTabKeyNavigation(False)
        lst.setProperty("showDropIndicator", True)
        lst.setDragEnabled(False)
        lst.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        lst.setMovement(QtGui.QListView.Static)
        lst.setFlow(QtGui.QListView.TopToBottom)
        lst.setProperty("isWrapping", False)
        lst.setResizeMode(QtGui.QListView.Fixed)
        lst.setLayoutMode(QtGui.QListView.SinglePass)
        lst.setUniformItemSizes(False)
        lst.setWordWrap(False)
        lst.setSelectionRectVisible(False)
        
        btnApplyFilter = QtGui.QPushButton()
        btnApplyFilter.setMaximumSize(QtCore.QSize(100, 16777215))
        btnApplyFilter.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btnApplyFilter.setText('Apply Filter')
        btnApplyFilter.clicked.connect(self.applyFilter)

        
        btnClearFilter = QtGui.QPushButton()
        btnClearFilter.setMaximumSize(QtCore.QSize(100, 16777215))
        btnClearFilter.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btnClearFilter.setText('Clear Filter')
        btnClearFilter.clicked.connect(self.clearFilter)
        
        #Define attributes
        self.paramName = paramName
        self.paramValues  = paramValues
        self.label = lbl
        self.listbox = lst
        self.btnApplyFilter = btnApplyFilter

        self.btnClearFilter = btnClearFilter
        self.listboxItem = ListboxItem(self.listbox)
        self.selectedValues = paramValues
        self.isFiltered = False
        

        
        #Initiate the list and label
        self.label.setText(paramName)
        self.listboxItem.itemList = list(paramValues)
        self.listboxItem.nameList = list(paramValues)
        self.listboxItem.listInBox()
        
        #connect items to functions
        self.btnApplyFilter.clicked.connect(self.applyFilter)
        self.btnClearFilter.clicked.connect(self.clearFilter)
        

        
    def applyFilter(self):        
        
        if not self.listbox.selectedItems():
            return
        self.selectedValues =  [x.text() for x in self.listbox.selectedItems()]
        self.listboxItem.itemList = self.selectedValues
        self.listboxItem.nameList = self.selectedValues
        self.listboxItem.listInBox()
        self.isFiltered = True
        self.sigApplyFilter.emit()

        
    def clearFilter (self):
        
        self.listboxItem.itemList = self.paramValues
        self.listboxItem.nameList = self.paramValues
        self.listboxItem.listInBox()
        self.selectedValues = self.paramValues
        self.isFiltered = False
        self.sigClearFilter.emit()
        
        
    def updateParamValues (self,paramValues):
        
        self.paramValues = paramValues
        self.sigUpdateParamValues.emit()
        

            

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    frame = frmParameterFilter()
    
    # app.aboutToQuit.connect(app.deleteLater)
    # Frame = QtWidgets.QFrame()
    # ui = frmLoadData()
    # ui.setupUi(Frame)
    frame.show()
    app.exec_()

"""
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    frmParamFilter = QtGui.QFrame()
    ui = Ui_frmParamFilter()
    ui.setupUi(frmParamFilter)
    frmParamFilter.show()
    app.exec_()
    
"""

