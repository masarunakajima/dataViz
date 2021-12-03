
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import pyqtgraph as pg



backGround = '#FFF'
foreGround = 'k'

#dataInfo param
dfKey = 'df'
dfErrKey = 'dfErr'
addressSeparator = '/'
daqSplitter = '\t'
newLineSplitter = '\n'
daqStartKey = 'X_Value'
signalCommentKey = 'Comment'
endOfHeaderKey = '***End_of_Header***'

#signal info preference
shotNumKey = 'ShotNum'
digitizerIdKey = 'Digitizer'
channelIdKey = 'ChannelID'
slotAiKey = 'SlotAi'    
channelDescriptionKey = 'ChannelDescription'
calibrationKey = 'Calibration'
unitKey = 'Unit'
loadedTimeKey = 'loadedTime'
filePathKey = 'FilePath'
excelFilePathKey = 'ExcelFilePath'


#Excel file preferences
xExtensions =['csv','xlsx']
ffffffKey='ffffff'
sheetSlotKey = 'Slot Name Digitizer'
sheetAiKey = 'CH_Name'
sheetChannelDescriptionKey='Chanel_Description'
catSheetChannelDescriptionKey='Channel_Description'
sheetCalibrationKey = 'Calibration'
sheetUnitKey = 'Unit'
sheetTimeShiftKey  = 'time shift'
slotAisKey = 'SlotAis'

#basics plotting parameters

isSmoothKey = 'isSmooth'
nSmoothKey = 'nSmooth'
isDcCancelHeadKey = 'isDcCancelHead'
nDcCancelHeadKey = 'nDcCancelHead'
isDcCancelTailKey = 'isDcCancelTail'
nDcCancelTailKey = 'nDcCancelTail'
isDetrendKey = 'isDetrend'
nDetrendKey = 'nDetrend'
isAbsolutePhaseKey = 'isAbsolutePhase'
npersegKey = 'nperseg'
isUncalibratedSignalKey = 'isUncalibratedSignal'
isNormalizePsdKey = 'isNormalizePsd'
npersegKey = 'nperseg'
overlapKey = 'overlap'
xRegionKey = 'xRegion'
yRegionKey = 'yRegion'
overlapSpectrogramKey = 'overlap_spectrogram'
npersegSpectrogramKey = 'nperseg_spectrogram'
processCountKey = 'processCount'
isErrorBarKey = 'isErrorBarerre'

#IV characteristics process parameters
IV_isInvertIKey = 'IV_isInvertI'
IV_isSmoothKey = 'IV_isSmooth'
IV_smoothTimeKey = 'IV_smoothTime'
IV_isDcCancelHeadKey = 'IV_isDcCancelHead'
IV_dcCancelHeadTimeKey = 'IV_dcCancelHeadTime'
IV_isDcCancelTailKey = 'IV_isDcCancelTail'
IV_dcCancelTailTimeKey = 'IV_dcCancelTailTime'
IV_asymtoteFactorKey = 'IV_asymtote_Factor'
IV_voltRangeMin1Key = 'IV_VoltRangeMin1'
IV_voltRangeMax1Key = 'IV_VoltRangeMax1'
IV_voltRangeMin2Key = 'IV_VoltRangeMin2'
IV_voltRangeMax2Key = 'IV_VoltRangeMax2'
IV_voltRangeMin3Key = 'IV_VoltRangeMin3'
IV_voltRangeMax3Key = 'IV_VoltRangeMax3'

probeLocationList = ['TOP','BOTTOM','RADIALl1','RED1','RADIAL2','RAD2']


#daq header keys

Writer_VersionKey='Writer_Version'	
Reader_VersionKey = 'Reader_Version'	
SeparatorKey = 'Separator'	
Decimal_Separator='Decimal_Separator'	
Multi_HeadingsKey='Multi_Headings'	
X_ColumnsKey='X_Columns'	
Time_PrefKey='Time_Pref'	
OperatorKey='Operator'	
DateKey='Date'	
TimeKey='Time' #first header
ChannelsKey='Channels'														
SamplesKey='Samples'	
DateKey='Date'	
Y_Unit_LabelKey='Y_Unit_Label'	
X_DimensionKey='X_Dimension'	
X0Key='X0'	
Delta_XKey='Delta_X'
X_ValueKey = 'X_Value'

#plot pen preference
penWidth = 1
penWidthPsd = 3

foreGroundPenColor = [pg.mkColor(foreGround)]  
restOfPenColors = [
    QtGui.QColor(255,0,0,255),
    QtGui.QColor(0,255,0,255),
    QtGui.QColor(0,0,255,255),
    QtGui.QColor(255,0,255,255),
    QtGui.QColor(200,200,0,255),
    QtGui.QColor(0,255,255,255),
]
penColors  = foreGroundPenColor+restOfPenColors
plotPenList = [pg.mkPen(x, width= 1) for x in penColors]


penWidths = [1,1.5,2,2.5,3]

#legend preference
nStrLegend = 20 # number of letters to appear on legend
legendScale = 1.8 #

#axis preference
labelStyleArgs = {'color': foreGround,'font-size': '24pt'}
tickFont = QtGui.QFont('AnyStyle',24)
tickLength = 20      
yAxisWidth = 150
yTickTextOffset = 20
xAxisHeight = 100
xTickTextOffset = 20
 
axisPen = pg.mkPen(foreGround, width=3)
axisArgs = {'labelStyleArgs':labelStyleArgs,'tickFont':tickFont,\
            'tickLength':tickLength,'yAxisWidth':yAxisWidth,\
            'xAxisHeight':xAxisHeight,'axisPen':axisPen,\
            'yTickTextOffset':yTickTextOffset,'xTickTextOffset':xTickTextOffset}
            
symbolPlotArgs = {'pen': None, 'symbolSize':3}
            
            
# Error bar preference
errorBarBeam = 0.5
errorBarPenWidth = 2


#types of plot
pTypeKey = 'plot_Type'
pPrefKey = 'plot_Preference'
#pPrefMin

pTypeBasicKey = 'basic_Plot'

pTypePsdKey = 'psd_Plot'
pTypeCsdKey = 'csd_Plot'
pTypeCohKey = 'coh_Plot'
pTypePhaseKey = 'phase_Plot'
pTypeSpectrogramKey = 'spectrogram_Plot'
pTypeCsdSpectrogramKey = 'csdSpectrogram_Plot'
pTypeCohSpectrogramKey = 'cohSpectrogram_Plot'
pTypePhaseSpectrogramKey = 'phaseSpectrogram_Plot'
pTypeBicohKey = 'bicoherence_Plot'
pTypeXyView = 'XyView_Plot'

#plotInfo keys
plotInfoParamKey = 'param'
plotInfoPlotItemKey = 'PlotItem'
plotInfoLocationKey = 'plotLocation' #for list of location information [row,column,rowSpan,columnSpan]
plotInfoPNameKey= 'pName'
plotInfoLocationRowKey = 'row'
plotInfoLocationColumnKey = 'column'
plotInfoLocationRowSpanKey = 'rowSpan'
plotInfoLocationColumnSpanKey = 'columnSpan'
plotInfoColorKey = 'color'

# plot table preferences
plotTableFont = QtGui.QFont()
plotTableFont.setPointSize(10)
plotTableAlignment = QtCore.Qt.AlignCenter

#list and channel list preference 
listIncompleteMatchBgColor = pg.mkColor('y')
listBgColor = pg.mkColor('w')

#label types
plotYLabelTypes = ['ISAT','FLOAT','H_ALPHA',\
'MI','IV VOLTAGE','IV CURRENT','RMP CURRENTt','FLOAT NOISE','PSD','CSD','COH','Phase','ABS.','FREQUENCY','F1','BICOHERENCE',\
'PLASMA', 'CURRENT','LOOP', 'VOLTAGE', 'DC', 'BIAS','H','ALPHA','TE']
plotXLabelTypes = ['TIME','FREQUENCY','F2', 'VOLTAGE']

wHeightOffset=12
wHeightInc = 6
wWidthOffset = 12
wWidthInc = 6
pHeightOffset = 2
pWidthOffset = 2

catalystDir = '//PP006097232D7E/t'

#plot panel preference
panelVbKey = 'panelVb'
panelColorKey = 'panelColor'
panelAxisKey = 'panelAxis'
panelUnitKey = 'panelUnit'


#all parameters
keys = {'addressSeparator':addressSeparator,'daqSplitter':daqSplitter,\
'newLineSplitter':newLineSplitter,'daqStartKey':daqStartKey,'signalCommentKey':signalCommentKey,\
'endOfHeaderKey':endOfHeaderKey,'shotNumKey':shotNumKey,'digitizerIdKey':digitizerIdKey,\
'channelIdKey':channelIdKey,'slotAiKey':slotAiKey,'channelDescriptionKey':channelDescriptionKey,\
'calibrationKey':calibrationKey,'unitKey':unitKey,'loadedTimeKey':loadedTimeKey,\
'filePathKey':filePathKey,'excelFilePathKey':excelFilePathKey,'xExtensions':xExtensions,\
'ffffffKey':ffffffKey,'sheetSlotKey':sheetSlotKey,'sheetAiKey':sheetAiKey,\
'sheetChannelDescriptionKey':sheetChannelDescriptionKey,'catSheetChannelDescriptionKey':catSheetChannelDescriptionKey,\
'sheetCalibrationKey':sheetCalibrationKey,'sheetUnitKey':sheetUnitKey,'sheetTimeShiftKey':sheetTimeShiftKey,\
'slotAisKey':slotAisKey, 'isSmoothKey':isSmoothKey , 'nSmoothKey':nSmoothKey ,\
'isDcCancelHeadKey':isDcCancelHeadKey , 'nDcCancelHeadKey':nDcCancelHeadKey ,\
'isDcCancelTailKey':isDcCancelTailKey , 'nDcCancelTailKey':nDcCancelTailKey ,\
'npersegKey': npersegKey, 'isUncalibratedSignalKey':isUncalibratedSignalKey,\
'isNormalizePsdKey':isNormalizePsdKey,'xRegionKey':xRegionKey,'yRegionKey':yRegionKey,\
'Writer_VersionKey':Writer_VersionKey,'Reader_VersionKey':Reader_VersionKey,\
'SeparatorKey':SeparatorKey,'Decimal_Separator':Decimal_Separator,\
'Multi_HeadingsKey':Multi_HeadingsKey,'X_ColumnsKey':X_ColumnsKey,\
'Time_PrefKey':Time_PrefKey,'OperatorKey':OperatorKey,'DateKey':DateKey,\
'TimeKey':TimeKey,'ChannelsKey':ChannelsKey,'SamplesKey':SamplesKey,\
'DateKey':DateKey,'Y_Unit_LabelKey':Y_Unit_LabelKey,'X_DimensionKey':X_DimensionKey,\
'X0Key':X0Key,'Delta_XKey':Delta_XKey,'plotPenList':plotPenList,\
'plotYLabelTypes':plotYLabelTypes,'plotXLabelTypes':plotXLabelTypes}
