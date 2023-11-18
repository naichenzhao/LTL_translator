# State class for the gcode translator
#   I am using this as a better way of keeping track of the previous state
#   Hopefully this make the code make more sense
class State:

    def __init__(self):
        # Set state location
        self.point = {'X':0, 'Y':0, 'Z':0}
        
        # Set enifactor atributes
        self.tool = 0
        self.run = 0
    
    def __str__(self):
        return "Current position X:{0}, Y:{1}, Z:{2}, \nToolstate tool:{3}, running:{4}".format(self.point['X'], self.point['Y'], self.point['Z'], self.tool, self.run)
    
    
    def home(self):
        self.point['X'] = 0
        self.point['Y'] = 0
        self.point['Z'] = 0
        
        

    