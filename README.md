# autostopmarket
This python script will set up a stop market order on Binance Futures, to avoid paying liquidation fees.
You can also setup a fixed/percentage loss amount and it will create the stop market order for you.

# Install intructions:

requires Python 3+ and the following modules:

requests
websocket
apscheduler
rich (not essential, just some fancy console coloring)

If you are starting with a fresh python install, make sure to run "pip install requests" and "pip install websocket" and "pip install apscheduler" to get your python environment set up to run everything that this script asks for.

rename api_data_template.py to api_data.py and add you binance API key/secret inside the file.

Quick install video using Conda on osx (its similiar on win/linux): https://youtu.be/5Lxrox0wxbo 


# Demo video
https://youtu.be/x2ohPL17rn4
=======

Using the fixed/percentage options to limit losses:
https://youtu.be/GmjA9kaI2rA


If you like this and or it saved your bacon, feel free to contribute<br/>
btc: 1DN6jvGZbQkYT9RoCjCVzTs5MwC3xvdmMh<br/>
ltc: LTT8Gj8nnwBCEGAcapjfLy9EyZtiu6Ntqh
