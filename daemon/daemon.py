#!/usr/bin/python3

import time
import os

baseDir = '/etc/amd-gpu-fan'

def getConf():
    with open(f'{baseDir}/conf.txt', 'r') as file:
        confName = file.read().strip()

    with open(f'{baseDir}/conf/{confName}', 'r') as conf:
        config = conf.read()

    config = config.split('\n')
    low = None
    mid = None
    high = None

    lowSpeed = None
    midSpeed = None
    highSpeed = None
    
    for line in config:
        if 'low-temp' in line:
            low = int(float(line.split(' ')[1]))

        elif 'mid-temp' in line:
            mid = int(float(line.split(' ')[1]))

        elif 'high-temp' in line:
            high = int(float(line.split(' ')[1]))

        elif 'low-speed' in line:
            lowSpeed = int(float(line.split(' ')[1]))

        elif 'mid-speed' in line:
            midSpeed = int(float(line.split(' ')[1]))

        elif 'high-speed' in line:
            highSpeed = int(float(line.split(' ')[1]))

    return low, mid, high, lowSpeed, midSpeed, highSpeed

def gpuTemp():
    with open('/sys/class/drm/card0/device/hwmon/hwmon1/temp1_input', 'r') as tempFile:
        return int(tempFile.read()) / 1000

def enablePWM():
    os.system('echo 1 > /sys/class/drm/card0/device/hwmon/hwmon1/pwm1_enable')

def setSpeed(speed):
    os.system(f'echo {speed} > /sys/class/drm/card0/device/hwmon/hwmon1/fan1_target')

def fix(value, inMin, inMax, outMin, outMax):
    return (value - inMin) * (outMax - outMin) / (inMax - inMin) + outMin

if __name__ == '__main__':
    low, mid, high, lowSpeed, midSpeed, highSpeed = getConf()
    
    while True:
        temperature = gpuTemp()
        enablePWM()

        if temperature < low:
            setSpeed(lowSpeed)

        elif temperature >= low and temperature < mid:
            speed = fix(temperature, low, mid, lowSpeed, midSpeed)
            setSpeed(speed)

        elif temperature >= mid and temperature < high:
            speed = fix(temperature, mid, high, midSpeed, highSpeed)
            setSpeed(speed)

        else:
            setSpeed(highSpeed)

        time.sleep(2)