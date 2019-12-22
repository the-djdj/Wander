from stages.build import BuildSystem
from stages.downloads import Downloader
from stages.partitions import Partitions
from stages.preparations import Preparations
from stages.prerequisites import Prerequisites
from util import Output, Commands

from os import path
from yaml import safe_load as load, YAMLError

class Main:
    ''' The main class. This holds all of the methods used in building the
        wander system.'''


    def __init__(self, PATH):
        ''' The constructor. This creates the main object, and sets all of the
            default variables.'''
        # Create the command system
        self.commands = Commands()

        # Create the different systems used in the build
        self.prerequisites = Prerequisites(self.commands, PATH)
        self.partitions    = Partitions()
        self.downloader    = Downloader(PATH)

        # Create the preparations and build systems
        self.preparations  = list()
        self.build         = list()

        # Populate the stages environments
        self.create_stages(PATH)


    def create_stages(self, PATH):
        ''' The system to create all of the preparation and build stages for
            use in the build.'''
        # Create a placeholder for elements
        elements = dict()
        stages   = dict()

        # Load the YAML file
        with open(path.join(PATH, '__metadata.yaml'), 'r') as stream:

            # Read from the stream
            try:

                # Store the file contents
                elements = load(stream)

                # Get each of the stages
                stages = elements.get('stages')

                # Iterate through each of the stages
                for stage in stages:

                    # Extract information about the stage
                    description = stages[stage].get('description')
                    folder      = stage
                    bypass      = stages[stage].get('bypass')

                    # Check if we're meant to bypass this stage
                    if not bypass:

                        # And append the items to the lists
                        self.preparations.append(Preparations(self.commands, PATH, (description, folder), self.partitions))
                        self.build.append(BuildSystem(self.commands, PATH, self.downloader, (description, folder)))

            # If the syntax is improper, indicate as such
            except YAMLError as error:
                print(error)


    def begin(self):
        ''' The begin method. This starts the build of the new wander
            system.'''
        # Send a friendly message to the user
        Output.header('Welcome to Wander!\n')

        # Create a list of modules needed to build the system
        modules = [self.prerequisites,
                   self.partitions,
                   self.downloader]

        # Collect each of our new stages
        for stage in range(len(self.preparations)):

            # And add them to the list
            modules.append(self.preparations[stage])
            modules.append(self.build[stage])

        # Iterate through each of the modules, and ensure that they succeed
        for error, module in enumerate(modules):

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
    # Create a list of all of the distributions
    dists = list()

    # Add the distributions to a list
    for index, dist in enumerate(glob('dists/*/__metadata.yaml')):

        # Add the path of this distribution to the build system
        dists.append(dist.replace('__metadata.yaml', ''))


    # Check that there are valid distributions
    if len(dists) == 0:

        # Inform the user that nothing was found
        print('No Wander distributions were found. Exiting...')

        # And close the application
        exit(-1)

    # If there is only one item, bypass the check entirely
    elif len(dists) == 1:

        # Set the PATH variable
        PATH = dists[0]

    # Otherwise, let the user choose
    else:

        # Print some nice user messages
        print("The Wander Linux build system has detected the following releases:")

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

        # And store the path
        PATH = dists[selection]


    # Create the build environment
    main = Main(PATH)
    main.begin()
