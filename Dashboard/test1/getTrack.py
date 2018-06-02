import os
import serial


# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
)
ser.isOpen()


def getTime(string,format,returnFormat):
        return time.strftime(returnFormat, time.strptime(string, format)) # Convert date and time to a nice printable format

        
def getLat(lines):
        latString = lines[3]
        lat = "0"
        if (len(latString) > 0 ):
               lat = latString[:2].lstrip('0') + "." + "%.7s" % str(float(latString[2:])*1.0/60.0).lstrip("0.")
        return(float(lat))

def getLng(lines):
        lngString = lines[5]
        lng = "0"
        #print(lngString[3:])
        if (len(lngString) > 0 ):
               lng = float(lngString[:3]) + float(lngString[3:])/60
        return(float(lng))

def decode(lines):
        #print("Time:", lines[1][0:2]+":"+lines[1][2:4]+":"+lines[1][4:6])
        #print("Status (A=OK,V=KO):", lines[2])
        latlng = getLatLng(lines[3],lines[5])
        #print("Lat,Long: ", latlng[0], lines[4], ", ", latlng[1], lines[6])
        #print("Speed (knots):", lines[7])

def getGpsTime(lines):
        return(lines[1][0:2]+":"+lines[1][2:4]+":"+lines[1][4:6])
        
def getGpsSpeed(lines):
		  ch = lines[7]
		  if ( ch == ''):
		  	   ch = '0'
		  km = float(ch)*1.852	   
		  return(int(km))


def checksum(line):
   checkString = line.partition("*")
   checksum = 0
   for c in checkString[0]:
      checksum ^= ord(c)

   try: # Just to make sure
      inputChecksum = int(checkString[2].rstrip(), 16);
   except:
      #print("Error in string")
      return False
	
   if checksum == inputChecksum:
	   return True
   else:
      #print(hex(checksum), "!=", hex(inputChecksum))
      return False

def readString():
        while 1:
                while ser.read().decode("utf-8") != '$': # Wait for the begging of the string
                      pass # Do nothing
                line = ser.readline().decode("utf-8") # Read the entire string
                return line             

          
class GpsPoint():
	
    latitude = 0
    longitude = 0
	
    def gpsPrint(self):
       print("pos:", self.latitude, self.longitude)	
	
    def __init__(self, Lat=0, Long=0):	
        self.latitude = Lat
        self.longitude = Long
        	
    def GpsPoint():
        latitude = 0.0
        longitude = 0.0
	   
    def GpsSetPoint(self, Lat, Long):
        latitude = Lat
        longitude = Long
        #print("set", Lat, Long)

           
class Track():
	 
	 
    finishLinePoint1 = GpsPoint(43.711176, 4.0112896)
    finishLinePoint2 = GpsPoint(43.7111471,4.0023978)
    
    start = GpsPoint()
    finish = GpsPoint()
    
    def printline(self):
      print("line:", self.finishLinePoint1.gpsPrint(), self.finishLinePoint2.gpsPrint())
       
    
    def readGPRMC(self):
      while 1:
         line = readString()
         #print(line)
         lines = line.split(",")
         #print(lines)
         if lines[0] == "GPRMC":
            return lines

    def isFinishLinePassed(self):

        start = self.start
        finish = self.finish
        #print(self.finishLinePoint1.latitude,self.finishLinePoint2.latitude,finish.longitude,start.longitude)
        delta0 = (self.finishLinePoint1.latitude - self.finishLinePoint2.latitude) * (finish.longitude - start.longitude)
        delta0 = delta0 -(self.finishLinePoint1.longitude - self.finishLinePoint2.longitude) * (finish.latitude - start.latitude)
        if (delta0 == 0.0 ):
             return(0)
        delta1 = (self.finishLinePoint1.longitude - self.finishLinePoint2.longitude) * (start.latitude - self.finishLinePoint2.latitude)
        delta1 = delta1 -(self.finishLinePoint1.latitude - self.finishLinePoint2.latitude) * (start.longitude - self.finishLinePoint2.longitude)	
        delta2 = (finish.longitude - start.longitude) * (start.latitude - self.finishLinePoint2.latitude)
        delta2 = delta2 -(finish.latitude - start.latitude) * (start.longitude - self.finishLinePoint2.longitude)

        ka = delta1/delta0
        kb = delta2/delta0
		
        if (ka < 0 or ka > 1 or kb < 0 or kb > 1):
      	  return(0)
      
        Long = start.longitude + ka * (finish.longitude - start.longitude)
        Lat = start.latitude + ka * (finish.latitude - start.latitude)

        intersection = GpsPoint(Lat, Long);
        return(1)         
		  

def firstPoint(lines):
   #print(lines)
   Lat = getLat(lines)
   #print(Lat)
   Long = getLng(lines)
   #print(Long)
   start = GpsPoint(Lat, Long)
   return start  
   
	  
myTrack = Track()
#myTrack.start = GpsPoint(0,0) 
start = GpsPoint(0,0)
    
      

lines = myTrack.readGPRMC()
myTrack.start = firstPoint(lines)

pLine = 0
while (pLine == 0 ):
   lines = myTrack.readGPRMC()
   print(lines)
                                                   
        
