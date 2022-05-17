
import sys
import os
from os import path 
sys.path.append(path.join(path.dirname(__file__), "project"))
from project.frmMain import * 



def main():

    import sys
    app = QtWidgets.QApplication(sys.argv)
    frame = frmMainWindow()
    
    # app.aboutToQuit.connect(app.deleteLater)
    # Frame = QtWidgets.QFrame()
    # ui = frmLoadData()
    # ui.setupUi(Frame)
    frame.show()
    app.exec_()

    from IPython import embed; embed()



if __name__ == "__main__":
    main()

