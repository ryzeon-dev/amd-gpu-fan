#!/usr/bin/python3
import sys
import time
import os
import json

baseDir = '/etc/amd-gpu-fan'
hwmonDir = '/sys/class/drm/card0/device/hwmon/'
hwmonDir += os.listdir(hwmonDir)[0]

def getConf():
    with open(f'{baseDir}/conf.txt', 'r') as file:
        confName = file.read().strip()

    with open(f'{baseDir}/conf/{confName}', 'r') as conf:
        config = json.load(conf)

    low = config.get('temp').get('low')
    mid = config.get('temp').get('mid')
    high = config.get('temp').get('high')

    lowSpeed = config.get('speed').get('low')
    midSpeed = config.get('speed').get('mid')
    highSpeed = config.get('speed').get('high')

    performanceMode = config.get('performance')

    return low, mid, high, lowSpeed, midSpeed, highSpeed, performanceMode

def gpuTemp():
    with open(f'{hwmonDir}/temp1_input', 'r') as tempFile:
        return int(tempFile.read()) / 1000

def enableFanControl():
    os.system(f'echo 2 > {hwmonDir}/pwm1_enable')
    os.system(f'echo 1 > {hwmonDir}/fan1_enable')

def setSpeed(speed):
    os.system(f'echo {speed} > {hwmonDir}/fan1_target')

def setPerformance(mode):
    os.system(f'echo {mode} > /sys/class/drm/card0/device/power_dpm_force_performance_level')

def fix(temperature, minTemp, maxTemp, minSpeed, maxSpeed):
    return (temperature - minTemp) * (maxSpeed - minSpeed) / (maxTemp - minTemp) + minSpeed

if __name__ == '__main__':
    conf = getConf()
    if None in conf:
        print('Error: unvalid configuration file', file=sys.stderr)
        sys.exit(0)

    low, mid, high, lowSpeed, midSpeed, highSpeed, performanceMode = conf
    enableFanControl()

    while True:
        temperature = gpuTemp()

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

        setPerformance(performanceMode)
        time.sleep(2)