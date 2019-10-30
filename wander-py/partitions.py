from util import Output

import parted
from _ped import IOException
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
        disk = None

        # Get the partition which we are going to use
        while disk is None:

            # Prompt the user to give some input
            Output.text('Enter the disk on which to build Wander (/dev/sdX):')

            # See if we can use the disk
            try:

                # And store the input
                disk, device = self.getDevice(self.getDisk(input()))

            except IOException:

                # If we catch an exception, the disk is not available
                disk = None

        return True


    def getDisk(self, input):
        ''' A method which ensures that disk text correctly formatted.'''
        # Check if the disk is a fullname
        if search('^.*[a-z]$', input) is not None:

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
