# Instruction Parameters Overview

## Getting started
This document outlines the parameters used in the code for proper configuration and utilization of the program. Please read through the following details to ensure accurate parameter settings.

### Structure of Experiment
![image](https://github.com/user-attachments/assets/3dea517f-845f-4f38-a40d-4e11938ef349)
### Fuzzed Data Set
* LF Trigger Commands
  * MLF [01, 03, 05, 06, 07, 09, 10, 12, 13, 14, 17, 20]
    * MLF 01: 0x25 0x7F 0x80 0x05 **0x01** -> 257F800501
    * MLF 03: 0x25 0x7F 0x80 0x05 **0x03** -> 257F800503
* Unsupported LF Trigger Commands
  * 0x00~0xFF, except MLF
    * 0x25 0x7f 0x80 0x05 **0x00** -> 257F800500
    * 0x25 0x7f 0x80 0x05 **0xFF** -> 257F8005FF
### Parameter members
* max  
**Type**: Integer  
**Range**: 0 to 65535  
**Description**: Represents the maximum value supported. Ensure it does not exceed 65535.  
* supportCommand  
**Type**: Array of Strings  
**Description**: Defines the supported set of commands. Must be in string format, and if there are consecutive numbers exceeding 3, it is recommended to use "-" to denote the range.  
* originString  
**Type**: String  
**Description**: The preamble of the command, must be in string format. Used to identify the start of a command.  
* repeatTime  
**Type**: Integer  
**Description**: The number of times the command should be repeated. Ensure setting a correct integer value.  
* sensorID  
**Type**: String  
**Description**: Represents the ID of the sensor. Please use string format.  
* typeID  
**Type**: String  
**Description**: Another type of ID. Please use string format.  

### Example
{  
  "max": 65535,  
  "supportCommand": ["01", "03"],  
  "originString": "257f8005",  
  "repeatTime": 30,  
  "sensorID": "AAAAAAAA",  
  "typeID": "T=-50"  
}  
  
Adjust the values and configurations of the parameters according to your specific requirements.
