
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QShortcut



from PyQt5.QtCore import QObject, pyqtSignal


import os,sys

from os import path
dirname = path.dirname(__file__)
fname = "frmWindowLayout.ui"
fpath = path.join(dirname, fname)

from dataGuiBaseClasses import *
from constants import *



class frmWindowLayout(QtWidgets.QFrame,dataGuiBaseClass):

    def __init__(self):
        super().__init__()
        uic.loadUi(fpath, self)


        #create shortcut for deselecting for all the lists
        self.lstWidgetList = [getattr(self, n) for n in dir(self) if 'lst' in n]
        for lst in self.lstWidgetList:
            QShortcut(QKeySequence(QtCore.Qt.Key_Escape), lst,  lst.clearSelection,context=QtCore.Qt.WidgetShortcut)
        
        
      
        
        
        #make a litboxitem
        self.windowListboxItem = ListboxItem(self.lstWindow)
        

        
        #connect doubleclick on window list to a function "showOnTop"
        self.lstWindow.doubleClicked.connect(self.showOnTop)
        self.lstWindow.itemSelectionChanged.connect (self.updatePlotLayouts)
        
        #make list of tables
        self.tableList = [self.tblPlot1, self.tblPlot2]
        self.tableLabelList = [self.lblCurrentWindow1,self.lblCurrentWindow2]
        
        #create shortcut for tblPlot 
        QShortcut(QKeySequence(QtCore.Qt.Key_Escape), self.tblPlot1,  self.tblPlot1.clearSelection,context=QtCore.Qt.WidgetShortcut)
        QShortcut(QKeySequence(QtCore.Qt.Key_Escape), self.tblPlot2,  self.tblPlot2.clearSelection,context=QtCore.Qt.WidgetShortcut)   
        
        
    
        
        self.selectedWindexes=[]


    
    def showOnTop (self):
        if not self.lstWindow.selectedIndexes():
            return
        windex = self.lstWindow.selectedIndexes()[0].row()
        
        self.ws[windex].setWindowState(self.ws[windex].windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        
        
    def updatePlotLayouts(self):
        self.selectedWindexes = [x.row() for x in self.lstWindow.selectedIndexes()]
        
        if not self.ws :
            return

        for i in range(len(self.tableList)):
            table = self.tableList[i]
            label = self.tableLabelList[i]
            label.setText('')
            #clear the table
            table.clear()
            for i in range(table.rowCount()):
                for j in range(table.columnCount()):
                    table.setItem(i,j,QTableWidgetItem())
                    # table.setSpan(i,j,1,1)
                    # cell_index = table.model().index(i,j)
                    # print(i,j)
                    # table.selectionModel().select(cell_index,
                            # QtCore.QItemSelectionModel.Select)
                        
        if len(self.lstWindow.selectedItems())==1:
            windex = self.lstWindow.selectedIndexes()[0].row()
            self.updatePlotLayout(self.tableList[0],self.tableLabelList[0],windex)
            for table in self.tableList[1:]:
                table.windex=None
        
        if len(self.lstWindow.selectedItems())>1:
            for i in range(2):
                windex = self.lstWindow.selectedIndexes()[i].row()
                self.updatePlotLayout(self.tableList[i],self.tableLabelList[i],windex)
            
    
    def updatePlotLayout(self,tblPlot,lblCurrentWindow,windex):
        locations = [x.location for x in self.ps[windex]]

        for i in range(len(locations)):
            row,column,rowSpan,columnSpan = locations[i]         
            item = tblPlot.item(row,column)
            item.setText('Plot %i' % i)
            if rowSpan+columnSpan>2:
                tblPlot.setSpan(row,column,rowSpan,columnSpan)
            item.setBackground(restOfPenColors[i%len(restOfPenColors)])
            item.setTextAlignment(plotTableAlignment)
            item.setFont(plotTableFont)
            
        lblCurrentWindow.setText('Window %i' %windex)
        tblPlot.windex = windex
        
        
    def updateWindowList (self):
        selectedIndexes = [x.row() for x in self.lstWindow.selectedIndexes()]
        nWindows = len(self.ws)
        l = ['Window %i' %index for index in range(nWindows)]
        self.windowListboxItem.nameList = l
        self.windowListboxItem.itemList = l
        self.windowListboxItem.listInBox()
        for i in selectedIndexes:
            self.lstWindow.item(i).setSelected(True)
        


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    frame = frmWindowLayout()
    
    # app.aboutToQuit.connect(app.deleteLater)
    # Frame = QtWidgets.QFrame()
    # ui = frmLoadData()
    # ui.setupUi(Frame)
    frame.show()
    app.exec_()
        

# if __name__ == "__main__":
    # import sys
    # app = QtGui.QApplication(sys.argv)
    # frmWindowLayout = QtGui.QFrame()
    # ui = Ui_frmWindowLayout()
    # ui.setupUi(frmWindowLayout)
    # frmWindowLayout.show()
    # app.exec_()

