from stages.build import BuildSystem
from stages.partitions import Partitions
from stages.preparations import Preparations
from stages.prerequisites import Prerequisites
from util import Output, Commands

class Main:
    ''' The main class. This holds all of the methods used in building the
        wander system.'''

    # The application errors for if something goes wrong
    ERROR_NONE                = 0
    ERROR_PREREQUISITE        = 1
    ERROR_PARTITIONS          = 2
    ERROR_PREPARATIONS        = 3
    ERROR_TEMPORARY_SYSTEM    = 4
    ERROR_SYSTEM_PREPARATIONS = 5
    ERROR_BASE_SYSTEM         = 6

    # The path at which the YAML files can be found
    PATH = './'


    def __init__(self, path):
        ''' The constructor. This creates the main object, and sets all of the
            default variables.'''
        global PATH
        PATH = path


        # Create the command system
        self.commands = Commands()

        # Create the different systems used in the build
        self.prerequisites = Prerequisites(self.commands, Main.PATH)
        self.partitions    = Partitions()
        self.preparations  = Preparations(self.commands, Main.PATH, Preparations.TEMPORARY_SYSTEM, self.partitions)
        self.temporary     = BuildSystem(self.commands, Main.PATH, BuildSystem.TEMPORARY_SYSTEM)
        self.system        = Preparations(self.commands, Main.PATH, Preparations.BUILD_SYSTEM)
        self.base_system   = BuildSystem(self.commands, Main.PATH, BuildSystem.BASE_SYSTEM, self.partitions)


    def begin(self):
        ''' The begin method. This starts the build of the new wander
            system.'''
        # Send a friendly message to the user
        Output.header('Welcome to Wander!\n')

        # Create a list of modules needed to build the system
        modules = [(self.prerequisites, Main.ERROR_PREREQUISITE),
                   (self.partitions,    Main.ERROR_PARTITIONS),
                   (self.preparations,  Main.ERROR_PREPARATIONS),
                   (self.temporary,     Main.ERROR_TEMPORARY_SYSTEM),
                   (self.system,        Main.ERROR_SYSTEM_PREPARATIONS),
                   (self.base_system,   Main.ERROR_BASE_SYSTEM)]

        # Iterate through each of the modules, and ensure that they succeed
        for module, error in modules:

            # Check the prerequisites
            if not module.verify():

                # Get the user input
                if not input().lower() == 'y':

                    # Close the application
                    self.end(error)

            # Add some nice spacing
            print()


        # And exit gracefully
        self.end(Main.ERROR_NONE)


    def end(self, status):
        ''' The end method. This terminates the build of the wander system.'''
        # Close the application
        exit(status)


from glob import glob
from yaml import safe_load as load, YAMLError

if __name__ == '__main__':
    ''' The entry point into the wander-py application. This starts the whole
        process, so that things can run smoothly.'''
    # Print some nice user messages
    print("The Wander Linux build system has detected the following releases:")

    # Create a list of all of the distributions
    dists = list()

    # Add the distributions to a list
    for index, dist in enumerate(glob('dists/*/__metadata.yaml')):

        # Add the path of this distribution to the build system
        dists.append(dist.replace('__metadata.yaml', ''))


    # Store the user's selection
    selection = -1

    # Make sure that the user's input is valid
    while selection < 0 or selection >= len(dists):

        # Iterate through each of the found distributions
        for index, dist in enumerate(glob('dists/*/__metadata.yaml')):

            # Load the YAML file
            with open(dist, 'r') as stream:

                # Get all of the elements in the distribution file
                elements = load(stream)

                # Print information about the build
                print('[{}] {} ({}-{}) {}'.format(index, elements['distribution'],
                                                         elements['version'],
                                                         elements['status'],
                                                         elements['release']))


        # Ask the user for details on which build they are going to use
        selection = int(input('Please enter the number of the system you wish to build: '))


    # Create the build environment
    main = Main(dists[selection])
    main.begin()
