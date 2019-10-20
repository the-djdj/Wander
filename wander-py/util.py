from subprocess import Popen, PIPE, STDOUT


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
