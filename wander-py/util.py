from exception import CommandException

from subprocess import Popen, PIPE, STDOUT
from yaml import safe_load as load, YAMLError


class Output:
    ''' The output class. This creates a new object for managing the output,
        and provides an array of useful methods for console output.'''


    def __init__(self):
        ''' The constructor. This assigns the default values used in the\
            object.'''
        pass



class Commands:
    ''' The commands class. This allows for commands to be run as a subprocess
        and for the results of that command to be stored.'''


    def call(self, command):
        ''' The call command. This executes a command on a subprocess and
            returns the output that that command generates.'''
        # Store the raw output of the command
        raw = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)

        # Get the stdout and stderr from the command
        stdout, stderr = raw.communicate()

        # Return the results of the command
        return stdout, stderr



class YAMLObject:
    ''' The YAMLObject class. This is the object which is loaded from a YAML
        file.'''


    def __init__(self, commands):
        ''' The init method. This creates a new YAML object.'''
        # Create all of the lists for the application
        self.preamble = list()

        # Create the command system
        self.commands = commands


    def load(self, filename):
        ''' The system that loads the object yaml file.'''
        # Load the YAML file
        with open(filename, 'r') as stream:

            # Read from the stream
            try:

                # Store the file contents
                elements = load(stream)

                # Sort out the preamble
                for element in elements['preamble']:
                    self.preamble.append(element)

                # Sort out the elements
                for element in elements['elements']:
                    self.elements.append(element)

            # If the syntac is improper, indicate as such
            except YAMLError as error:
                print(error)


    def run(self, elements):
        ''' The run method, which runs a list of commands, and returns the
            results.'''
        # Create a list for the result of the commands
        result = list()

        # Iterate through each of the commands in the preamble.
        for element in elements:
            # Get the response of the command
            command = self.commands.call(element)

            # Check if there were any errors
            if command[1] is not None:
                raise CommandException(command[1])

            # And append the output
            result.append(command[0])

        # And return the output
        return result
