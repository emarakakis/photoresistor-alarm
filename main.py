import serial
import time
import asyncio
import re
import os

RATE = 100
THRESHOLD = 300
START_TIME = 0

alarm_on = False

statistics_file_name = "statistics.txt"

photo_values = []
photo_time = []

arduino_task = None

def statistics():
    max_val = max(photo_values)
    min_val = min(photo_values)
    samples = len(photo_values)
    avg_val = sum(photo_values) / samples
    
    low_light_time = 0
    
    last_iter_time = START_TIME
    for val, t in zip(photo_values, photo_time):
        if val < THRESHOLD:
            low_light_time += t - last_iter_time
            
        last_iter_time = t

    print("\n----- SESSION RESULTS -----")
    print(f"Duration:       {time.time() - START_TIME:.2f}")
    print(f"Samples:        {samples}")
    print(f"Minimum light:  {min_val}")
    print(f"Maximum light:  {max_val}")
    print(f"Average light:  {avg_val:.2f}")
    print(f"Low light time:  {low_light_time:.2f}")
    print("---------------------------\n")
        
    


def manipulate_led(arduino: serial.Serial,switch: bool):
    arduino.write(f"ALARM {"ON" if switch else "OFF"}\n".encode())

def set_streaming(arduino: serial.Serial, switch: bool):
    arduino.write(f"{"START" if switch else "STOP"}\n".encode())
    
async def single_stream(arduino: serial.Serial)->int:
    line = await asyncio.to_thread(arduino.readline)
    line = line.decode().strip()
    if not any(c == ":" for c in line):
        print("Skipping")
        return None
    
    print(line)
    
    light_value = int(line.split(':')[1])
    timestamp = time.time()
    photo_values.append(light_value)
    photo_time.append(timestamp)
    
    return light_value, timestamp

async def get_stream(arduino: serial.Serial):
    with open(statistics_file_name, "a") as file:
        result = await single_stream(arduino=arduino)
        
        if result is None:
            print("Something aint right")
            return
        
        light_value, timestamp = result
        file.write(f"{light_value}-{timestamp}\n")
    
    file.close()
    
async def streaming_data(arduino: serial.Serial):
    global alarm_on
    print("Controlling arduino")
    last_flash = 0
    index = 0
    with open(statistics_file_name, "a") as file:
        while(True):
            
            result = await single_stream(arduino=arduino)
                
            if result is None:
                continue
            
            light_value, timestamp = result
            file.write(f"{light_value}-{timestamp}\n")
            
            tmp_alarm = light_value < THRESHOLD
            
            if tmp_alarm != alarm_on:
                alarm_on = tmp_alarm
                manipulate_led(arduino=arduino, switch=alarm_on)
                
                        
            index += 1
            
            if last_flash + 5 <= index:
                file.flush()
                last_flash = index
    
def set_rate(arduino: serial.Serial, rate_string: str):
    arduino.write(f"{rate_string}\n".encode())
    
async def main():
    global START_TIME
    arduino = serial.Serial("COM5", baudrate=9600, timeout = 5)
    if os.path.exists(statistics_file_name):
        os.remove(statistics_file_name)
    while True:
        print("Enter your command from START, STOP, GET, RATE X")
        command = await asyncio.to_thread(input, "> ")
        
        match command:
            case "START":
                START_TIME = time.time()
                set_streaming(arduino=arduino, switch=True)
                arduino_task = asyncio.create_task(streaming_data(arduino=arduino))
            case "STOP":
                set_streaming(arduino=arduino, switch=False)
                arduino_task.cancel()
                statistics()
            case "GET":
                arduino.write(b"GET\n")
                await get_stream(arduino=arduino)
                
                                
            case _ if re.fullmatch("RATE [0-9]+", command):
                set_rate(arduino=arduino, rate_string=command)
                
if __name__ == "__main__":
    asyncio.run(main())