# AMD-GPU-Fan controller
This tool provides a daemon, a CLI and a GUI, allowing the user to create and manage maps for GPU fans

### DISCLAIMER
This tool only works with AMD GPUs, and is developed for Linux\
Feel free to extend its function for other Operative Systems, and if you do, please patch your changes and submit them as commits

## Installation
Run the installation script as root
```commandline
sudo ./install.sh
```

## Usage
Both CLI and GUI allow to manage and create new configurations\
CLI usage is explained in the "help" section, just run `agf-cli --help`\
To create a new configuration you must specify all the needed elements, such as in the following example:
```commandline
agf-cli --mkconf low-temp=40,low-speed=1700,mid-temp=55,mid-speed=3000,high-temp=70,high-speed=5300
```

GUI is self-explaning, needs no guide.

