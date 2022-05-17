

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QShortcut



from PyQt5.QtCore import QObject, pyqtSignal


import os,sys
from os import path
dirname = path.dirname(__file__)
fname = "frmMain.ui"
fpath = path.join(dirname, fname)

from dataGuiBaseClasses import *


backGround = '#FFF'
foreGround = 'k'

pg.setConfigOption('background', backGround)
pg.setConfigOption('foreground', foreGround)
pg.setConfigOptions(antialias=True)

from frmLoadData import frmLoadData
from frmShotChannel import frmShotChannel
from frmComAction import frmComAction
from frmParameterFilter import frmParameterFilter



class frmMainWindow(QtWidgets.QFrame, dataGuiBaseClass):

    def __init__(self):
        super().__init__()
        uic.loadUi(fpath, self)

        dataGuiBaseClass().reset()

        self.lstWidgetList = [getattr(self, n) for n in dir(self) if 'lst' in n]
        for lst in self.lstWidgetList:
            QShortcut(QKeySequence(QtCore.Qt.Key_Escape), lst,  lst.clearSelection,context=QtCore.Qt.WidgetShortcut)


        #initiate the frames

        #set frmLoadData
        self.frmLoadData = frmLoadData()
        # self.frmLoadData.setupUi(self.frmLoadData)
        self.gridLayout_2.addWidget(self.frmLoadData, 0, 0, 1, 1)


        #set frmComAction

        self.Ui_frmComAction = frmComAction(displayType = 'list')
        # self.Ui_frmComAction.setupUi(self.frmComAction)
        self.gridLayout.addWidget(self.Ui_frmComAction, 0, 2, 2, 1)




        #make paramFilterLayout

        self.Ui_frmParamFilter = frmParameterFilter()
        # self.Ui_frmParamFilter.setupUi(self.frmParameterFilter)
        self.gloParamFilter.addWidget(self.Ui_frmParamFilter, 0, 0, 1, 1)


        self.Ui_frmComAction_2 = frmComAction(displayType = 'table')
        # self.Ui_frmComAction_2.setupUi(self.frmComAction_2)
        self.gridLayout_5.addWidget(self.Ui_frmComAction_2, 0, 1, 2, 1)



        #connect signals

        self.frmLoadData.sigLoaded.connect(self.updateAfterLoading)


        #self.Ui_frmShotChannel.sigChannelListDoubleClicked.connect(functools.partial(self.plotBasic,self.Ui_frmShotChannel,self.Ui_frmWindowLayout,self.Ui_frmAction1))

        self.Ui_frmParamFilter.sigFilterChanged.connect(self.updateChannelTable)


        #connect two window lists
        self.Ui_frmComAction.sigWindowOpened.connect(self.Ui_frmComAction_2.updateAfterWindowOpened)
        self.Ui_frmComAction_2.sigWindowOpened.connect(self.Ui_frmComAction.updateAfterWindowOpened)


        self.Ui_frmComAction.sigIvDataAdded.connect(self.updateAfterLoading)
        self.Ui_frmComAction_2.sigIvDataAdded.connect(self.updateAfterLoading)
        self.Ui_frmComAction.sigArithmeticsDataAdded.connect(self.updateAfterLoading)
        self.Ui_frmComAction_2.sigArithmeticsDataAdded.connect(self.updateAfterLoading)






    def updateAfterLoading(self):

        self.Ui_frmComAction.updateChannelOptions(paramDf = self.params)
        self.Ui_frmComAction_2.updateChannelOptions(paramDf = self.Ui_frmParamFilter.filteredParamDf)
        self.Ui_frmParamFilter.updateParamList()

    def updateChannelTable(self):
        self.Ui_frmComAction_2.updateChannelOptions(self.Ui_frmParamFilter.filteredParamDf)




    def openNewWindow(self):
        windex = len(self.ws)
        glw = pg.GraphicsLayoutWidget()
        glw.resize(800,600)

        name = 'Window %i' % windex
        glw.setWindowTitle(name)
        glw.show()
        glw.windex =windex



        self.ws.append(glw)
        self.ps.append([])
        self.ds.append([])

        self.sigWindowOpened.emit()
        return windex

    def openNewWindow1(self):
        glw = pg.GraphicsLayoutWidget()
        glw.resize(800,600)
        windex = self.ws.count()
        name = 'Window %i' % windex
        glw.setWindowTitle(name)
        glw.show()
        glw.index =windex

        self.Ui_frmWindowLayout.windowListboxItem.nameList.append(name)
        self.Ui_frmWindowLayout.windowListboxItem.itemList.append(glw)
        self.Ui_frmWindowLayout.windowListboxItem.listInBox()

        return windex



    def addNewPlot(self,windex,location):
        pindex = len(self.ps[windex])
        p = pg.PlotItem()
        p.pindex = pindex
        p.location = location
        p.addLegend()
        p.legend.setScale(self.legendScale)
        self.ws[windex].addItem(p,location[0],location[1],location[2],location[3])
        self.ps[windex].append(p)
        self.ds[windex].append([])
        return pindex

    def addNewDataItem(self, windex,pindex,plotType,dataParam,processParam):

        dindex = len(self.ds[windex][pindex])


        pen = pg.mkPen(self.penColors[dindex%len(self.penColors)],width=self.penWidth)
        #pen = pg.mkPen('k',width=1)
        item = pg.PlotDataItem(pen=pen)
        item.plotType = plotType
        item.dataParam = dataParam
        item.dindex = dindex
        item.processParam = processParam
        item.pen = pen

        item.rawData = self.getData(dataParam)

        self.exeProcessFunction(item)
        self.ps[windex][pindex].addItem(item)
        self.ds[windex][pindex].append(item)
        return dindex

    def addNewImageItem (self, windex,pindex,plotType,dataParam,processParam):
        dindex = len(self.ds[windex][pindex])


        item = pg.ImageItem()
        item.plotType = plotType
        item.dataParam = dataParam
        item.dindex = dindex
        item.processParam = processParam


        item.rawData = self.getData(dataParam)

        self.exeProcessFunction(item)
        self.ps[windex][pindex].addItem(item)
        self.ds[windex][pindex].append(item)
        return dindex



    def updateYAxis(self,ax,*args,**kargs):
        vb = ax.linkedView()
        dataItems = [x for x in vb.addedItems if type(x)==type(pg.PlotDataItem())]
        axisArg = self.axisArgs
        yUnits = np.unique([item.yUnit for item in dataItems])
        names = [item.yName for item in dataItems]
        yUnit,yLabel = '',''
        if len(yUnits)==1:
            yUnit = yUnits[0]
        commonWords = []
        for word in names[0].split(' '):
            present = True
            for name in names:
                if word.upper() not in [x.upper() for x in name.split(' ')]:
                    present = False
            if present:
                commonWords.append(word)
        commonLabels =[word for word in commonWords if word.upper() in self.plotYLabelTypes or word in self.plotYLabelTypes]
        if len(commonLabels)>0:
            maxLen = np.max([len(x) for x in commonLabels])
            yLabel = [x for x in commonLabels if len(x)==maxLen][0]

        ax.setLabel(yLabel,units = yUnit,**axisArg['labelStyleArgs'])

        ax.tickFont = axisArg['tickFont']
        ax.setPen(axisArg['axisPen'])
        ax.setStyle(tickLength = axisArg['tickLength'])

        ax.setWidth(w=axisArg['yAxisWidth'])
        ax.setStyle(tickTextOffset = axisArg['yTickTextOffset'])
        return ax

    def updateXAxis(self,ax,*args,**kargs):
        vb = ax.linkedView()
        dataItems = [x for x in vb.addedItems if type(x)==type(pg.PlotDataItem())]
        axisArg = self.axisArgs
        xUnits = np.unique([item.xUnit for item in dataItems])
        names = [item.xName for item in dataItems]
        xUnit,xLabel = '',''

        if len(xUnits)==1:
            xUnit = xUnits[0]
        commonWords = []
        for word in names[0].split(' '):
            present = True
            for name in names:
                if word.upper() not in [x.upper() for x in name.split(' ')]:
                    present = False
            if present:
                commonWords.append(word)
        commonLabels =[word for word in commonWords if word.upper() in self.plotXLabelTypes or word in self.plotYLabelTypes]
        if len(commonLabels)>0:
            maxLen = np.max([len(x) for x in commonLabels])
            xLabel = [x for x in commonLabels if len(x)==maxLen][0]

        ax.setLabel(xLabel,units = xUnit,**axisArg['labelStyleArgs'])
        ax.tickFont = axisArg['tickFont']
        ax.setPen(axisArg['axisPen'])
        ax.setStyle(tickLength = axisArg['tickLength'])
        ax.setHeight(h=axisArg['xAxisHeight'])
        ax.setStyle(tickTextOffset = axisArg['xTickTextOffset'])
        return ax

    def updateViews(self,p):
        vbs = [x for x in p.scene().items() if type(x) ==type(pg.ViewBox())][1:]
        for vb in vbs:
            vb.setGeometry(p.vb.sceneBoundingRect())
            ## need to re-update linked axes since this was called
            ## incorrectly while views had different shapes.
            ## (probably this should be handled in ViewBox.resizeEvent)
            vb.linkedViewChanged(p.vb,vb.XAxis)





    def plotBasic(self, shotChannelItem, windowLayoutItem,actionItem):

        nPlotRow,nPlotColumn = 1,1
        windex,pindexes,dataParam,processParam = self.getInitialInfo(shotChannelItem, windowLayoutItem,actionItem,nPlotRow=nPlotRow,nPlotColumn=nPlotColumn)
        if windex ==None:
            return

        #prepare dataParams
        dataParamList = [dataParam[dataParam.index==i] for i in range(len(dataParam))]
        pTypeList = self.pTypeBasicKey
        for dataParam in dataParamList:
            #dindex = self.addNewDataItem(windex,pindexes[0][0],pTypeList, dataParam,processParam)
            dindex = self.addNewDataItem(windex,pindexes[0][0],pTypeList, dataParam,processParam)
        self.updateXAxis(self.ps[windex][pindexes[0][0]].getAxis('bottom'))
        self.updateYAxis(self.ps[windex][pindexes[0][0]].getAxis('left'))

        windowLayoutItem.lstWindow.item(windex).setSelected(True)
        windowLayoutItem.updatePlotLayouts()
        if self.selectPlot:
            windowLayoutItem.tblPlot1.item(self.tempSelectedRow,self.tempSelectedColumn).setSelected(True)





    def getInitialInfo(self,shotChannelItem, windowLayoutItem,actionItem,
                       nPlotRow=1,nPlotColumn=1):
      #print ("begin getInitialInfo")
      # return if shotnum or channel is not selected
      if not shotChannelItem.selectedChannelIDs:
        print ("shotchannel not selected")
        return None,None,None,None

      if len(windowLayoutItem.lstWindow.selectedItems())>1:
        print ("too many windows")
        return None,None,None,None
      windex,location = self.getStartingLocation(windowLayoutItem)
      pindexes = self.getPindexes(windex=windex,location=location, nPlotRow=nPlotRow, nPlotColumn=nPlotColumn)
      if pindexes == None:
        print("no pindex")
        return  None,None,None,None
      #print ("made it")
      # get indexes for channels

      processParam = actionItem.getProcessParams()
      dataParam=self.params[self.params[self.channelIdKey].isin(np.array(shotChannelItem.selectedChannelIDs).astype(self.params[self.channelIdKey].dtype))].reset_index(drop=True)
      return windex,pindexes,dataParam,processParam



    def plotPsd(self,shotChannelItem, windowLayoutItem,actionItem):
        self.times = []

        nPlotRow,nPlotColumn = 2,1
        windex,pindexes,dataParam,processParam = self.getInitialInfo(shotChannelItem, windowLayoutItem,actionItem,nPlotRow=nPlotRow,nPlotColumn=nPlotColumn)
        if windex == None:
            return

        #prepare dataParams
        dataParamList = [dataParam[dataParam.index==i] for i in range(len(dataParam))]
        pTypeList = [self.pTypePsdKey,self.pTypeBasicKey]

        for i in range(2):
            for dataParam in dataParamList:
                dindex = self.addNewDataItem(windex,pindexes[i][0],pTypeList[i], dataParam,processParam)
            self.updateXAxis(self.ps[windex][pindexes[i][0]].getAxis('bottom'))
            self.updateYAxis(self.ps[windex][pindexes[i][0]].getAxis('left'))

        xRegion = pg.LinearRegionItem()
        xRegion.xRegionSlot = None
        xRegion.setZValue(10)
        xRegion.sigRegionChanged.connect(lambda: self.updateXRegion(windex,pindexes[0][0],xRegion,**self.keys))
        self.ps[windex][pindexes[1][0]].addItem(xRegion,ignoreBounds=True)
        self.ps[windex][pindexes[0][0]].setAutoVisible(y=True)
        self.ps[windex][pindexes[1][0]].setAutoVisible(y=True)
        xRegion.setRegion([0.018,0.020])
        #xRegion.setRegion([0.018, 0.020])
        windowLayoutItem.lstWindow.item(windex).setSelected(True)
        windowLayoutItem.updatePlotLayouts()
        if self.selectPlot:
            windowLayoutItem.tblPlot1.item(self.tempSelectedRow,self.tempSelectedColumn).setSelected(True)


    def plotCsd(self,shotChannelItem, windowLayoutItem,actionItem):
        self.times = []

        nPlotRow,nPlotColumn = 4,1
        windex,pindexes,dataParam,processParam = self.getInitialInfo(shotChannelItem, windowLayoutItem,actionItem,nPlotRow=nPlotRow,nPlotColumn=nPlotColumn)
        if windex == None:
            return

        #prepare dataParams
        pTypeList = [self.pTypeCsdKey,self.pTypeCohKey,self.pTypePhaseKey,self.pTypeBasicKey]
        paramList  = [dataParam[dataParam.index==i] for i in range(len(dataParam))]

        self.addNewDataItem(windex,pindexes[0][0],pTypeList[0], dataParam,processParam)
        yAx,xAx = self.ps[windex][pindexes[0][0]].getAxis('left'),self.ps[windex][pindexes[0][0]].getAxis('bottom')
        self.updateYAxis(yAx)
        self.updateXAxis(xAx)
        #self.ps[windex][pindexes[0][0]].legend.hide()
        xAx.setStyle(tickLength = -self.tickLength, showValues=False)
        xAx.showLabel(False)
        xAx.setMaximumHeight(0)

        self.addNewDataItem(windex,pindexes[1][0],pTypeList[1], dataParam,processParam)
        yAx,xAx = self.ps[windex][pindexes[1][0]].getAxis('left'),self.ps[windex][pindexes[1][0]].getAxis('bottom')
        self.ps[windex][pindexes[1][0]].legend.hide()
        self.updateYAxis(yAx)
        self.updateXAxis(xAx)
        xAx.setStyle(tickLength = -self.tickLength, showValues=False)
        xAx.showLabel(False)
        xAx.setMaximumHeight(0)

        self.addNewDataItem(windex,pindexes[2][0],pTypeList[2], dataParam,processParam)
        self.updateYAxis(self.ps[windex][pindexes[2][0]].getAxis('left'))
        self.updateXAxis(self.ps[windex][pindexes[2][0]].getAxis('bottom'))
        self.ps[windex][pindexes[2][0]].legend.hide()
        self.ps[windex][pindexes[2][0]].getAxis('bottom').setStyle(tickLength = -self.tickLength)

        self.ps[windex][pindexes[0][0]].setXLink(self.ps[windex][pindexes[2][0]])
        self.ps[windex][pindexes[1][0]].setXLink(self.ps[windex][pindexes[2][0]])
        #self.ps[windex][pindexes[2][0]].vb.sigResized.connect(functools.partial(self.linkMaxHeight,self.ps[windex][pindexes[2][0]].vb,[self.ps[windex][pindexes[1][0]],self.ps[windex][pindexes[0][0]]]))
        #self.ps[windex][pindexes[2][0]].vb.sigResized.connect(functools.partial(self.TESTPRINT,self.ps[windex][pindexes[2][0]]))
        #self.ws[windex].sigDeviceRangeChanged.connect(functools.partial(self.linkMaxHeight,windex,[self.ps[windex][pindexes[0][0]],self.ps[windex][pindexes[1][0]],self.ps[windex][pindexes[2][0]],self.ps[windex][pindexes[3][0]]]))

        for i in range(2):
            dindex = self.addNewDataItem(windex,pindexes[3][0],pTypeList[3], paramList[i],processParam)
            #self.updateXAxis(self.ps[windex][pindexes[i][0]].getAxis('bottom'))
        self.updateYAxis(self.ps[windex][pindexes[3][0]].getAxis('left'))
        self.updateXAxis(self.ps[windex][pindexes[3][0]].getAxis('bottom'))

        #self.ps[windex][pindexes[0][0]].getAxis('bottom').label.hide()
        #self.ws[windex].sigDeviceRangeChanged.connect(functools.partial(self.linkMaxHeight,windex,[pindexes[0][0],pindexes[1][0],pindexes[2][0],pindexes[3][0]]))
        self.ws[windex].sigDeviceRangeChanged.connect(functools.partial(self.linkMaxHeight,windex,[pindexes[0][0],pindexes[1][0],pindexes[2][0],pindexes[3][0]]))
        xRegion = pg.LinearRegionItem()
        xRegion.xRegionSlot = None
        xRegion.setZValue(10)
        xRegion.sigRegionChanged.connect(lambda: self.updateXRegion(windex,pindexes[0][0],xRegion,**self.keys))
        xRegion.sigRegionChanged.connect(lambda: self.updateXRegion(windex,pindexes[1][0],xRegion,**self.keys))
        xRegion.sigRegionChanged.connect(lambda: self.updateXRegion(windex,pindexes[2][0],xRegion,**self.keys))
        self.ps[windex][pindexes[3][0]].addItem(xRegion,ignoreBounds=True)
        self.ps[windex][pindexes[0][0]].setAutoVisible(y=True)
        self.ps[windex][pindexes[1][0]].setAutoVisible(y=True)
        self.ps[windex][pindexes[2][0]].setAutoVisible(y=True)
        xRegion.setRegion([0.018,0.020])
        #xRegion.setRegion([0.018, 0.020])
        windowLayoutItem.lstWindow.item(windex).setSelected(True)

        windowLayoutItem.updatePlotLayouts()
        if self.selectPlot:
            windowLayoutItem.tblPlot1.item(self.tempSelectedRow,self.tempSelectedColumn).setSelected(True)


    def TESTPRINT(self,view):
        print (view.height())


    def linkMaxHeight(self,windex,pindexes):
        ##START HERE
        p=pg.PlotItem()
        w = self.ws[windex]
        items,locs = [x for x in w.ci.items.keys()],[x for x in w.ci.items.values()]

        ps= [items[i] for i in range(len(items)) if type(items[i])==type(p)]

        plocs=[locs[i] for i in range(len(items)) if type(items[i])==type(p)]

        rows,columns = [],[]

        for ploc in plocs:
            rows+=[x[0] for x in ploc]
            columns+=[x[1] for x in ploc]
        rows,columns = np.unique(rows), np.unique(columns)
        pUnitHeight = (w.height()-self.wHeightOffset-self.wHeightInc*len(rows))/len(rows)
        pUnitWidth  = (w.width()-self.wWidthOffset-self.wWidthInc*len(columns))/len(columns)

        for column in columns:
            indexes = [i for i in range(len(ps)) if column in [x[1] for x in plocs[i]]]
            rowSpans = [len([x for x in plocs[i] if column==x[1]]) for i in indexes]
            totalRows = np.sum(rowSpans)
            availHeight = pUnitHeight*totalRows
            for i in indexes:
                p=ps[i]
                cItems = p.childItems()
                availHeight -= cItems[0].height()+cItems[1].height()+self.pHeightOffset
            vUnitHeight = availHeight/totalRows

            for i in range(len(indexes)):
                p=ps[indexes[i]]
                cItems = p.childItems()
                p.setMaximumHeight(vUnitHeight*rowSpans[i]+cItems[0].height()+cItems[1].height()+self.pHeightOffset)
                p.setMinimumHeight(vUnitHeight*rowSpans[i]+cItems[0].height()+cItems[1].height()+self.pHeightOffset)

        for row in rows:
            indexes = [i for i in range(len(ps)) if row in [x[0] for x in plocs[i]]]
            columnSpans = [len([x for x in plocs[i] if row==x[0]]) for i in indexes]
            totalColumns = np.sum(columnSpans)
            availWidth = pUnitWidth*totalColumns
            for i in indexes:
                p=ps[i]
                cItems = p.childItems()
                availWidth -= cItems[2].width()+cItems[3].width()+self.pWidthOffset
            vUnitWidth = availWidth/totalColumns

            for i in range(len(indexes)):
                p=ps[indexes[i]]
                cItems = p.childItems()
                p.setMaximumWidth(vUnitWidth*columnSpans[i]+cItems[2].width()+cItems[3].width()+self.pWidthOffset)
                p.setMinimumWidth(vUnitWidth*columnSpans[i]+cItems[2].width()+cItems[3].width()+self.pWidthOffset)

        """
        plots = [self.ps[windex][i] for i in pindexes]
        totalHeight = 0

        #self.ws[windex].updateScene()
        for p in plots:
            totalHeight+=p.height()
        print self.ws[windex].geometry().height()-totalHeight


        print self.ws[windex].geometry()

        plots = [self.ps[windex][i] for i in pindexes]

        for p in plots:
            p.setMaximumHeight(12000)
        self.ws[windex].ci._updateView()

        totalHeight = 0

        #self.ws[windex].updateScene()
        for p in plots:
            totalHeight+=p.vb.height()
            #print v.height()
        height = totalHeight/(len(plots)+0.0)


        for p in plots:
            #p.setMaximumHeight(p.height()+height-p.vb.height())
            p.setMinimumHeight(p.height()+height-p.vb.height())
        """






    def getProcessParam(self):
        # get parameters


        nperseg = self.cmbNperseg.currentText()
        if nperseg =='-':
            nperseg = 512
        elif not nperseg.isdigit():
            nperseg = 512
        else:
            nperseg = int (nperseg)

        overlap = self.sbxOverlap.text()
        if overlap =='':
            overlap = 50
        elif not overlap.isdigit():
            overlap = 50
        else:
            overlap = int(overlap)
        processParams = {self.isSmoothKey:self.cbxSmooth.isChecked(),
                        self.nSmoothKey: self.ledNSmooth.text(),
                        self.isDcCancelHeadKey: self.rbtDcCancelHead.isChecked(),
                        self.nDcCancelHeadKey: self.ledNDcCancelHead.text(),
                        self.isDcCancelTailKey: self.rbtDcCancelTail.isChecked(),
                        self.nDcCancelTailKey: self.ledNDcCancelTail.text(),
                        self.npersegKey:nperseg,
                        self.isUncalibratedSignalKey:self.cbxUncalibratedSignal.isChecked(),
                        self.isNormalizePsdKey:self.cbxNormalizePsd.isChecked(),
                        self.overlapKey:overlap
                        }
        return processParams

    def getParams(self,shotChannelItem):

        param = self.params[self.params[self.channelIdKey].isin(shotChannelItem.selectedChannelIDs)].reset_index(drop=True)
        return param

    def getData (self,param):

        data = pd.DataFrame()
        for shotNum in list (param[self.shotNumKey].unique()):
            dataIndex = [x for x in range(len(self.dataList)) if self.dataList[x][self.shotNumKey]==str(shotNum)][0]
            tempData = self.dataList[dataIndex][self.dfKey]
            tempParam = param[param[self.shotNumKey]==shotNum].reset_index(drop=True)
            channels = list(tempParam[self.channelDescriptionKey].unique())
            channelMask = np.zeros(len(tempData.columns)).astype(bool)
            for channelName in channels:
                para = tempParam[tempParam[self.channelDescriptionKey]==channelName].reset_index(drop=True)
                channelId = para[self.channelIdKey][0]
                channelMask = channelMask | (tempData.columns==channelId)
            tempData = tempData[tempData.columns[channelMask]]
            data= pd.concat([data, tempData], axis=1).reset_index(drop=True)
        null = pd.isnull(data).any(1).nonzero()[0]
        if len(null)>0:
            data = data.ix[:(null[0]-1),:]
        return data



    def activateWindow(self):
        if len(self.Ui_frmWindowLayout.lstWindow.selectedIndexes())==0:
            return
        windex = self.Ui_frmWindowLayout.lstWindow.selectedIndexes()[0].row()
        window = self.ws[windex]
        window.setWindowState(window.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        window.activateWindow()


    def updateAvailChannel(self):

        for item in [self.Ui_frmShotChannel.lstChannel.item(i) for i in range(self.Ui_frmShotChannel.lstChannel.count())]:
            item.setFlags(item.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            item.setBackgroundColor(self.listBgColor)

        if len(self.Ui_frmShotChannel.lstLoadedShot.selectedItems())==0:
            return

        shotNums = [x.text() for x in self.Ui_frmShotChannel.lstLoadedShot.selectedItems()]
        for item in [self.Ui_frmShotChannel.lstChannel.item(i) for i in range(self.Ui_frmShotChannel.lstChannel.count())]:
            count = 0
            for shotNum in shotNums:
                tempParam = self.params[self.params[self.shotNumKey]==int(shotNum)]
                if item.text() in list(tempParam[self.channelDescriptionKey]):
                    count +=1

            if count == 0: #if the channel cannot be found in any shots selected
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable & ~QtCore.Qt.ItemIsEnabled)
            elif count < len(shotNums):#only some but not all the shots selected have the channel
                item.setBackgroundColor(self.listIncompleteMatchBgColor)


    def updateAvailShot (self):
        for item in [self.Ui_frmShotChannel.lstLoadedShot.item(i) for i in range(self.Ui_frmShotChannel.lstLoadedShot.count())]:
            item.setFlags(item.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            item.setBackgroundColor(self.listBgColor)

        if len(self.Ui_frmShotChannel.lstChannel.selectedItems())==0:
            return

        channels = [x.text() for x in self.Ui_frmShotChannel.lstChannel.selectedItems()]
        for item in [self.Ui_frmShotChannel.lstLoadedShot.item(i) for i in range(self.Ui_frmShotChannel.lstLoadedShot.count())]:
            count = 0
            for channel in channels:
                tempParam = self.params[self.params[self.channelDescriptionKey]==channel]
                if int(item.text()) in list(tempParam[self.shotNumKey]):
                    count +=1

            if count == 0: #if the channel cannot be found in any shots selected
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable & ~QtCore.Qt.ItemIsEnabled)
            elif count < len(channels):#only some but not all the shots selected have the channel
                item.setBackgroundColor(self.listIncompleteMatchBgColor)

    def selectPlotLayout(self,windex=None, pindexes=[]):
        if windex==None or not pindexes:
            return
        locations = [self.ps[windex][i] in pindexes]
        for location in locations:
            row, column = location[:2]
            self.Ui_frmWindowLayout.tblPlot1.item(row,column).setSelected(True)


    def getPlotItemLocation(self,windex=None,pNumber=None):
        if windex==None or pNumber ==None:
            return None,None
        gl = self.Ui_frmWindowLayout.windowListboxItem.itemList[windex].ci
        items = gl.items.keys()
        pindexes = [i for i in range(len(items)) if type(items[i])==type(PlotItem1D())]
        locations = gl.items.values()
        for pindex in pindexes:
            if items[pindex].number == pNumber:
                return items[pindex],locations[pindexes]
        return None,None

    def getStartingLocation (self,windowLayoutItem):
        self.selectPlot = False #select the plot in the layout after plotting

        # return if # of cells have conflict with occupied cells (not for basic plot)
        if not windowLayoutItem.lstWindow.selectedItems():
            windex = self.openNewWindow()

        else:
            windex = windowLayoutItem.lstWindow.selectedIndexes()[0].row()

        if not windowLayoutItem.tblPlot1.selectedItems():
            # find the lowest column and highest to row to start
            # check for interference
            row,column = self.findAvailableLocation(windex)
            location = (row,column,1,1)
        else:
            location = locationToPlot(windowLayoutItem.tblPlot1)
            self.selectPlot=True
            self.tempSelectedRow,self.tempSelectedColumn = windowLayoutItem.tblPlot1.selectedItems()[0].row(),windowLayoutItem.tblPlot1.selectedItems()[0].column()
        return windex,location


    def findAvailableLocation (self,windex):
        if len(self.ps[windex])==0:
            return 0,0

        locations = [x.location for x in self.ps[windex]]
        minColumn = np.min([x[1] for x in locations])
        pLocs = [x for x in locations if x[1]==minColumn]
        maxRow = np.max([x[0] for x in pLocs])
        lastLoc = [x for x in pLocs if x[0] == maxRow][0]
        row,column = lastLoc[0]+lastLoc[2],lastLoc[1]
        return row,column

    def getPindexes(self, windex=None,location=(0,0,1,1), nPlotRow=1, nPlotColumn=1):
        if windex ==None:
            return None
        rowSpan,columnSpan = location[2],location[3]
        occupiedLocations = [x.location for x in self.ps[windex]]

        pindexes = []

        planLocations = []
        for i in range(nPlotRow):
            planRow = []
            for j in range(nPlotColumn):
                planRow.append((location[0]+i*rowSpan,location[1]+j*columnSpan,rowSpan,columnSpan))
            planLocations.append(planRow)

        #check if location is on one of the plots
        if planLocations[0][0] in occupiedLocations:
            for i in range(nPlotRow):
                rowOfPindexes = []
                for j in range(nPlotColumn):
                    if planLocations[i][j] not in occupiedLocations:
                        return None
                    else:
                        rowOfPindexes.append(occupiedLocations.index(planLocations[i][j]))
                pindexes.append(rowOfPindexes)
            return pindexes

        else:
            for i in range(nPlotRow):
                for j in range(nPlotColumn):
                    if planLocations[i][j] in occupiedLocations:
                        return None

            for i in range(nPlotRow):
                rowOfPindexes = []
                for j in range(nPlotColumn):
                    pindex = self.addNewPlot(windex,planLocations[i][j])
                    rowOfPindexes.append(pindex)

                pindexes.append(rowOfPindexes)
            return pindexes

    def processFunctionBasic (self,pItem, *args,**kargs):

        para = pItem.dataParam.reset_index(drop=True).ix[0]
        y = np.array(pItem.rawData[para[self.channelIdKey]])


        #calibration and unit
        if pItem.processParam[self.isUncalibratedSignalKey]:
            yUnit = para[self.Y_Unit_LabelKey]
        else:
            y = y*float(para[self.calibrationKey])
            yUnit = para[self.unitKey]

        #smooth
        if pItem.processParam[self.isSmoothKey]:
            if pItem.processParam[self.nSmoothKey].isdigit():
                if 0<int(pItem.processParam[self.nSmoothKey]) and int(pItem.processParam[self.nSmoothKey]) <len(y):
                    y = smooth(y,int(pItem.processParam[self.nSmoothKey]))

        #dc cancel
        if pItem.processParam[self.isDcCancelHeadKey]:
            if pItem.processParam[self.nDcCancelHeadKey].isdigit():
                if 0<int(pItem.processParam[self.nDcCancelHeadKey]) and int(pItem.processParam[self.nDcCancelHeadKey]) <len(y):
                    y = y - np.average(y[:int(pItem.processParam[self.nDcCancelHeadKey])])
        elif pItem.processParam[self.isDcCancelTailKey]:
            if pItem.processParam[self.nDcCancelTailKey].isdigit():
                if 0<int(pItem.processParam[self.nDcCancelTailKey]) and int(pItem.processParam[self.nDcCancelTailKey]) <len(y):
                    y = y - np.average(y[-int(pItem.processParam[self.nDcCancelTailKey]):])
        # create x array
        x = float(para[self.X0Key])+float(para[self.Delta_XKey])*np.arange(len(y))
        xName = para[self.X_DimensionKey]
        xUnit = ''
        if xName.lower()=='time':
            xUnit = 's'
        yName = para[self.channelDescriptionKey]
        name = '%i : %s'%(para[self.shotNumKey],para[self.channelDescriptionKey][:20])
        pItem.setData(x,y, name=name)
        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = xName
        pItem.yName = yName
        #return pItem



    def processFunctionPsd (self,pItem, *args,**kargs):

        para = pItem.dataParam.reset_index(drop=True).ix[0]
        s = np.array(pItem.rawData[para[self.channelIdKey]])
        t = float(para[self.X0Key])+float(para[self.Delta_XKey])*np.arange(len(s))

        nperseg = pItem.processParam[self.npersegKey]
        overlap = pItem.processParam[self.overlapKey]
        noverlap = nperseg*overlap//100

        fs = float(1/(t[1]-t[0]))

        if not pItem.processParam[self.isUncalibratedSignalKey]:
            s = s*float(para[self.calibrationKey])

        if self.xRegionKey in pItem.processParam:
            xRegion = pItem.processParam[self.xRegionKey]
        else:
            xRegion = (t[0],t[-1])


        mask1 = (t>xRegion[0])
        mask2 = (t<xRegion[1])
        mask = mask1 & mask2
        t,s = t[mask],s[mask]


        if len(t)<nperseg:
            nperseg = len(t)
            noverlap = None


        if para[self.X_DimensionKey].lower()=='time':
            xName = 'Frequency'
            xUnit = 'Hz'
        else:
            xName = ''
            xUnit = ''

        if pItem.processParam[self.isNormalizePsdKey]:
            s = s/np.average(s)
            yUnit = ''
        else:
            if pItem.processParam[self.isUncalibratedSignalKey]:
                yUnit = ' %s<sup>2</sup>/%s'  %(para[self.Y_Unit_LabelKey][0],xUnit)
            else:
                yUnit = ' %s<sup>2</sup>/%s'  %(para[self.unitKey],xUnit)


        f,psd = welch(x = s, fs = fs, nperseg = nperseg, noverlap = noverlap)

        yName = 'PSD'

        name = '%i : %s'%(para[self.shotNumKey],para[self.channelDescriptionKey][:20])
        pItem.pen.setWidth(self.penWidthPsd)
        pItem.setData(f,psd, pen=pItem.pen,name=name)
        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = xName
        pItem.yName = yName
        #return pItem

    def processFunctionCsd (self,pItem, *args,**kargs):

        para1 = pItem.dataParam.reset_index(drop=True).ix[0]
        para2 = pItem.dataParam.reset_index(drop=True).ix[1]
        s1 = np.array(pItem.rawData[para1[self.channelIdKey]])
        s2 = np.array(pItem.rawData[para2[self.channelIdKey]])
        t = float(para1[self.X0Key])+float(para1[self.Delta_XKey])*np.arange(len(s1))
        nperseg = pItem.processParam[self.npersegKey]
        overlap = pItem.processParam[self.overlapKey]
        noverlap = nperseg*overlap//100

        fs = float(1/(t[1]-t[0]))

        if not pItem.processParam[self.isUncalibratedSignalKey]:
            s1 = s1*float(para1[self.calibrationKey])
            s2 = s2*float(para2[self.calibrationKey])

        if self.xRegionKey in pItem.processParam:
            xRegion = pItem.processParam[self.xRegionKey]
        else:
            xRegion = (t[0],t[-1])

        mask1 = (t>xRegion[0])
        mask2 = (t<xRegion[1])
        mask = mask1 & mask2
        t,s1,s2 = t[mask],s1[mask],s2[mask]

        if len(t)<nperseg:
            nperseg = len(t)
            noverlap = None

        if pItem.processParam[self.isNormalizePsdKey]:
            s1 = s1/np.average(s1)
            s2 = s2/np.average(s2)

        f,Csd = csd(s1,s2, fs = fs, nperseg = nperseg, noverlap = noverlap)

        if para1[self.X_DimensionKey].lower()=='time':
            xName = 'Frequency'
            xUnit = 'Hz'
        else:
            xName = ''
            xUnit = ''

        yUnit = ''
        yName = 'CSD'
        name = '%i : %s - %s'%(para1[self.shotNumKey],para1[self.channelDescriptionKey][:15],para2[self.channelDescriptionKey][:15])
        pItem.pen.setWidth(self.penWidthPsd)
        pItem.setData(f,np.absolute(Csd), pen=pItem.pen,name=name)
        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = xName
        pItem.yName = yName

    def processFunctionCoh (self,pItem, *args,**kargs):

        para1 = pItem.dataParam.reset_index(drop=True).ix[0]
        para2 = pItem.dataParam.reset_index(drop=True).ix[1]
        s1 = np.array(pItem.rawData[para1[self.channelIdKey]])
        s2 = np.array(pItem.rawData[para2[self.channelIdKey]])
        t = float(para1[self.X0Key])+float(para1[self.Delta_XKey])*np.arange(len(s1))
        nperseg = pItem.processParam[self.npersegKey]
        overlap = pItem.processParam[self.overlapKey]
        noverlap = nperseg*overlap//100

        fs = float(1/(t[1]-t[0]))

        if not pItem.processParam[self.isUncalibratedSignalKey]:
            s1 = s1*float(para1[self.calibrationKey])
            s2 = s2*float(para2[self.calibrationKey])

        if self.xRegionKey in pItem.processParam:
            xRegion = pItem.processParam[self.xRegionKey]
        else:
            xRegion = (t[0],t[-1])

        mask1 = (t>xRegion[0])
        mask2 = (t<xRegion[1])
        mask = mask1 & mask2
        t,s1,s2 = t[mask],s1[mask],s2[mask]

        if len(t)<nperseg:
            nperseg = len(t)
            noverlap = None

        if pItem.processParam[self.isNormalizePsdKey]:
            s1 = s1/np.average(s1)
            s2 = s2/np.average(s2)

        f,coh = coherence(s1,s2, fs = fs, nperseg = nperseg, noverlap = noverlap)

        if para1[self.X_DimensionKey].lower()=='time':
            xName = 'Frequency'
            xUnit = 'Hz'
        else:
            xName = ''
            xUnit = ''

        yUnit = ''
        yName = 'Coh'
        name = '%i : %s - %s'%(para1[self.shotNumKey],para1[self.channelDescriptionKey][:15],para2[self.channelDescriptionKey][:15])
        pItem.pen.setWidth(self.penWidthPsd)
        pItem.setData(f,coh, pen=pItem.pen,name=name)
        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = xName
        pItem.yName = yName

    def processFunctionPhase (self,pItem, *args,**kargs):

        para1 = pItem.dataParam.reset_index(drop=True).ix[0]
        para2 = pItem.dataParam.reset_index(drop=True).ix[1]
        s1 = np.array(pItem.rawData[para1[self.channelIdKey]])
        s2 = np.array(pItem.rawData[para2[self.channelIdKey]])
        t = float(para1[self.X0Key])+float(para1[self.Delta_XKey])*np.arange(len(s1))
        nperseg = pItem.processParam[self.npersegKey]
        overlap = pItem.processParam[self.overlapKey]
        noverlap = nperseg*overlap//100

        fs = float(1/(t[1]-t[0]))

        if not pItem.processParam[self.isUncalibratedSignalKey]:
            s1 = s1*float(para1[self.calibrationKey])
            s2 = s2*float(para2[self.calibrationKey])

        if self.xRegionKey in pItem.processParam:
            xRegion = pItem.processParam[self.xRegionKey]
        else:
            xRegion = (t[0],t[-1])

        mask1 = (t>xRegion[0])
        mask2 = (t<xRegion[1])
        mask = mask1 & mask2
        t,s1,s2 = t[mask],s1[mask],s2[mask]

        if len(t)<nperseg:
            nperseg = len(t)
            noverlap = None

        if pItem.processParam[self.isNormalizePsdKey]:
            s1 = s1/np.average(s1)
            s2 = s2/np.average(s2)

        f,Csd = csd(s1,s2, fs = fs, nperseg = nperseg, noverlap = noverlap)

        if para1[self.X_DimensionKey].lower()=='time':
            xName = 'Frequency'
            xUnit = 'Hz'
        else:
            xName = ''
            xUnit = ''

        yUnit = ''
        yName = 'Phase'
        name = '%i : %s - %s'%(para1[self.shotNumKey],para1[self.channelDescriptionKey][:15],para2[self.channelDescriptionKey][:15])
        pItem.pen.setWidth(self.penWidthPsd)
        pItem.setData(f,np.angle(Csd)/np.pi, pen=pItem.pen,name=name)
        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = xName
        pItem.yName = yName


    def updateXRegion(self,windex,pindex,xRegion,*args,**kargs):
        dataItems = self.ds[windex][pindex]
        for dataItem in dataItems:
            dataItem.processParam[self.xRegionKey]=xRegion.getRegion()
            self.exeProcessFunction(dataItem)


    def updateXRegion1(self,wNumber,pNumber,*args,**kargs):

        glw = [x for x in self.Ui_frmWindowLayout.windowListboxItem.itemList if x.number ==wNumber][0]
        p = [x for x in glw.ci.items.keys() if type(x)==type(pg.PlotItem()) and x.number ==pNumber][0]
        self.times=[]
        self.times.append(datetime.now())
        vbs = [x for x in p.childItems() if type(x) ==type(pg.ViewBox())]
        dataItems = []
        self.times.append(datetime.now())
        for vb in vbs:
            dataItems += [x for x in vb.addedItems if type(x) == type(pg.PlotDataItem())]

        for dataItem in dataItems:
            dataItem.processParam['xRegion']=p.xRegion.getRegion()
            self.exeProcessFunction(dataItem,**self.keys)


    def exeProcessFunction(self,item,*args,**kargs):
        if item.plotType==self.pTypeBasicKey:
            self.processFunctionBasic(item,*args,**kargs)
            return
        elif item.plotType == self.pTypePsdKey :
            self.processFunctionPsd(item,*args,**kargs)
            return
        elif item.plotType == self.pTypeCsdKey:
            self.processFunctionCsd(item,*args,**kargs)
            return
        elif item.plotType == self.pTypeCohKey:
            self.processFunctionCoh(item,*args,**kargs)
            return
        elif item.plotType == self.pTypePhaseKey:
            self.processFunctionPhase(item,*args,**kargs)
            return
        elif item.plotType == self.pTypeSpectrogramKey:
            self.processFunctionSpectrogram(item,*args,**kargs)
            return
        elif item.plotType == self.pTypeCsdSpectrogramKey:
            self.processFunctionCsdSpectrogram(item,*args,**kargs)
            return


    def linkX (self):
        if len(self.Ui_frmWindowLayout.tblPlot1.selectedItems())+len(self.Ui_frmWindowLayout.tblPlot2.selectedItems())<2:
            return
        pLocations = []
        for table in self.Ui_frmWindowLayout.tableList:
            windex = table.windex
            if windex==None:
                continue
            for item in table.selectedItems():
                pindex = int(item.text().split(' ')[-1])
                pLocations.append((windex,pindex))
        for x in pLocations[1:]:
            self.ps[x[0]][x[1]].setXLink(self.ps[pLocations[0][0]][pLocations[0][1]])



    def linkY(self):
        if len(self.Ui_frmWindowLayout.tblPlot1.selectedItems())+len(self.Ui_frmWindowLayout.tblPlot2.selectedItems())<2:
            return
        pLocations = []
        for table in self.Ui_frmWindowLayout.tableList:
            windex = table.windex
            if windex==None:
                continue
            for item in table.selectedItems():
                pindex = int(item.text().split(' ')[-1])
                pLocations.append((windex,pindex))
        for x in pLocations[1:]:
            self.ps[x[0]][x[1]].setYLink(self.ps[pLocations[0][0]][pLocations[0][1]])


    def linkXY(self):
        if len(self.Ui_frmWindowLayout.tblPlot1.selectedItems())+len(self.Ui_frmWindowLayout.tblPlot2.selectedItems())<2:
            return
        pLocations = []
        for table in self.Ui_frmWindowLayout.tableList:
            windex = table.windex
            if windex==None:
                continue
            for item in table.selectedItems():
                pindex = int(item.text().split(' ')[-1])
                pLocations.append((windex,pindex))
        for x in pLocations[1:]:
            self.ps[x[0]][x[1]].setXLink(self.ps[pLocations[0][0]][pLocations[0][1]])
            self.ps[x[0]][x[1]].setYLink(self.ps[pLocations[0][0]][pLocations[0][1]])

    def linkXRegion(self):
        if len(self.Ui_frmWindowLayout.tblPlot1.selectedItems())+len(self.Ui_frmWindowLayout.tblPlot2.selectedItems())<2:
            return
        xRegions = []
        for table in self.Ui_frmWindowLayout.tableList:
            windex = table.windex
            if windex==None:
                continue
            for item in table.selectedItems():
                pindex = int(item.text().split(' ')[-1])
                regions = [x for x in self.ps[windex][pindex].items if type(x)==type(pg.LinearRegionItem()) and x.orientation ==pg.LinearRegionItem.Vertical]
                for region in regions:
                    xRegions.append(region)

        if not self.xRegionGroups:
            self.xRegionGroups.append(xRegions)
            index=0
        else:
            index = -1
            for i in range(len(self.xRegionGroups)):
                for xRegion in xRegions:
                    if xRegion in self.xRegionGroups[i]:
                        for r in self.xRegionGroups[i]:
                            r.sigRegionChanged.disconnect(r.xRegionSlot)
                        index = i
                        uniqueRegions = [x for x in xRegions if x not in self.xRegionGroups[i]]
                        self.xRegionGroups[i] +=uniqueRegions
                        break
            if index==-1:
                index = len(self.xRegionGroups)
                self.xRegionGroups.append(xRegions)

        xRegions = self.xRegionGroups[index]

        for r in xRegions:
            restOfRegions = [x for x in xRegions if x is not r]
            r.xRegionSlot = functools.partial(self.followXRegion1,r,restOfRegions)
            r.sigRegionChanged.connect(r.xRegionSlot)




    def followXRegion1 (self,r, regions):

        newRegion = r.getRegion()

        for region in regions:
            region.sigRegionChanged.disconnect(region.xRegionSlot)

        for region in regions:
            region.setRegion(newRegion)

        for region in regions:
            region.sigRegionChanged.connect(region.xRegionSlot)

        self.btnParamSelect.clicked.connect(lambda: self.ParamSelect(self.lstParam))
        self.btnParamSelectClear.clicked.connect(lambda: self.ParamSelectClear(self.lstParam))
        self.btnParamAdd.clicked.connect(lambda: self.ParamAdd(self.lstParam))

        self.btnParamSelect.clicked.connect(functools.partial(self.ParamSelect,self.lstParam))
        self.btnParamSelectClear.clicked.connect(functools.partial(self.ParamSelectClear,self.lstParam))
        self.btnParamAdd.clicked.connect(functools.partial(self.ParamAdd,self.lstParam))

    def ParamSelect(self, listbox):
        if not listbox.selectedItems():
            return
        self.paramFilterLayout.deleteAllParamFilterItems()
        names = [x.text() for x in listbox.selectedItems()]
        self.paramFilterLayout.addParams(names)

    def ParamSelectClear (self, listbox):
        1

    def ParamAdd (self, listbox):
        1




    def plotBasic_2 (self):
        1

    def plotPsd_2 (self):
        1

    def plotCsd_2 (self):
        1

    def linkX_2 (self):
        1

    def linkY_2 (self):
        1

    def linkXY_2 (self):
        1

    def linkXRegion_2 (self):
        1







if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    frame = frmMainWindow()
    
    # app.aboutToQuit.connect(app.deleteLater)
    # Frame = QtWidgets.QFrame()
    # ui = frmLoadData()
    # ui.setupUi(Frame)
    frame.show()
    app.exec_()



# if __name__ == "__main__":
    # import sys

    # # app = QApplication([])
    # # app.aboutToQuit.connect(app.deleteLater)
    # # Frame = QFrame()
    # # ui = Ui_frmDataGui0_0_0()
    # # ui.setupUi(Frame)
    # # Frame.show()
    # # app.exec_()
    # app = QApplication(sys.argv)
    # app.aboutToQuit.connect(app.deleteLater)
    # Frame = QFrame()
    # ui = Ui_frmDataGui0_0_0()
    # ui.setupUi(Frame)
    # Frame.show()
    # app.exec_()
