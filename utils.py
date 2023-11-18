'''
    +------------------------------------------------------+
    |                                                      |
    |       Functions for interpreting commands            |
    |                                                      |
    +------------------------------------------------------+
'''

# Function for formatting a Gx command for 2PP
# G0 --> Movement command
# G1 --> Extrusion command
def format_G_2PP(name, tokens, state):
    # Calculate the movement stroke
    move = name + " "  # Add command name
    move += get_attribute('X', tokens, state) + " "
    move += get_attribute('Y', tokens, state) + " "
    move += get_attribute('Z', tokens, state) + " "

    return move

# Function for formatting a Gx command for the aerotech stage
# G0 --> Movement command
# G1 --> Extrusion command
def format_G_AE(name, tokens, state):  
    
    # get the first line linear coordinates
    move = "LINEAR "
    move += get_attribute('X', tokens, state) + "*$SCALE "
    move += get_attribute('Y', tokens, state) + "*$SCALE "
    move += " F0.200*$VEL\n" # Not entirely sure what this value is, hard coded for now
    
    # Im not sure what the DWELl thing is but im adding it
    move += "DWELL 0.01\n"
    
    # Set whether or not we enable the laser
    move += "$DO[0].X={0}\n".format(name[1])
    
    # Im not sure what the DWELl thing is but im adding it
    move += "DWELL 0.200\n"
    
    return move





'''
    +------------------------------------------------------+
    |                                                      |
    |            Preamble Generation Functions             |
    |                                                      |
    +------------------------------------------------------+
'''
def generate_preamble_AE(vel = 1, scale = 0.01):
    preamble = "\'Automatically generated aerotech stage code. Hopefully this works\n"
    
    # Define velocity and scale
    preamble += "DVAR $VEL\n"
    preamble += "DVAR $SCALE\n\n"
    
    # Set offsets
    preamble += "ABSOLUTE\n"
    preamble += "POSOFFSET SET X0 Y0\n\n\n"
    
    # Define variables
    preamble += "$VEL = {0}\n".format(vel)
    preamble += "$SCALE = {0}\n".format(scale)


    return preamble + "\n"

def generate_preamble_2PP():
    preamble = "Automatically generated 2PP code. Hopefully this works\n"
    return preamble




'''
    +------------------------------------------------------+
    |                                                      |
    |                    Helper Functions                  |
    |                                                      |
    +------------------------------------------------------+
'''
def get_attribute(attribute, curr_token, state):
    ''' 
    Adds atribute for a command line
        > attribute = attribute type
        > curr_token = tokens for current command
        > prev_token = tokens for reference point

    '''
    if attribute in curr_token.keys():
        # X value from current
        state.point[attribute] = curr_token[attribute]
        return attribute + str(curr_token[attribute])
    elif attribute in state.point.keys():
        # retain X from previous
        return attribute + str(state.point[attribute])
    else:
        return attribute + "0"
        # raise TranslationError("Error missing attribute: {0} \ntokens: {1} \nprevious tokens: {2}".format(attribute, curr_token, prev_token))     