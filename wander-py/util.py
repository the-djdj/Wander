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
    SETUP       = B_BLUE    + 'Setting up'
    PREPARING   = B_BLUE    + 'Preparing'
    COMPILING   = B_BLUE    + 'Compiling'
    CONFIGURING = B_BLUE    + 'Configuring'
    TESTING     = B_BLUE    + 'Testing'
    INSTALLING  = B_BLUE    + 'Installing'
    VALIDATING  = B_BLUE    + 'Validating'
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



from getpass import getuser
from os import setgid, setuid
from pwd import getpwnam
from subprocess import Popen, PIPE, STDOUT


class Commands:
    ''' The commands class. This allows for commands to be run as a subprocess
        and for the results of that command to be stored.'''


    def __init__(self):
        ''' The constructor, which creates a new Commands object, and creates
            the user objects.'''
        # Store the list of usernames used in the build
        self.users = {'root',
                      'wander',
                      'chroot',
                      'default'}

        # And upate the list of users
        self.update()


    def update(self):

        # Create the dictionary to store the users
        USERS = dict()

        # Attempt to add each of the users in turn
        for user in self.users:

            try:

                # Check for special users
                if user is 'chroot' or user is 'default':

                    USERS[user] = getpwnam(getuser())

                # Otherwise just add them
                else:

                    USERS[user] = getpwnam(user)

            # This will be thrown if a user doesn't exist (yet)
            except KeyError:

                # We don't have to do anything
                pass


        # And store the users for later use
        self.USERS = USERS


    def call(self, command, environment, executable, directory=None, user='default'):
        ''' The call command. This executes a command on a subprocess and
            returns the output that that command generates.'''
        # Store information about the user that we'll be running commands as
        user = self.USERS.get(user)

        # Do some work on the environment
        environment['HOME']    = user.pw_dir
        environment['LOGNAME'] = user.pw_name
        environment['USER']    = user.pw_name

        # Store the raw output of the command
        if directory is not None:
            # Set the last environment variable
            environment['PWD']  = directory

            # And prepare the subprocess system
            process = Popen(command, shell=True, env=environment,
                            preexec_fn=self.demote(user.pw_uid, user.pw_gid),
                            stdout=PIPE,
                            stderr=STDOUT,
                            cwd=directory,
                            executable=executable)

        else:
            # Prepare the subprocess system
            process = Popen(command, shell=True, env=environment,
                            preexec_fn=self.demote(user.pw_uid, user.pw_gid),
                            stdout=PIPE,
                            stderr=STDOUT,
                            executable=executable)

        # Get the stdout and stderr from the command
        stdout, stderr = process.communicate(command)

        # Return the results of the command
        return stdout, stderr


    def demote(self, uid, gid):
        ''' A method which 'demotes' the system to a specified user, so that
            commands can be run properly as that user.'''

        def result():
            ''' The result method, which actually updates the uid and gid of the
                system.'''
            # Update the values using methods from the os package
            setgid(gid)
            setuid(uid)

        # And return the method which changes the user
        return result



from exception import CommandException
from os import environ
from platform import machine
from yaml import safe_load as load, YAMLError


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

                # And get any init which needs to be done
                self.init = elements.get('init')

                # Sort out the preamble
                preamble = elements.get('preamble')

                # Get the username of this section
                self.user = elements.get('user')

                # Sort out the elements
                self.elements = elements.get('elements')

                # And get any cleanup which needs to be done
                self.cleanup = elements.get('cleanup')

            # If the syntax is improper, indicate as such
            except YAMLError as error:
                print(error)

        # Process the preamble into a usable environment
        self.environment = dict()

        # Check whether or not we should populate the environment
        if self.user is not 'wander' and self.user is not 'chroot':

            # And duplicate the environment
            self.environment = environ.copy()

        # Check that a preamble exists
        preamble = preamble if preamble is not None else dict()

        # Iterate through each preamble element
        for element in preamble:

            # Make sure that the architecture of the system is defined
            if '{arch}' in preamble[element]:

                # Update the variable
                preamble[element] = preamble[element].replace('{arch}', machine())

            # Add the key-value pair to the environment
            self.environment[element] = preamble[element]


    def run(self, elements, test = False, directory = None, executable='/bin/sh', logger = None, phase = None, root = False):
        ''' The run method, which runs a list of commands, and returns the
            results.'''
        # Create a list for the result of the commands
        result = list()

        # Get the user for the commands
        user = self.user if not root else 'root'

        # Iterate through each of the commands in the preamble.
        for element in elements:
            # If we are in test mode, add something to the command
            if test:
                command = self.commands.call(element
                        + '; echo $?', self.environment,
                        user = user,
                        executable = executable)

            # If we have a directory set, run there
            elif directory is not None:
                command = self.commands.call(element, self.environment,
                        directory = directory,
                        user = user,
                        executable = executable)

            # Otherwise, get the response of the command
            else:
                command = self.commands.call(element, self.environment,
                        user = user,
                        executable = executable)

            # Check if there is an attached logger
            if logger is not None and phase is not 'unpacking':

                # And write the output to the logger
                logger.log(phase, element, command)

            # Check if there were any errors
            if command[1] is not None:
                raise CommandException(command[1])

            # And append the output
            result.append(str(command[0])[2:-3])

        # And return the output
        return result



from datetime import datetime as time
from os import path, makedirs as mkdirs


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
            file.write('stdout:\t' + str(result[0], 'utf-8', 'replace') + '\n')

            # Check if there are any errors
            if result[1] is not None:

                # And print them
                file.write('stderr:\t' + str(result[1], 'utf-8', 'replace') + '\n')

            # And note that we've finished this output
            file.write('\n   *****   \n')
