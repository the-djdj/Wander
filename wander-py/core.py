from prerequisites import Prerequisites
from util import Output, Commands

class Main:
    ''' The main class. This holds all of the methods used in building the
        wander system.'''

    # The application errors for if something goes wrong
    ERROR_NONE         = 0
    ERROR_PREREQUISITE = 1


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
        if not self.prerequisites.verify():
            
            # Get the user input
            if not input().lower() == 'y':
                
                # Close the application
                self.end(Main.ERROR_PREREQUISITE)

        # And exit gracefully
        self.end(Main.ERROR_NONE)


    def end(self, status):
        ''' The end method. This terminates the build of the wander system.'''
        # Close the application
        exit(status)



if __name__ == '__main__':
    ''' The entry point into the wander-py application. This starts the whole
        process, so that things can run smoothly.'''
    # Create the build environment
    main = Main()
    main.begin()
