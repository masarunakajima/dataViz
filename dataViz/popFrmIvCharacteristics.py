

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QShortcut



from PyQt5.QtCore import QObject, pyqtSignal

from pyqtgraph import functions as fn

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
from constants import *



class popFrmIvCharacteristics(QtWidgets.QFrame, dataGuiBaseClass):
    sigIvDataAdded = QtCore.pyqtSignal()

    def __init__(self ,displayType='list'):
        super().__init__()
        uic.loadUi('popFrmIvCharacteristics.ui', self)
        
        #create shortcut for deselecting for all the lists
        self.lstWidgetList = [getattr(self, n) for n in dir(self) if 'lst' in n]
        for lst in self.lstWidgetList:
            QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Escape), lst,  lst.clearSelection,context=QtCore.Qt.WidgetShortcut)
        
        
        #create ListboxItem instances

        self.ListboxItemLoadedShot = ListboxItem(self.lstLoadedShot)  
        self.ListboxItemChannelI = ListboxItem (self.lstChannelI)
        self.ListboxItemChannelV = ListboxItem (self.lstChannelV)
        self.ListboxItemSelectedLoadedShot = ListboxItem(self.lstSelectedShot)
        self.ListboxItemSelectedChannelI = ListboxItem (self.lstSelectedChannelI)
        self.ListboxItemSelectedChannelV = ListboxItem (self.lstSelectedChannelV)
        
        self.lstChannelList = [self.lstChannelI,self.lstChannelV]
        self.listboxItemList = [self.ListboxItemChannelI,self.ListboxItemChannelV]
        
        
        
        self.selectedShots = []
        self.selectedChannels = []
        self.selectedChannelIDs = []
        
        
        #Connect



        
        self.lstLoadedShot.itemSelectionChanged.connect(self.updateAvailChannel)
        #self.lstChannel.itemSelectionChanged.connect(self.updateAvailShot)
        
        #list shots and channels
        self.listLoadedShots()
        self.listChannels()
        
        #define parameters
        self.selectedShots = []
        self.selectedChannelI = []
        self.selectedChannelV = []
        
        #connect buttons
        self.btnShotRefresh.clicked.connect(self.shotRefresh)
        self.btnAddShot.clicked.connect(self.addShot)
        self.btnAddIv.clicked.connect(self.addIv)
        self.btnClearShot.clicked.connect(self.clearShot)
        self.btnClearChannel.clicked.connect(self.clearChannel)
        self.btnCalculate.clicked.connect(self.calculate)
        
        #make a list of line entries that expect numbers
        self.ledList = [getattr(self, n) for n in dir(self) if 'led' in n]
        
        #make a list of line entrie for voltranges
        self.voltRangeMinList = [getattr(self, n) for n in dir(self) if 'ledVoltRangeMin' in n]
        self.voltRangeMaxList = [getattr(self, n) for n in dir(self) if 'ledVoltRangeMax' in n]
        
        
        #set initial process parameters
        self.cbxInvertI.setChecked(True)
        self.cbxSmooth.setChecked(True)
        self.ledSmoothTime.setText('0.1')
        self.rbtDcCancelTail.setChecked(True)
        self.ledDcCancelTailTime.setText('5')
        self.ledAsymtoteFactor.setText('4')
        self.ledVoltRangeMin1.setText('30')
        self.ledVoltRangeMax1.setText('50')
        
        
        
    
        
    def clearChannel (self):
        self.selectedChannelI = []
        self.selectedChannelV = []
        self.updateSelectedShotChannel()
        
        
    def clearShot (self):
        self.selectedShots = []
        self.updateSelectedShotChannel()
        
    
        
    def updateSelectedShotChannel(self):
        self.ListboxItemSelectedLoadedShot.nameList = self.selectedShots
        self.ListboxItemSelectedLoadedShot.itemList = self.selectedShots
        self.ListboxItemSelectedLoadedShot.listInBox()
        
        self.ListboxItemSelectedChannelI.nameList = self.selectedChannelI
        self.ListboxItemSelectedChannelI.itemList = self.selectedChannelI
        self.ListboxItemSelectedChannelI.listInBox() 

        self.ListboxItemSelectedChannelV.nameList = self.selectedChannelV
        self.ListboxItemSelectedChannelV.itemList = self.selectedChannelV
        self.ListboxItemSelectedChannelV.listInBox()   
        
        
        
        
    def addIv (self):

        if len(self.lstChannelI.selectedItems())!=1 or len(self.lstChannelV.selectedItems())!=1:
            return
        listI = [x.text() for x in self.lstChannelI.selectedItems()]
        listV = [x.text() for x in self.lstChannelV.selectedItems()]
        
        self.selectedChannelI += listI
        self.selectedChannelV += listV
        self.updateSelectedShotChannel()
        
        
    def addShot(self):
        if len(self.lstLoadedShot.selectedItems())==0:
            return
        l = [x.text() for x in self.lstLoadedShot.selectedItems()]
        self.selectedShots += l
        
        self.updateSelectedShotChannel()
            
        

    def shotRefresh (self) :
        self.listLoadedShots()
        self.listChannels()
        
    def listLoadedShots(self):
        if len(self.params)==0:
            return
        l = list(self.params[self.shotNumKey].unique())  

        self.ListboxItemLoadedShot.nameList = l
        self.ListboxItemLoadedShot.itemList = l                
        self.ListboxItemLoadedShot.listInBox()       
        
        
    def listChannels (self):
        if len(self.params)==0:
            return

        l = list(self.params[self.channelDescriptionKey].unique())  
        l = [str(x) for x in l if self.X_ValueKey not in str(x)]   
        for listboxItem in self.listboxItemList:
            listboxItem.nameList = l
            listboxItem.itemList = l                
            listboxItem.listInBox()


    def updateAvailChannel(self):

        for lst in self.lstChannelList:
            
            for item in [lst.item(i) for i in range(lst.count())]:
                item.setFlags(item.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                item.setBackgroundColor(self.listBgColor)
   
        if len(self.lstLoadedShot.selectedItems())==0:
            return
        
        shotNums = [x.text() for x in self.lstLoadedShot.selectedItems()]
        
        for lst in self.lstChannelList:
            for item in [lst.item(i) for i in range(lst.count())]:
                count = 0
                for shotNum in shotNums:               
                    tempParam = self.params[self.params[self.shotNumKey]==int(shotNum)]
                    if item.text() in list(tempParam[self.channelDescriptionKey]):
                        count +=1
                        
                if count == 0: #if the channel cannot be found in any shots selected
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable & ~QtCore.Qt.ItemIsEnabled)
                elif count < len(shotNums):#only some but not all the shots selected have the channel
                    item.setBackgroundColor(self.listIncompleteMatchBgColor)
                

        

                
                
    def getIvProcessParam(self):
        # return None if any of them have wrong entries
        for led in self.ledList :
            if led.text()!='' and not led.text().replace('-','').replace('.','').isdigit():
                return None
        if self.ledAsymtoteFactor.text() =='':
            return None
        anyRange = False
        for i in range(len(self.voltRangeMaxList)):
            if self.voltRangeMinList[i].text()!='' and self.voltRangeMaxList[i].text()!='':
                anyRange = True
        if not anyRange:
            return None


        processParams = {self.IV_isInvertIKey: self.cbxInvertI.isChecked(),
                        self.IV_isSmoothKey:self.cbxSmooth.isChecked(),
                        self.IV_smoothTimeKey: self.ledSmoothTime.text(),
                        self.IV_isDcCancelHeadKey: self.rbtDcCancelHead.isChecked(), 
                        self.IV_dcCancelHeadTimeKey: self.ledDcCancelHeadTime.text(),
                        self.IV_isDcCancelTailKey: self.rbtDcCancelTail.isChecked(),
                        self.IV_dcCancelTailTimeKey: self.ledDcCancelTailTime.text(),
                        self.IV_asymtoteFactorKey: self.ledAsymtoteFactor.text(),
                        self.IV_voltRangeMin1Key: self.ledVoltRangeMin1, 
                        self.IV_voltRangeMax1Key: self.ledVoltRangeMax1,
                        self.IV_voltRangeMin2Key: self.ledVoltRangeMin2, 
                        self.IV_voltRangeMax2Key: self.ledVoltRangeMax2,
                        self.IV_voltRangeMin3Key: self.ledVoltRangeMin3, 
                        self.IV_voltRangeMax3Key: self.ledVoltRangeMax3,

                        }
        return processParams
        
    def calculate(self):
        if len(self.selectedShots)==0 or len(self.selectedChannelI)==0:
            return
        
        ivProcessParam = self.getIvProcessParam()
        if not ivProcessParam :
            return
        
        for shot in self.selectedShots:
            tempParamDf = self.params[self.params[self.shotNumKey].isin(np.array([shot]).astype(self.params[self.shotNumKey].dtype))].reset_index(drop=True)
            for i in range(len(self.selectedChannelI)):
                paramI = tempParamDf[tempParamDf[self.channelDescriptionKey].isin(np.array([self.selectedChannelI[i]]).astype(tempParamDf[self.channelDescriptionKey].dtype))].reset_index(drop=True)
                paramV = tempParamDf[tempParamDf[self.channelDescriptionKey].isin(np.array([self.selectedChannelV[i]]).astype(tempParamDf[self.channelDescriptionKey].dtype))].reset_index(drop=True)
                if len(paramI) ==1 and len(paramV)==1:          
                    self.calculateIV(paramI, paramV,ivProcessParam)
        
    
    def calculateIV (self, paramI, paramV, ivProcessParam):
        dataI = self.getData(paramI)
        dataV = self.getData(paramV)
        
        Ifactor = 1.0
        if ivProcessParam[self.IV_isInvertIKey]:
            Ifactor = -1.0
        
        paraI = paramI.reset_index(drop=True).ix[0]
        I1 = Ifactor*np.array(dataI[paraI[self.channelIdKey]])
        tI = float(paraI[self.X0Key])+np.arange(len(I1))*float(paraI[self.Delta_XKey])
        
        paraV = paramV.reset_index(drop=True).ix[0]
        V1 = np.array(dataV[paraV[self.channelIdKey]])
        tV = float(paraV[self.X0Key])+np.arange(len(V1))*float(paraI[self.Delta_XKey])
        
        I1,V1 = alignLength ([I1,V1])
        
        #calibration
        I2 = I1*float(paraI[self.calibrationKey])
        V2 = V1*float(paraV[self.calibrationKey])
        
        #smooth and Dc Cancel
        nSmoothI = nSmoothV = 1
        if ivProcessParam[self.IV_isSmoothKey]:
            if ivProcessParam[self.IV_smoothTimeKey]!='':
                tSmooth = float(ivProcessParam[self.IV_smoothTimeKey])*0.001
                nSmoothI = tSmooth/float(paraI[self.Delta_XKey])
                nSmoothV = tSmooth/float(paraV[self.Delta_XKey])
                
        dcCancelI =  dcCancelV = 0
        
        if ivProcessParam[self.IV_isDcCancelHeadKey]:
            if ivProcessParam[self.IV_dcCancelHeadTimeKey] !='':
                tDcCancel = float(ivProcessParam[self.IV_dcCancelHeadTimeKey])*0.001
                nDcCancelI = tDcCancel/float(paraI[self.Delta_XKey])
                nDcCancelV = tDcCancel/float(paraV[self.Delta_XKey])
                if 0<np.min([nDcCancelI, nDcCancelV]) and np.max([nDcCancelI, nDcCancelV]) <np.min([len(I2),len(V2)]):
                    dcCancelI = np.average(I2[:nDcCancelI])
                    dcCancelV = np.average(V2[:nDcCancelV])

        elif ivProcessParam[self.IV_isDcCancelTailKey]:
            if ivProcessParam[self.IV_dcCancelTailTimeKey] !='':
                tDcCancel = float(ivProcessParam[self.IV_dcCancelTailTimeKey])*0.001
                nDcCancelI = tDcCancel/float(paraI[self.Delta_XKey])
                nDcCancelV = tDcCancel/float(paraV[self.Delta_XKey])
                if 0<np.min([nDcCancelI, nDcCancelV]) and np.max([nDcCancelI, nDcCancelV]) <np.min([len(I2),len(V2)]):
                    dcCancelI = np.average(I2[-nDcCancelI:])
                    dcCancelV = np.average(V2[-nDcCancelV:])
        
        Iraw, Vraw = I2 - dcCancelI,  V2 - dcCancelV  
        I3, V3 = smooth(I2,nSmoothI)-dcCancelI, smooth(V2,nSmoothV)-dcCancelV          
        
        #psd to get dominant frequency
        f,psd = welch(V3,fs=1.0/float(paraV[self.Delta_XKey]),nperseg = 2048*4)
        sweepFreq = f[psd.argmax()]

        if sweepFreq == 0.0:
            return
        sweepPeriod = 1.0/sweepFreq
        nPeriod = int(sweepPeriod/float(paraV[self.Delta_XKey]))
        
        #find first peak
        argStart = V3[:nPeriod].argmax()
        asymtoteFactor = float(ivProcessParam[self.IV_asymtoteFactorKey])


        for i in range(len(self.voltRangeMinList)):
            rangeMin = self.voltRangeMinList[i].text()
            rangeMax = self.voltRangeMaxList[i].text()
            if rangeMin=='' or rangeMax =='':
                continue
            if float(rangeMin)>=float(rangeMax):
                continue
            vMin, vMax = float(rangeMin),float(rangeMax)

            global II3, VV3, ARGSTART, NPERIOD, ASYMTOTEFACTOR, VMIN, VMAX
            II3, VV3, ARGSTART, NPERIOD, ASYMTOTEFACTOR, VMIN, VMAX = I3,V3,argStart,nPeriod,asymtoteFactor, vMin, vMax

            TeList, ErList = self.calculateTe(I3,V3,argStart,nPeriod,asymtoteFactor, vMin, vMax,Iraw, Vraw)              
            
            
            location = 'NA'
            strI, strV = paraI[self.channelDescriptionKey].replace(' ','').upper(),paraV[self.channelDescriptionKey].replace(' ','').upper()
            for loc in self.probeLocationList:
                if loc in strI and loc in strV:
                    location = loc
            channelDescription = '*'+' Te '+location+ ' ('+ rangeMin + ' - ' + rangeMax+ ' V' +')'+'/'+str(datetime.now())
            
            
            channelId = str(paraI[self.shotNumKey])+'_'+channelDescription


            
            dic = paraI.copy()

            dic[self.channelDescriptionKey]=channelDescription
            dic[self.channelIdKey]=channelId
            dic[self.X0Key] = str(tI[argStart]+sweepPeriod/2)
            dic[self.Delta_XKey]= str(sweepPeriod)
            dic[self.unitKey] = 'eV'
            dic[self.calibrationKey] = 1.0
            dic[self.X_DimensionKey] = 'Time'
            dic[self.Y_Unit_LabelKey]='eV'
            

            for item in ivProcessParam.items():
                dic[item[0]]=item[1]
            
            param = pd.DataFrame([dic])
            dataGuiBaseClass.params=dataGuiBaseClass.params.append(param)
            
            df,dfErr = pd.DataFrame(), pd.DataFrame()
            df[channelId] = TeList
            dfErr[channelId] = ErList
            dataIndex = [x for x in range(len(self.dataList)) if self.dataList[x][self.shotNumKey]==str(paraI[self.shotNumKey])][0]
            dataGuiBaseClass.dataList[dataIndex][self.dfKey] = pd.concat([dataGuiBaseClass.dataList[dataIndex][self.dfKey],df], axis=1)
            dataGuiBaseClass.dataList[dataIndex][self.dfErrKey] = pd.concat([dataGuiBaseClass.dataList[dataIndex][self.dfErrKey],dfErr], axis=1)
        
            self.sigIvDataAdded.emit()
            
            
            
            
            
            
    def calculateTe (self,I,V,argStart,nPeriod,asymtoteFactor, vMin, vMax, Iraw, Vraw):
        TeList = []
        ErList = []
        
        j = 0  
        time = datetime.now()
        while argStart+(j+1)*nPeriod < len(V):

            segI = I[(argStart+j*nPeriod):(argStart+(j+1)*nPeriod)]
            segV = V[(argStart+j*nPeriod):(argStart+(j+1)*nPeriod)]
            segIraw = Iraw[(argStart+j*nPeriod):(argStart+(j+1)*nPeriod)]
            segVraw = Vraw[(argStart+j*nPeriod):(argStart+(j+1)*nPeriod)]
            
            
            argsort = segV.argsort()
            sortI, sortV = segI[argsort],segV[argsort]
            sortIraw, sortVraw = segIraw[argsort],segVraw[argsort]
            
            #find asysmtote
            slope, intercept, r_value, p_value, slopeErr = \
            stats.linregress([sortV[0],sortV[-1]*asymtoteFactor],[segI.min(),0.0])
            
            sortI = sortI-intercept-slope*sortV
            sortIraw = sortIraw-intercept-slope*sortVraw
            
            argPos = sortI>0
            argPosRaw = sortIraw>0
            
            logI, sortV2 = np.log(sortI[argPos]), sortV[argPos]
            logIraw, sortV2raw = np.log(sortIraw[argPosRaw]), sortVraw[argPosRaw]
            
            argMin, argMax = sortV2 > vMin, sortV2 < vMax
            argMinRaw, argMaxRaw = sortV2raw > vMin, sortV2raw < vMax
            
            logI1, sortV3 = logI[argMin*argMax]  , sortV2[argMin*argMax]
            logI1raw, sortV3raw = logIraw[argMinRaw*argMaxRaw]  , sortV2raw[argMinRaw*argMaxRaw]
            
            
            if len(logI1)<3:
                TeList.append(0.0)
                ErList.append(0.0)
                j+=1
                continue
            
            slope, intercept, r_value, p_value, slopeErr = stats.linregress(sortV3,logI1)
            
            
            line = slope*sortV3raw+intercept
            stdResidual = np.sqrt((np.sum(np.square(logI1raw-line)))/(len(sortV3raw)-2))
            vAve = np.average(sortV3raw)
            stdSlope = stdResidual/np.sqrt(np.sum(np.square(sortV3raw - vAve)))
            
            
            if 1/slope < 0 or 1/slope > 100:
                TeList.append(0.0)
                ErList.append(0.0)
                j+=1
                continue
            
            TeList.append(1/slope)            
            ErList.append(np.abs(stdSlope/np.square(slope)))
            
            j+=1
                        

            
        
        return TeList, ErList
        
        

        
            
        
        
                
                
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    frame = popFrmIvCharacteristics()
    
    # app.aboutToQuit.connect(app.deleteLater)
    # Frame = QtWidgets.QFrame()
    # ui = frmLoadData()
    # ui.setupUi(Frame)
    frame.show()
    app.exec_()


