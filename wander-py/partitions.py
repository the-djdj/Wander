from util import Output


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
        return True
