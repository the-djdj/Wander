from exception import CommandException
from util import Output, YAMLObject

from hashlib import md5
from urllib.request import urlretrieve as get
from os import listdir, mkdir, path
from shutil import copyfile, copytree, rmtree
import tarfile


class BuildSystem(YAMLObject):
    ''' The class responsible for building a portion of the system by iterating
        through each of the modules, compiling, configuring, and installing
        it.'''

    # Variables for the stage that is currently being built
    TEMPORARY_SYSTEM = ('temporary.yaml', 'Building temporary system...')


    def __init__(self, commands, location, stage):
        ''' The constructor. This creates the new system for building a set of
            modules used in wander.'''
        # Create the parent object
        YAMLObject.__init__(self, commands);

        # Store the command system
        self.commands = commands

        # Store the stage that we are in
        self.stage = stage

        # Load the elements list
        self.load(location + self.stage[0])


    def verify(self):
        ''' A simple method which checks that each of the modules has been built
            correctly.'''
        # Tell the user what's happening
        Output.header(self.stage[1])

        # List some directories which need to exist
        directories = ['sources',
                       self.environment['WANDER'] + '/sources']

        # Go through each of the directories and do the things
        for directory in directories:

            # Check that the directory exists
            if not path.exists(directory):

                # And create the directory if it does not
                mkdir(directory)

        # Store whether or not the modules are valid
        result = True

        # Iterate through each of the prerequisites, and verify them
        for element in self.elements:

            # Verify that the prerequisite is met
            result &= Module(self.elements[element], self).verify()

            # Add the final line of output
            print('')

        # Inform the user of the status
        Output.footer(result, self.stage[1][0:-3])

        # And return the result
        return result



class Module:
    ''' The module class, which stores build information about a single
        module.'''


    def __init__(self, element, parent):
        ''' The init method, used to create a new module object which can be
            built on the host system.'''
        # Store information about the prerequisite
        self.description   = element.get('description')
        self.version       = element.get('version')
        self.url           = element.get('url')
        self.md5           = element.get('md5')
        self.prerequisites = element.get('prerequisites')
        self.folder        = element.get('folder')
        self.commands      = element.get('commands')
        self.skip          = element.get('skip')

        # Store the system for running commands
        self.parent        = parent

        # Store the root file name
        self.source        = 'sources/' + self.md5
        self.target        = self.parent.environment['WANDER'] + '/' + self.source

        # Check if there are prerequisites
        if self.prerequisites is None:

            # And make it an empty list
            self.prerequisites = dict()

        # Note that we've started the check
        Output.log(Output.PENDING, self.description)


    def verify(self):
        ''' The verify method, which checks that a module built correctly, and
            prints that to the console.'''
        # Check if this module should be skipped
        if self.skip:

            # We're now finished with this prerequisite
            Output.clear()
            Output.log(Output.SKIPPED, self.description)

            # And return our result
            return True

        # Collect each of the elements which needs to be built
        elements = [(self.download,  Output.DOWNLOADING),
                    (self.checksum,  Output.VERIFYING),
                    (self.copy,      Output.COPYING),
                    (self.extract,   Output.EXTRACTING),
                    (self.prepare,   Output.PREPARING),
                    (self.compile,   Output.COMPILING),
                    (self.configure, Output.CONFIGURING),
                    (self.install,   Output.INSTALLING),
                    (self.cleanup,   Output.CLEANING)]

        # Store the result of the build
        result = True

        # Iterate through each of the phases
        for element, stage in elements:

            # Notify the user of what we're doing
            Output.clear()
            Output.log(stage, self.description)

            # Add the result to our results variable
            result &= element()

            # Check that everything is still fine
            if not result:

                # And stop our system
                Output.clear()
                Output.log(Output.FAILED, self.description)

                # And return our result
                return False

        # At this point, we're pretty much finished
        Output.clear()
        Output.log(Output.PASSED, self.description)

        # And return our result
        return True


    def download(self):
        ''' A simple method which checks if the archive exists in the local
            sources directory, and if not, downloads it from the specified
            address.'''
        # Check that the file doesn't exist
        if not path.isfile(self.source):

            # Download the file
            get(self.url, self.source)

        # Store the result of the prerequisite downloads
        result = True

        # Do the same for all of the prerequisites
        for key, value in self.prerequisites.items():

            # Store some variables about the prerequisite
            source = 'sources/' + value.get('md5')
            target = self.parent.environment['WANDER'] + '/' + source

            # Check that the prerequisite doesn't exist
            if not path.isfile(source):

                # Download the file
                get(value.get('url'), source)

                # Check if the file downloaded
                result &= path.isfile(source)


        # And return if the file exists
        return path.isfile(self.source) and result


    def checksum(self):
        ''' A simple method which checks if the downloaded file has the correct
            checksum and was not tampered with on the download.'''
        # Open the file to verify it
        with open(self.source, 'rb') as file:

            # Generate the MD5 has
            hash = md5()

            # Read the data in a loop
            while True:

                # Read in a chunk of data
                data = file.read(8192)

                # Check that that chunk is not empty
                if not data:
                    break

                # And update our hash
                hash.update(data)

        # Store the result of the prerequisite verification
        result = True

        # Do the same for all of the prerequisites
        for key, value in self.prerequisites.items():

            # Store some variables about the prerequisite
            source = 'sources/' + value.get('md5')

            # Open the file to verify it
            with open(source, 'rb') as file:

                # Generate the MD5 has
                subhash = md5()

                # Read the data in a loop
                while True:

                    # Read in a chunk of data
                    data = file.read(8192)

                    # Check that that chunk is not empty
                    if not data:
                        break

                    # And update our hash
                    subhash.update(data)

            # Update our result
            result &= subhash.hexdigest() == value.get('md5')


        # And return if our file matches
        return hash.hexdigest() == self.md5 and result


    def copy(self):
        ''' A simple method which copies our downloaded archive into the build
            systems' sources directory.'''
        # Copy the file over
        copyfile(self.source, self.target)

        # Store the result of the prerequisites
        result = True

        # Copy over each of the prerequisites
        for key, value in self.prerequisites.items():

            # Store some variables about the prerequisite
            source = 'sources/' + value.get('md5')
            target = self.parent.environment['WANDER'] + '/' + source

            # Copy them each in turn
            copyfile(source, target)

            # And update our prerequisite variable
            result &= path.isfile(target)


        # And return if the file exists
        return path.isfile(self.target) and result


    def extract(self):
        ''' A simple method which extracts the downloaded tarball so that it can
            be used.'''
        # Open the archive
        with tarfile.open(self.source) as file:

            # Create the directory for the extraction
            mkdir(self.source + '.raw/')

            # Extract the archive contents
            file.extractall(self.source + '.raw/')

            # Get a list of folders that we've just extracted
            folder = self.source + '.raw/' + listdir(self.source + '.raw/')[0]

            # Move the contents one directory up
            copytree(folder, self.target + '.d/')

            # And delete the unneeded files
            rmtree(self.source + '.raw/')

        # Store the result of the extraction of the prerequisites
        result = True

        # And do the same for all of the prerequisites
        for key, value in self.prerequisites.items():

            # Store some variables about the prerequisite
            source = 'sources/' + value.get('md5')
            target = self.parent.environment['WANDER'] + '/' + source

            # Open the archive
            with tarfile.open(source) as file:

                # Create the directory for the extraction
                mkdir(source + '.raw/')

                # Extract the archive contents
                file.extractall(source + '.raw/')

                # Get a list of folders that we've just extracted
                folder = source + '.raw/' + listdir(source + '.raw/')[0]

                # Move the contents one directory up
                copytree(folder, self.target + '.d/' + value.get('folder'))

                # Delete the unneeded files
                rmtree(source + '.raw/')

                # And update the results variable
                result &= path.isdir(self.target + '.d/' + value.get('folder'))


        # And return if the directory exists
        return path.isdir(self.target + '.d/') and result


    def prepare(self):
        ''' A simple method which ensures that the build environment is fully
            prepared for compilation.'''
        # Check that there is a preparation for this module
        if self.commands.get('preparation') is None:

            # If there's nothing to do, return
            return True


        # Check if the folder variable is set
        if self.folder and not path.isdir(self.target + '.d/' + self.folder):

            # Create the build directory
            mkdir(self.target + '.d/' + self.folder)

        elif not self.folder:

            # Empty the folder variable
            self.folder = ''

        # Attempt to run all of the commands
        try:

            # Run the commands
            self.parent.run(self.commands.get('preparation'),
                    directory = self.target + '.d/' + self.folder)

            # And return if there are no errors
            return True

        except CommandException:

            # And return how we did
            return False


    def compile(self):
        ''' A simple method which ensures that the build environment compiles
            properly and without any issues.'''
        # Check that there is a set of compilation instructions for this module
        if self.commands.get('compilation') is None:

            # If there's nothing to do, return
            return True


        # Check if the folder variable is set
        if self.folder and not path.isdir(self.target + '.d/' + self.folder):

            # Create the build directory
            mkdir(self.target + '.d/' + self.folder)

        elif not self.folder:

            # Empty the folder variable
            self.folder = ''

        # Attempt to run all of the commands
        try:

            # Run the commands
            self.parent.run(self.commands.get('compilation'),
                    directory = self.target + '.d/' + self.folder)

            # And return if there are no errors
            return True

        except CommandException:

            # And return how we did
            return False


    def configure(self):
        ''' A simple method which ensures that the build environment is fully
            configured without any issues.'''
        # Check that there is a set of configuration instructions
        if self.commands.get('configuration') is None:

            # If there's nothing to do, return
            return True


        # Check if the folder variable is set
        if self.folder and not path.isdir(self.target + '.d/' + self.folder):

            # Create the build directory
            mkdir(self.target + '.d/' + self.folder)

        elif not self.folder:

            # Empty the folder variable
            self.folder = ''

        # Attempt to run all of the commands
        try:

            # Run the commands
            self.parent.run(self.commands.get('configuration'),
                    directory = self.target + '.d/' + self.folder)

            # And return if there are no errors
            return True

        except CommandException:

            # And return how we did
            return False


    def install(self):
        ''' A simple method installs a compiled package so that it can be used
            by the host system.'''
        # Check that there is a set of installation instructions for this module
        if self.commands.get('installation') is None:

            # If there's nothing to do, return
            return True


        # Check if the folder variable is set
        if self.folder and not path.isdir(self.target + '.d/' + self.folder):

            # Create the build directory
            mkdir(self.target + '.d/' + self.folder)

        elif not self.folder:

            # Empty the folder variable
            self.folder = ''

        # Attempt to run all of the commands
        try:

            # Run the commands
            self.parent.run(self.commands.get('installation'),
                    directory = self.target + '.d/' + self.folder)

            # And return if there are no errors
            return True

        except CommandException:

            # And return how we did
            return False


    def cleanup(self):
        ''' A simple method which cleans up any source files which remain on the
            build system.'''
        # Cleanup the build system
        rmtree(self.target + '.d/')

        # And return that things went okay
        return True
