# emteq-LSL-client

![image](https://github.com/emteqlabs/emteq-LSL-client/assets/40773550/69476a89-fa54-4bd3-82be-f8b8bbf3e8a7)


This is simple LabStreamingLayer client app with multi device receiving capabilities, realtime plotting and saving data into CSV files.

## Features

- multidevice realtime receiving
- realtime plotting
- recording timestamped data to LSL
## How to use

requirements:
- python

### 1. Install prerequisites

`python -m pip install -r requirements.txt`

for linux you need to install lsl with conda:

`conda install -c conda-forge liblsl`

### 2. Run main.py

`python ./src/main.py`

### [Optional] run test LSL device

`python ./tester/example.py`
