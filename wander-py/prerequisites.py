from exception import CommandException
from util import Output, YAMLObject

from subprocess import call


class Prerequisites(YAMLObject):
    ''' The class responsible for ensuring that a host meets the minimum
        requirements for building wander. It holds a list of requirement
        objects and checks each one.'''


    def __init__(self, output, commands):
        ''' The constructor. This creates the new system for checking that a
            host meets the necessary requirements for building wander.'''
        # Create the parent object
        YAMLObject.__init__(self);

        # Store the output system
        self.output = output

        # Store the command system
        self.commands = commands

        # Populate the prerequisites list
        self.prerequisites = list()

        # Load the prerequisites list
        self.load('../prerequisites.yaml')


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
