
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



class popFrmArithmetics(QtWidgets.QFrame, dataGuiBaseClass):
    sigNewDataAdded = QtCore.pyqtSignal()

    def __init__(self ,displayType='list'):
        super().__init__()
        uic.loadUi('popFrmArithmetics.ui', self)

        #creat lists of objects
        self.listCbxOperator = [getattr(self, n) for n in dir(self) if 'cbxOperator' in n]
        self.listCbxShotNum = [getattr(self, n) for n in dir(self) if 'cbxShotNum' in n]
        self.listCbxChannel = [getattr(self, n) for n in dir(self) if 'cbxChannel' in n]
        self.listLedMultiplier = [getattr(self, n) for n in dir(self) if 'ledMultiplier' in n]
        self.listCbx = [getattr(self, n) for n in dir(self) if 'cbx' in n and 'cbxOperator' not in n]

        #initiate the combo boxes
        for i in range(len(self.listCbxShotNum)):
            self.listCbxShotNum[i].currentIndexChanged.connect(functools.partial(self.updateAfterShotNumSelection,i))
            self.listCbxShotNum[i].selected = False
        for i in range(len(self.listCbxChannel)):
            self.listCbxChannel[i].currentIndexChanged.connect(functools.partial(self.updateAfterChannelSelection,i))
            self.listCbxChannel[i].selected = False

        if len(self.params)!=0:
            for cbxShotNum in self.listCbxShotNum:
                cbxShotNum.addItems(['']+list(np.unique(self.params[shotNumKey]).astype(str)))



        #connect buttons
        self.btnClear.clicked.connect(self.clear)
        self.btnCalculate.clicked.connect(self.calculate)

    def updateAfterShotNumSelection(self,i):

        self.listCbxChannel[i].clear()
        shotNum = self.listCbxShotNum[i].currentText()
        if shotNum == '':
            self.listCbxChannel[i].addItems([''])
            self.listCbxShotNum[i].selected = False

        else:
            self.listCbxShotNum[i].selected = True
            tempParam = self.params[self.params[shotNumKey]==int(shotNum)]
            self.listCbxChannel[i].addItems(['']+list(np.unique(tempParam[channelDescriptionKey]).astype(str)))

    def updateAfterChannelSelection (self,i):

        if self.listCbxChannel[i].currentText() =='':
            self.listCbxChannel[i].selected = False

        else:

            self.listCbxChannel[i].selected = True


    def clear(self):
        for cbxShotNum in self.listCbxShotNum:
            cbxShotNum.setCurrentIndex(0)

        for cbxOperator in self.listCbxOperator:
            cbxOperator.setCurrentIndex(0)

    def calculate(self):
        if not self.cbxShotNum.selected or not self.cbxChannel.selected:
            return
        if not any (self.listCbxShotNum[i+1].selected and self.listCbxChannel[i+1].selected for i in range(len(self.listCbxShotNum)-1)):
            if self.ledMultiplier.text() == '' or self.ledMultiplier.text() == '1':
                return

        listSelectedIndex = [0]+[i+1 for i in range(len(self.listCbxShotNum)-1) if self.listCbxShotNum[i+1].selected and self.listCbxChannel[i+1].selected]
        selectedTraces = []
        selectedMultipliers = []
        selectedOperators = []
        shotNum = str(self.listCbxShotNum[0].currentText())

        channelDescriptions = []
        for i in listSelectedIndex:
            tempParam1 = self.params[self.params[shotNumKey]==int(self.listCbxShotNum[i].currentText())]
            param = tempParam1[tempParam1[channelDescriptionKey]==self.listCbxChannel[i].currentText()].reset_index(drop=True)
            para = param.loc[0,:]
            if i ==0:
                param2 = param.loc[0,:].copy()

            channelDescriptions.append(self.listCbxChannel[i].currentText())



            if self.listLedMultiplier[i].text() == '' or \
               not str(self.listLedMultiplier[i].text().replace('.','').replace('-','').replace('e','').replace('E','')).isdigit():
                multiplier = 1.0
            else:
                multiplier = float(self.listLedMultiplier[i].text())
            selectedMultipliers.append(multiplier)

            selectedTraces.append(np.array(self.getData(param).loc[:,0])*multiplier*para[calibrationKey])

            if i ==0:
                selectedOperators.append('+')
            else:
                selectedOperators.append(self.listCbxOperator[i-1].currentText())

        aligned = True
        for i in range(len(selectedTraces)-1):
            if len(selectedTraces[i]) != len(selectedTraces[i+1]):
                aligned = False

        if not aligned:
            selectedTraces = list (alignLength(selectedTraces))





        selectedTraces1, selectedOperators1,selectedMultipliers1 = selectedTraces[:], selectedOperators[:], selectedMultipliers[:]

        higherOperatorIndexes = [i for i in range(len(selectedTraces)) if selectedOperators[i]=='x' or selectedOperators[i]=='/']

        for i in range(len(higherOperatorIndexes)):
            index = higherOperatorIndexes[i]-i
            if selectedOperators[index]=='x':
                selectedTraces[index-1]=selectedTraces[index-1]*selectedTraces[index]
            else:
                selectedTraces[index-1]=selectedTraces[index-1]/selectedTraces[index]
            selectedTraces.pop(index)
            selectedOperators.pop(index)

        result = np.zeros(len(selectedTraces[0]))
        for i in range(len(selectedTraces)):
            if selectedOperators[i]=='+':
                result += selectedTraces[i]
            else:
                result -= selectedTraces[i]



        channelDescription = '* '

        for i in range(len(channelDescriptions)):
            if i ==0:
                channelDescription+= channelDescriptions[i]+'(x '+ str(selectedMultipliers1[i])+') '
            else:
                channelDescription+= selectedOperators1[i] +' '+ channelDescriptions[i]+'(x '+ str(selectedMultipliers1[i])+') '


        channelDescription += str(datetime.now())
        channelId = shotNum+'_'+channelDescription

        param2[channelDescriptionKey] = channelDescription
        param2[channelIdKey] = channelId
        param2[calibrationKey] = 1.0

        dataGuiBaseClass.params = dataGuiBaseClass.params.append(pd.DataFrame([param2])).reset_index(drop=True)
        df = pd.DataFrame()
        df[channelId] = result
        dataIndex = [x for x in range(len(self.dataList)) if self.dataList[x][shotNumKey]==shotNum][0]
        dataGuiBaseClass.dataList[dataIndex][dfKey] = pd.concat([dataGuiBaseClass.dataList[dataIndex][dfKey],df], axis=1).reset_index(drop=True)



        self.sigNewDataAdded.emit()






if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    frame = popFrmArithmetics()
    
    # app.aboutToQuit.connect(app.deleteLater)
    # Frame = QtWidgets.QFrame()
    # ui = frmLoadData()
    # ui.setupUi(Frame)
    frame.show()
    app.exec_()




