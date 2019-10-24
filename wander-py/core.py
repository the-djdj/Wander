from prerequisites import Prerequisites
from util import Output, Commands

class Main:
    ''' The main class. This holds all of the methods used in building the
        wander system.'''


    def __init__(self):
        ''' The constructor. This creates the main object, and sets all of the
            default variables.'''
        # Create the command system
        self.commands = Commands()

        # Create the prerequisites system
        self.prerequisites = Prerequisites(self.commands)


    def begin(self):
        ''' The begin method. This starts the build of the new wander
            system.'''
        # Send a friendly message to the user
        Output.header('Welcome to Wander!\n')

        # Check the prerequisites
        self.prerequisites.verify()
        print('')



if __name__ == '__main__':
    ''' The entry point into the wander-py application. This starts the whole
        process, so that things can run smoothly.'''
    # Create the build environment
    main = Main()
    main.begin()
