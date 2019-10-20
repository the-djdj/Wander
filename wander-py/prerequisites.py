from exception import CommandException
from util import Output

from subprocess import call
from yaml import safe_load as load, FullLoader, YAMLError


class Prerequisites:
    ''' The class responsible for ensuring that a host meets the minimum
        requirements for building wander. It holds a list of requirement
        objects and checks each one.'''


    def __init__(self, output, commands):
        ''' The constructor. This creates the new system for checking that a
            host meets the necessary requirements for building wander.'''
        # Store the output system
        self.output = output

        # Store the command system
        self.commands = commands

        # Create the list of preamble commands
        self.preamble = list()

        # Populate the prerequisites list
        self.prerequisites = list()

        # Load the prerequisites list
        self.load('../prerequisites.yaml')


    def load(self, filename):
        ''' The system that loads the prerequisites yaml file and creates the
            checking system.'''
        # Load the YAML file
        with open(filename, 'r') as stream:

            # Read from the stream
            try:
                # Store the file contents
                elements = load(stream)

                # Sort out the preamble
                preamble = elements['preamble']['commands']
                for element in preamble:
                    self.preamble.append(element)

            # If the syntac is improper, indicate as such
            except YAMLError as error:
                print(error)


    def prepare(self):
        ''' The preamble method, used for ensuring a clean environment for
            checking prerequisites.'''
        # Create a list for the result of the commands
        result = list()

        # Iterate through each of the commands in the preamble.
        for element in self.preamble:
            # Get the response of the command
            command = self.commands.call(element)

            # Check if there were any errors
            if command[1] is not None:
                raise CommandException(command[1])

            # And append the output
            result.append(command[0])

        # And return the output
        return result


    def verify(self):
        ''' A simple method which checks that each of the requirements has been
            met.'''
        # Execute the preamble
        self.prepare()

        # Iterate through each of the prerequisites, and verify them
        for prerequisite in self.prerequisites:
            prerequisite.verify()



class Prerequisite:
    ''' The prerequisite class, which stores information about a single
        prerequisite.'''


    def __init__(self):
        pass


    def verify(self):
        pass
