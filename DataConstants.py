ClientConnect_True = 'CONNECT_TRUE'
ClientConnect_False = 'CONNECT_FALSE'
ClientReconnect = 'CONNECT_RECONNECT'

# 帧头
DATA_HEAD = 'CC'                   #发送包头
DATA_RET_HEAD = 'BB'               #接收包头
# 设备类型
DEVTYPE_IO = '01'
DEVTYPE_PWM = '02'
DEVTYPE_485 = '03'
# 命令类型
CMD_CTRL = '01'                     #控制命令
CMD_INTERVAL = '03'                 #定时收集传感器数据
# 数据类型
DATATYPE_BOOL = '01'                #BOOL型
DATATYPE_INT = '02'                 #整型
DATATYPE_FLOAT = '03'               #浮点型
DATATYPE_ARRAY = '04'               #数组型
# 索引编号
INDEX_FIRST = '00'
INDEX_SECOND = '01'
# 传感器类型
SENSOR_IO_SMOKE_VR = '01'          #烟雾
SENSOR_IO_BODY_VR = '07'           #人体
SENSOR_IO_RAIN_VR = '04'           #雨雪
SENSOR_IO_INFRA_VR = '06'          #红外对射
SENSOR_IO_ALCOHOL_VR = '02'        #酒精

SENSOR_IO_ILLUMINATION_VR = '01'   #光照
SENSOR_485_TEMP_VR = '02'          #温度
SENSOR_485_HUMI_VR = '03'          #湿度

SENSOR_485_ULTRASONIC = '0C'    #超声波测距
SENSOR_IO_TOUCH = '19'          #触摸按键

# 执行器类型
SENSOR_PWM_POWERONLOCK_VR = '03'   #电磁锁
SENSOR_PWM_ALARMLIGHT_VR = '05'    #报警灯
SENSOR_PWM_FAN_VR = '06'           #风扇
SENSOR_PWM_LAMP_VR = '01'           #调光灯

SENSOR_IO_STEER_VR = '14'           #舵机

SENSOR_485_RELAY_VR = 'A0'           #继电器

SENSOR_PWM_SEG = '09'           #数码管




