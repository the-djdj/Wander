from exception import CommandException

from datetime import datetime as time
from os import environ, path, makedirs as mkdirs
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
    PENDING     = B_BLACK   + 'Pending'
    SKIPPED     = B_MAGENTA + 'Skipped'
    DOWNLOADING = B_BLUE    + 'Downloading'
    VERIFYING   = B_BLUE    + 'Verifying'
    COPYING     = B_BLUE    + 'Copying'
    EXTRACTING  = B_BLUE    + 'Extracting'
    PREPARING   = B_BLUE    + 'Preparing'
    COMPILING   = B_BLUE    + 'Compiling'
    CONFIGURING = B_BLUE    + 'Configuring'
    TESTING     = B_BLUE    + 'Testing'
    INSTALLING  = B_BLUE    + 'Installing'
    CLEANING    = B_BLUE    + 'Cleaning'
    EXECUTING   = B_BLUE    + 'Executing'
    PASSED      = B_GREEN   + 'Passed'
    FAILED      = B_RED     + 'Failed'

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
                        + '. Do you want to continue anyway? [Yn] ', end = '')


    def log(status, data):
        ''' The method which logs an item to the output. This adds the item
            with a designated status.'''
        print('\r' + Output.RESET + ' * [' + status + Output.RESET + '] '
                + Output.D_WHITE + data, end='')


    def text(data, newline = True):
        ''' The method which prints text, with no decorations.'''
        # Print the output
        print(Output.RESET + data + ' ', end = '')

        # And if we need to print a newline, do that
        if newline:
            print()


    def clear():
        ''' A method which clears the last line printed, so that the output can
            be updated.'''
        print(Output.CLEAR, end='')



class Commands:
    ''' The commands class. This allows for commands to be run as a subprocess
        and for the results of that command to be stored.'''


    def call(self, command, environment, directory=None):
        ''' The call command. This executes a command on a subprocess and
            returns the output that that command generates.'''
        # Store the raw output of the command
        if directory is not None:
            raw = Popen(command, shell=True, env=environment,
                        stdout=PIPE,
                        stderr=STDOUT,
                        cwd=directory)

        else:
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
        self.environment = environ.copy()

        # Iterate through each preamble element
        for element in preamble:

            # Add the key-value pair to the environment
            if self.environment.get(element) is None:
                self.environment[element] = preamble[element]

            else:
                self.environment[element] += ':' + preamble[element]


    def run(self, elements, test = False, directory = None, logger = None, phase = None):
        ''' The run method, which runs a list of commands, and returns the
            results.'''
        # Create a list for the result of the commands
        result = list()

        # Iterate through each of the commands in the preamble.
        for element in elements:
            # If we are in test mode, add something to the command
            if test:
                command = self.commands.call(element
                        + '&& echo True || echo False', self.environment)

            # If we have a directory set, run there
            elif directory is not None:
                command = self.commands.call(element, self.environment,
                        directory = directory)

            # Otherwise, get the response of the command
            else:
                command = self.commands.call(element, self.environment)

            # Check if there is an attached logger
            if logger is not None:

                # And write the output to the logger
                logger.log(phase, element, command)

            # Check if there were any errors
            if command[1] is not None:
                raise CommandException(command[1])

            # And append the output
            result.append(str(command[0])[2:-3])

        # And return the output
        return result


class Logger:
    ''' The logging system used in wander, which writes the output of a command
        to a specific file.'''


    def __init__(self, stage, name):
        ''' The default constructor. This creates a new logging system with a
            specified stage, used to delineate the logs into different folders,
            and the name of the module, which decides the name of the log
            file.'''
        # Store the filename and folder to write
        self.folder = path.join('logs', stage, name)

        # Check that the folder to write the logs in exists
        if not path.isdir(self.folder):

            # And create the file
            mkdirs(self.folder)


    def log(self, phase, command, result):
        ''' The method which actually logs information to a file.'''
        # Open the file to write it
        with open(path.join(self.folder, phase), 'a') as file:

            # First, print the time that the command was issued
            file.write(str(time.now()) + '\n')

            # Then, print the command that was used
            file.write('$ ' + command + '\n')

            # Print the actual output
            file.write('stdout:\t' + str(result[0]) _ '\n')

            # Check if there are any errors
            if not result[1]:

                # And print them
                file.write('stderr:\t' + str(result[1]) + \n)

            # And note that we've finished this output
            file.write('\n   *****   \n')
