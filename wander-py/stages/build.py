from os import chroot

from exception import CommandException
from util import Logger, Output, YAMLObject


class BuildSystem(YAMLObject):
    ''' The class responsible for building a portion of the system by iterating
        through each of the modules, compiling, configuring, and installing
        it.'''

    # Variables for the stage that is currently being built
    TEMPORARY_SYSTEM = ('temporary.yaml', 'Building temporary system...', 'temp')
    BASE_SYSTEM      = ('basic.yaml',     'Building base system...',      'base')


    def __init__(self, commands, location, downloader, stage, partitions = None):
        ''' The constructor. This creates the new system for building a set of
            modules used in wander.'''
        # Create the parent object
        YAMLObject.__init__(self, commands)

        # Store the command system
        self.commands = commands

        # Store the patches and packages for use later
        self.packages = downloader.packages
        self.patches  = downloader.patches

        # Store the stage that we are in
        self.stage = stage

        # Store the executable
        self.executable = '/bin/sh'

        # Load the elements list
        self.load(location + self.stage[0])


    def verify(self):
        ''' A simple method which checks that each of the modules has been built
            correctly.'''
        # Tell the user what's happening
        Output.header(self.stage[1])

        # Change the root if necessary
        if self.user == 'chroot':

            # Set our shell
            self.executable = '/tools/bin/bash'

            # And change our root
            chroot(self.environment['WANDER'])

        # Store whether or not the modules are valid
        result = True

        # Get ready to run the stage
        result &= self.initialise()

        # Iterate through each of the prerequisites, and verify them
        for element in self.elements:

            # Verify that the prerequisite is met
            result &= Module(self.elements[element], self).verify()

            # Add the final line of output
            print('')

        # Cleanup the stage
        result &= self.clean()

        # Inform the user of the status
        Output.footer(result, self.stage[1][0:-3])

        # And return the result
        return result


    def initialise(self):
        ''' A method which initialises the system before the current stage has
            begun.'''
        # First check that there is initialisation to do
        if self.init is None:

            # And escape
            return True

        # And try to initialise the system
        try:

            # Create a logger
            logger = Logger(self.stage[2], 'init')

            # Run the commands
            self.run(self.init,
                    logger = logger,
                    phase = 'init',
                    executable = self.executable)

            # And note that we were successful
            return True

        except CommandException:

            # And return how we did
            return False


    def clean(self):
        ''' A method which cleans up the system after the current stage has
            finished.'''
        # First check that there is cleanup to do
        if self.cleanup is None:

            # And escape
            return True

        # And try to clean up the system
        try:

            # Create a logger
            logger = Logger(self.stage[2], 'cleanup')

            # Run the commands
            self.run(self.cleanup,
                    logger = logger,
                    phase = 'cleanup',
                    root = True,
                    executable = self.executable)

            # And note that we were successful
            return True

        except CommandException:

            # And return how we did
            return False



from os import listdir, mkdir, path
from shutil import move, rmtree
import tarfile


class Module:
    ''' The module class, which stores build information about a single
        module.'''


    def __init__(self, element, parent):
        ''' The init method, used to create a new module object which can be
            built on the host system.'''
        # Store information about the prerequisite
        self.package  = element.get('package')
        self.modules  = element.get('modules')
        self.folder   = element.get('folder')
        self.commands = element.get('commands')
        self.skip     = element.get('skip')
        self.result   = element.get('result')

        # Store the system for running commands
        self.parent   = parent

        # Extract information on the package archive itself
        self.package = parent.packages.elements[self.package]

        self.description = self.package.get('description') if element.get('description') is None else element.get('description')
        self.version     = self.package.get('version')
        self.file        = self.package.get('file').replace('{version}', str(self.version))
        self.extension   = self.package.get('extension')

        # Store the root file name
        self.target = path.join(self.parent.environment['WANDER'], 'sources', self.file)

        # Check if there are prerequisites
        if self.modules is None:

            # And make it an empty list
            self.modules = list()

        # Initialise the logger
        self.logger = Logger(self.parent.stage[2], self.file)

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
        elements = [(self.extract,   Output.EXTRACTING),
                    (self.setup,     Output.SETUP),
                    (self.prepare,   Output.PREPARING),
                    (self.compile,   Output.COMPILING),
                    (self.configure, Output.CONFIGURING),
                    (self.test,      Output.TESTING),
                    (self.install,   Output.INSTALLING),
                    (self.validate,  Output.VALIDATING),
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


    def extract(self):
        ''' A simple method which extracts the downloaded tarball so that it can
            be used.'''
        # Open the archive
        with tarfile.open(self.target + self.extension) as archive:

            # Create the directory for the extraction
            mkdir(self.target)

            # Extract the archive contents
            archive.extractall(self.target)

        # Now that the archive has been extracted, sanitise the file name
        self.file = self.file.replace('-src', '')

        # Iterate through each of the folders we've just extracted
        for item in listdir(path.join(self.target, self.file)):

            # Move the contents one directory up
            move(path.join(self.target, self.file, item), self.target)

        # Check if the folder variable is set
        if self.folder is not None and not path.isdir(path.join(self.target, self.folder)):

            # Create the build directory
            mkdir(path.join(self.target, self.folder))

        elif self.folder is None:

            # Empty the folder variable
            self.folder = ''

        # Store the result of the extraction of the prerequisites
        result = True

        # And do the same for all of the prerequisites
        for value in self.modules:

            # Extract information on the package archive itself
            package = self.parent.packages.elements[value]

            # Store some variables about the prerequisite
            description = package.get('description')
            version     = package.get('version')
            file        = package.get('file').replace('{version}', value.get('version'))
            extension   = package.get('extension')
            folder      = value
            target      = path.join(self.parent.environment['WANDER'], 'sources', file)
            location    = path.join(self.parent.environment['WANDER'], 'sources', self.file)

            # Open the archive
            with tarfile.open(target + extension) as archive:

                # Extract the archive contents
                archive.extractall(path = location)

            # Move the contents one directory up
            move(path.join(location, file), path.join(location, folder))

            # And update the results variable
            result &= path.isdir(path.join(self.target, folder))


        # Finally, ensure that the extracted files have the correct permissions
        try:

            # Run the commands
            self.parent.run(['chown -v -R wander ' + self.target],
                directory = path.join(self.target, self.folder),
                logger = self.logger, phase = 'unpacking', root = True)

        except CommandException:

            # And return how we did
            return False

        # And return if the directory exists
        return path.isdir(self.target) and result


    def setup(self):
        ''' A simple method which ensures that the build environment is fully
            set up for compilation.'''
        # Check that there is a preparation for this module
        if self.commands.get('setup') is None:

            # If there's nothing to do, return
            return True


        # Attempt to run all of the commands
        try:

            # Run the commands
            self.parent.run(self.commands.get('setup'),
                    directory = self.target,
                    logger = self.logger,
                    phase = 'setup',
                    executable = self.parent.executable)

            # And return if there are no errors
            return True

        except CommandException:

            # And return how we did
            return False


    def prepare(self):
        ''' A simple method which ensures that the build environment is fully
            prepared for compilation.'''
        # Check that there is a preparation for this module
        if self.commands.get('preparation') is None:

            # If there's nothing to do, return
            return True


        # Attempt to run all of the commands
        try:

            # Run the commands
            self.parent.run(self.commands.get('preparation'),
                    directory = path.join(self.target, self.folder),
                    logger = self.logger,
                    phase = 'preparation',
                    executable = self.parent.executable)

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


        # Attempt to run all of the commands
        try:

            # Run the commands
            self.parent.run(self.commands.get('compilation'),
                    directory = path.join(self.target, self.folder),
                    logger = self.logger,
                    phase = 'compilation',
                    executable = self.parent.executable)

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


        # Attempt to run all of the commands
        try:

            # Run the commands
            self.parent.run(self.commands.get('configuration'),
                    directory = path.join(self.target, self.folder),
                    logger = self.logger,
                    phase = 'configuration',
                    executable = self.parent.executable)

            # And return if there are no errors
            return True

        except CommandException:

            # And return how we did
            return False


    def test(self):
        ''' A simple method for ensuring that a compiled package works properly,
            by testing whether or not any exceptions occur.'''
        # Check that there is a set of testing instructions for this module
        if self.commands.get('testing') is None:

            # If there's nothing to do, return
            return True


        # Attempt to run all of the commands
        try:

            # Run the commands
            result = self.parent.run(self.commands.get('testing'),
                            directory = path.join(self.target, self.folder),
                            logger = self.logger,
                            phase = 'testing',
                            executable = self.parent.executable)

            # If nothing went wrong, return True
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


        # Attempt to run all of the commands
        try:

            # Run the commands
            self.parent.run(self.commands.get('installation'),
                    directory = path.join(self.target, self.folder),
                    logger = self.logger,
                    phase = 'installation',
                    executable = self.parent.executable)

            # And return if there are no errors
            return True

        except CommandException:

            # And return how we did
            return False


    def validate(self):
        ''' A simple method for ensuring that an installed package works
            properly by comparing the result of test code to an expected
            result.'''
        # Check that there is a set of validation instructions for this module
        if self.commands.get('validation') is None:

            # If there's nothing to do, return
            return True


        # Attempt to run all of the commands
        try:

            # Run the commands
            result = self.parent.run(self.commands.get('validation'),
                            directory = path.join(self.target, self.folder),
                            logger = self.logger,
                            phase = 'validation',
                            executable = self.parent.executable)

            # Check that we are expecting a result
            if self.result is None:

                # And return True, as we haven't encountered errors
                return True

            # Iterate through each of the acceptable results
            for possibility in self.result:

                # And return if the output matches
                if result[-1].strip() in possibility:

                    return True

            # If we don't have a match, return false
            return False

        except CommandException:

            # And return how we did
            return False


    def cleanup(self):
        ''' A simple method which cleans up any source files which remain on the
            build system.'''
        # Check if there is any specific cleanup
        if self.commands.get('cleanup') is not None:

            # Attempt to run all of the commands
            try:

                # Run the commands
                self.parent.run(self.commands.get('cleanup'),
                        directory = path.join(self.target, self.folder),
                        logger = self.logger,
                        phase = 'cleanup',
                        executable = self.parent.executable)

            except CommandException:

                # Ignore errors here, they aren't a train smash
                pass


        # Cleanup the build system
        rmtree(self.target)

        # And return that things went okay
        return not path.isdir(self.target)
