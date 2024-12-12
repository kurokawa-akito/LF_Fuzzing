import json
import time
from comProcess import comPortReceiver


class configContent:
    maxValue = 255
    supportCommand = []
    originString = ""
    repeatTime = 0
    sensorID = ""
    typeID = ""


def readConfig(configValues):
    try:
        jsonFile = open("parameter.json", "r")
        parameter = json.load(jsonFile)

        configValues.maxValue = parameter["max"]
        configValues.supportCommand = parameter["supportCommand"]
        configValues.originString = parameter["originString"]
        configValues.repeatTime = parameter["repeatTime"]
        configValues.sensorID = parameter["sensorID"]
        configValues.typeID = parameter["typeID"]
    except Exception as e:
        raise (e)


def openComPort():
    try:
        dataSending = comPortReceiver("COM6")
        dataReceive = comPortReceiver("COM12")
    except Exception as e:
        raise (e)
    return dataSending, dataReceive


def receiveLoop(dataReceive, sensorID, typeID):
    receivedResult = ""
    receiveResponse = False
    readRetryTimes = 50

    while readRetryTimes > 0:
        readLine = dataReceive.readOneLine()
        if not readLine == None:
            byteArray = bytearray(readLine)
            receivedResult = byteArray.decode("utf-8")
            if sensorID in receivedResult and typeID not in receivedResult:
                receiveResponse = True
        readRetryTimes = readRetryTimes - 1
        time.sleep(0.1)
    return receiveResponse


def unsupportReceiveLoop(dataReceive, sensorID, typeID):
    unsupportReceivedResult = ""
    unsupportReceiveResponse = False
    unsupportRetryTimes = 50

    while unsupportRetryTimes > 0:
        unsupportReadLine = dataReceive.readOneLine()
        if not unsupportReadLine == None:
            unsupportByteArray = bytearray(unsupportReadLine)
            unsupportReceivedResult = unsupportByteArray.decode("utf-8")
            if (
                sensorID in unsupportReceivedResult
                and typeID not in unsupportReceivedResult
            ):
                unsupportReceiveResponse = True
        unsupportRetryTimes = unsupportRetryTimes - 1
        time.sleep(0.1)
    return unsupportReceiveResponse


def sendNotConnection(dataSending):
    if not dataSending.isConnected():
        print("Transmitter connection drop.")
        outputFile.write("Transmitter connection drop.\n")
        return True


def receiveNotConnection(dataReceive):
    if not dataReceive.isConnected():
        print("Receiver connection drop.")
        outputFile.write("Receiver connection drop.\n")
        return True


def clearReceiveBuffer(dataReceive):
    dataReceive.inputBufferClear()
    dataReceive.outputBufferClear()


def buildSupportStringCmd(supportCommand):
    finalCmdList = []
    if isinstance(supportCommand, list) == True:
        for command in supportCommand:
            if "-" in command:  # If the string in the list contains "-"
                parts = command.split("-")
                start = parts[0]
                end = parts[1]
                if len(start) < 2 or len(end) < 2:
                    raise ValueError("You should enter at less two digits.")
                if (
                    int(start, 16) > configValues.maxValue
                    or int(end, 16) > configValues.maxValue
                ):
                    raise ValueError(
                        "Support command range should be within [0, maxValue(Hex)]."
                    )
                if int(start, 16) >= int(end, 16):
                    raise ValueError("You enter wrong format.")
                finalCmdList.extend(
                    [format(i, "02x") for i in range(int(start, 16), int(end, 16) + 1)]
                )
            else:
                if len(command) < 2:
                    raise ValueError("You should enter at less two digits.")
                if int(command, 16) > configValues.maxValue:
                    raise ValueError(
                        "Support command should be within [0, maxValue(Hex)]."
                    )
                finalCmdList.append(format(int(command, 16), "02x"))
    return finalCmdList


def checkSupportCommand(
    configValues, dataSending, dataReceive, supportStringCommand, outputFile
):
    latestSuccessCommand = ""
    for i in range(0, len(supportStringCommand)):
        if sendNotConnection(dataSending) and receiveNotConnection(dataReceive):
            break
        if dataReceive.bufferHasData():
            clearReceiveBuffer(dataReceive)

        combinedString = configValues.originString + supportStringCommand[i]
        for k in range(configValues.repeatTime):
            dataSending.dataSend(combinedString)
            time.sleep(0.1)

        dataReceive.receive()
        dataSending.inputBufferClear()
        firstCheck = receiveLoop(
            dataReceive, configValues.sensorID, configValues.typeID
        )
        # if receiver return data
        if firstCheck == True:
            print(f"{combinedString} Pass")
            outputFile.write(f"{combinedString} Pass\n")
            latestSuccessCommand = combinedString
        # if receiver doesn't return data
        else:
            # Resend (repeatTime) times to confirm if the instructions are correct.
            for j in range(configValues.repeatTime):
                if sendNotConnection(dataSending) and receiveNotConnection(dataReceive):
                    break
                if dataReceive.bufferHasData():
                    clearReceiveBuffer(dataReceive)

                for k in range(configValues.repeatTime):
                    dataSending.dataSend(combinedString)
                    time.sleep(0.1)

                dataReceive.receive()
                dataSending.inputBufferClear()
                doubleCheck = receiveLoop(
                    dataReceive, configValues.sensorID, configValues.typeID
                )
                # If there is a response after the resend
                if doubleCheck == True:
                    print(f"{combinedString} Pass")
                    outputFile.write(f"{combinedString} Pass\n")
                    latestSuccessCommand = combinedString
                    clearReceiveBuffer(dataReceive)
                    break
                # If there is no response after the resend
                else:
                    print(f"{combinedString} Failed, no response receive.")
                    outputFile.write(f"{combinedString} Failed, no response receive.\n")
                    break
    return latestSuccessCommand


def checkUnsupportCommand(
    configValues,
    dataSending,
    dataReceive,
    supportStringCommand,
    successCommand,
    outputFile,
):
    unsupportStringCommand = []
    if successCommand == "":
        # no success command before, no need to continue...
        return

    for i in range(0, configValues.maxValue + 1):
        intToHex = format(i, "02x")
        if intToHex not in supportStringCommand:
            unsupportStringCommand.append(intToHex)

    for i in range(0, len(unsupportStringCommand)):
        if sendNotConnection(dataSending) and receiveNotConnection(dataReceive):
            break
        if dataReceive.bufferHasData():
            clearReceiveBuffer(dataReceive)

        unsupportCombinedString = configValues.originString + unsupportStringCommand[i]
        for k in range(configValues.repeatTime):
            dataSending.dataSend(unsupportCombinedString)
            time.sleep(0.1)

        dataReceive.receive()
        dataSending.inputBufferClear()
        unsupportCheck = unsupportReceiveLoop(
            dataReceive, configValues.sensorID, configValues.typeID
        )
        # has reaction
        if unsupportCheck == True:
            print(f"{unsupportCombinedString} has vulnerability.")
            outputFile.write(f"{unsupportCombinedString} has vulnerability.\n")
            clearReceiveBuffer(dataReceive)
        # no reaction
        else:
            # Use support command to check whether systom has problem or not.
            for j in range(configValues.repeatTime):
                if sendNotConnection(dataSending) and receiveNotConnection(dataReceive):
                    break
                for k in range(configValues.repeatTime):
                    dataSending.dataSend(successCommand)
                    time.sleep(0.1)

                dataReceive.receive()
                dataSending.inputBufferClear()
                unsupportDoubleCheck = unsupportReceiveLoop(
                    dataReceive, configValues.sensorID, configValues.typeID
                )
                # If there is a response to the support command input, it means the system is no problem. Confirm that the unSupportCombinedString[i] is indeed invalid.
                if unsupportDoubleCheck == True:
                    print(f"{unsupportCombinedString} Pass, System Alive.")
                    outputFile.write(f"{unsupportCombinedString} Pass, System Alive.\n")
                    clearReceiveBuffer(dataReceive)
                    break
                # If there is no response after inputting the support command for (repeatTime) times, then it is considered that the system may has problem.
                else:
                    print(f"System Crash.")
                    outputFile.write(f"System Crash.\n")
                    break


if __name__ == "__main__":
    with open("output.txt", "w") as outputFile:
        dataSending = None
        dataReceive = None
        successCommand = ""  # store successful trigger command
        supportStringCommand = []
        configValues = configContent()

        readConfig(configValues)

        if not isinstance(configValues.originString, str):
            raise ValueError("wrong preamble value.")
        if not isinstance(configValues.maxValue, int) or configValues.maxValue > 65535:
            raise ValueError("maxValue should be an integer in the range [0, 65535].")
        if (
            not isinstance(configValues.repeatTime, int)
            or configValues.repeatTime > 100
        ):
            raise ValueError("repeatTime should be an integer less than 100.")
        if not isinstance(configValues.supportCommand, list):
            raise ValueError("illegal configure file.")
        if not isinstance(configValues.sensorID, str):
            raise ValueError("sensorID should be a string.")

        dataSending, dataReceive = openComPort()

        dataSending.connect()
        dataReceive.connect()
        if not dataReceive.isConnected():
            raise ConnectionRefusedError("The receiver can not be connected.")
        if not dataSending.isConnected():
            raise ConnectionRefusedError("Transmitter can not be connected.")

        # part of support Command
        print("[Start of Supported Commands]\n")
        outputFile.write("[Start of Supported Commands]\n")
        outputFile.write("\n")

        if len(configValues.supportCommand) > 0:
            supportStringCommand = buildSupportStringCmd(configValues.supportCommand)

            successCommand = checkSupportCommand(
                configValues, dataSending, dataReceive, supportStringCommand, outputFile
            )

            # part of unSupport Command
            print("\n")
            print("[Start of Unsupported Commands]\n")
            outputFile.write("\n")
            outputFile.write("[Start of Unsupported Commands]\n")

            checkUnsupportCommand(
                configValues,
                dataSending,
                dataReceive,
                supportStringCommand,
                successCommand,
                outputFile,
            )
        else:
            print("Supported Commands should not empty.")
            outputFile.write("Supported Commands should not empty.\n")
            outputFile.write("\n")

        dataSending.disconnect()
        dataReceive.disconnect()
