class CanData:
            can_id = ''
            Name =''
            Description =''
            Units = 'Deg'
            DataType = ''
            Start = 0
            End = 1
            Freq = 0
            MinVal = 0
            ValueMin = 0
            MaxVal = 255
            ValueMax = 150        

            def __init__(self, can_id, Name, Description, Units, DataType, Start, End, Freq, MinVal, ValueMin, MaxVal, ValueMax):
                self.can_id = can_id
                self.Name = Name
                self.Description = Description
                self.Units = Units
                self.DataType = DataType
                self.Start = Start
                self.End = End 
                self.Freq = Freq 
                self.MinVal = MinVal 
                self.ValueMin = ValueMin
                self.MaxVal = MaxVal 
                self.ValueMax = ValueMax
                

class CanTool:
    
            CanTab = {}
            Temp = 0
            Volt = 0
            Map = 0
            Lambda1 = 0
            Lambda2 = 0
            
            
            def __init__ (self):
                self.CanTab.update({'TH2o': CanData('30B','TH2o', 'Coolant Temperature', 'DegC', 'uchar', 0, 1, 6, 0, 10, 255, 150 )})
                self.CanTab.update({'VBATT': CanData('308','VBATT', 'Battery Voltage', 'Volt', 'ushort', 0, 2, 12, 0, 0, 1023, 16 )})
                self.CanTab.update({'MAP': CanData('300','MAP', 'Manifold Air Pressure', 'mBar', 'ushort', 4, 2, 50, 0, 0, 1000, 1000 )})
                self.CanTab.update({'Lambda1': CanData('305','Lambda1', 'Actual Measure Lambda Bank1', '', 'uchar', 0, 1, 25, 0, 0, 255, 2 )})
                self.CanTab.update({'Lambda2': CanData('301','Lambda2', 'Actual Measure Lambda Bank2', '', 'uchar', 2, 1, 25, 0, 0, 255, 2 )})
                
            def decode(self, canid, data):
                if ( canid == '300' ):
                    Map = int(data[4])*256+int(data[5])
                if ( canid == '301' ):
                    Lambda2 = (int(data[2])*2)/255
                if ( canid == '305' ):
                    Lambda1=  (int(data[0])*2)/255
                if ( canid == '308'):
                    Volt = ((int(data[0])*256+int(data[1]))*18)/1023
                if ( canid == '30B '):
                    Temp = (int(data[0])*140)/255+10
                    
                    
                
        