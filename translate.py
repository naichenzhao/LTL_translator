import sys
import argparse
from tqdm import tqdm

from utils import *
from state import *

'''
------------ Program to translate CURA gcode to 2PP gcode ------------

Mapping between CURA and 2PP should be a 1:100 ratio

CURA printer settings:
- 95mm x 95mm build plate
- non-centered coordinates
- 0.3mm print nozzle

2PP settings
- 95um x 95um
- 300nm laser resolution
- 1nm movement resolution


Honestly, the formatting is pretty shit. 
Will probably make better another day.

'''


# Set this to true to invert the model
INVERT_MODEL = 0

# set the output type for translation
#   - 0: 2PP printert
#   - 1: aerotech stage
OUTPUT_TYPE = 0




# Globally keep track of previous location
state = State()


def tokenize(command):
    '''
    Takes in a CURA command line and splits it into tokens
    > Name: Command type
    > Tokens: Dictionary of key-value pairings of atribute:information

    e.g. G1 F1800 X10 Y10 Z10 E5
        name = G1
        token = {'X':'10', 'Y':'10', 'Z':'10', 'E':'5'}

    '''
    # Remove command comments
    de_com = command.split(";")

    # GRab tokens
    split = de_com[0].split(" ")
    name = split[0]
    tokens = {}

    for i in split[1:]:
        if len(i) > 1:
            try: 
                tokens[i[0]] = i[1:]
            except:
                print("Invalid attribute value:", i)

    # Add comments if they exist
    if len(de_com) >= 2:
        tokens["C"] = de_com[1]

    return name, tokens




def translate_line(curr_line):
    ''' Function for translating each line of the code
    Takes in a CURA gcode line as input and outputs the new 2PP line


    +------------------------------------------------------+
    |                                                      |
    |             ADD ANY NEW COMMANDS HERE                |
    |                                                      |
    +------------------------------------------------------+


    Command reference:
    > ; (Comments)
        - Gives back input with an added newLine

    > G0: non-extruding linear movement
        - translates the coordinates
        - Adds any missing X, Y and Z values into the command

    > G1: extruding linear movement
        - translates the coordinates
        - Changes the numerical extruder value to E1 for laser power
        - Adds any missing X, Y and Z values into the command
        - Operates each path twice to ensure proper polymerization

    > G92: Localization
        - Ignores localization commands --> return none

    > Tx : Change tool
        - Tx for x = number corresponding to the toolhead number
        - T0 = Standard 2PP, T1 = Galvo Scanner
    
    > Mx : Turn laser on/off
        - Mx for x = number corresponding to the command
        - M3 = turn on laser
        - M5 = turn off laser

    '''
    # Ignore comments
    if curr_line.startswith(";"):
        return None
    
    #Serialize command into tokens
    name, tokens = tokenize(curr_line)
    
    if OUTPUT_TYPE == 0 :
        
        # G28 --> Homing command, everything is set to 0
        if name == "G28":
            state.home()
            return name + " X0 Y0 Z0"
    
        if name[0] == "G":
            return format_G_2PP(name, tokens, state)
        
    elif OUTPUT_TYPE == 1 :   
        
        # Erase all extraneous lines
        if name == "G90" or name == "G21" :
            return None
        
        if name[0] == "M":
            return format_M_AE(name, tokens, state)
        
        if name[0] == "G":
            return format_G_AE(name, tokens, state)

    else:
        raise TranslationError("[ERROR]: output type not defined")

    
    # If command not recognized, return nothing and print an error
    if len(curr_line) > 1:
        print("Command not recognized:", curr_line)
    
    return None





def run(read_file, write_file):
    '''
    Runs the translater on the specified file

    '''
    
    # Read all lines from file
    text = read_file.read().split("\n")
    

    # Set initial values:
    if OUTPUT_TYPE == 0 :
        write_value = generate_preamble_2PP()
    elif OUTPUT_TYPE == 1 : 
        write_value = generate_preamble_AE()
    else:
        write_value = ""

    # Iterate through lines and translate lines
    print("Reading lines...")
    for i in tqdm(text):
        translated = translate_line(i)
        if translated is not None:
            write_value += translated + "\n"


    # Write back the file
    if INVERT_MODEL:
        inverted_array = write_value.split("\n")[::-1]
        inv_write = ""
        for i in inverted_array:
            if len(i) > 2:
                inv_write += i + "\n"
        write_file.write(inv_write)

    else:
        write_file.write(write_value)
    
    print("\nTranslation Completed")


class TranslationError(Exception):
    """Exception indicating an error in gcode values"""
    pass

if __name__ == '__main__':
    '''
        Main function of the translator program

        Reads file argument and writes into new Gcode file
        - File format does not need to include the .gcode for it to work

    '''
    
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-filename', '-f', type=str, default='structure', 
                        help = 'gcode file we want to read from'
    )
    parser.add_argument('-invert_model', '-i', type=bool, default=False, 
                        help = 'If we want to invert the model. This should only be used for the 2PP mode'
    )
    parser.add_argument('-type', '-t', type=int, default=0, 
                        help = 'The file type we want to translate to: 0) 2PP printer, 1} Aerotech Stage'
    )
    args = parser.parse_args()
    
    
    # Setup program parameters
    INVERT_MODEL = args.invert_model
    OUTPUT_TYPE = args.type
    
    # Setup the read file and save the data
    raw_file_name = args.filename
    
    if raw_file_name.endswith(".gcode"):
        file_name = raw_file_name.strip('.gcode')
    else:
        file_name = raw_file_name
    
    # Set the file we read from
    read_file = open("gcode/" + file_name + ".gcode", 'r')
    
    # Set the output file:
    if OUTPUT_TYPE == 0 :
        write_file = open("generated/" + file_name + "_2PP" + ".gcode", 'w')
    elif OUTPUT_TYPE == 1 :
        write_file = open("generated/" + file_name + "_AE" + ".txt", 'w')
    
    
    
    # Run the file - Initiate translation
    print("\nRunning...\n")
    run(read_file, write_file)

