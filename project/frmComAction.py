
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QShortcut



from PyQt5.QtCore import QObject, pyqtSignal

from pyqtgraph import functions as fn

import os,sys

from os import path
dirname = path.dirname(__file__)
fname = "frmComAction.ui"
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

from frmShotChannel import frmShotChannel
from frmShotChannelTable import frmShotChannelTable
from frmWindowLayout import frmWindowLayout
from frmAction1 import frmAction1
from dlgXyView import dlgXyView


class frmComAction(QtWidgets.QFrame, dataGuiBaseClass):
    sigWindowOpened = QtCore.pyqtSignal()
    sigIvDataAdded = QtCore.pyqtSignal()
    sigArithmeticsDataAdded = QtCore.pyqtSignal()
    def __init__(self ,displayType='list'):
        super().__init__()
        uic.loadUi(fpath, self)

        self.displayType = displayType

        if self.displayType == 'table':
            self.frmAvailableChannel = frmShotChannelTable()
            # self.frmAvailableChannel.show()
            # self.Ui_frmAvailableChannel.setupUi(self.frmAvailableChannel)

        else :
            self.frmAvailableChannel = frmShotChannel()
            # self.frmAvailableChannel.show()
            # self.Ui_frmAvailableChannel.setupUi(self.frmAvailableChannel)

        if self.displayType=='list':
            self.frmAvailableChannel.lstChannel.doubleClicked.connect(self.plotBasic)

        self.frmWindowLayout = frmWindowLayout()
        # self.frmWindowLayout.show()
        # self.frmWindowLayout.setupUi(self.frmWindowLayout)

        self.frmAction = frmAction1()
        # self.Ui_frmAction.setupUi(self.frmAction)


        self.gridLayout.addWidget(self.frmAvailableChannel, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.frmWindowLayout, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.frmAction, 0, 2, 1, 1)


        #connect buttons
        self.frmAction.btnPlot.clicked.connect(self.plotBasic)
        self.frmAction.btnPlotCsv.clicked.connect(self.plotBasicCsv)
        self.frmAction.btnPsd.clicked.connect(self.plotPsd)
        self.frmAction.btnCsd.clicked.connect(self.plotCsd)
        self.frmAction.btnLinkX.clicked.connect(self.linkX)
        self.frmAction.btnLinkY.clicked.connect(self.linkY)
        self.frmAction.btnLinkXY.clicked.connect(self.linkXY)
        self.frmAction.btnLinkRegion.clicked.connect(self.linkXRegion)
        self.frmAction.btnSpectrogram.clicked.connect(self.plotSpectrogram)
        self.frmAction.btnCsdSpectrogram.clicked.connect(self.plotCsdSpectrogram)
        self.frmAction.btnBicoh.clicked.connect(self.plotBicoh)
        self.frmAction.btnXyView.clicked.connect(self.plotXyView)
        self.frmAction.btnSaveError.clicked.connect(self.saveError)

        self.sigWindowOpened.connect(self.updateAfterWindowOpened)

        self.frmAction.sigIvDataAdded.connect(self.ivDataAdded)
        self.frmAction.sigDataAdded.connect(self.sigArithmeticsDataAdded.emit)

        self.frmAvailableChannel.listChannel()
        self.frmAvailableChannel.listLoadedShots()
        self.frmWindowLayout.updateWindowList()



    def ivDataAdded(self):
        self.sigIvDataAdded.emit()


    def updateAfterWindowOpened(self):
        self.frmWindowLayout.updateWindowList()


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
        glw.windex =windex

        self.frmWindowLayout.windowListboxItem.nameList.append(name)
        self.frmWindowLayout.windowListboxItem.itemList.append(glw)
        self.frmWindowLayout.windowListboxItem.listInBox()

        return windex

    def exportCsv (self,windex, pindex):
        if len(self.ds[windex][pindex])==0:
            return

        df=pd.DataFrame()
        for item in self.ds[windex][pindex]:
            xHeader = "%s (%s) [%s]" %(item.xName, item.xUnit,item.name())
            yHeader = "%s (%s) [%s]" %(item.yName, item.yUnit,item.name())
            df[xHeader] = item.xData
            df[yHeader] = item.yData


        filePath = QFileDialog.getSaveFileName (parent = None, caption = "Select file name", filter ="csv (*.csv *.)")
        if filePath == "":
            return
        # print(df.head(), filePath)
        df.to_csv(filePath[0])


    def addNewPlot(self,windex,location):
        pindex = len(self.ps[windex])
        p = pg.PlotItem()
        p.windex = windex
        p.pindex = pindex
        p.location = location
        p.panels = []
        p.addLegend()
        #add option to export csv files
        p.vb.menu.ExportCsv = QAction("Export to csv", p.vb.menu)
        p.vb.menu.ExportCsv.triggered.connect(lambda: self.exportCsv(int(windex),int(pindex)))
        p.vb.menu.addAction(p.vb.menu.ExportCsv)





        p.legend.setScale(legendScale)
        self.ws[windex].addItem(p,location[0],location[1],location[2],location[3])
        self.ps[windex].append(p)
        self.ds[windex].append([])





        return pindex



    def addNewLut(self,windex,location):
        pindex = len(self.ps[windex])
        p = pg.HistogramLUTItem()
        p.windex = windex
        p.pindex = pindex
        p.location = location

        self.ws[windex].addItem(p,location[0],location[1],location[2],location[3])
        self.ps[windex].append(p)
        self.ds[windex].append([])
        return pindex

    def addNewDataItem(self, windex,pindex,plotType,dataParam,processParam):

        dindex = len(self.ds[windex][pindex])
        plot = self.ps[windex][pindex]
        pen = pg.mkPen(penColors[dindex%len(penColors)],width=penWidth)
        #pen = pg.mkPen('k',width=1)
        item = pg.PlotDataItem(pen=pen)
        item.plotType = plotType
        item.dataParam = dataParam
        item.windex=windex
        item.pindex = pindex
        item.dindex = dindex
        item.processParam = processParam
        item.pen = pen
        item.color = penColors[dindex%len(penColors)]


        item.errorBarPen = pg.mkPen(item.color,width=errorBarPenWidth)

        item.rawData = self.getData(dataParam)
        item.errData = self.getErr(dataParam)
        para = dataParam.reset_index(drop=True).iloc[0,:]
        x = float(para[X0Key])
        + float(para[Delta_XKey])*np.arange(len(item.rawData.iloc[:,0]))
        y = item.rawData.iloc[:,0]
        item.errorBarItem = pg.ErrorBarItem(x = x , y=y)
        self.exeProcessFunction(item)

        if dindex == 0:
            panel = {}
            panel[panelVbKey]=plot.vb
            panel[panelColorKey]=item.color
            panel[panelAxisKey] = plot.getAxis('left')
            panel[panelUnitKey] = item.yUnit
            plot.panels.append(panel)
            panelIndex=0

        else:
            #try if any panel's unit matches the item's
            panelIndex = -1
            for i, panel in enumerate(plot.panels):
                if panel[panelUnitKey]==item.yUnit:
                    panelIndex = i
                    break

            if panelIndex ==-1:  #if not panel's unit matches
                if len(plot.panels)==1:
                    panel = {}
                    vb, axis = pg.ViewBox(), plot.getAxis('right')
                    plot.showAxis('right')
                    plot.scene().addItem(vb)
                    axis.linkToView(vb)
                    vb.setXLink(plot)

                    panel[panelVbKey]=vb
                    panel[panelColorKey]=penColors[dindex%len(penColors)]
                    panel[panelAxisKey] = axis
                    panel[panelUnitKey] = item.yUnit
                    plot.panels.append(panel)

                    self.updateVb(plot,vb)
                    plot.vb.sigResized.connect(functools.partial(self.updateVb, plot, vb))

                    panelIndex = 1
                else:
                    col = len(plot.panels)+1
                    panel = {}
                    vb, axis = pg.ViewBox(), pg.AxisItem('right')
                    panel[panelVbKey]=vb
                    plot.layout.addItem(axis,2,col)
                    plot.scene().addItem(vb)
                    axis.linkToView(vb)
                    vb.setXLink(plot)
                    panel[panelColorKey]=penColors[dindex%len(penColors)]
                    panel[panelAxisKey] = axis
                    panel[panelUnitKey] = item.yUnit
                    plot.panels.append(panel)

                    self.updateVb(plot,vb)
                    plot.vb.sigResized.connect(functools.partial(self.updateVb, plot, vb))
                    panelIndex = col-1


        plot.panels[panelIndex][panelVbKey].addItem(item.errorBarItem)
        plot.panels[panelIndex][panelVbKey].addItem(item)


        self.ds[windex][pindex].append(item)


        plot.legend.addItem(item, name=item.name())

        return dindex

    def addNewDataItemCsv(self, windex,pindex,plotType,dataParam,processParam):

        dindex = len(self.ds[windex][pindex])
        plot = self.ps[windex][pindex]
        pen = pg.mkPen(penColors[dindex%len(penColors)],width=penWidth)
        #pen = pg.mkPen('k',width=1)
        item = pg.PlotDataItem(pen=pen)
        item.plotType = plotType
        item.dataParam = dataParam
        item.windex=windex
        item.pindex = pindex
        item.dindex = dindex
        item.processParam = processParam
        item.pen = pen
        item.color = penColors[dindex%len(penColors)]

        item.errorBarPen = pg.mkPen(item.color,width=errorBarPenWidth)

        item.rawData = self.getData(dataParam)
        item.errData = self.getErr(dataParam)
        para = dataParam.reset_index(drop=True).iloc[0,:]
        x = float(para[X0Key])
        + float(para[Delta_XKey])*np.arange(len(item.rawData.iloc[:,0]))
        y = item.rawData.iloc[:,0]
        item.errorBarItem = pg.ErrorBarItem(x = x , y=y)
        self.exeProcessFunction(item)

        plot.addItem(item.errorBarItem)
        plot.addItem(item)


        self.ds[windex][pindex].append(item)


        plot.legend.addItem(item, name=item.name())

        return dindex


    def updateVb(self, p, vb):
        vb.setGeometry(p.vb.sceneBoundingRect())
        vb.linkedViewChanged(p.vb, vb.XAxis)



    def addNewImageItem (self, windex,pindex,plotType,dataParam,processParam):
        dindex = len(self.ds[windex][pindex])


        item = pg.ImageItem()
        item.plotType = plotType
        item.dataParam = dataParam
        item.windex = windex
        item.pindex = pindex
        item.dindex = dindex
        item.processParam = processParam


        item.rawData = self.getData(dataParam)
        item.errData = self.getErr(dataParam)
        opts = {}
        opts['pen']=fn.mkPen(255,255,255,100)
        opts['brush'] = fn.mkBrush(100,100,100,500)
        opts['size']=1
        item.opts=opts




        self.exeProcessFunction(item)
        self.ps[windex][pindex].addItem(item)
        self.ds[windex][pindex].append(item)
        return dindex





    def updateYAxis(self,ax,*args,**kargs):
        vb = ax.linkedView()
        dataItems = [x for x in vb.addedItems if type(x)==type(pg.PlotDataItem())or type(x)==type(pg.ImageItem())]
        axisArg = axisArgs
        yUnits = np.unique([item.yUnit for item in dataItems])
        names = [item.yName for item in dataItems]
        yUnit,yLabel = '',''
        if len(yUnits)==1:
            yUnit = yUnits[0]
        commonWords = []
        # pgColor = dataItems[0].color
        # color = pg.colorStr(pgColor)



        for word in names[0].replace('(',' ').replace(')',' ').replace('_',' ').replace('-',' ').split(' '):
            present = True
            for name in names:
                if word.upper() not in [x.upper() for x in name.replace('(',' ').replace(')',' ').replace('_',' ').replace('-',' ').split(' ')]:
                    present = False
            if present:
                commonWords.append(word)
        commonLabels =[word for word in commonWords if word.upper() in plotYLabelTypes or word in plotYLabelTypes]
        """
        if len(commonLabels)>0:
            maxLen = np.max([len(x) for x in commonLabels])
            yLabel = [x for x in commonLabels if len(x)==maxLen][0]
        """
        yLabel = ' '.join(commonLabels)

        # axisArg['labelStyleArgs']['color']=color
        # axisArg['axisPen'].setColor(pgColor)

        ax.setLabel(yLabel,units = yUnit,**axisArg['labelStyleArgs'])

        ax.tickFont = axisArg['tickFont']
        ax.setPen(axisArg['axisPen'])
        ax.setStyle(tickLength = axisArg['tickLength'])

        ax.setWidth(w=axisArg['yAxisWidth'])
        ax.setStyle(tickTextOffset = axisArg['yTickTextOffset'])
        return ax

    def updateXAxis(self,ax,*args,**kargs):
        vb = ax.linkedView()
        dataItems = [x for x in vb.addedItems if type(x)==type(pg.PlotDataItem()) or type(x)==type(pg.ImageItem())]
        axisArg = axisArgs
        xUnits = np.unique([item.xUnit for item in dataItems])
        names = [item.xName for item in dataItems]
        xUnit,xLabel = '',''
        # pgColor = dataItems[0].color
        # color = pg.colorStr(pgColor)
        color = 'r'



        if len(xUnits)==1:
            xUnit = xUnits[0]
        commonWords = []
        for word in names[0].replace('(',' ').replace(')',' ').replace('_',' ').replace('-',' ').split(' '):
            present = True
            for name in names:
                if word.upper() not in [x.upper() for x in name.replace('(',' ').replace(')',' ').replace('_',' ').replace('-',' ').split(' ')]:
                    present = False
            if present:
                commonWords.append(word)
        commonLabels =[word for word in commonWords if word.upper() in plotXLabelTypes or word in plotYLabelTypes]
        if len(commonLabels)>0:
            maxLen = np.max([len(x) for x in commonLabels])
            xLabel = [x for x in commonLabels if len(x)==maxLen][0]

        axisArg['labelStyleArgs']['color']=color
        # print(axisArg['axisPen'])
        # axisArg['axisPen'].setColor(pgColor)

        ax.setLabel(xLabel,units = xUnit,**axisArg['labelStyleArgs'])
        ax.tickFont = axisArg['tickFont']
        ax.setPen(axisArg['axisPen'])
        ax.setStyle(tickLength = axisArg['tickLength'])
        ax.setHeight(h=axisArg['xAxisHeight'])
        ax.setStyle(tickTextOffset = axisArg['xTickTextOffset'])
        return ax


    def updateAxes (self, windex, pindex,*args,**kargs):
        plot = self.ps[windex][pindex]
        axes = [x for x in plot.allChildItems() if type(x) ==type(pg.AxisItem('left'))]
        yAxes = [x for x in axes if x.orientation=='left' or x.orientation=='right']
        xAxes = [x for x in axes if x.orientation == 'bottom']


        for yAxis in yAxes:
            self.updateYAxis(yAxis, *args,**kargs)
        for xAxis in xAxes:
            self.updateXAxis(xAxis, *args,**kargs)

    def updateViews(self,p):
        vbs = [x for x in p.scene().items() if type(x) ==type(pg.ViewBox())][1:]
        for vb in vbs:
            vb.setGeometry(p.vb.sceneBoundingRect())
            ## need to re-update linked axes since this was called
            ## incorrectly while views had different shapes.
            ## (probably this should be handled in ViewBox.resizeEvent)
            vb.linkedViewChanged(p.vb,vb.XAxis)





    def plotBasic(self):

        nPlotRow,nPlotColumn = 1,1
        windex,pindexes,dataParam,processParam = self.getInitialInfo(nPlotRow=nPlotRow,nPlotColumn=nPlotColumn)
        if windex ==None:
          print("none window")
          return

        #prepare dataParams
        dataParamList = [dataParam[dataParam.index==i] for i in range(len(dataParam))]
        pTypeList = pTypeBasicKey
        for dataParam in dataParamList:
            #dindex = self.addNewDataItem(windex,pindexes[0][0],pTypeList, dataParam,processParam)
            dindex = self.addNewDataItem(windex,pindexes[0][0],pTypeList, dataParam,processParam.copy())
        self.updateAxes(windex,pindexes[0][0])

        ## self.updateXAxis(self.ps[windex][pindexes[0][0]].getAxis('bottom'))
        ## self.updateYAxis(self.ps[windex][pindexes[0][0]].getAxis('left'))

        self.frmWindowLayout.lstWindow.item(windex).setSelected(True)
        self.frmWindowLayout.updatePlotLayouts()
        if self.selectPlot:
            self.frmWindowLayout.tblPlot1.item(self.tempSelectedRow,self.tempSelectedColumn).setSelected(True)
       #test begins###########################################
        # plot = self.ps[windex][pindexes[0][0]]
        # axes = [x for x in plot.allChildItems() if type(x) ==type(pg.AxisItem('left'))]
        # yAxes = [x for x in axes if x.orientation=='left' or x.orientation=='right']
        # xAxes = [x for x in axes if x.orientation == 'bottom']
        # ax = xAxes[0]
        # font1=QtGui.QFont() 
        # font1.setPixelSize(20) 
        # xAxes[0].tickFont = font1

        # for yAxis in yAxes:
            # self.updateYAxis(yAxis)
        # for xAxis in xAxes:
            # self.updateXAxis(xAxis, *args,**kargs)
       #test ends ###########################################

    def plotBasicCsv(self):

        nPlotRow,nPlotColumn = 1,1
        windex,pindexes,dataParam,processParam = self.getInitialInfo(nPlotRow=nPlotRow,nPlotColumn=nPlotColumn)
        if windex ==None:
            return

        #prepare dataParams
        dataParamList = [dataParam[dataParam.index==i] for i in range(len(dataParam))]
        pTypeList = pTypeBasicKey
        for dataParam in dataParamList:
            #dindex = self.addNewDataItem(windex,pindexes[0][0],pTypeList, dataParam,processParam)
            dindex = self.addNewDataItemCsv(windex,pindexes[0][0],pTypeList, dataParam,processParam.copy())
        self.updateAxes(windex,pindexes[0][0])

        #self.updateXAxis(self.ps[windex][pindexes[0][0]].getAxis('bottom'))
        #self.updateYAxis(self.ps[windex][pindexes[0][0]].getAxis('left'))

        self.frmWindowLayout.lstWindow.item(windex).setSelected(True)
        self.frmWindowLayout.updatePlotLayouts()
        if self.selectPlot:
            self.frmWindowLayout.tblPlot1.item(self.tempSelectedRow,self.tempSelectedColumn).setSelected(True)






    def getInitialInfo(self,nPlotRow=1,nPlotColumn=1,lut=False,
                       plotMatrix =None,spanMatrix=None, external=False):
      # return if shotnum or channel is not selected
      if not self.frmAvailableChannel.selectedChannelIDs and not external:
        print("no channel selected.")
        return None,None,None,None

      if len(self.frmWindowLayout.selectedWindexes)>1 :
        print("too many windows selected")
        return None,None,None,None
      windex,location = self.getStartingLocation()
      pindexes = self.getPindexes(windex=windex,location=location, nPlotRow=nPlotRow, nPlotColumn=nPlotColumn, lut = lut,plotMatrix =plotMatrix,spanMatrix=spanMatrix)
      if pindexes == None:
        print("pindex none")
        return  None,None,None,None
      #print ("made it here!")

      # get indexes for channels

      processParam = self.frmAction.getProcessParams()
      if external:
          dataParam = None
      else:
          dataParam=self.params[self.params[channelIdKey].isin(np.array(self.frmAvailableChannel.selectedChannelIDs).astype(self.params[channelIdKey].dtype))].reset_index(drop=True)

      return windex,pindexes,dataParam,processParam




    def plotPsd(self):
        self.times = []

        nPlotRow,nPlotColumn = 2,1
        windex,pindexes,dataParam,processParam = self.getInitialInfo(nPlotRow=nPlotRow,nPlotColumn=nPlotColumn)
        if windex == None:
            return

        #prepare dataParams
        dataParamList = [dataParam[dataParam.index==i] for i in range(len(dataParam))]
        pTypeList = [pTypePsdKey,pTypeBasicKey]

        for i in range(2):
            for dataParam in dataParamList:
                dindex = self.addNewDataItem(windex,pindexes[i][0],pTypeList[i], dataParam,processParam.copy())
            #self.updateXAxis(self.ps[windex][pindexes[i][0]].getAxis('bottom'))
            #self.updateYAxis(self.ps[windex][pindexes[i][0]].getAxis('left'))
            self.updateAxes(windex,pindexes[i][0])

        if not any(type(x)==type(pg.LinearRegionItem()) for x in self.ps[windex][pindexes[1][0]].allChildItems()):

            xRegion = pg.LinearRegionItem()
            xRegion.xRegionSlot = None
            xRegion.setZValue(10)
            xRegion.sigRegionChanged.connect(lambda: self.updateXRegion(windex,pindexes[0][0],xRegion,**keys))
            self.ps[windex][pindexes[1][0]].addItem(xRegion,ignoreBounds=True)
            xRegion.setRegion([0.008,0.010])
        self.ps[windex][pindexes[0][0]].setAutoVisible(y=True)
        self.ps[windex][pindexes[1][0]].setAutoVisible(y=True)


        self.frmWindowLayout.lstWindow.item(windex).setSelected(True)
        self.frmWindowLayout.updatePlotLayouts()
        if self.selectPlot:
            self.frmWindowLayout.tblPlot1.item(self.tempSelectedRow,self.tempSelectedColumn).setSelected(True)

    def plotXyView(self):
        # dialog = QtWidgets.QDialog()
        ui = dlgXyView()
        # ui.show()
        # ui.setupUi(dialog)
        dataParam1 = ui.getXY()
        if len(dataParam1) == 0:
            return



        nPlotRow,nPlotColumn = 2,1
        windex,pindexes,dataParam,processParam = self.getInitialInfo(nPlotRow=nPlotRow,nPlotColumn=nPlotColumn, external=True)
        if windex == None:
            return
        dataParam = dataParam1



        #prepare dataParams
        dataParamList = [dataParam[dataParam.index==i] for i in range(len(dataParam))]
        if len(dataParamList) !=2:
            return


        dindex = self.addNewDataItem(windex,pindexes[0][0],pTypeXyView, dataParam,processParam.copy())

        for dataPara in dataParamList:
            dindex = self.addNewDataItem(windex,pindexes[1][0],pTypeBasicKey, dataPara,processParam.copy())

        self.updateAxes(windex,pindexes[0][0])
        self.updateAxes(windex,pindexes[1][0])

        if not any(type(x)==type(pg.LinearRegionItem()) for x in self.ps[windex][pindexes[1][0]].allChildItems()):

            xRegion = pg.LinearRegionItem()
            xRegion.xRegionSlot = None
            xRegion.setZValue(10)
            xRegion.sigRegionChanged.connect(lambda: self.updateXRegion(windex,pindexes[0][0],xRegion,**keys))
            self.ps[windex][pindexes[1][0]].addItem(xRegion,ignoreBounds=True)
            xRegion.setRegion([0.008,0.010])
        self.ps[windex][pindexes[0][0]].setAutoVisible(y=True)
        self.ps[windex][pindexes[1][0]].setAutoVisible(y=True)


        self.frmWindowLayout.lstWindow.item(windex).setSelected(True)
        self.frmWindowLayout.updatePlotLayouts()
        if self.selectPlot:
            self.frmWindowLayout.tblPlot1.item(self.tempSelectedRow,self.tempSelectedColumn).setSelected(True)

    def plotCsd(self):
        self.times = []

        nPlotRow,nPlotColumn = 4,1
        windex,pindexes,dataParam,processParam = self.getInitialInfo(nPlotRow=nPlotRow,nPlotColumn=nPlotColumn)
        if windex == None:
            return

        #prepare dataParams
        pTypeList = [pTypeCsdKey,pTypeCohKey,pTypePhaseKey,pTypeBasicKey]
        paramList  = [dataParam[dataParam.index==i] for i in range(len(dataParam))]

        self.addNewDataItem(windex,pindexes[0][0],pTypeList[0], dataParam,processParam.copy())
        yAx,xAx = self.ps[windex][pindexes[0][0]].getAxis('left'),self.ps[windex][pindexes[0][0]].getAxis('bottom')
        #self.updateYAxis(yAx)
        #self.updateXAxis(xAx)
        self.updateAxes(windex,pindexes[0][0])

        #self.ps[windex][pindexes[0][0]].legend.hide()
        xAx.setStyle(tickLength = -tickLength, showValues=False)
        xAx.showLabel(False)
        xAx.setMaximumHeight(0)

        self.addNewDataItem(windex,pindexes[1][0],pTypeList[1], dataParam,processParam.copy())
        yAx,xAx = self.ps[windex][pindexes[1][0]].getAxis('left'),self.ps[windex][pindexes[1][0]].getAxis('bottom')
        self.ps[windex][pindexes[1][0]].legend.hide()
        #self.updateYAxis(yAx)
        #self.updateXAxis(xAx)
        self.updateAxes(windex,pindexes[1][0])
        xAx.setStyle(tickLength = -tickLength, showValues=False)
        xAx.showLabel(False)
        xAx.setMaximumHeight(0)

        self.addNewDataItem(windex,pindexes[2][0],pTypeList[2], dataParam,processParam.copy())
        #self.updateYAxis(self.ps[windex][pindexes[2][0]].getAxis('left'))
        #self.updateXAxis(self.ps[windex][pindexes[2][0]].getAxis('bottom'))
        self.updateAxes(windex,pindexes[2][0])
        self.ps[windex][pindexes[2][0]].legend.hide()
        self.ps[windex][pindexes[2][0]].getAxis('bottom').setStyle(tickLength = -tickLength)

        self.ps[windex][pindexes[0][0]].setXLink(self.ps[windex][pindexes[2][0]])
        self.ps[windex][pindexes[1][0]].setXLink(self.ps[windex][pindexes[2][0]])
        #self.ps[windex][pindexes[2][0]].vb.sigResized.connect(functools.partial(self.linkMaxHeight,self.ps[windex][pindexes[2][0]].vb,[self.ps[windex][pindexes[1][0]],self.ps[windex][pindexes[0][0]]]))
        #self.ps[windex][pindexes[2][0]].vb.sigResized.connect(functools.partial(self.TESTPRINT,self.ps[windex][pindexes[2][0]]))
        #self.ws[windex].sigDeviceRangeChanged.connect(functools.partial(self.linkMaxHeight,windex,[self.ps[windex][pindexes[0][0]],self.ps[windex][pindexes[1][0]],self.ps[windex][pindexes[2][0]],self.ps[windex][pindexes[3][0]]]))

        for i in range(2):
            dindex = self.addNewDataItem(windex,pindexes[3][0],pTypeList[3], paramList[i],processParam.copy())
            #self.updateXAxis(self.ps[windex][pindexes[i][0]].getAxis('bottom'))
        #self.updateYAxis(self.ps[windex][pindexes[3][0]].getAxis('left'))
        #self.updateXAxis(self.ps[windex][pindexes[3][0]].getAxis('bottom'))
        self.updateAxes(windex,pindexes[3][0])

        #self.ps[windex][pindexes[0][0]].getAxis('bottom').label.hide()
        #self.ws[windex].sigDeviceRangeChanged.connect(functools.partial(self.linkMaxHeight,windex,[pindexes[0][0],pindexes[1][0],pindexes[2][0],pindexes[3][0]]))
        self.ws[windex].sigDeviceRangeChanged.connect(functools.partial(self.linkMaxHeight,windex,[pindexes[0][0],pindexes[1][0],pindexes[2][0],pindexes[3][0]]))
        self.ws[windex].sigDeviceRangeChanged.connect(functools.partial(self.linkMaxWidth,windex,[pindexes[0][0],pindexes[1][0],pindexes[2][0],pindexes[3][0]]))
        if not any(type(x)==type(pg.LinearRegionItem()) for x in self.ps[windex][pindexes[3][0]].allChildItems()):
            xRegion = pg.LinearRegionItem()
            xRegion.xRegionSlot = None
            xRegion.setZValue(10)
            xRegion.sigRegionChanged.connect(lambda: self.updateXRegion(windex,pindexes[0][0],xRegion,**keys))
            xRegion.sigRegionChanged.connect(lambda: self.updateXRegion(windex,pindexes[1][0],xRegion,**keys))
            xRegion.sigRegionChanged.connect(lambda: self.updateXRegion(windex,pindexes[2][0],xRegion,**keys))
            self.ps[windex][pindexes[3][0]].addItem(xRegion,ignoreBounds=True)
            xRegion.setRegion([0.018,0.020])
        self.ps[windex][pindexes[0][0]].setAutoVisible(y=True)
        self.ps[windex][pindexes[1][0]].setAutoVisible(y=True)
        self.ps[windex][pindexes[2][0]].setAutoVisible(y=True)

        #xRegion.setRegion([0.018, 0.020])
        self.frmWindowLayout.lstWindow.item(windex).setSelected(True)

        self.frmWindowLayout.updatePlotLayouts()
        if self.selectPlot:
            self.frmWindowLayout.tblPlot1.item(self.tempSelectedRow,self.tempSelectedColumn).setSelected(True)



    def plotSpectrogram (self):
        nPlotRow,nPlotColumn = 1,2
        windex,pindexes,dataParam,processParam = self.getInitialInfo(nPlotRow=nPlotRow,nPlotColumn=nPlotColumn,lut=True)
        if windex == None:
            return

        if len(dataParam) !=1:
            return
        #prepare dataParams
        dataParamList = [dataParam[dataParam.index==i] for i in range(len(dataParam))]

        pType = pTypeSpectrogramKey
        dindex = self.addNewImageItem(windex,pindexes[0][0],pType, dataParamList[0],processParam.copy())

        dataItem = self.ds[windex][pindexes[0][0]][dindex]
        plot = self.ps[windex][pindexes[0][0]]
        hist = self.ps[windex][pindexes[0][1]]
        plot.legend.addItem(dataItem,dataItem.name)
        plot.legend.setAutoFillBackground(True)

        hist.setImageItem(dataItem)
        hist.setLevels(dataItem.dataMin,dataItem.dataMax)
        hist.plot.yName = dataItem.zName
        hist.plot.yUnit = dataItem.zUnit
        plot.autoBtn.clicked.connect(functools.partial(self.refreshLut, hist,windex,pindexes[0][0],dindex))

        self.updateXAxis(plot.getAxis('bottom'))
        self.updateYAxis(plot.getAxis('left'))
        self.updateYAxis(hist.axis)





        self.frmWindowLayout.lstWindow.item(windex).setSelected(True)
        self.frmWindowLayout.updatePlotLayouts()
        if self.selectPlot:
            self.frmWindowLayout.tblPlot1.item(self.tempSelectedRow,self.tempSelectedColumn).setSelected(True)



    def plotCsdSpectrogram(self):
        nPlotRow,nPlotColumn = 3,2
        windex,pindexes,dataParam,processParam = self.getInitialInfo(nPlotRow=nPlotRow,nPlotColumn=nPlotColumn,lut=True)
        if windex == None:
            return

        #prepare dataParams
        if len(dataParam)!=2:
            return

        pTypeList  = [pTypeCsdSpectrogramKey, pTypeCohSpectrogramKey, pTypePhaseSpectrogramKey]

        #CSD
        dindex = self.addNewImageItem(windex,pindexes[0][0],pTypeList[0], dataParam,processParam.copy())
        dataItem = self.ds[windex][pindexes[0][0]][dindex]
        plot = self.ps[windex][pindexes[0][0]]
        hist = self.ps[windex][pindexes[0][1]]
        plot.legend.addItem(dataItem,dataItem.name)
        plot.legend.setAutoFillBackground(True)

        hist.setImageItem(dataItem)
        hist.setLevels(dataItem.dataMin,dataItem.dataMax)
        hist.plot.yName = dataItem.zName
        hist.plot.yUnit = dataItem.zUnit
        plot.autoBtn.clicked.connect(functools.partial(self.refreshLut, hist,windex,pindexes[0][0],dindex))
        self.updateYAxis(hist.axis)

        yAx,xAx = plot.getAxis('left'),plot.getAxis('bottom')
        self.updateXAxis(xAx)
        self.updateYAxis(yAx)
        xAx.setStyle(tickLength = -tickLength, showValues=False)
        xAx.showLabel(False)
        xAx.setMaximumHeight(0)

        #Coherence
        dindex = self.addNewImageItem(windex,pindexes[1][0],pTypeList[1], dataParam,processParam.copy())
        dataItem = self.ds[windex][pindexes[1][0]][dindex]
        plot = self.ps[windex][pindexes[1][0]]
        hist = self.ps[windex][pindexes[1][1]]
        plot.legend.addItem(dataItem,dataItem.name)
        plot.legend.setAutoFillBackground(True)

        hist.setImageItem(dataItem)
        hist.setLevels(dataItem.dataMin,dataItem.dataMax)
        hist.plot.yName = dataItem.zName
        hist.plot.yUnit = dataItem.zUnit
        plot.autoBtn.clicked.connect(functools.partial(self.refreshLut, hist,windex,pindexes[1][0],dindex))
        self.updateYAxis(hist.axis)

        yAx,xAx = plot.getAxis('left'),plot.getAxis('bottom')
        self.updateXAxis(xAx)
        self.updateYAxis(yAx)
        xAx.setStyle(tickLength = -tickLength, showValues=False)
        xAx.showLabel(False)
        xAx.setMaximumHeight(0)

        #Phase
        dindex = self.addNewImageItem(windex,pindexes[2][0],pTypeList[2], dataParam,processParam.copy())
        dataItem = self.ds[windex][pindexes[2][0]][dindex]
        plot = self.ps[windex][pindexes[2][0]]
        hist = self.ps[windex][pindexes[2][1]]
        plot.legend.addItem(dataItem,dataItem.name)
        plot.legend.setAutoFillBackground(True)

        hist.setImageItem(dataItem)
        hist.setLevels(dataItem.dataMin,dataItem.dataMax)
        hist.plot.yName = dataItem.zName
        hist.plot.yUnit = dataItem.zUnit
        plot.autoBtn.clicked.connect(functools.partial(self.refreshLut, hist,windex,pindexes[2][0],dindex))
        self.updateYAxis(hist.axis)

        yAx,xAx = plot.getAxis('left'),plot.getAxis('bottom')
        self.updateXAxis(xAx)
        self.updateYAxis(yAx)

        #link x and y
        self.ps[windex][pindexes[0][0]].setXLink(self.ps[windex][pindexes[2][0]])
        self.ps[windex][pindexes[1][0]].setXLink(self.ps[windex][pindexes[2][0]])
        self.ps[windex][pindexes[0][0]].setYLink(self.ps[windex][pindexes[2][0]])
        self.ps[windex][pindexes[1][0]].setYLink(self.ps[windex][pindexes[2][0]])

        self.ws[windex].sigDeviceRangeChanged.connect(functools.partial(linkMaxHeight,windex,[pindexes[0][0],pindexes[1][0],pindexes[2][0]]))







        self.frmWindowLayout.lstWindow.item(windex).setSelected(True)
        self.frmWindowLayout.updatePlotLayouts()
        if self.selectPlot:
            self.frmWindowLayout.tblPlot1.item(self.tempSelectedRow,self.tempSelectedColumn).setSelected(True)

    def plotBicoh (self):
        nPlotRow,nPlotColumn = 2,2
        plotMatrix = np.ones((nPlotRow, nPlotColumn))
        plotMatrix[1,1]=0
        spanMatrix = np.ones((nPlotRow, nPlotColumn))
        spanMatrix[1,0]=2
        windex,pindexes,dataParam,processParam = self.getInitialInfo(nPlotRow=nPlotRow,nPlotColumn=nPlotColumn,lut=True, plotMatrix = plotMatrix,spanMatrix=spanMatrix)
        if windex == None:
            return

        if len(dataParam) !=1:
            return

        #prepare dataParams
        dataParamList = [dataParam[dataParam.index==i] for i in range(len(dataParam))]
        pTypeList = [pTypeBicohKey,pTypeBasicKey]

        #bicoh image
        global PINDEXES

        PINDEXES = pindexes

        dindex = self.addNewImageItem(windex,pindexes[0][0],pTypeList[0], dataParam,processParam.copy())
        dataItem = self.ds[windex][pindexes[0][0]][dindex]
        plot = self.ps[windex][pindexes[0][0]]
        hist = self.ps[windex][pindexes[0][1]]
        plot.legend.addItem(dataItem,dataItem.name)
        plot.legend.setAutoFillBackground(True)

        hist.setImageItem(dataItem)
        hist.setLevels(dataItem.dataMin,dataItem.dataMax)
        hist.plot.yName = dataItem.zName
        hist.plot.yUnit = dataItem.zUnit
        plot.autoBtn.clicked.connect(functools.partial(self.refreshLut, hist,windex,pindexes[0][0],dindex))
        self.updateYAxis(hist.axis)

        yAx,xAx = plot.getAxis('left'),plot.getAxis('bottom')
        self.updateXAxis(xAx)
        self.updateYAxis(yAx)

        #raw signal
        dindex = self.addNewDataItem(windex,pindexes[1][0],pTypeList[1], dataParam,processParam.copy())
        self.updateXAxis(self.ps[windex][pindexes[1][0]].getAxis('bottom'))
        self.updateYAxis(self.ps[windex][pindexes[1][0]].getAxis('left'))

        xRegion = pg.LinearRegionItem()
        xRegion.xRegionSlot = None
        xRegion.setZValue(10)

        xRegion.sigRegionChangeFinished.connect(lambda: self.updateXRegion(windex,pindexes[0][0],xRegion,**keys))
        self.ps[windex][pindexes[1][0]].addItem(xRegion,ignoreBounds=True)
        self.ps[windex][pindexes[0][0]].setAutoVisible(y=True)
        self.ps[windex][pindexes[1][0]].setAutoVisible(y=True)
        xRegion.setRegion([0.018,0.020])


        self.frmWindowLayout.lstWindow.item(windex).setSelected(True)
        self.frmWindowLayout.updatePlotLayouts()
        if self.selectPlot:
            self.frmWindowLayout.tblPlot1.item(self.tempSelectedRow,self.tempSelectedColumn).setSelected(True)


    def refreshLut (self,hist,windex,pindex,dindex):
        item = self.ds[windex][pindex][dindex]
        hist.setLevels(item.dataMin,item.dataMax)

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
        pUnitHeight = (w.height()-wHeightOffset-wHeightInc*len(rows))/len(rows)
        pUnitWidth  = (w.width()-wWidthOffset-wWidthInc*len(columns))/len(columns)

        for column in columns:
            indexes = [i for i in range(len(ps)) if column in [x[1] for x in plocs[i]]]
            rowSpans = [len([x for x in plocs[i] if column==x[1]]) for i in indexes]
            totalRows = np.sum(rowSpans)
            availHeight = pUnitHeight*totalRows
            for i in indexes:
                p=ps[i]
                cItems = p.childItems()
                availHeight -= cItems[0].height()+cItems[1].height()+pHeightOffset
            vUnitHeight = availHeight/totalRows

            for i in range(len(indexes)):
                p=ps[indexes[i]]
                cItems = p.childItems()
                p.setMaximumHeight(vUnitHeight*rowSpans[i]+cItems[0].height()+cItems[1].height()+pHeightOffset)
                p.setMinimumHeight(vUnitHeight*rowSpans[i]+cItems[0].height()+cItems[1].height()+pHeightOffset)

    def linkMaxWidth(self,windex,pindexes):
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
        pUnitHeight = (w.height()-wHeightOffset-wHeightInc*len(rows))/len(rows)
        pUnitWidth  = (w.width()-wWidthOffset-wWidthInc*len(columns))/len(columns)

        for row in rows:
            indexes = [i for i in range(len(ps)) if row in [x[0] for x in plocs[i]]]
            columnSpans = [len([x for x in plocs[i] if row==x[0]]) for i in indexes]
            totalColumns = np.sum(columnSpans)
            availWidth = pUnitWidth*totalColumns
            for i in indexes:
                p=ps[i]
                cItems = p.childItems()
                availWidth -= cItems[2].width()+cItems[3].width()+pWidthOffset
            vUnitWidth = availWidth/totalColumns

            for i in range(len(indexes)):
                p=ps[indexes[i]]
                cItems = p.childItems()
                p.setMaximumWidth(vUnitWidth*columnSpans[i]+cItems[2].width()+cItems[3].width()+pWidthOffset)
                p.setMinimumWidth(vUnitWidth*columnSpans[i]+cItems[2].width()+cItems[3].width()+pWidthOffset)





    def getProcessParam(self):
        # get parameters


        nperseg = self.cmbNperseg.currentText()
        if nperseg =='-':
            nperseg = 512
        elif not str(nperseg).isdigit():
            nperseg = 512
        else:
            nperseg = int (nperseg)

        overlap = self.sbxOverlap.text()
        if overlap =='':
            overlap = 50
        elif not str(overlap).isdigit():
            overlap = 50
        else:
            overlap = int(overlap)
        processParams = {isSmoothKey:self.cbxSmooth.isChecked(),
                        nSmoothKey: self.ledNSmooth.text(),
                        isDcCancelHeadKey: self.rbtDcCancelHead.isChecked(),
                        nDcCancelHeadKey: self.ledNDcCancelHead.text(),
                        isDcCancelTailKey: self.rbtDcCancelTail.isChecked(),
                        nDcCancelTailKey: self.ledNDcCancelTail.text(),
                        npersegKey:nperseg,
                        isUncalibratedSignalKey:self.cbxUncalibratedSignal.isChecked(),
                        isNormalizePsdKey:self.cbxNormalizePsd.isChecked(),
                        overlapKey:overlap
                        }
        return processParams

    def getParams(self,shotChannelItem):

        param = self.params[self.params[channelIdKey].isin(shotChannelItem.selectedChannelIDs)].reset_index(drop=True)
        return param





    def activateWindow(self):
        if len(self.frmWindowLayout.lstWindow.selectedIndexes())==0:
            return
        windex = self.frmWindowLayout.lstWindow.selectedIndexes()[0].row()
        window = self.ws[windex]
        window.setWindowState(window.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        window.activateWindow()




    def selectPlotLayout(self,windex=None, pindexes=[]):
        if windex==None or not pindexes:
            return
        locations = [self.ps[windex][i] in pindexes]
        for location in locations:
            row, column = location[:2]
            self.frmWindowLayout.tblPlot1.item(row,column).setSelected(True)


    def getPlotItemLocation(self,windex=None,pNumber=None):
        if windex==None or pNumber ==None:
            return None,None
        gl = self.frmWindowLayout.windowListboxItem.itemList[windex].ci
        items = gl.items.keys()
        pindexes = [i for i in range(len(items)) if type(items[i])==type(PlotItem1D())]
        locations = gl.items.values()
        for pindex in pindexes:
            if items[pindex].number == pNumber:
                return items[pindex],locations[pindexes]
        return None,None

    def getStartingLocation (self):
        self.selectPlot = False #select the plot in the layout after plotting

        # return if # of cells have conflict with occupied cells (not for basic plot)
        if not self.frmWindowLayout.selectedWindexes:
            windex = self.openNewWindow()

        else:
            windex = self.frmWindowLayout.selectedWindexes[0]

        if not self.frmWindowLayout.tblPlot1.selectedItems():
            # find the lowest column and highest to row to start
            # check for interference
            row,column = self.findAvailableLocation(windex)
            location = (row,column,1,1)
        else:
            location = locationToPlot(self.frmWindowLayout.tblPlot1)
            self.selectPlot=True
            self.tempSelectedRow,self.tempSelectedColumn = self.frmWindowLayout.tblPlot1.selectedItems()[0].row(),self.frmWindowLayout.tblPlot1.selectedItems()[0].column()
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

    def getPindexes(self, windex=None,location=(0,0,1,1), nPlotRow=1, nPlotColumn=1,lut = False,plotMatrix =None,spanMatrix=None):
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

                    loc = planLocations[i][j]
                    if type(spanMatrix)!=type(None):
                        l = list(loc)
                        l[3]=int(l[3]*spanMatrix[i,j])
                        loc = tuple(l)


                    if j != 1:
                        if type(plotMatrix)==type(None):
                            pindex = self.addNewPlot(windex,loc)
                            rowOfPindexes.append(pindex)
                        else:
                            if plotMatrix[i,j]==0:
                                continue
                            else:
                                pindex = self.addNewPlot(windex,loc)
                                rowOfPindexes.append(pindex)
                    else:
                        if type(plotMatrix)==type(None):
                            if lut:
                                pindex = self.addNewLut(windex,loc)
                                rowOfPindexes.append(pindex)

                            else:
                                pindex = self.addNewPlot(windex,loc)
                                rowOfPindexes.append(pindex)
                        else:
                            if plotMatrix[i,j]==0:
                                continue
                            else:
                                if lut:
                                    pindex = self.addNewLut(windex,loc)
                                    rowOfPindexes.append(pindex)

                                else:
                                    pindex = self.addNewPlot(windex,loc)
                                    rowOfPindexes.append(pindex)


                pindexes.append(rowOfPindexes)
            return pindexes

    def processFunctionBasic (self,pItem, *args,**kargs):

        para = pItem.dataParam.reset_index(drop=True).iloc[0]
        y = np.array(pItem.rawData[para[channelIdKey]])
        windex,pindex, = pItem.windex, pItem.pindex


        #calibration and unit
        if pItem.processParam[isUncalibratedSignalKey]:
            yUnit = para[Y_Unit_LabelKey]
        else:
            y = y*float(para[calibrationKey])
            yUnit = para[unitKey]

        #smooth
        if pItem.processParam[isSmoothKey]:
            if str(pItem.processParam[nSmoothKey]).isdigit():
                if 0<int(pItem.processParam[nSmoothKey]) and int(pItem.processParam[nSmoothKey]) <len(y):
                    y = smooth(y,int(pItem.processParam[nSmoothKey]))

        #dc cancel

        if pItem.processParam[isDcCancelHeadKey]:
            if str(pItem.processParam[nDcCancelHeadKey]).isdigit():
                if 0<int(pItem.processParam[nDcCancelHeadKey]) and int(pItem.processParam[nDcCancelHeadKey]) <len(y):
                    y = y - np.average(y[:int(pItem.processParam[nDcCancelHeadKey])])
        elif pItem.processParam[isDcCancelTailKey]:

            if str(pItem.processParam[nDcCancelTailKey]).isdigit():
                if 0<int(pItem.processParam[nDcCancelTailKey]) and int(pItem.processParam[nDcCancelTailKey]) <len(y):
                    y = y - np.average(y[-int(pItem.processParam[nDcCancelTailKey]):])




        # create x array
        x = float(para[X0Key])+float(para[Delta_XKey])*np.arange(len(y))


        #error bar
        if pItem.processParam[isErrorBarKey]:

            if para[channelIdKey] in pItem.errData.columns:
                err = np.array(pItem.errData[para[channelIdKey]])
                if not len(err)==0:
                    if len(x) == len(err):
                        pItem.errorBarItem.setData(x=x, y=y, top=err,bottom=err, beam=self.errorBarBeam*(x[1]-x[0]), pen =pItem.errorBarPen)


        xName = para[X_DimensionKey]
        xUnit = ''
        if xName.lower()=='time':
            xUnit = 's'
        yName = para[channelDescriptionKey]
        name = '%i : %s'%(para[shotNumKey],para[channelDescriptionKey][:21])
        pItem.setData(x,y, name=name)

        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = xName
        pItem.yName = yName
        #return pItem



    def processFunctionPsd (self,pItem, *args,**kargs):

        para = pItem.dataParam.reset_index(drop=True).iloc[0]
        s = np.array(pItem.rawData[para[channelIdKey]])
        t = float(para[X0Key])+float(para[Delta_XKey])*np.arange(len(s))

        nperseg = pItem.processParam[npersegKey]
        overlap = pItem.processParam[overlapKey]
        noverlap = nperseg*overlap//100

        fs = float(1/(t[1]-t[0]))

        if not pItem.processParam[isUncalibratedSignalKey]:
            s = s*float(para[calibrationKey])

        if xRegionKey in pItem.processParam:
            xRegion = pItem.processParam[xRegionKey]
        else:
            xRegion = (t[0],t[-1])


        mask1 = (t>xRegion[0])
        mask2 = (t<xRegion[1])
        mask = mask1 & mask2
        t,s = t[mask],s[mask]


        if len(t)<nperseg:
            nperseg = len(t)
            noverlap = None


        if para[X_DimensionKey].lower()=='time':
            xName = 'Frequency'
            xUnit = 'Hz'
        else:
            xName = ''
            xUnit = ''

        if pItem.processParam[isNormalizePsdKey]:
            s = s/np.average(s)
            yUnit = ''
        else:
            if pItem.processParam[isUncalibratedSignalKey]:
                yUnit = ' %s<sup>2</sup>/%s'  %(para[Y_Unit_LabelKey][0],xUnit)
            else:
                yUnit = ' %s<sup>2</sup>/%s'  %(para[unitKey],xUnit)

        if pItem.processParam[isDetrendKey]:
            if pItem.processParam[nDetrendKey]!='' and \
            str(pItem.processParam[nDetrendKey]).isdigit():
                nDetrend = int(pItem.processParam[nDetrendKey])
                s = s - smooth(s,nDetrend)


        f,psd = welch(x = s, fs = fs, nperseg = nperseg, noverlap = noverlap)

        yName = 'PSD'

        name = '%i : %s'%(para[shotNumKey],para[channelDescriptionKey][:20])
        pItem.pen.setWidth(penWidthPsd)
        pItem.setData(f,psd, pen=pItem.pen,name=name)
        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = xName
        pItem.yName = yName
        #return pItem

    def processFunctionXyView (self,pItem, *args,**kargs):

        para1 = pItem.dataParam.reset_index(drop=True).iloc[0]
        para2 = pItem.dataParam.reset_index(drop=True).iloc[1]
        x = np.array(pItem.rawData[para1[channelIdKey]])
        y = np.array(pItem.rawData[para2[channelIdKey]])
        t = float(para1[X0Key])+float(para1[Delta_XKey])*np.arange(len(x))




        #calibration and unit
        if pItem.processParam[isUncalibratedSignalKey]:
            xUnit,yUnit = para1[Y_Unit_LabelKey], para2[Y_Unit_LabelKey]
        else:
            x,y = x*float(para1[calibrationKey]), y*float(para2[calibrationKey])
            xUnit,yUnit = para1[unitKey], para2[unitKey]

        #smooth
        if pItem.processParam[isSmoothKey]:
            if str(pItem.processParam[nSmoothKey]).isdigit():
                if 0<int(pItem.processParam[nSmoothKey]) and int(pItem.processParam[nSmoothKey]) <len(y):
                    x = smooth(x,int(pItem.processParam[nSmoothKey]))
                    y = smooth(y,int(pItem.processParam[nSmoothKey]))

        #dc cancel

        if pItem.processParam[isDcCancelHeadKey]:

            if str(pItem.processParam[nDcCancelHeadKey]).isdigit():
                if 0<int(pItem.processParam[nDcCancelHeadKey]) and int(pItem.processParam[nDcCancelHeadKey]) <len(y):
                    x = x - np.average(x[:int(pItem.processParam[nDcCancelHeadKey])])
                    y = y - np.average(y[:int(pItem.processParam[nDcCancelHeadKey])])
        elif pItem.processParam[isDcCancelTailKey]:

            if str(pItem.processParam[nDcCancelTailKey]).isdigit():
                if 0<int(pItem.processParam[nDcCancelTailKey]) and int(pItem.processParam[nDcCancelTailKey]) <len(y):
                    x = x - np.average(x[-int(pItem.processParam[nDcCancelTailKey]):])
                    y = y - np.average(y[-int(pItem.processParam[nDcCancelTailKey]):])




        if xRegionKey in pItem.processParam:
            xRegion = pItem.processParam[xRegionKey]
        else:
            xRegion = (t[0],t[-1])

        mask1 = (t>xRegion[0])
        mask2 = (t<xRegion[1])
        mask = mask1 & mask2
        x,y = x[mask],y[mask]







        name = '%i : x: %s - y: %s'%(para1[shotNumKey],para1[channelDescriptionKey][:21],para2[channelDescriptionKey][:21])

        pItem.setData(x,y, symbolPen=pItem.pen,name=name, **symbolPlotArgs)
        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = para1[channelDescriptionKey]
        pItem.yName = para2[channelDescriptionKey]

    def processFunctionCsd (self,pItem, *args,**kargs):

        para1 = pItem.dataParam.reset_index(drop=True).iloc[0]
        para2 = pItem.dataParam.reset_index(drop=True).iloc[1]
        s1 = np.array(pItem.rawData[para1[channelIdKey]])
        s2 = np.array(pItem.rawData[para2[channelIdKey]])
        t = float(para1[X0Key])+float(para1[Delta_XKey])*np.arange(len(s1))
        nperseg = pItem.processParam[npersegKey]
        overlap = pItem.processParam[overlapKey]
        noverlap = nperseg*overlap//100

        fs = float(1/(t[1]-t[0]))

        if not pItem.processParam[isUncalibratedSignalKey]:
            s1 = s1*float(para1[calibrationKey])
            s2 = s2*float(para2[calibrationKey])

        if xRegionKey in pItem.processParam:
            xRegion = pItem.processParam[xRegionKey]
        else:
            xRegion = (t[0],t[-1])

        mask1 = (t>xRegion[0])
        mask2 = (t<xRegion[1])
        mask = mask1 & mask2
        t,s1,s2 = t[mask],s1[mask],s2[mask]

        if len(t)<nperseg:
            nperseg = len(t)
            noverlap = nperseg*overlap//100

        if pItem.processParam[isNormalizePsdKey]:
            s1 = s1/np.average(s1)
            s2 = s2/np.average(s2)

        if pItem.processParam[isDetrendKey]:
            if pItem.processParam[nDetrendKey]!='' and \
            str(pItem.processParam[nDetrendKey]).isdigit():
                nDetrend = int(pItem.processParam[nDetrendKey])
                s1 = s1 - smooth(s1,nDetrend)
                s2 = s2 - smooth(s2,nDetrend)

        f,Csd = csd(s1,s2, fs = fs, nperseg = nperseg, noverlap = noverlap)

        if para1[X_DimensionKey].lower()=='time':
            xName = 'Frequency'
            xUnit = 'Hz'
        else:
            xName = ''
            xUnit = ''

        yUnit = ''
        yName = 'CSD'
        name = '%i : %s - %s'%(para1[shotNumKey],para1[channelDescriptionKey][:21],para2[channelDescriptionKey][:21])
        pItem.pen.setWidth(penWidthPsd)
        pItem.setData(f,np.absolute(Csd), pen=pItem.pen,name=name)
        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = xName
        pItem.yName = yName

    def processFunctionCoh (self,pItem, *args,**kargs):

        para1 = pItem.dataParam.reset_index(drop=True).iloc[0]
        para2 = pItem.dataParam.reset_index(drop=True).iloc[1]
        s1 = np.array(pItem.rawData[para1[channelIdKey]])
        s2 = np.array(pItem.rawData[para2[channelIdKey]])
        t = float(para1[X0Key])+float(para1[Delta_XKey])*np.arange(len(s1))
        nperseg = pItem.processParam[npersegKey]
        overlap = pItem.processParam[overlapKey]
        noverlap = nperseg*overlap//100

        fs = float(1/(t[1]-t[0]))

        if not pItem.processParam[isUncalibratedSignalKey]:
            s1 = s1*float(para1[calibrationKey])
            s2 = s2*float(para2[calibrationKey])

        if xRegionKey in pItem.processParam:
            xRegion = pItem.processParam[xRegionKey]
        else:
            xRegion = (t[0],t[-1])

        mask1 = (t>xRegion[0])
        mask2 = (t<xRegion[1])
        mask = mask1 & mask2
        t,s1,s2 = t[mask],s1[mask],s2[mask]

        if len(t)<nperseg:
            nperseg = len(t)
            noverlap = nperseg*overlap//100

        if pItem.processParam[isNormalizePsdKey]:
            s1 = s1/np.average(s1)
            s2 = s2/np.average(s2)

        if pItem.processParam[isDetrendKey]:
            if pItem.processParam[nDetrendKey]!='' and \
            str(pItem.processParam[nDetrendKey]).isdigit():
                nDetrend = int(pItem.processParam[nDetrendKey])
                s1 = s1 - smooth(s1,nDetrend)
                s2 = s2 - smooth(s2,nDetrend)

        f,coh = coherence(s1,s2, fs = fs, nperseg = nperseg, noverlap = noverlap)

        if para1[X_DimensionKey].lower()=='time':
            xName = 'Frequency'
            xUnit = 'Hz'
        else:
            xName = ''
            xUnit = ''

        yUnit = ''
        yName = 'Coh'
        name = '%i : %s - %s'%(para1[shotNumKey],para1[channelDescriptionKey][:20],para2[channelDescriptionKey][:20])
        pItem.pen.setWidth(penWidthPsd)
        pItem.setData(f,coh, pen=pItem.pen,name=name)
        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = xName
        pItem.yName = yName

    def processFunctionPhase (self,pItem, *args,**kargs):

        para1 = pItem.dataParam.reset_index(drop=True).iloc[0]
        para2 = pItem.dataParam.reset_index(drop=True).iloc[1]
        s1 = np.array(pItem.rawData[para1[channelIdKey]])
        s2 = np.array(pItem.rawData[para2[channelIdKey]])
        t = float(para1[X0Key])+float(para1[Delta_XKey])*np.arange(len(s1))
        nperseg = pItem.processParam[npersegKey]
        overlap = pItem.processParam[overlapKey]
        noverlap = nperseg*overlap//100

        fs = float(1/(t[1]-t[0]))

        if not pItem.processParam[isUncalibratedSignalKey]:
            s1 = s1*float(para1[calibrationKey])
            s2 = s2*float(para2[calibrationKey])

        if xRegionKey in pItem.processParam:
            xRegion = pItem.processParam[xRegionKey]
        else:
            xRegion = (t[0],t[-1])

        mask1 = (t>xRegion[0])
        mask2 = (t<xRegion[1])
        mask = mask1 & mask2
        t,s1,s2 = t[mask],s1[mask],s2[mask]

        if len(t)<nperseg:
            nperseg = len(t)
            noverlap = nperseg*overlap//100

        if pItem.processParam[isNormalizePsdKey]:
            s1 = s1/np.average(s1)
            s2 = s2/np.average(s2)

        if pItem.processParam[isDetrendKey]:
            if pItem.processParam[nDetrendKey]!='' and \
            str(pItem.processParam[nDetrendKey]).isdigit():
                nDetrend = int(pItem.processParam[nDetrendKey])
                s1 = s1 - smooth(s1,nDetrend)
                s2 = s2 - smooth(s2,nDetrend)

        f,Csd = csd(s1,s2, fs = fs, nperseg = nperseg, noverlap = noverlap)

        if para1[X_DimensionKey].lower()=='time':
            xName = 'Frequency'
            xUnit = 'Hz'
        else:
            xName = ''
            xUnit = ''
        phase = np.angle(Csd)/np.pi
        if pItem.processParam[isAbsolutePhaseKey]:
            phase = np.absolute(phase)
            yName = 'Abs. Phase'
        else:
            yName = 'Phase'

        yUnit = 'pi'
        name = '%i : %s - %s'%(para1[shotNumKey],para1[channelDescriptionKey][:20],para2[channelDescriptionKey][:20])
        pItem.pen.setWidth(penWidthPsd)
        pItem.setData(f,phase, pen=pItem.pen,name=name)
        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = xName
        pItem.yName = yName

    def processFunctionSpectrogram (self,pItem, *args,**kargs):

        para1 = pItem.dataParam.reset_index(drop=True).iloc[0]

        s1 = np.array(pItem.rawData[para1[channelIdKey]])

        t = float(para1[X0Key])+float(para1[Delta_XKey])*np.arange(len(s1))
        nperseg = pItem.processParam[npersegKey]
        npersegSpectrogram = pItem.processParam[npersegSpectrogramKey]
        overlap = pItem.processParam[overlapKey]
        overlapSpectrogram = pItem.processParam[overlapSpectrogramKey]

        noverlap = nperseg*overlap//100
        noverlapSpectrogram = npersegSpectrogram*overlapSpectrogram//100

        if 2*nperseg - noverlap >npersegSpectrogram:
            noverlap = 2*nperseg-npersegSpectrogram

        fs = float(1/(t[1]-t[0]))

        if not pItem.processParam[isUncalibratedSignalKey]:
            s1 = s1*float(para1[calibrationKey])



        if len(t)<npersegSpectrogram:
            npersegSpectrogram = len(t)
            noverlapSpectrogram = npersegSpectrogram//2
            nperseg = npersegSpectrogram//2
            noverlap = nperseg//2

        normalized = False
        if pItem.processParam[isNormalizePsdKey]:
            zUnit = ''
            normalized = True
        else:
            if pItem.processParam[isUncalibratedSignalKey]:
                zUnit = ' %s<sup>2</sup>/%s'  %(para1[Y_Unit_LabelKey],'Hz')
            else:
                zUnit = ' %s<sup>2</sup>/%s'  %(para1[unitKey],'Hz')


        if pItem.processParam[isDetrendKey]:
            if pItem.processParam[nDetrendKey]!='' and \
            str(pItem.processParam[nDetrendKey]).isdigit():
                nDetrend = int(pItem.processParam[nDetrendKey])
                s1 = s1 - smooth(s1,nDetrend)


        f,t1,Sxx = psdSpectrogram (s1, fs = fs, npersegSpectrogram=npersegSpectrogram, nperseg = nperseg,noverlapSpectrogram=noverlapSpectrogram, noverlap = noverlap,normalized=normalized)
        data = np.absolute(Sxx.transpose())

        pItem.setImage(data)

        if pItem.processParam[processCountKey]==0:
            pItem.scale(t1[1]-t1[0],f[1]-f[0])
            pItem.translate(float(para1[X0Key])/(t1[1]-t1[0]),0)

        pItem.processParam[processCountKey]+=1

        #print t1[1]-t1[0]


        xName = 'Time'
        xUnit = 's'


        yName = 'Frequency'

        yUnit = 'Hz'
        name = '%i : %s'%(para1[shotNumKey],para1[channelDescriptionKey][:15])
        zName = 'PSD'



        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = xName
        pItem.yName = yName
        pItem.name = name
        pItem.dataMin = np.min(data)
        pItem.dataMax = np.max(data)
        pItem.zName = zName
        pItem.zUnit = zUnit

    def processFunctionCsdSpectrogram (self,pItem, *args,**kargs):

        para1 = pItem.dataParam.reset_index(drop=True).iloc[0]
        para2 = pItem.dataParam.reset_index(drop=True).iloc[1]
        s1 = np.array(pItem.rawData[para1[channelIdKey]])
        s2 = np.array(pItem.rawData[para2[channelIdKey]])
        s1,s2 = alignLength([s1,s2])
        t = float(para1[X0Key])+float(para1[Delta_XKey])*np.arange(len(s1))
        nperseg = pItem.processParam[npersegKey]
        npersegSpectrogram = pItem.processParam[npersegSpectrogramKey]
        overlap = pItem.processParam[overlapKey]
        overlapSpectrogram = pItem.processParam[overlapSpectrogramKey]

        noverlap = nperseg*overlap//100
        noverlapSpectrogram = npersegSpectrogram*overlapSpectrogram//100

        if 2*nperseg - noverlap >npersegSpectrogram:
            noverlap = 2*nperseg-npersegSpectrogram

        fs = float(1/(t[1]-t[0]))

        if not pItem.processParam[isUncalibratedSignalKey]:
            s1 = s1*float(para1[calibrationKey])
            s2 = s2*float(para2[calibrationKey])

        if len(t)<npersegSpectrogram:
            npersegSpectrogram = len(t)
            noverlapSpectrogram = npersegSpectrogram//2
            nperseg = npersegSpectrogram//2
            noverlap = nperseg//2

        normalized = pItem.processParam[isNormalizePsdKey]

        if pItem.processParam[isDetrendKey]:
            if pItem.processParam[nDetrendKey]!='' and \
            str(pItem.processParam[nDetrendKey]).isdigit():
                nDetrend = int(pItem.processParam[nDetrendKey])
                s1 = s1 - smooth(s1,nDetrend)
                s2 = s2 - smooth(s2,nDetrend)


        f,t1,CSDxy = csdSpectrogram(s1,s2,fs = fs, npersegSpectrogram=npersegSpectrogram, nperseg = nperseg,noverlapSpectrogram=noverlapSpectrogram, noverlap = noverlap,normalized=normalized)
        Csd = np.absolute(CSDxy.transpose())



        if para1[X_DimensionKey].lower()=='time':
            yName = 'Frequency'
            yUnit = 'Hz'
            xName = 'Time'
            xUnit = 's'
        else:
            yName = ''
            yUnit = ''
            xName = ''
            xUnit = ''

        zName = 'CSD'
        zUnit = ''



        name = '%i : %s - %s'%(para1[shotNumKey],para1[channelDescriptionKey][:15],para2[channelDescriptionKey][:15])

        pItem.setImage(Csd)

        if pItem.processParam[processCountKey]==0:
            pItem.scale(t1[1]-t1[0],f[1]-f[0])
            pItem.translate(float(para1[X0Key])/(t1[1]-t1[0]),0)

        pItem.processParam[processCountKey]+=1

        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = xName
        pItem.yName = yName
        pItem.name = name
        pItem.dataMin = np.min(Csd)
        pItem.dataMax = np.max(Csd)
        pItem.zName = zName
        pItem.zUnit = zUnit

    def processFunctionCohSpectrogram (self,pItem, *args,**kargs):

        para1 = pItem.dataParam.reset_index(drop=True).iloc[0]
        para2 = pItem.dataParam.reset_index(drop=True).iloc[1]
        s1 = np.array(pItem.rawData[para1[channelIdKey]])
        s2 = np.array(pItem.rawData[para2[channelIdKey]])
        s1,s2 = alignLength([s1,s2])
        t = float(para1[X0Key])+float(para1[Delta_XKey])*np.arange(len(s1))
        nperseg = pItem.processParam[npersegKey]
        npersegSpectrogram = pItem.processParam[npersegSpectrogramKey]
        overlap = pItem.processParam[overlapKey]
        overlapSpectrogram = pItem.processParam[overlapSpectrogramKey]

        noverlap = nperseg*overlap//100
        noverlapSpectrogram = npersegSpectrogram*overlapSpectrogram//100

        if 2*nperseg - noverlap >npersegSpectrogram:
            noverlap = 2*nperseg-npersegSpectrogram

        fs = float(1/(t[1]-t[0]))

        if not pItem.processParam[isUncalibratedSignalKey]:
            s1 = s1*float(para1[calibrationKey])
            s2 = s2*float(para2[calibrationKey])

        if len(t)<npersegSpectrogram:
            npersegSpectrogram = len(t)
            noverlapSpectrogram = npersegSpectrogram//2
            nperseg = npersegSpectrogram//2
            noverlap = nperseg//2

        normalized = pItem.processParam[isNormalizePsdKey]

        if pItem.processParam[isDetrendKey]:
            if pItem.processParam[nDetrendKey]!='' and \
            str(pItem.processParam[nDetrendKey]).isdigit():
                nDetrend = int(pItem.processParam[nDetrendKey])
                s1 = s1 - smooth(s1,nDetrend)
                s2 = s2 - smooth(s2,nDetrend)


        f,t1,COHxy = cohSpectrogram(s1,s2,fs = fs, npersegSpectrogram=npersegSpectrogram, nperseg = nperseg,noverlapSpectrogram=noverlapSpectrogram, noverlap = noverlap,normalized=normalized)
        coh = COHxy.transpose()


        if para1[X_DimensionKey].lower()=='time':
            yName = 'Frequency'
            yUnit = 'Hz'
            xName = 'Time'
            xUnit = 's'
        else:
            yName = ''
            yUnit = ''
            xName = ''
            xUnit = ''

        zName = 'Coh'
        zUnit = ''



        name = '%i : %s - %s'%(para1[shotNumKey],para1[channelDescriptionKey][:15],para2[channelDescriptionKey][:15])

        pItem.setImage(coh)

        if pItem.processParam[processCountKey]==0:
            pItem.scale(t1[1]-t1[0],f[1]-f[0])
            pItem.translate(float(para1[X0Key])/(t1[1]-t1[0]),0)

        pItem.processParam[processCountKey]+=1

        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = xName
        pItem.yName = yName
        pItem.name = name
        pItem.dataMin = np.min(coh)
        pItem.dataMax = np.max(coh)
        pItem.zName = zName
        pItem.zUnit = zUnit

    def processFunctionPhaseSpectrogram (self,pItem, *args,**kargs):

        para1 = pItem.dataParam.reset_index(drop=True).iloc[0]
        para2 = pItem.dataParam.reset_index(drop=True).iloc[1]
        s1 = np.array(pItem.rawData[para1[channelIdKey]])
        s2 = np.array(pItem.rawData[para2[channelIdKey]])
        s1,s2 = alignLength([s1,s2])
        t = float(para1[X0Key])+float(para1[Delta_XKey])*np.arange(len(s1))
        nperseg = pItem.processParam[npersegKey]
        npersegSpectrogram = pItem.processParam[npersegSpectrogramKey]
        overlap = pItem.processParam[overlapKey]
        overlapSpectrogram = pItem.processParam[overlapSpectrogramKey]

        noverlap = nperseg*overlap//100
        noverlapSpectrogram = npersegSpectrogram*overlapSpectrogram//100

        if 2*nperseg - noverlap >npersegSpectrogram:
            noverlap = 2*nperseg-npersegSpectrogram

        fs = float(1/(t[1]-t[0]))

        if not pItem.processParam[isUncalibratedSignalKey]:
            s1 = s1*float(para1[calibrationKey])
            s2 = s2*float(para2[calibrationKey])

        if len(t)<npersegSpectrogram:
            npersegSpectrogram = len(t)
            noverlapSpectrogram = npersegSpectrogram//2
            nperseg = npersegSpectrogram//2
            noverlap = nperseg//2

        normalized = pItem.processParam[isNormalizePsdKey]

        if pItem.processParam[isDetrendKey]:
            if pItem.processParam[nDetrendKey]!='' and \
            str(pItem.processParam[nDetrendKey]).isdigit():
                nDetrend = int(pItem.processParam[nDetrendKey])
                s1 = s1 - smooth(s1,nDetrend)
                s2 = s2 - smooth(s2,nDetrend)


        f,t1,CSDxy = csdSpectrogram(s1,s2,fs = fs, npersegSpectrogram=npersegSpectrogram, nperseg = nperseg,noverlapSpectrogram=noverlapSpectrogram, noverlap = noverlap,normalized=normalized)

        phase = np.angle(CSDxy.transpose())/np.pi
        if pItem.processParam[isAbsolutePhaseKey]:
            phase = np.absolute(phase)
            zName = 'Abs. Phase'
        else:
            zName = 'Phase'




        if para1[X_DimensionKey].lower()=='time':
            yName = 'Frequency'
            yUnit = 'Hz'
            xName = 'Time'
            xUnit = 's'
        else:
            yName = ''
            yUnit = ''
            xName = ''
            xUnit = ''


        zUnit = 'pi'



        name = '%i : %s - %s'%(para1[shotNumKey],para1[channelDescriptionKey][:15],para2[channelDescriptionKey][:15])

        pItem.setImage(phase)


        if pItem.processParam[processCountKey]==0:
            pItem.scale(t1[1]-t1[0],f[1]-f[0])
            pItem.translate(float(para1[X0Key])/(t1[1]-t1[0]),0)

        pItem.processParam[processCountKey]+=1

        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = xName
        pItem.yName = yName
        pItem.name = name
        pItem.dataMin = np.min(phase)
        pItem.dataMax = np.max(phase)
        pItem.zName = zName
        pItem.zUnit = zUnit


    def processFunctionBicoh (self,pItem, *args,**kargs):

        para = pItem.dataParam.reset_index(drop=True).iloc[0]
        s = np.array(pItem.rawData[para[channelIdKey]])
        t = float(para[X0Key])+float(para[Delta_XKey])*np.arange(len(s))

        nperseg = pItem.processParam[npersegKey]
        overlap = pItem.processParam[overlapKey]


        fs = float(1/(t[1]-t[0]))

        if not pItem.processParam[isUncalibratedSignalKey]:
            s = s*float(para[calibrationKey])

        if xRegionKey in pItem.processParam:
            xRegion = pItem.processParam[xRegionKey]
        else:
            xRegion = (t[0],t[-1])


        mask1 = (t>xRegion[0])
        mask2 = (t<xRegion[1])
        mask = mask1 & mask2
        t,s = t[mask],s[mask]


        if len(t)<nperseg:
            nperseg = len(t)



        if para[X_DimensionKey].lower()=='time':
            xName = 'F1'
            xUnit = 'Hz'
            yName = 'F2'
            yUnit = 'Hz'
        else:
            xName = ''
            xUnit = ''
            yName = ''
            yUnit == ''



        if pItem.processParam[isDetrendKey]:
            if pItem.processParam[nDetrendKey]!='' and \
            str(pItem.processParam[nDetrendKey]).isdigit():
                nDetrend = int(pItem.processParam[nDetrendKey])
                s = s - smooth(s,nDetrend)


        f, bic = bicoh (s, fs = fs, nperseg = nperseg,overlap=overlap)
        fUnit = f[1]-f[0]
        data = np.absolute(bic)

        pItem.setImage(data)

        if pItem.processParam[processCountKey]==0:
            pItem.scale(fUnit,fUnit)
            pItem.translate(f[0]/fUnit,f[0]/fUnit)

        pItem.processParam[processCountKey]+=1

        #print t1[1]-t1[0]


        name = '%i : %s'%(para[shotNumKey],para[channelDescriptionKey][:15])
        zName = 'Bicoherence'
        zUnit = ''



        pItem.xUnit = xUnit
        pItem.yUnit = yUnit
        pItem.xName = xName
        pItem.yName = yName
        pItem.name = name
        pItem.dataMin = np.min(data)
        pItem.dataMax = np.max(data)
        pItem.zName = zName
        pItem.zUnit = zUnit



    def updateXRegion(self,windex,pindex,xRegion,*args,**kargs):
        dataItems = self.ds[windex][pindex]
        for dataItem in dataItems:
            dataItem.processParam[xRegionKey]=xRegion.getRegion()
            self.exeProcessFunction(dataItem)


    def updateXRegion1(self,wNumber,pNumber,*args,**kargs):

        glw = [x for x in self.frmWindowLayout.windowListboxItem.itemList if x.number ==wNumber][0]
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
            self.exeProcessFunction(dataItem,**keys)


    def exeProcessFunction(self,item,*args,**kargs):
        if item.plotType==pTypeBasicKey:
            self.processFunctionBasic(item,*args,**kargs)
            return
        elif item.plotType == pTypePsdKey :
            self.processFunctionPsd(item,*args,**kargs)
            return
        elif item.plotType == pTypeCsdKey:
            self.processFunctionCsd(item,*args,**kargs)
            return
        elif item.plotType == pTypeCohKey:
            self.processFunctionCoh(item,*args,**kargs)
            return
        elif item.plotType == pTypePhaseKey:
            self.processFunctionPhase(item,*args,**kargs)
            return
        elif item.plotType == pTypeSpectrogramKey:
            self.processFunctionSpectrogram(item,*args,**kargs)
            return
        elif item.plotType == pTypeCsdSpectrogramKey:
            self.processFunctionCsdSpectrogram(item,*args,**kargs)
            return
        elif item.plotType == pTypeCohSpectrogramKey:
            self.processFunctionCohSpectrogram(item,*args,**kargs)
            return
        elif item.plotType == pTypePhaseSpectrogramKey:
            self.processFunctionPhaseSpectrogram(item,*args,**kargs)
            return
        elif item.plotType == pTypeBicohKey:
            self.processFunctionBicoh(item,*args,**kargs)
            return

        elif item.plotType == pTypeXyView:
            self.processFunctionXyView(item,*args,**kargs)
            return


    def linkX (self):
        if len(self.frmWindowLayout.tblPlot1.selectedItems())+len(self.frmWindowLayout.tblPlot2.selectedItems())<2:
            return
        pLocations = []
        for table in self.frmWindowLayout.tableList:
            windex = table.windex
            if windex==None:
                continue
            for item in table.selectedItems():
                pindex = int(item.text().split(' ')[-1])
                pLocations.append((windex,pindex))
        for x in pLocations[1:]:
            self.ps[x[0]][x[1]].setXLink(self.ps[pLocations[0][0]][pLocations[0][1]])



    def linkY(self):
        if len(self.frmWindowLayout.tblPlot1.selectedItems())+len(self.frmWindowLayout.tblPlot2.selectedItems())<2:
            return
        pLocations = []
        for table in self.frmWindowLayout.tableList:
            windex = table.windex
            if windex==None:
                continue
            for item in table.selectedItems():
                pindex = int(item.text().split(' ')[-1])
                pLocations.append((windex,pindex))
        for x in pLocations[1:]:
            self.ps[x[0]][x[1]].setYLink(self.ps[pLocations[0][0]][pLocations[0][1]])


    def linkXY(self):
        if len(self.frmWindowLayout.tblPlot1.selectedItems())+len(self.frmWindowLayout.tblPlot2.selectedItems())<2:
            return
        pLocations = []
        for table in self.frmWindowLayout.tableList:
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
        if len(self.frmWindowLayout.tblPlot1.selectedItems())+len(self.frmWindowLayout.tblPlot2.selectedItems())<2:
            return
        xRegions = []
        for table in self.frmWindowLayout.tableList:
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

        #self.btnParamSelect.clicked.connect(lambda: self.ParamSelect(self.lstParam))
        #self.btnParamSelectClear.clicked.connect(lambda: self.ParamSelectClear(self.lstParam))
        #self.btnParamAdd.clicked.connect(lambda: self.ParamAdd(self.lstParam))

        #self.btnParamSelect.clicked.connect(functools.partial(self.ParamSelect,self.lstParam))
        #self.btnParamSelectClear.clicked.connect(functools.partial(self.ParamSelectClear,self.lstParam))
        #self.btnParamAdd.clicked.connect(functools.partial(self.ParamAdd,self.lstParam))


    def updateChannelOptions (self,paramDf):
        self.frmAvailableChannel.updateChannelOptions(paramDf)

    def updateWindowList(self):
        self.frmWindowLayout.updateWindowList()

    def saveError(self):
        1
        filePath = QFileDialog.getSaveFileName (parent = None, caption = "Select file name", directory = None)
        if filePath == "":
            return

        param = self.params[self.params[channelIdKey].isin(np.array(self.frmAvailableChannel.selectedChannelIDs).astype(self.params[channelIdKey].dtype))].reset_index(drop=True)
        if len (param) == 0:
            return

        errData = self.getErr(param)

        if len (errData)==0:
            print ("return")
            return

        errData.to_csv(filePath)





if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    frame = frmComAction()
    
    # app.aboutToQuit.connect(app.deleteLater)
    # Frame = QtWidgets.QFrame()
    # ui = frmLoadData()
    # ui.setupUi(Frame)
    frame.show()
    app.exec_()

