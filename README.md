 pip install matplotlib
 pip install pylab
 pip install numpy
 sudo apt install libopenblas-dev
 pip install can
 python main.py
 
vi /boot/config.txt

add at the end : 

dtparam=spi=on
dtoverlay=mcp2515-can0,oscillator=16000000,interrupt=25
#dtoverlay=spi-bcm2835-overlay 
