# Arduino Light Monitoring System

A light monitoring and alarm system built using an **Arduino**, a **photoresistor (LDR)**, and a **Python application** communicating through Serial.

The project was created as an exercise in combining embedded programming with a higher-level Python application. The Arduino is responsible for sensor acquisition and hardware control, while Python handles communication, data collection, logging, statistics, and system control.

## Overview

The system continuously measures ambient light using a photoresistor connected to the Arduino.

A Python application communicates with the Arduino over USB Serial using a simple custom command protocol.

The user can:

- Start and stop continuous light monitoring
- Request a single light measurement
- Change the measurement rate at runtime
- Automatically control an alarm LED based on a light threshold
- Log measurements to a file
- Calculate statistics for a monitoring session

The communication is bidirectional:

```text
                USB Serial

Python  -------------------------->  Arduino
        START / STOP / GET
        RATE X / ALARM ON/OFF

Python  <--------------------------  Arduino
             LIGHT:value
```

## Hardware

The project uses components from the Arduino Starter Kit:

- Arduino board
- Photoresistor (LDR)
- LED
- Resistors
- Breadboard
- Jumper wires
- USB connection to the computer

## Architecture

The project separates responsibilities between the Arduino and the Python application.

### Arduino

The Arduino is responsible for:

- Reading the photoresistor
- Controlling the sampling interval
- Streaming measurements over Serial
- Parsing commands received from Python
- Controlling the alarm LED

### Python

The Python application is responsible for:

- Sending commands to the Arduino
- Receiving measurements
- Running Serial communication asynchronously
- Logging measurements
- Keeping timestamps
- Detecting low-light conditions
- Sending alarm commands back to the Arduino
- Calculating session statistics

## Serial Protocol

Communication uses a simple text-based protocol.

### Python → Arduino

| Command | Description |
|---|---|
| `START` | Start continuous measurement streaming |
| `STOP` | Stop continuous measurement streaming |
| `GET` | Request a single measurement |
| `RATE X` | Set the measurement interval to X milliseconds |
| `ALARM ON` | Turn the alarm LED on |
| `ALARM OFF` | Turn the alarm LED off |

Example:

```text
START
RATE 500
STOP
GET
```

### Arduino → Python

Measurements are transmitted using:

```text
LIGHT:<value>
```

For example:

```text
LIGHT:724
LIGHT:718
LIGHT:695
```

This makes the Serial data easy to parse on the Python side.

## Non-Blocking Arduino Sampling

Continuous measurements are scheduled using `millis()` instead of `delay()`.

Conceptually:

```cpp
if (millis() > lastMeasurement + RATE) {
    // Take measurement
}
```

This allows the Arduino to continue processing incoming Serial commands while waiting for the next measurement.

Using `delay(RATE)` would block execution and make the Arduino less responsive to commands such as `STOP` or `RATE`.

## Asynchronous Python Application

The Python application uses `asyncio` so that user input and Serial communication can be handled concurrently.

The Serial reading operation is blocking, so it is executed using:

```python
await asyncio.to_thread(arduino.readline)
```

Continuous monitoring runs as a separate task:

```python
arduino_task = asyncio.create_task(
    streaming_data(arduino)
)
```

This allows the main application to continue accepting commands while measurements are received in the background.

When monitoring is stopped, the streaming task can be cancelled.

## Data Logging

Measurements are stored together with their timestamps:

```text
<light_value>-<timestamp>
```

Example:

```text
724-1788512032.42
718-1788512032.53
695-1788512032.64
```

Measurements are periodically flushed to the file while the monitoring session is running.

## Alarm System

Python compares incoming measurements against a configurable threshold:

```python
THRESHOLD = 300
```

When the light value falls below the threshold, Python sends:

```text
ALARM ON
```

When the light level returns above the threshold:

```text
ALARM OFF
```

The Arduino receives the command and controls the physical LED.

This creates bidirectional communication:

```text
LDR
 │
 ▼
Arduino
 │
 │ LIGHT:250
 ▼
Python
 │
 │ value < threshold
 │
 │ ALARM ON
 ▼
Arduino
 │
 ▼
LED ON
```

## Session Statistics

Measurements are stored in Python during a monitoring session.

When the session ends, the application calculates:

- Session duration
- Number of samples
- Minimum light value
- Maximum light value
- Average light value
- Total time spent below the light threshold

Example output:

```text
----- SESSION RESULTS -----
Duration:        32.41
Samples:         324
Minimum light:   183
Maximum light:   891
Average light:   537.24
Low light time:  4.81
---------------------------
```

## Running the Project

### Requirements

Python 3 and `pyserial` are required.

Install pySerial with:

```bash
pip install pyserial
```

### Arduino

Upload the Arduino sketch to the board and connect the photoresistor and LED.

### Python

Set the correct Serial port:

```python
arduino = serial.Serial(
    "COM5",
    baudrate=9600,
    timeout=5
)
```

Then run:

```bash
python main.py
```

Available commands:

```text
START
STOP
GET
RATE <milliseconds>
```

## Concepts Practiced

This project was primarily created as a learning exercise and covers:

- Arduino analog input
- Photoresistors and voltage measurement
- Serial/UART communication
- Bidirectional communication
- Custom text-based communication protocols
- Command parsing in C/C++
- C-style strings and `strcmp`
- Runtime configuration
- Non-blocking timing with `millis()`
- Python `pyserial`
- Python `asyncio`
- Blocking vs asynchronous operations
- `asyncio.create_task()`
- `asyncio.to_thread()`
- File I/O and buffering
- Sensor data logging
- Timestamp-based statistics
- Separation of hardware acquisition and application logic

## Project Structure

A possible repository structure is:

```text
photoresistor-monitor/
│
├── arduino/
│   └── photoresistor_monitor.ino
│
├── python/
│   └── main.py
│
├── README.md
└── .gitignore
```

Generated statistics/log files can be excluded from Git using `.gitignore` if they are only runtime data.

## Possible Future Improvements

Possible extensions include:

- Real-time visualization with Matplotlib
- Configurable alarm thresholds
- More robust Serial message parsing
- CSV-based data logging
- Multiple sensors
- Persistent configuration
- A graphical user interface
- Wi-Fi communication instead of USB Serial

## Purpose

The main goal of this project was to move beyond using `Serial.println()` only for debugging and instead use Serial as a real communication interface between an embedded device and a Python application.

The resulting system demonstrates a simple architecture where the Arduino handles real-world sensor acquisition and hardware control, while Python provides higher-level control, data processing, logging, and analysis.