from util import Output, YAMLObject


class Preparations(YAMLObject):
    ''' The class responsible for ensuring that a host is fully prepared to
        build a temporary system with which wander will be built. It holds a
        list of preparation objects and checks each one.'''


    # Variables for the stage that is currently being built
    TEMPORARY_SYSTEM = ('preparations.yaml', 'Preparing host environment...')
    BUILD_SYSTEM     = ('system.yaml',       'Preparing build environment...')


    def __init__(self, commands, location, stage, partitions = None):
        ''' The constructor. This creates the new system for ensuring that the
            host is prepared for building wander.'''
        # Create the parent object
        YAMLObject.__init__(self, commands);

        # Store the command system
        self.commands = commands

        # Store the partitions system
        self.partitions = partitions

        # Store the stage that we are in
        self.stage = stage

        # Load the elements list
        self.load(location + self.stage[0])


    def verify(self):
        ''' A simple method which ensures that the host system is ready...'''
        # Check that the partition system is defined
        if self.partitions is not None:

            # Add the folder location
            if self.environment.get('LOCATION') is None:
                self.environment['LOCATION'] = self.partitions.path

            else:
                self.environment['LOCATION'] += ':' + self.partitions.path

        # Tell the user what's happening
        Output.header(self.stage[1])

        # Store whether or not the preparations are valid
        result = True

        # Iterate through each of the preparations, and verify them
        for element in self.elements:

            # Verify that the prerequisite is met
            result &= Preparation(self.elements[element], self).verify()

            # Add the final line of output
            print('')

        # Inform the user of the status
        Output.footer(result, self.stage[1][0:-3])

        # And return the result
        return result



class Preparation:
    ''' The preparation class, which stores information about a single
        preparation object.'''


    def __init__(self, element, parent):
        ''' The init method, used to create a new preparation object which can
            be ensured on the host system.'''
        # Store information about the preparation object
        self.description = element.get('description')
        self.test        = element.get('test')
        self.commands    = element.get('commands')

        # Store the system for running commands
        self.parent = parent

        # Note that we've started the check
        Output.log(Output.PENDING, self.description)


    def verify(self):
        ''' The verify method, which checks that a requirement is valid, and
            prints that to the console.'''
        # Perform the tests
        Output.clear()
        Output.log(Output.EXECUTING, self.description)

        # Iterate up to the test
        for element in range(self.test + 1):

            # Execute the commands
            result = self.parent.run([self.commands[element]], True)[-1]

        # And execute the rest of the commands
        for element in range(self.test + 1, len(self.commands)):

            # Execute the final commands
            self.parent.run([self.commands[element]])

        # Check that the output is correct
        if result.endswith("True"):

            # If the endpoints are the same, things are good
            Output.clear()
            Output.log(Output.PASSED, self.description)

            # And return our result
            return True

        # At this point, we obviously don't have the correct requirement
        Output.clear()
        Output.log(Output.FAILED, self.description)

        # And return our bad result
        return False
