from exception import CommandException

import os
from subprocess import Popen, PIPE, STDOUT
from yaml import safe_load as load, YAMLError


class Output:
    ''' The output class. This creates a new object for managing the output,
        and provides an array of useful methods for console output.'''


    # The status colours in the application
    D_BLACK   = '\u001b[30m'
    D_RED     = '\u001b[31m'
    D_GREEN   = '\u001b[32m'
    D_YELLOW  = '\u001b[33m'
    D_BLUE    = '\u001b[34m'
    D_MAGENTA = '\u001b[35m'
    D_CYAN    = '\u001b[36m'
    D_WHITE   = '\u001b[37m'
    B_BLACK   = '\u001b[30;1m'
    B_RED     = '\u001b[31;1m'
    B_GREEN   = '\u001b[32;1m'
    B_YELLOW  = '\u001b[33;1m'
    B_BLUE    = '\u001b[34;1m'
    B_MAGENTA = '\u001b[35;1m'
    B_CYAN    = '\u001b[36;1m'
    B_WHITE   = '\u001b[37;1m'
    BOLD      = '\u001b[1m'
    UNDERLINE = '\u001b[4m'
    REVERSED  = '\u001b[7m'
    CLEAR     = '\u001b[2K'
    RESET     = '\u001b[0m'

    # The status that an output has
    PENDING   = B_BLACK + "Pending"
    TESTING   = B_BLUE  + "Testing"
    PASSED    = B_GREEN + "Passed"
    FAILED    = B_RED   + "Failed"

    # Some lower case alternatives
    L_PASSED  = B_GREEN + "passed"
    L_FAILED  = B_RED   + "failed" 


    def header(data):
        ''' The start section. This starts a new output section and prints the
            header.'''
        print(Output.RESET + Output.BOLD + data)


    def footer(status, data):
        '''The end section. This ends an output section and prints the
            result.'''
        # Print the start of the message
        print(Output.RESET + data + " ", end = '')

        # Check the status
        if status:
            # Print the success message
            print(Output.L_PASSED + Output.RESET + '.')

        else:
            # Print the error message, and conform if the user is okay
            print(Output.L_FAILED + Output.RESET
                        + '. Do you want to continue anyway? [Yn]')


    def log(status, data):
        ''' The method which logs an item to the output. This adds the item
            with a designated status.'''
        print('\r' + Output.RESET + ' * [' + status + Output.RESET + '] '
                + Output.B_BLACK + data, end='')


    def clear():
        ''' A method which clears the last line printed, so that the output can
            be updated.'''
        print(Output.CLEAR, end='')
        


class Commands:
    ''' The commands class. This allows for commands to be run as a subprocess
        and for the results of that command to be stored.'''


    def call(self, command, environment):
        ''' The call command. This executes a command on a subprocess and
            returns the output that that command generates.'''
        # Store the raw output of the command
        raw = Popen(command, shell=True, env=environment,
                        stdout=PIPE,
                        stderr=STDOUT)

        # Get the stdout and stderr from the command
        stdout, stderr = raw.communicate(command)

        # Return the results of the command
        return stdout, stderr



class YAMLObject:
    ''' The YAMLObject class. This is the object which is loaded from a YAML
        file.'''


    def __init__(self, commands):
        ''' The init method. This creates a new YAML object.'''
        # Create all of the lists for the application
        self.preamble = dict()
        self.elements = dict()

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
                preamble = elements['preamble']

                # Sort out the elements
                self.elements = elements['elements']

            # If the syntac is improper, indicate as such
            except YAMLError as error:
                print(error)

        # Process the preamble into a usable environment
        self.environment = os.environ.copy()

        # Iterate through each preamble element
        for element in preamble:

            # Add the key-value pair to the environment
            if self.environment.get(element) is None:
                self.environment[element] = preamble[element]

            else:
                self.environment[element] += ':' + preamble[element]


    def run(self, elements):
        ''' The run method, which runs a list of commands, and returns the
            results.'''
        # Create a list for the result of the commands
        result = list()

        # Iterate through each of the commands in the preamble.
        for element in elements:
            # Get the response of the command
            command = self.commands.call(element, self.environment)

            # Check if there were any errors
            if command[1] is not None:
                raise CommandException(command[1])

            # And append the output
            result.append(str(command[0])[2:-3])

        # And return the output
        return result
