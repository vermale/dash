class CanProtocol:
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
                
        
        
        