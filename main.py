import sys
from wsnDemo import *
from PyQt5.QtWidgets import QApplication, QMainWindow

#设置参数窗口
import DBConnSetting as db_cs
import ConnSetting as cs

#服务器连接参数
import DataConstants
import DataFormat
import SocketWsnThread

# 服务器参数
serverIpAddress = None
serverPort = None
isConnectedToServer = False
socketThread = None

#联动控制标志
isDetectFog = False
isDetectTemp = False
isDetectLight = False

class wsnDemo(QMainWindow):
    def __init__(self):
        super(wsnDemo, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.m_flag = False

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.show()

        #按钮相关信号与槽
        self.ClickEvent()

        # 初始化数据库
        db_cs.initDataBase()

        # 查询数据库并显示默认ip、port
        self.refreshMain_IpPort()

        # 物联网数据服务初始化
        self.initEnv()
        self.sensorList = None
        # 物联网数据服务初始化
        self.socket_connect()

    def initEnv(self):
        # IOT部分
        global isConnectedToServer
        isConnectedToServer = DataConstants.ClientConnect_False

        # 禁用控制按钮
        self.ctlButton(False)

        global socketThread
        socketThread = SocketWsnThread.socketMainThread()

    def ClickEvent(self):
        # click事件，弹出对话框设置网络参数
        self.ui.btn_setting.clicked.connect(self.showConnSettingUi)
        self.ui.btn_connect.clicked.connect(self.socket_connect)
        self.ui.btn_disconnect.clicked.connect(self.socket_disconnect)

        self.ui.pushButton_lamp_on.clicked.connect(self.lampOn)
        self.ui.pushButton_lamp_off.clicked.connect(self.lampOff)
        self.ui.pushButton_fan_on.clicked.connect(self.fanOn)
        self.ui.pushButton_fan_off.clicked.connect(self.fanOff)
        self.ui.pushButton_alarm_on.clicked.connect(self.alarmOn)
        self.ui.pushButton_alarm_off.clicked.connect(self.alarmOff)
        #self.ui.pushButton_lock_on.clicked.connect(self.lockOn)
        #self.ui.pushButton_relay_on.clicked.connect(self.relayOn)
        #self.ui.pushButton_relay_off.clicked.connect(self.relayOff)
        #self.ui.pushButton_steer_on.clicked.connect(self.steerOn)
        #self.ui.pushButton_steer_off.clicked.connect(self.steerOff)
        
        #########
        self.ui.pushButton_detect_fog_on.clicked.connect(self.detectFogOn)
        self.ui.pushButton_detect_fog_off.clicked.connect(self.detectFogOff)
        self.ui.pushButton_detect_light_on.clicked.connect(self.detectLightOn)
        self.ui.pushButton_detect_light_off.clicked.connect(self.detectLightOff)
        self.ui.pushButton_detect_temp_on.clicked.connect(self.detectTempOn)
        self.ui.pushButton_detect_temp_off.clicked.connect(self.detectTempOff)
        
        
    def detectFogOn(self):
        global isDetectFog
        isDetectFog = True
        self.ui.detect_fog_text.setText("已启用")
        self.ui.detect_fog_text.setStyleSheet("color:Red;")
    
    def detectFogOff(self):
        global isDetectFog
        isDetectFog = False
        self.ui.detect_fog_text.setText("未启用")
        self.ui.detect_fog_text.setStyleSheet("color: rgb(0,139,0);")
        
    def detectLightOn(self):
        global isDetectLight
        isDetectLight = True
        self.ui.detect_light_text.setText("已启用")
        self.ui.detect_light_text.setStyleSheet("color:Red;")
    
    def detectLightOff(self):
        global isDetectLight
        isDetectLight = False
        self.ui.detect_light_text.setText("未启用")
        self.ui.detect_light_text.setStyleSheet("color: rgb(0,139,0);")
    
    def detectTempOn(self):
        global isDetectTemp
        isDetectTemp = True
        self.ui.detect_temp_text.setText("已启用")
        self.ui.detect_temp_text.setStyleSheet("color:Red;")
    
    def detectTempOff(self):
        global isDetectTemp
        isDetectTemp = False    
        self.ui.detect_temp_text.setText("未启用")
        self.ui.detect_temp_text.setStyleSheet("color: rgb(0,139,0);")
    

    # 服务连接按钮动作
    def socket_connect(self):
        global socketThread
        global serverIpAddress
        global serverPort
        try:
            # 查询数据库，获取IP和PORT
            result = db_cs.queryDataBase()
            serverIpAddress = str(result[0][1])
            serverPort = result[0][2]
        except Exception as ret:
            self.StatusFaceInfo.showMessage('请检查目标IP，目标端口')
        else:
            # 使用SocketWsnThread类中的socketMainThread进行socket连接
            socketThread = SocketWsnThread.socketMainThread()
            # 使用信号槽机制：设置信号signal_smthread_status，用于触发接收连接状态status_socket_showinfo
            socketThread.signal_smthread_status.connect(self.status_socket_showinfo)
            # 使用信号槽机制：设置信号signal_smthread_data，用于触发接收写入数据动作dataDispose
            socketThread.signal_smthread_data.connect(self.dataDispose)
            socketThread.start()
            SocketWsnThread.scanTimer.start(200)

    # 服务断开连接按钮动作
    def socket_disconnect(self):
        self.ui.statusbar.showMessage('手动断开网络')
        self.sensorList = []
        self.uiReset()
        self.mainThreadReset()

    # socketThread 数据抛出接收显示
    def status_socket_showinfo(self, msg):
        global isConnectedToServer
        if msg == DataConstants.ClientConnect_True:
            # 标识isConnectedToServer为True
            isConnectedToServer = DataConstants.ClientConnect_True
            # 连接成功,切换按钮
            msg = 'TCP客户端已连接IP:%s端口:%s\n' % (serverIpAddress, serverPort)
            # 使能“断开连接”按钮，禁止“建立连接”按钮
            self.ui.btn_connect.setEnabled(False)
            self.ui.btn_disconnect.setEnabled(True)
            # 使能执行器控制按钮
            self.ctlButton(True)
        else:
            if msg == DataConstants.ClientReconnect:
                isConnectedToServer = DataConstants.ClientReconnect
                msg = '服务器已断开'
                self.uiReset()
                self.mainThreadReset()
        self.ui.statusbar.showMessage(msg)

    # 接收到wsnData的完整数据，msg2bytes格式化成列表
    def dataDispose(self, data):
        packet = DataFormat.msg2bytes(data)
        print(packet)

        #io类型
        if (packet[2] == DataConstants.DEVTYPE_IO and packet[6] == DataConstants.CMD_INTERVAL):
            if (packet[4] == DataConstants.SENSOR_IO_SMOKE_VR):
                self.showSmoke(packet)
            elif (packet[4] == DataConstants.SENSOR_IO_BODY_VR):
                self.showBody(packet)
            elif (packet[4] == DataConstants.SENSOR_IO_RAIN_VR):
                self.showRain(packet)
            elif (packet[4] == DataConstants.SENSOR_IO_INFRA_VR):
                self.showInfra(packet)
            elif (packet[4] == DataConstants.SENSOR_IO_ALCOHOL_VR):
                self.showAlcohol(packet)
        #通讯类型
        elif (packet[2] == DataConstants.DEVTYPE_485 and packet[6] == DataConstants.CMD_INTERVAL):
            if (packet[4] == DataConstants.SENSOR_IO_ILLUMINATION_VR):
                self.showIllu(packet)
            elif (packet[4] == DataConstants.SENSOR_485_TEMP_VR):
                self.showTemp(packet)
            elif (packet[4] == DataConstants.SENSOR_485_HUMI_VR):
                self.showHumi(packet)

    def showSmoke(self, data):
        v = data[13]
        global isDetectFog
        if(v == '01'):
            v = '异常'
            color = "color:Red"
            if isDetectFog:
                self.alarmOn()
        else:
            v = '正常'
            color = "color:Green"
            if isDetectFog:
                self.alarmOff()
        self.ui.label_smog.setStyleSheet(color)
        self.ui.label_smog.setText(str(v))

    def showBody(self, data):
        v = data[13]
        if(v == '01'):
            v = '异常'
            color = "color:Red"
        else:
            v = '正常'
            color = "color:Green"
        self.ui.label_ihum.setStyleSheet(color)
        self.ui.label_ihum.setText(str(v))

    def showRain(self, data):
        v = data[13]
        if(v == '01'):
            v = '有雨雪'
            color = "color:Red"
        else:
            v = '无雨雪'
            color = "color:Green"
        self.ui.label_rain.setStyleSheet(color)
        self.ui.label_rain.setText(str(v))

    def showInfra(self, data):
        v = data[13]
        if(v == '01'):
            v = '异常'
            color = "color:Red"
        else:
            v = '正常'
            color = "color:Green"
        self.ui.label_infra.setStyleSheet(color)
        self.ui.label_infra.setText(str(v))

    def showAlcohol(self, data):
        v = data[13]
        if (v == '01'):
            v = '异常'
            color = "color:Red"
        else:
            v = '正常'
            color = "color:Green"
        self.ui.label_alcohol.setStyleSheet(color)
        self.ui.label_alcohol.setText(str(v))

    def showIllu(self, data):
        illu = ((int(data[10], 16) * 256 + int(data[11], 16)) * 65536 + int(data[12], 16) * 256 + int(data[13], 16))
        self.ui.label_illu.setText(str(illu) + '  Lux')
        global isDetectLight
        if isDetectLight:
            if illu < int(self.ui.edit_light.text()):
                self.lampOn()
            else:
                self.lampOff()

    def showTemp(self, data):
        ftemp = ((int(data[10], 16) * 256 + int(data[11], 16)) * 65536 + int(data[12], 16) * 256 + int(data[13],
                                                                                                       16)) / 10000.0
        ftemp = round(ftemp, 2)
        self.ui.label_temp.setText(str(ftemp) + '℃')
        global isDetectTemp
        if isDetectTemp:
            if ftemp > int(self.ui.edit_temp.text()):
                self.fanOn()
            else:
                self.fanOff()

    def showHumi(self, data):
        fhumi = ((int(data[10], 16) * 256 + int(data[11], 16)) * 65536 + int(data[12], 16) * 256 + int(data[13],
                                                                                                       16)) / 10000.0
        fhumi = round(fhumi, 2)
        self.ui.label_humi.setText(str(fhumi) + '%')

    # 发送命令
    def sendControlCmd(self, dev_type, addr, index, data_type, arg):
        cmd = []
        cmd.append(DataConstants.DATA_HEAD)  # 'CC'
        cmd.append('10')
        cmd.append(dev_type)  # '02'
        cmd.append('00')
        cmd.append(addr)  # '0F'
        cmd.append(index)  # 协议类型
        cmd.append(DataConstants.CMD_CTRL)
        cmd.append(data_type)
        for i in range(5):
            cmd.append('00')
        cmd.append('{:02X}'.format(arg))
        DataFormat.setCRC(cmd)
        SocketWsnThread.socketsend(DataFormat.list2str(cmd))

    # 发送命令
    def sendControlCmdL(self, dev_type, addr, index, data_type,  arg1, arg2):
        cmd = []
        cmd.append(DataConstants.DATA_HEAD)  # 'CC'
        cmd.append('10')
        cmd.append(dev_type)  # '02'
        cmd.append('00')
        cmd.append(addr)  # '0F'
        cmd.append(index)  # 协议类型
        cmd.append(DataConstants.CMD_CTRL)
        cmd.append(data_type)
        for i in range(4):
            cmd.append('00')
        cmd.append('{:02X}'.format(arg1))
        cmd.append('{:02X}'.format(arg2))
        DataFormat.setCRC(cmd)
        SocketWsnThread.socketsend(DataFormat.list2str(cmd))

    def lampOn(self):
        self.sendControlCmd(DataConstants.DEVTYPE_PWM, DataConstants.SENSOR_PWM_LAMP_VR, DataConstants.INDEX_FIRST, DataConstants.DATATYPE_INT, 0x09)
        self.ui.light.setStyleSheet("background-color:rgb(76, 190, 51);")
    def lampOff(self):
        self.sendControlCmd(DataConstants.DEVTYPE_PWM, DataConstants.SENSOR_PWM_LAMP_VR, DataConstants.INDEX_FIRST, DataConstants.DATATYPE_INT, 0x00)
        self.ui.light.setStyleSheet("background-color:rgb(255, 0, 0);")

    def fanOn(self):
        self.sendControlCmd(DataConstants.DEVTYPE_PWM, DataConstants.SENSOR_PWM_FAN_VR, DataConstants.INDEX_FIRST, DataConstants.DATATYPE_BOOL, 0x01)
        self.ui.fan.setStyleSheet("background-color:rgb(76, 190, 51);")
    def fanOff(self):
        self.sendControlCmd(DataConstants.DEVTYPE_PWM, DataConstants.SENSOR_PWM_FAN_VR, DataConstants.INDEX_FIRST, DataConstants.DATATYPE_BOOL, 0x00)
        self.ui.fan.setStyleSheet("background-color:rgb(255, 0, 0);")

    def alarmOn(self):
        self.sendControlCmd(DataConstants.DEVTYPE_PWM, DataConstants.SENSOR_PWM_ALARMLIGHT_VR, DataConstants.INDEX_FIRST, DataConstants.DATATYPE_BOOL, 0x01)
        self.ui.alert.setStyleSheet("background-color:rgb(76, 190, 51);")
    def alarmOff(self):
        self.sendControlCmd(DataConstants.DEVTYPE_PWM, DataConstants.SENSOR_PWM_ALARMLIGHT_VR, DataConstants.INDEX_FIRST, DataConstants.DATATYPE_BOOL, 0x00)
        self.ui.alert.setStyleSheet("background-color:rgb(255, 0, 0);")

    def lockOn(self):
        self.sendControlCmd(DataConstants.DEVTYPE_PWM, DataConstants.SENSOR_PWM_POWERONLOCK_VR, DataConstants.INDEX_FIRST, DataConstants.DATATYPE_BOOL, 0x01)

    def relayOn(self):#开窗帘
        self.sendControlCmdL(DataConstants.DEVTYPE_485, DataConstants.SENSOR_485_RELAY_VR, DataConstants.INDEX_FIRST, DataConstants.DATATYPE_ARRAY, 0xAA, 0xA1)
    def relayOff(self):#关窗帘
        self.sendControlCmdL(DataConstants.DEVTYPE_485, DataConstants.SENSOR_485_RELAY_VR, DataConstants.INDEX_FIRST, DataConstants.DATATYPE_ARRAY, 0xAA, 0xA4)

    def steerOn(self):
        self.sendControlCmd(DataConstants.DEVTYPE_IO, DataConstants.SENSOR_IO_STEER_VR, DataConstants.INDEX_FIRST, DataConstants.DATATYPE_BOOL, 0x01)
    def steerOff(self):
        self.sendControlCmd(DataConstants.DEVTYPE_IO, DataConstants.SENSOR_IO_STEER_VR, DataConstants.INDEX_FIRST, DataConstants.DATATYPE_BOOL, 0x00)

    def uiReset(self):
        global isConnectedToServer
        if isConnectedToServer != DataConstants.ClientReconnect:
            isConnectedToServer = DataConstants.ClientConnect_False

        self.ctlButton(False)
        self.ui.btn_connect.setEnabled(True)
        self.ui.btn_disconnect.setEnabled(False)

    def mainThreadReset(self):
        # IOT
        global socketThread
        if socketThread.isRunning():
            SocketWsnThread.socketClientID.close()
            socketThread.terminate()

    # 控制按钮
    def ctlButton(self, status):
        self.ui.pushButton_lamp_on.setEnabled(status)
        self.ui.pushButton_lamp_off.setEnabled(status)
        self.ui.pushButton_fan_on.setEnabled(status)
        self.ui.pushButton_fan_off.setEnabled(status)
        self.ui.pushButton_alarm_on.setEnabled(status)
        self.ui.pushButton_alarm_off.setEnabled(status)
        # self.ui.pushButton_lock_on.setEnabled(status)
        # self.ui.pushButton_relay_on.setEnabled(status)
        # self.ui.pushButton_relay_off.setEnabled(status)
        # self.ui.pushButton_steer_on.setEnabled(status)
        # self.ui.pushButton_steer_off.setEnabled(status)
        # self.ui.pushButton_seg_on.setEnabled(status)
        # self.ui.pushButton_seg_off.setEnabled(status)

    # 弹出服务器信息设置按钮
    def showConnSettingUi(self):
        # 显示WindowConnSetting界面
        self.csUi = cs.DialogConnSetting()
        self.csUi.show()
        # 接收Dialog_NetSetting中的Signal_Dialog_NetSetting信号，完成refreshMain_IpPort
        self.csUi.Signal_Dialog_ConnSetting.connect(self.refreshMain_IpPort)

    #UI界面显示服务器信息
    def refreshMain_IpPort(self):
        #查询数据库，并显示
        result = db_cs.queryDataBase()
        self.ui.edit_addr.setText(str(result[0][1]))
        self.ui.edit_port.setText(str(result[0][2]))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.isMaximized() == False:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()                #获取鼠标相对窗口位置
            event.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))         #更改鼠标图标

    def mouseMoveEvent(self, mouse_event):
        if QtCore.Qt.LeftButton and self.m_flag:
            self.move(mouse_event.globalPos() - self.m_Position)            #更改窗口位置
            mouse_event.accept()

    def mouseReleaseEvent(self, mouse_event):
        self.m_flag = False
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = wsnDemo()
    sys.exit(app.exec_())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/