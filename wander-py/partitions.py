from util import Output

import parted
from _ped import DeviceException, IOException
from re import search


class Partitions:
    ''' The class responsible for either creating or checking the partition on
        which wander will be built. This asks the user to enter the parition to
        build the os. If it exists, they can either overwrite it or add to it,
        and if it doesn't exist, it is created.'''


    def __init__(self):
        ''' The constructor. This creates all of the variables and systems
            needed to ensure the paritioning system.'''
        pass


    def verify(self):
        # Tell the user what's happening
        Output.header('Checking partition system...')

        # Create the disk variable
        disk, device = self.getPath()

        # Store the partition to use
        partition = self.getPartition(
                self.printPartitions(disk, device), device)

        # Store the partition that we're using
        self.path = device.path + str(partition)

        # Ask the user if they wish to format the disk
        Output.text('Do you want to format ' + self.path + ' to ext4? [Yn]',
                False)
        if input().lower() == 'y':
            # Do the formatting
            pass
        else:
            pass

        return True


    def getPath(self):
        ''' A method which gets the path of the device on which to build the
            system.'''
        # Create the disk variable
        disk = None

        # Get the disk which we are going to use
        while disk is None:

            # Prompt the user to give some input
            Output.text('Enter the disk on which to build Wander (/dev/sdX):',
                False)

            # See if we can use the disk
            try:

                # And store the input
                disk, device = self.getDevice(self.getDisk(input()))

            except (DeviceException, IOException):

                # If we catch an exception, the disk is not available
                disk = None

        # And return what we have
        return disk, device


    def printPartitions(self, disk, device):
        ''' The method which prints all of the partitions on a device, and
            creates a list of the partitions to reference later.'''
        # Create a variable to store the list of partitions
        partitions = list()

        # Print a list of partitions on the disk
        Output.text(f'The device {device.path} contains the following '
                + 'partitions:')
        for partition in disk.partitions:

            # Store the partition in a list
            partitions.append(partition.number)

            # Get the partition filesystem information
            filesystem = partition.fileSystem
            filesystem = filesystem.type if filesystem else 'unknown'

            Output.text(f'Partition {partition.number} ({partition.path})\n'
                + f'    size: {round(partition.getSize() / 1024, 2)} GiB\n'
                + f'    type: {filesystem}')

        # And return what we have
        return partitions


    def getPartition(self, partitions, device):
        ''' A method which returns the partition of the device on which to build
            the system.'''
        # Create the partition variable
        partition = None

        # Get the partition which we are going to use
        while partition is None:

            # Prompt the user to give some input
            Output.text(f'Enter the partition of {device.path} on which to'
                    + ' build Wander:', False)

            # Get the partition input
            partition = int(input())

            # And check if the partition is valid
            if partition not in partitions:
                partition = None

        # And return what we have
        return partition


    def getDisk(self, input):
        ''' A method which ensures that disk text correctly formatted.'''
        # Check if the disk is a fullname
        if search('^.*[a-z]$', input.lower()) is not None:

            # We have a very nice match
            return '/dev/sd' + input[-1]

        # Otherwise, something went wrong
        return None


    def getDevice(self, input):
        ''' A method which gets information about the specified device.'''
        # Grab the parted device
        device = parted.getDevice(input)

        # And return a disk instance
        return parted.newDisk(device), device


    def debug(self, disk, device):
        ''' A method which prints all of the debugging information associated
            with a specific disk and device.'''
        # Check that the disk exists and is sane
        print("***** sanity check *****")
        print(f"result: {disk.check()}")

        # Print device information
        print("===== device =====")
        print(f"  model:                 {device.model}")
        print(f"  path:                  {device.path}")
        print(f"  sectorSize:            {device.sectorSize}")
        print(f"  physicalSectorSize:    {device.physicalSectorSize}")
        print(f"  length:                {device.length}")
        print(f"  size (MB):             {device.getSize()}")

        # Print disk information
        print("===== disk =====")
        print(f"  type:                  {disk.type}")
        print(f"  lastPartitionNumber:   {disk.lastPartitionNumber}")
        print(f"  primaryPartitionCount: {disk.primaryPartitionCount}")
        print( "  free space regions:")

        # Collect the fre space regions
        space = disk.getFreeSpaceRegions()
        for i, region in enumerate(space):
            print(f"    {i}")
            print(f"      start:             {region.start}")
            print(f"      end:               {region.end}")
            print(f"      length:            {region.length}")

        # Print partition information
        print("===== partitions =====")
        for partition in disk.partitions:
            print(f"Partition {partition.number}")
            print(f"  length:                {partition.getLength()}")
            print(f"  active:                {partition.active}")
            print(f"  busy:                  {partition.busy}")
            print(f"  path:                  {partition.path}")
            print(f"  type:                  {partition.type}")
            print(f"  size (MB):             {partition.getSize()}")

            # Print filesystem information
            filesystem = partition.fileSystem
            print(f"  filesystem:")
            if filesystem:
                print(f"    type:                {filesystem.type}")
                print(f"    checked:             {filesystem.checked}")
            else:
                print(f"    Filesystem info missing!")

            # Print geometry information
            geometry = partition.geometry
            print(f"  geometry:")
            print(f"    start:               {geometry.start}")
            print(f"    end:                 {geometry.end}")
            print(f"    length:              {geometry.length}")
