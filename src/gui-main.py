#!/usr/bin/python3

import os
import sys
import time
import customtkinter as ctk
from subprocess import getoutput as terminal
from _thread import start_new_thread
import tempfile

class Configuration:
    def __init__(self):
        pass

    def loadCurrentConfiguration(self):
        with open('/etc/amd-gpu-fan/conf.txt', 'r') as confPath:
            currentConfFile = confPath.read().strip()

        with open(f'/etc/amd-gpu-fan/conf/{currentConfFile}', 'r') as configuration:
            config = configuration.read()

        for line in config.split('\n'):
            if 'low-temp' in line:
                self.lowTemp = line.split(' ')[1]

            elif 'mid-temp' in line:
                self.midTemp = line.split(' ')[1]

            elif 'high-temp' in line:
                self.highTemp = line.split(' ')[1]

            elif 'low-speed' in line:
                self.lowSpeed = line.split(' ')[1]

            elif 'mid-speed' in line:
                self.midSpeed = line.split(' ')[1]

            elif 'high-speed' in line:
                self.highSpeed = line.split(' ')[1]

    def applyCurrentConfiguration(self):
        tempFile = tempfile.mktemp(prefix='agf-gui', suffix='.sh')

        with open(tempFile,'w') as file:
            file.write(
                f'''#!/bin/bash
echo "low-speed {int(self.lowSpeed * 5300)}\nmid-speed {int(self.midSpeed * 5300)}\nhigh-speed {int(self.highSpeed * 5300)}\nlow-temp {int(self.lowTemp * 100)}\nmid-temp {int(self.midTemp * 100)}\nhigh-temp {int(self.highTemp * 100)}" > /etc/amd-gpu-fan/conf/custom.conf
echo "custom.conf" > /etc/amd-gpu-fan/conf.txt
systemctl daemon-reload
systemctl restart amd-gpu-fan.service
'''
            )

        os.system(f'pkexec sudo /bin/sh {tempFile}')

class Slider(ctk.CTkFrame):
    def __init__(self, master, labelText, min, max, unit=''):
        super().__init__(master, fg_color='transparent')

        self.min = min
        self.max = max
        self.unit = unit

        self.label = ctk.CTkLabel(self, text=labelText)
        self.label.pack(padx=10)

        self.slider = ctk.CTkSlider(self, width=20, height=300, command=self.__updateLabel__, orientation='vertical')
        self.slider.configure(number_of_steps=self.max - self.min)

        self.slider.set(0)
        self.slider.pack()

        self.value = ctk.CTkLabel(self, text='0')
        self.value.pack()

    def __updateLabel__(self, *args):
        value = self.slider.get() * (self.max - self.min) + self.min
        self.value.configure(text=str(int(value)) + self.unit)

    def set(self, value):
        self.slider.set(int(value) / (self.max - self.min))
        self.__updateLabel__()

    def get(self):
        return self.slider.get()

class ProgressBar(ctk.CTkFrame):
    def __init__(self, master, text, min, max, unit=''):
        super().__init__(master, fg_color='transparent')

        self.min = min
        self.max = max
        self.unit = unit

        self.label = ctk.CTkLabel(self, text=text)
        self.label.pack(pady=5)

        self.progress = ctk.CTkProgressBar(self, width=400, height=10)
        self.progress.pack(pady=5)

        self.value = ctk.CTkLabel(self, text=0)
        self.value.pack(pady=5)

    def set(self, value):
        self.value.configure(text=str(value) + self.unit)
        self.progress.set(float(value) / (self.max - self.min))

class Interface:
    def __init__(self):
        self.configuration = Configuration()
        self.configuration.loadCurrentConfiguration()

        self.minRpm = int(terminal('cat /sys/class/drm/card0/device/hwmon/hwmon1/fan1_min'))
        self.maxRpm = int(terminal('cat /sys/class/drm/card0/device/hwmon/hwmon1/fan1_max'))

        self.do = True

        self.root = ctk.CTk()
        self.root.title('amd-gpu-fan GUI')
        self.mainFrame = ctk.CTkFrame(self.root)

        self.make()

        self.mainFrame.pack(padx=10, pady=10)
        self.root.mainloop()

    def make(self):
        self.topFrame = ctk.CTkFrame(self.mainFrame, fg_color='transparent')
        self.topFrame.pack(pady=10, padx=10)

        self.lowTempSlider = Slider(self.topFrame, 'Low Temp', 0, 100, ' C')
        self.lowTempSlider.grid(row=0, column=0)

        self.lowSpeedSlider = Slider(self.topFrame, 'Low Temp Speed', 0, self.maxRpm, ' rpm')
        self.lowSpeedSlider.grid(row=0, column=1)

        self.midTempSlider = Slider(self.topFrame, 'Mid Temp', 0, 100, ' C')
        self.midTempSlider.grid(row=0, column=2)

        self.midSpeedSlider = Slider(self.topFrame, 'Mid Temp Speed', 0, self.maxRpm, ' rpm')
        self.midSpeedSlider.grid(row=0, column=3)

        self.highTempSlider = Slider(self.topFrame, 'High Temp', 0, 100, ' C')
        self.highTempSlider.grid(row=0, column=4)

        self.highSpeedSlider = Slider(self.topFrame, 'High Temp Speed', 0, self.maxRpm, ' rpm')
        self.highSpeedSlider.grid(row=0, column=5)

        self.midFrame = ctk.CTkFrame(self.mainFrame, fg_color='transparent')
        self.midFrame.pack(padx=10, pady=10)

        self.currentTemp = ProgressBar(self.midFrame, 'Current temperature', 0, 100, ' C')
        self.currentTemp.pack()

        self.currentSpeed = ProgressBar(self.midFrame, 'Current speed', self.minRpm, self.maxRpm, ' rpm')
        self.currentSpeed.pack()

        self.lowFrame = ctk.CTkFrame(self.mainFrame)
        self.lowFrame.pack(pady=10, padx=10)

        self.loadButton = ctk.CTkButton(self.lowFrame, text='Load current configuration', command=self.loadConfiguration)
        self.loadButton.grid(row=0, column=0, padx=10, pady=10)

        self.loadStd = ctk.CTkButton(self.lowFrame, text='Load standard configuration', command=self.loadStdConf)
        self.loadStd.grid(row=0, column=1, padx=10, pady=10)

        self.loadTurbo = ctk.CTkButton(self.lowFrame, text='Load turbo configuration', command=self.loadTurboConf)
        self.loadTurbo.grid(row=0, column=2, padx=10, pady=10)

        self.saveButton = ctk.CTkButton(self.lowFrame, text='Save and apply configuration', command=self.save)
        self.saveButton.grid(row=0, column=3, padx=10, pady=10)

        start_new_thread(self.threadedLoop, ())

    def loadConfiguration(self):
        self.lowTempSlider.set(self.configuration.lowTemp)
        self.lowSpeedSlider.set(self.configuration.lowSpeed)

        self.midTempSlider.set(self.configuration.midTemp)
        self.midSpeedSlider.set(self.configuration.midSpeed)

        self.highTempSlider.set(self.configuration.highTemp)
        self.highSpeedSlider.set(self.configuration.highSpeed)

    def loadStdConf(self):
        self.lowTempSlider.set(40)
        self.lowSpeedSlider.set(1700)

        self.midTempSlider.set(55)
        self.midSpeedSlider.set(3000)

        self.highTempSlider.set(70)
        self.highSpeedSlider.set(5300)

    def loadTurboConf(self):
        self.lowTempSlider.set(10)
        self.lowSpeedSlider.set(5300)

        self.midTempSlider.set(20)
        self.midSpeedSlider.set(5300)

        self.highTempSlider.set(30)
        self.highSpeedSlider.set(5300)

    def threadedLoop(self):
        while self.do:
            rpm = terminal('cat /sys/class/drm/card0/device/hwmon/hwmon1/fan1_input')
            tmp = terminal('cat /sys/class/drm/card0/device/hwmon/hwmon1/temp1_input')

            self.currentTemp.set(int(tmp) / 1000)
            self.currentSpeed.set(int(rpm))

            time.sleep(1)

    def save(self):
        self.configuration.lowTemp = self.lowTempSlider.get()
        self.configuration.midTemp = self.midTempSlider.get()
        self.configuration.highTemp = self.highTempSlider.get()
        
        self.configuration.lowSpeed = self.lowSpeedSlider.get()
        self.configuration.midSpeed = self.midSpeedSlider.get()
        self.configuration.highSpeed = self.highSpeedSlider.get()

        self.configuration.applyCurrentConfiguration()

if __name__ == '__main__':
    try:
        Interface()
    except FileNotFoundError:
        print('Error: improper installation, configuration files not found', file=sys.stderr)
    except ValueError:
        print('Error: device\'s GPU drivers appear to not be compatible with the software', file=sys.stderr)
