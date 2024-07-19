#IOT部分
import os



def list2str(listbuf):
    return ''.join(listbuf)

def setSummationVerify(verbuf):
    ver = 0
    verbufLen = len(verbuf)
    for i in range(verbufLen):
        ver += int(verbuf[i],16)
    ver &= 0xff
    bVer = '%x'%ver
    return bVer

def setCRC(verbuf):
    crccmd = []
    Preset_Value = 0xFFFF
    Polynomial = 0xA001
    verbufLen = len(verbuf)
    for i in range(verbufLen):
        Preset_Value ^= (int(verbuf[i], 16) & 0xff)
        for j in range(8):
            if ((Preset_Value & 0x0001) != 0):
                Preset_Value = (Preset_Value >> 1) ^ Polynomial
            else:
                Preset_Value = (Preset_Value >> 1)

    val1 = hex(Preset_Value & 0xFF)
    val1 = val1[2:].upper()
    val2 = hex((Preset_Value & 0xFF00) >> 8)
    val2 = val2[2:].upper()

    verbuf.append(val1)
    verbuf.append(val2)
    return verbuf

def checkSummationVerify(verbuf):
    ver = 0
    verbufLen = len(verbuf) - 1
    for i in range(verbufLen):
        ver += int(verbuf[i], 16) & 0xff

    ver &= 0xff
    recvVer = int(verbuf[len(verbuf) - 1], 16)

    if recvVer == ver:
        return True
    return False

def checkCRC(verbuf):
    Preset_Value = 0xFFFF
    Polynomial = 0xA001
    verbufLen = len(verbuf) - 2
    for i in range(verbufLen):
        Preset_Value ^= (int(verbuf[i], 16) & 0xff)
        for j in range(8):
            if ((Preset_Value & 0x0001) != 0):
                Preset_Value = (Preset_Value >> 1) ^ Polynomial
            else:
                Preset_Value = (Preset_Value >> 1)

    retH = (Preset_Value & 0xFF00) >> 8
    retL = (Preset_Value & 0xFF)
    if (retL == int(verbuf[len(verbuf) - 2],16) and retH == int(verbuf[len(verbuf) - 1],16)):
        return True
    return False

def msg2bytes(msg):  # 把hex字符串转成2个字母组成的列表recv_data
    msglen = len(msg)

    recv_data = []
    for i in range(int(msglen / 2)):
        recv_data.append(msg[i * 2:i * 2 + 2])
    # print(recv_data)
    return recv_data

def baudrate2str(ibaudrate):
    baudrates = {
        4800: '00',
        9600: '01',
        38400: '02',
        57600: '03',
        115200: '04'
    }
    return baudrates.get(ibaudrate, None)