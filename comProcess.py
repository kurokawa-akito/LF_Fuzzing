import serial
from collections import deque


class comPortReceiver:
    def __init__(
        self,
        port,
        baudrate=460800,
        parity="E",
        bytesize=8,
        stopbits=1,
        timeout=3,
        bufferSize=1024,
    ):
        try:
            if self.__inited__ == True:
                raise Exception("forbiden to call init twice!")
        except AttributeError:
            # First time init
            pass

        self.__portOpen = False
        self.__serial = None
        self.__queue = None
        self.__version = "1.0"
        self.__fakeLog = ""
        if not baudrate in [9600, 19200, 38400, 115200, 230400, 460800, 921600]:
            raise TypeError(
                "Baudrate is allowed only 9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600"
            )
        if not parity in ["O", "N", "E"]:
            raise TypeError("Parity is allowed only O/N/E")
        if not bytesize in [5, 6, 7, 8]:
            raise TypeError("Byte size is allowed only 5,6,7,8")
        if not stopbits in [1, 1.5, 2]:
            raise TypeError("Stop bits is allowed only 1/1.5/2")
        if isinstance(timeout, int) == False:
            raise TypeError("Timeout is allowed only integer")
        if isinstance(bufferSize, int) == False or bufferSize <= 0:
            raise TypeError("Buffer size should be positive integer")

        self.__port = port
        # Default parameters
        self.__baudrate = baudrate
        self.__bytesize = bytesize
        if parity == "E":
            self.__parity = serial.PARITY_EVEN
        elif parity == "O":
            self.__parity = serial.PARITY_ODD
        else:
            self.__parity = serial.PARITY_NONE
        self.__stopbits = stopbits
        self.__timeout = timeout
        self.__bufferSize = bufferSize
        try:
            self.__queue = deque(maxlen=self.__bufferSize)
        except Exception as e:
            raise Exception("Initial queue fail!!")

        # To avoid to be called again
        self.__inited__ = True

    def __del__(self):
        try:
            if self.__inited__ == True:
                if self.__portOpen == True:
                    self.disconnect()
                self.__serial = None
                self.__portOpen = False
                if not self.__queue == None:
                    self.__queue.clear()
                    self.__queue = None
        except:
            # print("Object delete fail...")
            pass

    def getVersion(self):
        return self.__version

    def connect(self):
        if self.__portOpen == False:
            try:
                # Add fake port feature that we can debug without dongle
                if self.__port == "FAKEPORT":
                    self.__portOpen = True
                else:
                    self.__serial = serial.Serial(
                        self.__port,
                        self.__baudrate,
                        self.__bytesize,
                        self.__parity,
                        self.__stopbits,
                        timeout=self.__timeout,
                    )
                    if self.__serial.isOpen():
                        self.__serial.close()
                    self.__serial.open()
                    self.__portOpen = True
            except Exception as e:
                raise Exception("Open Port:" + self.__port + " error" + str(e))

    def receive(self):
        if self.__port == "FAKEPORT":
            # Give the fake data
            if len(self.__fakeLog) == 0:
                # I will not check the content, reserved for the possibility to test abnormal case
                return 0

            fakeLogList = [ord(c) for c in self.__fakeLog]
            if not self.__queue == None:
                if not len(self.__queue) == self.__bufferSize:
                    # Maybe Queue is not empty, so we can not use all
                    availableQueueSize = self.__bufferSize - len(self.__queue)
                    if availableQueueSize < len(fakeLogList):
                        return 0

                    readData = fakeLogList
                    for i in range(len(readData)):
                        self.__queue.append(readData[i])
                    return len(readData)
                else:
                    # Queue full..., receive nothing
                    return 0
        else:
            if self.__portOpen == True and not self.__serial == None:
                if not self.__queue == None:
                    if not len(self.__queue) == self.__bufferSize:
                        # Maybe Queue is not empty, so we can not use all
                        availableQueueSize = self.__bufferSize - len(self.__queue)
                        # Should we use read_until()?
                        readData = self.__serial.read(availableQueueSize)
                        for i in range(len(readData)):
                            self.__queue.append(readData[i])
                        return len(readData)
                    else:
                        # Queue full..., receive nothing
                        return 0

    def bufferRead(self):
        if not self.__queue == None:
            if not len(self.__queue) == 0:
                data = self.__queue.popleft()
                return data
            else:
                return None

    def bufferHasData(self):
        if not self.__queue == None:
            if not len(self.__queue) == 0:
                return True
            else:
                return False

    def bufferDataLen(self):
        if not self.__queue == None:
            return len(self.__queue)
        else:
            return 0

    # The API read a line in buffer and return the line length
    # If buffer empty or not contain '\n', will return None
    def readOneLine(self):
        if not self.__queue == None:
            # Note, the API supported after Python 3.5
            lfCharIndex = 0
            try:
                lfCharIndex = self.__queue.index(10)
            except:
                lfCharIndex = 0

            if not lfCharIndex == 0:
                retList = []
                for i in range(lfCharIndex + 1):
                    charValue = self.__queue.popleft()
                    retList.append(charValue)
                return retList
            else:
                return None
        else:
            return None

    def disconnect(self):
        if self.__portOpen == True:
            if not self.__serial == None:
                self.__serial.close()
            self.__portOpen = False

    def isConnected(self):
        return self.__portOpen

    def setFakeLog(self, log):
        if not isinstance(log, str):
            return
        self.__fakeLog = log

    def dataSend(self, message):
        byteSent = 0
        try:
            if self.__port == "FAKEPORT":
                pass
            else:
                if self.__portOpen == True and self.__serial.writable():
                    if isinstance(message, str) == True:
                        if not message.endswith("\r"):
                            message += "\r"
                        userMessage = message.encode("utf-8")
                        byteSent = self.__serial.write(userMessage)
        except Exception as e:
            print(e)
        return byteSent

    def inputBufferClear(self):
        if self.__portOpen == True:
            if not self.__serial == None:
                self.__serial.reset_input_buffer()

    def outputBufferClear(self):
        if self.__portOpen == True:
            if not self.__serial == None:
                self.__serial.reset_output_buffer()
