from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow

import WindowConnSetting as uiConnSetting
import DBConnSetting as db_cs

class DialogConnSetting(QMainWindow, uiConnSetting.Ui_WindowConnSetting):
    Signal_Dialog_ConnSetting = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(DialogConnSetting, self).__init__(parent)
        self.setupUi(self)

        #读取数据库中ip和port
        result = db_cs.queryDataBase()
        self.EditConnIpAddress.setText(str(result[0][1]))
        self.EditConnPort.setText(str(result[0][2]))

        #按钮click事件
        self.BtnConnSave.clicked.connect(self.dialogSave)
        self.BtnConnCancel.clicked.connect(self.dialogClose)

    def dialogSave(self):
        str_ip = self.EditConnIpAddress.text()
        str_port = self.EditConnPort.text()
        db_cs.updateDataBase(str_ip, int(str_port))
        self.close()
        #发信号，告诉设置窗口关闭
        self.Signal_Dialog_ConnSetting.emit()

    def dialogClose(self):
        self.close()