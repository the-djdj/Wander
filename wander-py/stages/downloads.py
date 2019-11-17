from os import path

import sys
from util import Output


class Downloader():
    ''' The class responsible for downloading all of the packages used in the
        system. This class completes the download, verifies the file, and then
        copies it onto the wander build system.'''


    def __init__(self, location):
        ''' The constructor. This creates the new system for downloading each of
            the packages.'''
        # Create the items for downloading packages and patches
        self.packages = DownloadList(path.join(location, 'packages.yaml'))
        self.patches  = DownloadList(path.join(location, 'patches.yaml'))


    def verify(self):
        ''' A simple method which downloads the packages and ensures that
            everything worked smoothly.'''
        # Tell the user what's happening
        Output.header("Downloading required packages and patches...")

        # Download all of the packages
        result = self.packages.verify()

        # And download all of the patches
        result &= self.patches.verify()

        # Inform the user of the status
        Output.footer(result, "Downloading required packages and patches")

        # And return the result
        return result



from hashlib import md5
from os import mkdir
from shutil import copyfile
from urllib.request import urlretrieve as get
from util import YAMLObject

class DownloadList(YAMLObject):
    ''' The class which actually downloads a list of packages specified in a
        YAML object.'''


    def __init__(self, object):
        ''' The constructor. This loads a list of objects to download from the
            YAML file.'''
        # Create the parent object
        YAMLObject.__init__(self)

        # Load the elements list
        self.load(object)

        # List some directories which need to exist
        directories = [path.join(sys.path[0], '..', 'sources'),
                       path.join(self.environment['WANDER'], 'sources')]

        # Go through each of the directories and do the things
        for directory in directories:

            # Check that the directory exists
            if not path.exists(directory):

                # And create the directory if it does not
                mkdir(directory)


    def verify(self):
        ''' The method which iterates through each item in the list and performs
            the appropriate actions.'''
        # Collect each of the elements which needs to be built
        elements = [(self.download,  Output.DOWNLOADING),
                    (self.checksum,  Output.VERIFYING),
                    (self.copy,      Output.COPYING)]

        # Store all of the results
        result = True

        # Iterate through each item in turn
        for element in self.elements:

            # Get the information from the file
            self.description = self.elements[element].get('description')
            self.version     = self.elements[element].get('version')
            self.file        = self.elements[element].get('file').replace('{version}', str(self.version))
            self.extension   = self.elements[element].get('extension')
            self.url         = path.join(self.elements[element].get('url').replace('{version}', str(self.version)), self.file + self.extension)
            self.md5         = self.elements[element].get('md5')

            # Store the root file name
            self.source      = path.join(sys.path[0], '..', 'sources', self.file)
            self.target      = path.join(self.environment['WANDER'], 'sources', self.file)

            # Notify the user of what's happening
            Output.log(Output.PENDING, self.description)

            # Iterate through each of the phases
            for element, stage in elements:

                # Notify the user of what we're doing
                Output.clear()
                Output.log(stage, self.description)

                # Add the result to our results variable
                result &= element()

            # At this point, we're pretty much finished
            Output.clear()
            Output.log(Output.PASSED if result else Output.FAILED, self.description)

            # Add the final line of output
            print('')

        # And return how we did
        return result


    def download(self):
        ''' A simple method which checks if the archive exists in the local
            sources directory, and if not, downloads it from the specified
            address.'''
        # Check that the file doesn't exist
        if not path.isfile(self.source + self.extension):

            # Download the file
            get(self.url, self.source + self.extension)

        # And return if the file exists
        return path.isfile(self.source + self.extension)


    def checksum(self):
        ''' A simple method which checks if the downloaded file has the correct
            checksum and was not tampered with on the download.'''
        # Open the file to verify it
        with open(self.source + self.extension, 'rb') as file:

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

        # And return if our file matches
        return hash.hexdigest() == self.md5


    def copy(self):
        ''' A simple method which copies our downloaded archive into the build
            systems' sources directory.'''
        # Copy the file over
        copyfile(self.source + self.extension, self.target + self.extension)

        # And return if the file exists
        return path.isfile(self.target + self.extension)
