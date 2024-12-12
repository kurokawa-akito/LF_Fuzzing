# Instruction Parameters Overview

## Getting started

This document outlines the parameters used in the code for proper configuration and utilization of the program. Please read through the following details to ensure accurate parameter settings.

### Parameter members

1. max
Type: Integer
Range: 0 to 65535
Description: Represents the maximum value supported. Ensure it does not exceed 65535.
2. supportCommand
Type: Array of Strings
Description: Defines the supported set of commands. Must be in string format, and if there are consecutive numbers exceeding 3, it is recommended to use "-" to denote the range.
3. originString
Type: String
Description: The preamble of the command, must be in string format. Used to identify the start of a command.
4. repeatTime
Type: Integer
Description: The number of times the command should be repeated. Ensure setting a correct integer value.
5. sensorID
Type: String
Description: Represents the ID of the sensor. Please use string format.
6. typeID
Type: String
Description: Another type of ID. Please use string format.

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
