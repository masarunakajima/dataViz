# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'frmShotChannel.ui'
#
# Created: Wed Jun 15 10:56:51 2016
#      by: PyQt5 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from constants import *




import warnings
import numpy as np
import pandas as pd
import os,sys
import matplotlib.pyplot as plt
import math as m
#%matplotlib inline 
import scipy
from scipy.interpolate import UnivariateSpline
from matplotlib import colors
import six
from scipy.fftpack import fft
from scipy.signal import *
import scipy

from datetime import datetime
import pyqtgraph as pg
import functools
from glob import glob
from time import sleep
from scipy.linalg import hankel
import scipy.io as sio

path =os.getcwd()
while len(path)>5:
    path = os.path.dirname(path)
    dirs = next(os.walk(path))[1]
    if path not in sys.path:
        sys.path.append(path)
    for Dir in dirs:
        if Dir not in sys.path:
            sys.path.append(os.path.join(path,Dir))




class dataGuiBaseClass(object):
    

    
    params = pd.DataFrame()
    dataList = []
    ws = []
    ps = []
    ds = []
    xRegionGroups=[]
    
    def __init__(self):
        1
        
        
    def reset(self):
        dataGuiBaseClass.params = pd.DataFrame()
        dataGuiBaseClass.dataList = []
        dataGuiBaseClass.ws = []
        dataGuiBaseClass.ps = []
        dataGuiBaseClass.ds = []
        
    def getData (self,param):
        
        data = pd.DataFrame()
        for shotNum in list (param[shotNumKey].unique()):
            dataIndex = [x for x in range(len(self.dataList)) if self.dataList[x][shotNumKey]==str(shotNum)][0]
            tempData = self.dataList[dataIndex][dfKey]
            tempParam = param[param[shotNumKey]==shotNum].reset_index(drop=True)
            channels = list(tempParam[channelDescriptionKey].unique())
            channelMask = np.zeros(len(tempData.columns)).astype(bool)
            for channelName in channels:
                para = tempParam[tempParam[channelDescriptionKey]==channelName].reset_index(drop=True)
                channelId = para[channelIdKey][0]
                channelMask = channelMask | (tempData.columns==channelId)
            tempData = tempData[tempData.columns[channelMask]]
            data= pd.concat([data, tempData], axis=1).reset_index(drop=True)
        null = pd.isnull(data).any(1).to_numpy().nonzero()[0]
        if len(null)>0:
            data = data.iloc[:(null[0]-1),:]
        return data
        
    def getErr (self,param):
        
        data = pd.DataFrame()
        for shotNum in list (param[shotNumKey].unique()):
            dataIndex = [x for x in range(len(self.dataList)) if self.dataList[x][shotNumKey]==str(shotNum)][0]
            tempData = self.dataList[dataIndex][dfErrKey]
            tempParam = param[param[shotNumKey]==shotNum].reset_index(drop=True)
            channels = list(tempParam[channelDescriptionKey].unique())
            channelMask = np.zeros(len(tempData.columns)).astype(bool)
            for channelName in channels:
                para = tempParam[tempParam[channelDescriptionKey]==channelName].reset_index(drop=True)
                channelId = para[channelIdKey][0]
                channelMask = channelMask | (tempData.columns==channelId)
            tempData = tempData[tempData.columns[channelMask]]
            data= pd.concat([data, tempData], axis=1).reset_index(drop=True)
        if len(data.columns)==0:
            return pd.DataFrame()
        null = pd.isnull(data).any(1).nonzero()[0]
        if len(null)>0:
            data = data.iloc[:(null[0]-1),:]
        return data
        
def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth
    
def alignLength(arrayList):
    
    lengthList = [len(x) for x in arrayList]
    minLen = np.min(lengthList)
    for i in range(len(arrayList)):
        arrayList[i] = arrayList[i][:minLen-1]  
        
    isnanList = []
    for array in arrayList:
        isnanList.append(np.isnan(array))
    truth = np.ones(len(arrayList[0]),dtype=bool)
    for isnan in isnanList:
        truth = truth*(~isnan)
        
    for i in range(len(arrayList)):
        arrayList[i] = arrayList[i][truth]
    
    return tuple(arrayList)
        
class ShotDaq(object):
    """
    This is a class for data collected by DAQ system.
    each class is identify by its shot number
    
    """
    def __init__(self,shotNum):
        
        self.shotNum=shotNum
        self.digitizerDataList = []
        
class DigitizerData(object):
    """
    This is a class for DAQ file in the form such as "133AB234856"
    digitizer Id corresponds to keys such as "133AB" and "133C"
    """
    def __init__(self, digitizerId):
        
        self.digitizerId = digitizerId
        self.header ={}
        self.info = pd.DataFrame()
        self.data = pd.DataFrame()
        
class ListboxItem (object): #convenient class for QtGui.QListWidget
    
    def __init__(self,listbox):
        self.listbox = listbox
        self.nameList = []
        self.itemList = []
    
    def listInBox (self):
        self.listbox.clear()
        for name in self.nameList:
            self.listbox.addItem(str(name))
            
class TableItem (object): #convenient class for QtGui.QTableWidget with fixed size
    def __init__(self,table):
        self.table = table
        #create a 2D list for items
        self.itemMatrix = []
        for i in range(self.table.rowCount()):
            self.itemMatrix.append([])
            for j in range(self.table.columnCount()):
                self.itemMatrix[i].append(None)
                self.table.setItem(i,j,QtGui.QTableWidgetItem())
        
    def addItem (self,item,name,row,column,rowSpan=1,columnSpan=1,color='white'):
        self.itemMatrix[row][column]=item
        self.table.setItem(row,column, QtGui.QTableWidgetItem(name))
        self.table.setSpan(row,column,rowSpan, columnSpan)
        

     
        
        
            
def getDigitizerData(filePath,**keys):
    
    loadedTime = datetime.now()

    dirPath = os.path.dirname(filePath)
    fileName = os.path.basename(filePath)
    digitizerId = fileName[:-6]
    shotNum = fileName[-6:]
    digitizerData = DigitizerData(digitizerId)
    
    count = 0
    f = open(filePath,'r')
    #return empty digitizerData if the file is empty
    if f.readline().replace(keys['newLineSplitter'],'') == '':
        f.close()
        return digitizerData

    # initialize for loading header
    line = 'rr'+keys['daqSplitter']+'jgg'
    split = line.split(keys['daqSplitter'])
    #assuming the header contains two columns
    while len(split)==2:
        line = f.readline().replace(keys['newLineSplitter'],'')
        split = line.split(keys['daqSplitter'])  
        if split[0] in keys:
            digitizerData.header[split[0]] = split[1]
        count += 1       

    #load signal information until encountering the "X_Value"
    Len = len(split)
    while Len == len(split) and not any(keys['daqStartKey'] in x for x in split):   
        params = ['0']+split[1:-1]     #add a row for X_value           
        if all (x.isdigit() for x in params): #if integer, store as integer
            digitizerData.info[split[0]]=[int(x) for x in params]
        elif all (x.replace('.','').replace('-','').replace('E','').isdigit() for x in params): #if float, store as float
            digitizerData.info[split[0]]=[float(x) for x in params]
        else:
            digitizerData.info[split[0]]=[x for x in params]  
        
        line = f.readline().replace(keys['newLineSplitter'],'')
        count += 1
        split = line.split(keys['daqSplitter'])  

        
    digitizerData.info[keys['slotAiKey']]=split[:-1] # assuming that the last column is "Comment" 
    #digitizerData.info = digitizerData.info[digitizerData.info[self.slotAi]!=self.keys['daqStartKey']] #dropping the row for X_Value
    #Assign channel ID, shotNum, and digitizer ID    
    digitizerData.info[keys['digitizerIdKey']]=digitizerId
    digitizerData.info[keys['shotNumKey']]=int(shotNum)
    digitizerData.info[keys['channelIdKey']]=str(shotNum)+'_'+str(digitizerId)+'_'+digitizerData.info[keys['slotAiKey']]
    for item in digitizerData.header.items():
        digitizerData.info[item[0]]=item[1]
    #read the main data
    data = pd.read_csv(filePath, sep=keys['daqSplitter'], header = count)
    #data.drop(self.keys['daqStartKey'], axis=1, inplace=True) #drop X_Value column
    #delete column for comment since it does not usually contain any information
    if keys['signalCommentKey'] in data.columns:
        data.drop(keys['signalCommentKey'], axis=1, inplace=True)
    for col in data.columns:
        data.rename(columns = {col:str(shotNum)+'_'+str(digitizerId)+'_'+col}, inplace=True)
    digitizerData.data=data
         
    f.close()
    
    digitizerData.info[keys['filePathKey']]=filePath
    digitizerData.info[keys['loadedTimeKey']]=loadedTime
    digitizerData.info[keys['channelDescriptionKey']]=str(digitizerId)+'_'+digitizerData.info[keys['slotAiKey']]
    digitizerData.info[keys['calibrationKey']]=1.0
    digitizerData.info[keys['unitKey']]='V'
    #clean up the info
    if keys['endOfHeaderKey'] in digitizerData.info.columns: # delete column for header
        digitizerData.info = digitizerData.info.drop(keys['endOfHeaderKey'], axis=1)
    if '' in digitizerData.info.columns: # delete empty column
        digitizerData.info = digitizerData.info.drop('', axis=1)
    
    xFiles = [x for x in next(os.walk(dirPath))[2] if len(x)>6 and x.split('.')[-1] in keys['xExtensions']and '$' not in x]
    shotStarts = [x.split('.')[-2][-13:-7] for x in xFiles]
    shotEnds= [x.split('.')[-2][-6:] for x in xFiles]   
    
    xFile = 1
    for i in range(len(xFiles)):
        if shotEnds[i].isdigit():
            if int(shotStarts[i]) <= int(shotNum) <= int(shotEnds[i]):
                xFile = xFiles[i]
        elif shotEnds[i] == keys['ffffffKey']:
            if int(shotStarts[i]) <= int(shotNum):
                xFile = xFiles[i]

    if xFile ==1: #If the shot number is within the limits of excel file iiiiii_ffffff
        return digitizerData
    exPath = os.path.join(dirPath,xFile)
    digitizerData.info[keys['excelFilePathKey']] = exPath
    #print xFiles
    Xls = pd.ExcelFile(exPath)
    sheetNames = Xls.sheet_names    
  
    if digitizerId  not in sheetNames:
        return digitizerData

    xlsSheet=Xls.parse(digitizerId)
    xlsSheet[keys['slotAisKey']] = xlsSheet[keys['sheetSlotKey']]+'/'+ xlsSheet[keys['sheetAiKey']]   
    for j in range(len(digitizerData.info)):
        if digitizerData.info.loc[j][keys['slotAiKey']] in list(xlsSheet[keys['slotAisKey']]):
            row = xlsSheet[xlsSheet[keys['slotAisKey']]==digitizerData.info.loc[j][keys['slotAiKey']]].reset_index()
            if row[keys['sheetChannelDescriptionKey']].astype(str)[0]!='nan':
                digitizerData.info.loc[j,keys['channelDescriptionKey']]=row[keys['sheetChannelDescriptionKey']][0]
            if row[keys['sheetCalibrationKey']].astype(str)[0]!='nan' and \
            row[keys['sheetCalibrationKey']].astype(str)[0].replace('.', '').replace('E','').replace('-','').isdigit():
                digitizerData.info.loc[j,keys['calibrationKey']]=float(row[keys['sheetCalibrationKey']][0])

            if type(row[keys['sheetUnitKey']][0])==str:
                if row[keys['sheetUnitKey']][0]!='nan':
                    digitizerData.info.loc[j,keys['unitKey']]=row[keys['sheetUnitKey']][0]

            # if type(row[keys['sheetUnitKey']][0])==str:
                # if row[keys['sheetUnitKey']][0].encode('ascii','ignore')!='nan':
                    # digitizerData.info.loc[j,keys['unitKey']]=str(row[keys['sheetUnitKey']][0].encode('ascii','ignore'))
            # else :
                # if row[keys['sheetUnitKey']].astype(str)[0]!='nan':
                    # digitizerData.info.loc[j,keys['unitKey']]=row[keys['sheetUnitKey']][0]
    
    
    # from IPython import embed; embed()
    return digitizerData
    
    
    
def catalyst_reader(path,param,**keys):  


    f = open(path,'rb')    
    
    """
    read the header information from the binary file
    
    the first byte in any FORTRAN unformatted sequential file is the value 75
    """
    
    get75 = np.fromfile(f,dtype='uint8', count=1)[0]
    
    if get75 != 75:
        print ('The binary file is incorrectly formatted')
        #return
    
    #read the number of bytes in the physical record that is just begining
    
    header_bytes=np.fromfile(f,dtype='uint8', count=1)[0]
    if header_bytes != 34:
        print ('An error occurred while reading the header of the binary file')
        #return;
    
    #get the block size - number of data values per block
    block_size=np.fromfile(f,dtype='uint16', count=1)[0]
    
    #get the number of Bits Per Data Word (bpdw)
    bpdw=np.fromfile(f,dtype='uint16', count=1)[0]
    if bpdw != 12:  #if the data is not in 12 bit resolution, the code will still work, but if bpdw>16 bits or bpdw<=8 bits, then the size of the data words read in later needs to be changed
          print ('An error occurred.  12 bit resolution per data word was\
                  expected')
          #return
    
    #get the period of the trace in units of 0.1nsec per point
    trace_period=np.fromfile(f,dtype='uint32', count=1)[0]

    
    #get the offset value (code corresponding to 0 Volts)
    mag_offset=np.fromfile(f,dtype='uint16', count=1)[0]
    
    #get the point where the trigger occurred (point corresponding to trigger time = first sample)
    trig_point=np.fromfile(f,dtype='uint32', count=1)[0]
    
    #get the amplitude in micro Volts per code
    amplitude=np.fromfile(f,dtype='uint32', count=1)[0]
    
    #get the offset (in bytes) to the actual start of data
    data_offset=np.fromfile(f,dtype='uint16', count=1)[0]
    
    #get the total number of data blocks (length of data divided by block size)
    num_data_blocks=np.fromfile(f,dtype='uint16', count=1)[0]
    
    #get the data type
    data_type=np.fromfile(f,dtype='uint16', count=1)[0]
    if data_type != 0:  #exit if data type is not 0 or 1
        if data_type != 1:
            print ('The data in the binary file does not correspond to either\
                    single channel vs time or multi-channel vs time format')
        #return
    
    #get the number of Blocks Per Channel (BPC)
    BPC=np.fromfile(f,dtype='uint16', count=1)[0]
    
    
    #get the start channel (for data type 1 only)
    start_channel=np.fromfile(f,dtype='uint16', count=1)[0]
    if data_type != 0:
        start_channel=0
    
    #get the exponent for the sampling period
    sample_period_expon=np.fromfile(f,dtype='uint16', count=1)[0]
    
    #get bytes 31-32 which are unused with data types 0 and 1
    crap=np.fromfile(f,dtype='uint16', count=1)[0]
    
    #get bytes 33-34 which are unused with data types 0 and 1
    crap=np.fromfile(f,dtype='uint16', count=1)[0]
    
    #read in the nymber of bytes in the physical record just finished
    header_bytes=np.fromfile(f,dtype='uint8', count=1)[0]
    if header_bytes != 34:
        print ( 'An error occurred while reading the header of the binary file' )
        #return
    
    #skip past the user comments (max 161 characters - terminated by $)
    comment_bytes=np.fromfile(f,dtype='uint8', count=1)[0]
    if comment_bytes != 129:
        print ( 'The comments in the binary file are incorrectly formatted' )
        #return
        
    comments_a=np.fromfile(f,dtype='B', count=128)
    comment_bytes=np.fromfile(f,dtype='uint8', count=1)[0]
    
    if comment_bytes != 129:
        print ( 'The comments in the binary file are incorrectly formatted' )
        #return
    
    comment_bytes=np.fromfile(f,dtype='uint8', count=1)[0]
    
    if comment_bytes != 33:
        print ( 'The comments in the binary file are incorrectly formatted' )
        #return;
    
    comments_b=np.fromfile(f,dtype='B', count=33)
    comment_bytes=np.fromfile(f,dtype='uint8', count=1)[0]
    
    if comment_bytes!=33:
        print ( 'The comments in the binary file are incorrectly formatted' )
        #return;
    
    #print np.fromfile(f,dtype='uint8', count=1)[0]
    
    #read in the data in [Volts]
    current_channel=start_channel
    data  = np.zeros((num_data_blocks,block_size))
    
    
    for i in range(num_data_blocks):
        block_count=0;
    
        while block_count<block_size-1:
            #read in the current physical record size
            data_bytes_a=np.fromfile(f,dtype='uint8', count=1)[0]
            if data_bytes_a==129:
                data_bytes=128
            else:
                data_bytes=data_bytes_a
            
            #read in the data in the current record
            if data_bytes%2==0:
                n = data_bytes//2
            else:
                n = 1+data_bytes//2
                
            for j in range(n): 
                
                data[current_channel,block_count]=np.fromfile(f,dtype='uint16', count=1).astype(float)[0]-mag_offset
                data[current_channel,block_count]=data[current_channel,block_count]*amplitude*1E-6;
                block_count+=1            
                
            #confirm current physical record size
            data_bytes_b=np.fromfile(f,dtype='uint8', count=1)[0]
            if data_bytes_b!=data_bytes_a:
                print ( 'An error occurred!  The data record is incorrectly formatted!' )
                #return 
        current_channel +=1
        if current_channel>num_data_blocks-1:
            current_channel=0
    
    #close the binary file
    f.close()
    if not f.closed:	#an error closing the file occurred
        print ( 'An error occurred while closing the binary file!' )
    
    time_shift=0.005
    #set up the time vector in [sec]
    x = np.zeros(block_size)
    x[0]=0-time_shift
    sample_period=(trace_period/(10**sample_period_expon))*0.1E-9
    
    #print sample_period, trace_period,sample_period_expon
    for j in range(block_size-1):
        x[j+1]=x[j]+sample_period
    
    trueData = np.vstack([x,data])
    
    columns = ['X_Value','Ch_1','Ch_l2']  #the second channel is Ch_l2 by mistake I assume.
    for i in range(num_data_blocks-2):
        columns.append('Ch_%i' %(i+3))
    
    df=pd.DataFrame(trueData.transpose(), columns=columns)
    
    digitizerId = os.path.basename(path)[:-7]
    catData = DigitizerData(digitizerId)
    loadedTime = datetime.now()
    
    info = pd.DataFrame()
    
    para = param.reset_index(drop=True).iloc[1]

    shotNum = str(para[keys['shotNumKey']])
    info[keys['slotAiKey']]=columns
    info[keys['channelIdKey']]=str(shotNum)+'_'+str(digitizerId)+'_'+info[keys['slotAiKey']]
    info[keys['digitizerIdKey']]=digitizerId
    info[keys['shotNumKey']]=int(shotNum)
    info[keys['DateKey']]=para[keys['DateKey']]
    info[keys['TimeKey']]=para[keys['TimeKey']]
    info[keys['Y_Unit_LabelKey']]=para[keys['Y_Unit_LabelKey']]
    info[keys['X_DimensionKey']]=para[keys['X_DimensionKey']]
    info[keys['filePathKey']]=path
    info[keys['loadedTimeKey']]=loadedTime
    info[keys['calibrationKey']]=1.0
    info[keys['unitKey']]='V'    
    info[keys['Delta_XKey']]=sample_period
    
    info[keys['X0Key']]= 0.005    #should be able to be adjusted to sync with NI DAQ
    
    for col in df.columns:
        df.rename(columns = {col:str(shotNum)+'_'+str(digitizerId)+'_'+col}, inplace=True)
        
    if keys['excelFilePathKey'] not in para.index:
        catData.info = info
        catData.data = df
        return catData   
        
    info[keys['excelFilePathKey']] = para[keys['excelFilePathKey']]        
    Xls = pd.ExcelFile(para[keys['excelFilePathKey']])
    sheetNames = Xls.sheet_names    
  
    if digitizerId  not in sheetNames:
        catData.info = info
        catData.data = df
        return catData  
    try:
        xlsSheet=Xls.parse(digitizerId)
    except ValueError:
        print ('Sheet "%s" in "%s" contains blank column. Try entering some value in one of the rows in the empty column.' %(str(digitizerId), str(para[keys['excelFilePathKey']]))) 
        catData.info = info
        catData.data = df
        return catData  
        
        
        
    xlsSheet[keys['slotAisKey']] = xlsSheet[keys['sheetAiKey']]   
    for j in range(len(info)):
        if info.loc[j][keys['slotAiKey']] in list(xlsSheet[keys['slotAisKey']]):
            row = xlsSheet[xlsSheet[keys['slotAisKey']]==info.loc[j][keys['slotAiKey']]].reset_index(drop=True)
            if row[keys['catSheetChannelDescriptionKey']].astype(str)[0]!='nan':
                info.loc[j,keys['channelDescriptionKey']]=row[keys['catSheetChannelDescriptionKey']][0]
            if row[keys['sheetCalibrationKey']].astype(str)[0]!='nan' and \
            row[keys['sheetCalibrationKey']].astype(str)[0].replace('.', '').replace('E','').replace('-','').isdigit():
                info.loc[j,keys['calibrationKey']]=float(row[keys['sheetCalibrationKey']][0])
            if type(row[keys['sheetUnitKey']][0])==str:
                if row[keys['sheetUnitKey']][0].encode('ascii','ignore')!='nan':
                    info.loc[j,keys['unitKey']]=row[keys['sheetUnitKey']][0].encode('ascii','ignore')
            else:
                if row[keys['sheetUnitKey']].astype(str)[0]!='nan':
                    info.loc[j,keys['unitKey']]=row[keys['sheetUnitKey']][0]
                    
            if 'ms' in row[keys['sheetTimeShiftKey']].astype(str)[0] and ' ' in row[keys['sheetTimeShiftKey']].astype(str)[0]:
                info[keys['X0Key']]=float(row[keys['sheetTimeShiftKey']].astype(str)[0].split(' ')[0])*0.001
            
                
    catData.info = info
    catData.data = df
    return catData 
        
    


 
    
    
    


def PlotInPlotItem(p,data,param,**keys): #plots in PlotItem and returns the resulting PlotItem
   
    param.reset_index(inplace=True,drop=True)
    for i in range(len(param)):
        para = param.iloc[i].copy()
        y = data[para[keys['channelIdKey']]]
        
        #calibration and unit 
        if para[keys['isUncalibratedSignalKey']]:
            unit = para[keys['unitKey']][0]
        else:
            y = y*float(para[keys['calibrationKey']])            
            unit = para[keys['Y_Unit_LabelKey']]
            
        
    return p
    
def locationToPlot(table):#given a list of tablewidgetItems, give row, column, rowSpan, and columnSpan    
    pItems = table.selectedItems()
    rows = [x.row() for x in pItems]
    columns = [x.column() for x in pItems]
    row,column = np.min(rows), np.min(columns)
    rowSpan,columnSpan = 1+(np.max(rows)-np.min(rows)),1+(np.max(columns)-np.min(columns))
    return (row,column,rowSpan,columnSpan)
    

    
    
    
    
class PlotItem1D (pg.PlotItem):
    """
    PlotItem with an additional attributes and methods
    attributes
    number: id number (starting from 0)
    
    methods
    addAxis: add right axis and associated viewbox
    
    
    """
    penColors = [
        QtGui.QColor(0,0,0,255),    
        QtGui.QColor(255,0,0,255),
        QtGui.QColor(0,255,0,255),
        QtGui.QColor(0,0,255,255),
        QtGui.QColor(255,0,255,255),
        QtGui.QColor(200,200,0,255),
        QtGui.QColor(0,255,255,255),
    ]
    penWidths = [1]
    def __init__(self, number=0,*args, **kargs):
        pg.PlotItem.__init__(self,*args,**kargs)
        self.number = number
        self.getAxis('left').number = 0
        self.vb.sigResized.connect(self.updateViews)
        self.addLegend() 
        self.legend.setScale(1.5)
        
    
    def addAxis(self):
        rAxes = [x for x in self.childItems() if type(x)==type(pg.AxisItem('top')) and x.orientation=='right']
        vb = pg.ViewBox()         
        if len([x for x in self.childItems() if type(x) == type(pg.ViewBox)])==1: #for the first time
            number = 1            
            ax = self.getAxis('right')
        else: 
            number = len(rAxes)+1            
            ax = pg.AxisItem('right')

        ax.number = number
        self.layout.addItem(ax, 2, number+1)
        self.scene().addItem(vb)
        ax.linkToView(vb)
        vb.setXLink(self)
        ax.setZValue(-10000)
        #ax3.setLabel('axis 3', color='#ff0000')
        self.updateViews()
        
        
        
    def updateViews(self):
        ## view has resized; update auxiliary views to match
        vbs = [x for x in self.scene().items() if type(x) ==type(pg.ViewBox())][1:]
        for vb in vbs:
            vb.setGeometry(self.vb.sceneBoundingRect())        
            ## need to re-update linked axes since this was called
            ## incorrectly while views had different shapes.
            ## (probably this should be handled in ViewBox.resizeEvent)
            vb.linkedViewChanged(self.vb, vb.XAxis)
            
    def addItem1D (self,item,*args,**kargs):
        i = len(self.dataItems)
        color = self.penColors[i%len(self.penColors)]
        pen = pg.mkPen(width=self.penWidths[0],color=color)
        item.setPen(pen)
        self.addItem(item)
        self.updateYAxis(self.getAxis('left'),*args,**kargs)        
        self.updateXAxis(self.getAxis('bottom'),*args,**kargs)
        
        
    def updateYAxis(self,ax,*args,**kargs):
        vb = ax.linkedView()  

        dataItems = [x for x in vb.addedItems if type(x)==type(PlotDataItem1D())]
        axisArg = kargs['axisArgs'] 
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
        commonLabels =[word for word in commonWords if word.upper() in kargs['plotYLabelTypes']]
        if len(commonLabels)>0:
            maxLen = np.max([len(x) for x in commonLabels])
            yLabel = [x for x in commonLabels if len(x)==maxLen][0]
        
        ax.setLabel(yLabel,units = yUnit,**axisArg['labelStyleArgs'])

        ax.tickFont = axisArg['tickFont']
        ax.setPen(axisArg['axisPen'])
        ax.setStyle(tickLength = axisArg['tickLength'])       

        ax.setWidth(w=axisArg['yAxisWidth'])
        ax.setStyle(tickTextOffset = axisArg['yTickTextOffset'])

    def updateXAxis(self,ax,*args,**kargs):
        vb = ax.linkedView()        
        dataItems = [x for x in vb.addedItems if type(x)==type(pg.PlotDataItem()) or type(x)==type(PlotDataItem1D())]
        axisArg = kargs['axisArgs'] 
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
        commonLabels =[word for word in commonWords if word.upper() in kargs['plotXLabelTypes']]
        if len(commonLabels)>0:
            maxLen = np.max([len(x) for x in commonLabels])
            xLabel = [x for x in commonLabels if len(x)==maxLen][0]
        
        ax.setLabel(xLabel,units = xUnit,**axisArg['labelStyleArgs'])
        ax.tickFont = axisArg['tickFont']
        ax.setPen(axisArg['axisPen'])
        ax.setStyle(tickLength = axisArg['tickLength'])       
        ax.setHeight(h=axisArg['xAxisHeight'])
        ax.setStyle(tickTextOffset = axisArg['xTickTextOffset'])
        
    def updateXRegion(self,xRegion,*args,**kargs):
        vbs = [x for x in self.scene().items() if type(x) ==type(pg.ViewBox())]
        dataItems = []
        
        for vb in vbs:
            dataItems += [x for x in vb.addedItems if type(x) == type(PlotDataItem1D())]
        print (len(dataItems))
        for dataItem in dataItems:

            dataItem.processParam['xRegion']=xRegion.getRegion()
            dataItem.updateData1D(*args,**kargs)

class paramFilterItem(QObject):
    
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
        
        
class paramFilterLayout (QObject):
    
    #define signals
    sigFilterChanged = QtCore.pyqtSignal()
    def __init__(self,layout):
        QObject.__init__(self)     

        #make items
        lbl = QtGui.QLabel()
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        lbl.setText('Selected Parameters')
        
        lst = QtGui.QListWidget()
        lst.setMinimumSize(QtCore.QSize(100, 50))
        lst.setMaximumSize(QtCore.QSize(200, 120000))
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
        
        
        btnApplyAllFilters = QtGui.QPushButton()
        btnApplyAllFilters.setMaximumSize(QtCore.QSize(100, 16777215))
        btnApplyAllFilters.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btnApplyAllFilters.setText('Apply All Filters')
        btnApplyAllFilters.clicked.connect(self.applyAllFilters)
        
        btnClearAllFilters = QtGui.QPushButton()
        btnClearAllFilters.setMaximumSize(QtCore.QSize(100, 16777215))
        btnClearAllFilters.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        btnClearAllFilters.setText('Clear All Filters')
        btnClearAllFilters.clicked.connect(self.clearAllFilters)
        
        #set attributes
        self.parentLayout = layout
        self.label = lbl
        self.paramListbox = lst
        self.paramListboxItem = ListboxItem(self.paramListbox)
        self.paramCount = 0
        self.paramFilterItems = []        
        self.btnApplyAllFilters = btnApplyAllFilters
        self.btnClearAllFilters = btnClearAllFilters
        self.filteredParams = []
        self.selectedParams = []
        self.paramDf = pd.DataFrame()
        self.filteredParamDf = pd.DataFrame()
        
        
        #display the items
        self.vloSelectedParams = QtGui.QVBoxLayout()
        self.vloSelectedParams.addWidget(self.label)
        self.vloSelectedParams.addWidget(self.paramListboxItem.listbox)
        self.vloSelectedParams.addWidget(self.btnApplyAllFilters)
        self.vloSelectedParams.addWidget(self.btnClearAllFilters)
        
        

        self.scrollArea_3 = QtGui.QScrollArea()
        self.scrollArea_3.setWidgetResizable(True)
        self.scrollAreaWidgetContents_3 = QtGui.QWidget()
        self.scrollAreaWidgetContents_3.setGeometry(QtCore.QRect(0, 0, 516, 273))
        self.gridLayout_9 = QtGui.QGridLayout(self.scrollAreaWidgetContents_3)
        self.layout = QtGui.QGridLayout()
        self.gridLayout_9.addLayout(self.layout, 0, 0, 1, 1)
        self.scrollArea_3.setWidget(self.scrollAreaWidgetContents_3)
        
        
        self.parentLayout.addLayout(self.vloSelectedParams,0,0,1,1)
        self.parentLayout.addWidget(self.scrollArea_3, 0, 1, 1, 1)
        
        
        
        
        

        

        
    def addParams (self,paramNames):
        for name in paramNames:
            self.addParam(name, list(self.paramDf[name]))
        
        

    def addParam (self, paramName, paramValues):
        #add to paraListbox
        self.selectedParams.append(paramName)
        filterItem = paramFilterItem(paramName, paramValues)
        self.paramFilterItems.append(filterItem)
        self.layout.addWidget(filterItem.label, 0,self.paramCount+1,1,1)
        self.layout.addWidget(filterItem.listbox, 1,self.paramCount+1,1,1)
        self.layout.addWidget(filterItem.btnApplyFilter, 2,self.paramCount+1,1,1)
        self.layout.addWidget(filterItem.btnClearFilter, 3,self.paramCount+1,1,1)
        self.paramCount +=1
        
        #connect signals
        filterItem.sigApplyFilter.connect(self.updateAvailableChannels)
        filterItem.sigClearFilter.connect(self.updateAvailableChannels)       
        
        self.updateParamList   
        
    def deleteAllParamFilterItems(self):
        for item in self.paramFilterItems:
            self.deleteParamFilterItem(item)
        self.filteredParams=[]
        self.selectedParams=[]
        self.paramFilterItems = []

        self.updateAvailableChannels()
        
    def deleteParamFilterItem (self, paramFilterItem):
        
        self.layout.removeWidget(paramFilterItem.label)
        self.layout.removeWidget(paramFilterItem.listbox)
        self.layout.removeWidget(paramFilterItem.btnApplyFilter)
        self.layout.removeWidget(paramFilterItem.btnClearFilter)
        
        paramFilterItem.label.deleteLater()
        paramFilterItem.listbox.deleteLater()
        paramFilterItem.btnApplyFilter.deleteLater()
        paramFilterItem.btnClearFilter.deleteLater()
        
        paramFilterItem.label = None
        paramFilterItem.listbox = None
        paramFilterItem.btnApplyFilter = None
        paramFilterItem.btnClearFilter = None

        self.paramCount -= 1
    
        
    def applyAllFilters(self):
        for item in self.paramFilterItems:
            item.sigApplyFilter.disconnect(self.updateAvailableChannels)
            item.applyFilter()
            item.sigApplyFilter.connect(self.updateAvailableChannels)
        self.updateAvailableChannels
        
        
        
        
    def clearAllFilters(self):
        for item in self.paramFilterItems:
            item.sigClearFilter.disconnect(self.updateAvailableChannels)
            item.clearFilter()
            item.sigClearFilter.connect(self.updateAvailableChannels)
        self.updateAvailableChannels
        

    def updateParamList(self):
        self.paramListboxItem.itemList = self.selectedParams
        self.paramListboxItem.nameList = self.selectedParams
        self.paramListboxItem.listInBox()
        for item in [self.paramListbox.item(i) for i in range(self.paramListbox.count())]:
            if item.text() in self.filteredParams:
                item.setBackgroundColor(pg.mkColor('y'))    
        
    def updateAvailableChannels(self):
        df = self.paramDf
        for item in self.paramFilterItems:
            df = df[df[item.paramName].isin(np.array(item.selectedValues).astype(df[item.paramName].dtype))]
            if item.isFiltered and item.paramName not in self.filteredParams:
                self.filteredParams.append(item.paramName)
        
        self.updateParamList()        
        self.sigFilterChanged.emit()
        

def psdSpectrogram (s1, fs = 1.0, npersegSpectrogram=256*2, nperseg = 256,noverlapSpectrogram=256, noverlap = 256/2,normalized=False):         

    
    nstep = npersegSpectrogram - noverlapSpectrogram
    
    i = 0
    t = []
    while i*nstep+npersegSpectrogram<len(s1):
        x1 = s1[i*nstep:i*nstep+npersegSpectrogram]
        if normalized:
            x1 =x1/np.average(x1)

        f,Psd = welch(x1,fs=fs, nperseg = nperseg,noverlap=noverlap)
        
        if i ==0:
            PSDxx = Psd
            t.append((2*i*nstep+npersegSpectrogram)/2/fs)
            i+=1
            continue
        PSDxx = np.vstack([PSDxx,Psd])
        t.append((2*i*nstep+npersegSpectrogram)/2/fs)
        i+=1
        
    
    t = np.array(t)
    PSDxx = PSDxx.transpose()
        
    
    return f, t, PSDxx       
        
def csdSpectrogram(s1,s2, fs = 1.0, npersegSpectrogram=256*2, nperseg = 256,noverlapSpectrogram=256, noverlap = 256/2,normalized=False):         
    s1,s2 = alignLength([s1,s2])

    
    nstep = npersegSpectrogram - noverlapSpectrogram
    
    i = 0
    t = []
    while i*nstep+npersegSpectrogram<len(s1):
        x1,x2 = s1[i*nstep:i*nstep+npersegSpectrogram], s2[i*nstep:i*nstep+npersegSpectrogram]
        if normalized:
            x1,x2 =x1/np.average(x1), x2/np.average(x2)

        f,Csd = csd(x1,x2,fs=fs, nperseg = nperseg,noverlap=noverlap)
        
        if i ==0:
            CSDxy = Csd
            t.append((2*i*nstep+npersegSpectrogram)/2/fs)
            i+=1
            continue
        CSDxy = np.vstack([CSDxy,Csd])
        t.append((2*i*nstep+npersegSpectrogram)/2/fs)
        i+=1
        
    
    t = np.array(t)
    CSDxy = CSDxy.transpose()
        
    
    return f, t, CSDxy
        
def cohSpectrogram(s1,s2, fs = 1.0, npersegSpectrogram=256*2, nperseg = 256,noverlapSpectrogram=256, noverlap = 256/2,normalized=False):         
    s1,s2 = alignLength([s1,s2])

    
    nstep = npersegSpectrogram - noverlapSpectrogram
    
    i = 0
    t = []
    while i*nstep+npersegSpectrogram<len(s1):
        x1,x2 = s1[i*nstep:i*nstep+npersegSpectrogram], s2[i*nstep:i*nstep+npersegSpectrogram]


        f,Coh = coherence(x1,x2,fs=fs, nperseg = nperseg,noverlap=noverlap)
        
        if i ==0:
            COHxy = Coh
            t.append((2*i*nstep+npersegSpectrogram)/2/fs)
            i+=1
            continue
        COHxy = np.vstack([COHxy,Coh])
        t.append((2*i*nstep+npersegSpectrogram)/2/fs)
        i+=1
        
    
    t = np.array(t)
    COHxy = COHxy.transpose()
        
    
    return f, t, COHxy
       



#needed for bicoh
def flat_eq(x, y):
    """
    Emulate MATLAB's assignment of the form
    x(:) = y
    """
    z = x.reshape(1, -1)
    z = y
    return z.reshape(x.shape)
  
def bicoh(y,nperseg=None, fs=1.0, nfft=None, overlap=None, wind=None, minNSam=10):

    
    
                                    # ly = 64, nrecs = 64
    #get the shapes
    defaultOverlap=50
    maxOverlap=80
    defaultNperseg=2**9
    if len(y.shape)==1:
        y = y.reshape(-1,1)
    
    
    (ly, nrecs) = y.shape
    
    if ly == 1:
        y = y.reshape(1,-1)
        ly = nrecs
        nrecs = 1
        
        
    if nrecs > 1: #if y is 2-D array
        overlap = 0 #regardless of specification, overlap is set to 0
        nperseg = ly  #regardless of specification, nsamp is set to ly
    else:       #if y is 1-D array
        if not overlap:
            overlap = defaultOverlap
            
        if not nperseg:
            nperseg  = defaultNperseg 
        
        overlapRatio = overlap/100.0
        advanceRatio = 1-overlapRatio
        nsam = (ly/nperseg-overlapRatio)/advanceRatio
    
        if minNSam > nsam:
            
            nSamLower = int((ly/nperseg-defaultOverlap/100.0)/(1-defaultOverlap/100.0))
            nSamUpper = int((ly/nperseg-maxOverlap/100.0)/(1-maxOverlap/100.0))
            #print nSamUpper
            if minNSam <= nSamLower:
                overlap = defaultOverlap
            elif minNSam <= nSamUpper:
                overlap = (minNSam - ly/nperseg)*(100.0/(minNSam-1))
            else:
                #nperseg has to be changed
                overlap = maxOverlap
                nperseg = int(ly / (minNSam - (minNSam-1) * overlap/100.0)) 
                        
    
    if not nfft:
        nfft = nperseg
    else:
        if nfft < nperseg:
            nfft = nperseg
        if nfft > nextpow2(nperseg):
            nfft = nextpow2(nperseg)
    
    noverlap  = int(nperseg * overlap/100.0)   #overlap = array(0.0)
    nadvance = nperseg - noverlap              #nadvance = 64
    nsamp    = int((ly*nrecs - nperseg) / float(nadvance) + 1) #nrecs = array(64.0)
    
    
    if not wind:                    #false
        wind = np.hanning(nperseg)    
    
    try:
        (rw, cw) = wind.shape
    except ValueError:
        (rw,) = wind.shape
        cw = 1
    
    if min(rw, cw) == 1 or max(rw, cw) == nperseg:        #True
        """
        print ( "Segment size is " + str(nperseg) )
        print ("Wind array is " + str(rw) + " by " + str(cw))
        print ( "Using default Hanning window" )
        print ( 'nperseg:%i'%nperseg )
        print ( 'overlap: %i'%overlap )
        print ( 'nfft: %i'%nfft )
        print ( 'nsamp: %i'%nsamp )
        print ( 'intermediateNsam: %i' %nsam )
        """
        
        wind = np.hanning(nperseg)
    
    wind = wind.reshape(1,-1)       #wind.shape (1L,64L)
    
    
    # Accumulate triple products
    
    bic = np.zeros([nfft, nfft])
    Pyy  = np.zeros([nfft,1])
    
    # from IPython import embed; embed()
    mask = hankel(np.arange(nfft),np.array([nfft-1]+list(range(nfft-1))))
    Yf12 = np.zeros([nfft,nfft])
    ind  = np.arange(nperseg)
    y = y.ravel(order='F')  #make 1 dimensional array
    
    if nfft%2 == 0:
        waxis = fs*np.transpose(np.arange(-1*nfft/2, nfft/2)*1.0) / nfft
    else:
        waxis = fs*np.transpose(np.arange(-1*(nfft-1)/2, (nfft-1)/2+1)*1.0) / nfft
        
    
    
    if nsamp<1 or nperseg<2**4:
        return waxis,bic
    
    for k in range(nsamp):
        ys = y[ind]    #get first segment 
        ys = (ys.reshape(1,-1) - np.mean(ys)) * wind
        
        Yf = np.fft.fft(ys, nfft)/nsamp
        CYf = np.conjugate(Yf)
        Pyy = Pyy + flat_eq(Pyy, (Yf*CYf))
        
        Yf12 = flat_eq(Yf12, CYf.ravel(order='F')[mask])
        
        bic = bic + ((Yf * np.transpose(Yf)) * Yf12)
        ind = ind + int(nadvance)
    
    
    bic = bic / nrecs
    Pyy = Pyy / nrecs
    mask = flat_eq(mask, Pyy.ravel(order='F')[mask])
    bic = abs(bic)**2 / ((Pyy * np.transpose(Pyy)) *  mask)
    bic = np.fft.fftshift(bic)


        
    return waxis,bic
