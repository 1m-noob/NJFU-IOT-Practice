import socket

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, QTimer

import DBConnSetting as db_cs
import DataConstants
import DataFormat

serverIpAddress = None
serverPort = None

isConnectedToServer = False
socketClientID = None

bDataLock = False
iDataIn = 0
iDataOut = 0
MAXBUFFLEN = 60
bytesDataRecBuff = []

scanTimer = None            #全局扫描处理数据定时器

def socketsend(strSendbuf):
    global socketClientID
    if isConnectedToServer == DataConstants.ClientConnect_True:
        try:
            cmd_bytes = bytes.fromhex(strSendbuf.upper())
            print("SocketSend：" + strSendbuf.upper())
            socketClientID.send(cmd_bytes)
        except Exception as ret:
            print('socketsend数据发送失败\n')

class socketMainThread(QThread):
    # 信号槽机制：设置一个信号，用于触发接收区写入动作
    signal_smthread_status = QtCore.pyqtSignal(str)
    signal_smthread_data = QtCore.pyqtSignal(str)

    def __init__(self):
        super(socketMainThread, self).__init__()

        #socket初始状态False
        global isConnectedToServer
        isConnectedToServer = DataConstants.ClientConnect_False

        global bytesDataRecBuff
        for i in range(MAXBUFFLEN):
            bytesDataRecBuff.insert(i, 0)

        global serverIpAddress
        global serverPort
        result = db_cs.queryDataBase()
        serverIpAddress = str(result[0][1])
        serverPort = result[0][2]
        # print('serverIpAddress = %s' %serverIpAddress)
        # print('serverPort = %s' % serverPort)

        # 启动scanTimer定时器，start只执行一次
        global scanTimer
        scanTimer = QTimer(self)
        scanTimer.timeout.connect(self.scanBuffer)

    def run(self):
        global isConnectedToServer
        global socketClientID

        while True:
            # print('isConnectedToServer = %s' %isConnectedToServer)
            if isConnectedToServer == DataConstants.ClientConnect_True:
                try:
                    try:
                        recv_msg = socketClientID.recv(1024)
                        if recv_msg:
                            # hex字符串
                            msg = recv_msg.hex().upper()
                            # print('on_socket_receive:%s' %msg)
                            # 缓冲区数据转列表
                            self.recviveData(DataFormat.msg2bytes(msg))
                            QThread.msleep(100)
                        else:
                            #服务器断开
                            isConnectedToServer = DataConstants.ClientReconnect
                            self.signal_smthread_status.emit(isConnectedToServer)

                    except Exception as e:
                        self.signal_smthread_status.emit(e)
                        break
                except Exception as errorcode:
                    print("reconn socket error :%s" % errorcode)
                    isConnectedToServer = DataConstants.ClientReconnect
                    self.signal_smthread_status.emit(isConnectedToServer)
                    socketClientID.close()
            else:
                if isConnectedToServer == DataConstants.ClientReconnect:
                    # 如果是断线重连，则3秒后重连
                    QThread.sleep(3)

                QThread.msleep(100)
                socketClientID = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # socketClientID.settimeout(10)
                try:
                    self.signal_smthread_status.emit('正在连接目标服务器')
                    socketClientID.connect((serverIpAddress,serverPort))
                except Exception as ret:
                    self.signal_smthread_status.emit('无法连接目标服务器\n')
                else:
                    isConnectedToServer = DataConstants.ClientConnect_True
                    self.signal_smthread_status.emit(isConnectedToServer)

    def recviveData(self, bRecData):
        global bDataLock
        global iDataIn
        global iDataOut
        global bytesDataRecBuff
        # print("FUN:recviveData")

        iDataLen = len(bRecData)
        # print('iDataLen: %d'%iDataLen)
        if bDataLock is False:
            bDataLock = True
            if(iDataIn + iDataLen < MAXBUFFLEN):
                for i in range(iDataLen):
                    bytesDataRecBuff[iDataIn + i] = bRecData[i]
                iDataIn += iDataLen
            else:
                if iDataIn + iDataLen == MAXBUFFLEN:
                    for i in range(iDataLen):
                        bytesDataRecBuff[iDataIn + i] = bRecData[i]
                    iDataIn = 0
                else:
                    for i in range(MAXBUFFLEN-iDataIn):
                        bytesDataRecBuff[i+iDataIn] = bRecData[i+iDataIn-iDataIn]
                    for i in range(iDataLen - MAXBUFFLEN + iDataIn):
                        bytesDataRecBuff[i] = bRecData[i+MAXBUFFLEN - iDataIn]
                    iDataIn = iDataLen - MAXBUFFLEN + iDataIn
            bDataLock = False

        # print(bytesDataRecBuff)
        # print('recviveData end')

    def scanBuffer(self):
        # print('scanBuffer start')
        global bDataLock
        global iDataIn
        global iDataOut

        if bDataLock is False:
            bDataLock = True
            while (iDataIn != iDataOut):
                if bytesDataRecBuff[iDataOut] == 'BB':
                    iValidLen = self.validReceiveLen()
                    if iValidLen < 8:
                        bDataLock = False
                        return

                    iPacketLen = int(bytesDataRecBuff[self.dataOutLocation(1)], 16)

                    if iValidLen < iPacketLen:
                        bDataLock = False
                        return

                    if (iPacketLen > 7 and iPacketLen < 40):
                        buf = []
                        for i in range(iPacketLen):
                            buf.insert(i, 0)
                        for i in range(iPacketLen):
                            buf[i] = bytesDataRecBuff[self.dataOutLocation(i)]
                        # 校验
                        if DataFormat.checkCRC(buf):
                            iDataOut = self.dataOutLocation(iPacketLen)
                            bDataLock = False
                            self.signal_smthread_data.emit(DataFormat.list2str(buf))
                            return
                iDataOut = self.dataOutLocation(1)
            bDataLock = False

    # 获取缓冲区内的有效长度
    def validReceiveLen(self):
        if iDataOut < iDataIn:
            return iDataIn - iDataOut
        else:
            if iDataOut > iDataIn:
                return MAXBUFFLEN - iDataOut + iDataIn
        return 0

    # 返回后面第iNum有效数据的位置
    def dataOutLocation(self, iMove):
        ret = 0
        if (iDataOut + iMove < MAXBUFFLEN):
            ret = iDataOut + iMove
        else:
            if (iDataOut + iMove > MAXBUFFLEN):
                ret = iDataOut + iMove - MAXBUFFLEN
        return ret


