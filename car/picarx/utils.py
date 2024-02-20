from readerwriterlock import rwlock

class Bus(object):
    """Simple class to act as Bus structure for communication between different modules"""

    def __init__(self):
        """Initialize the class"""

        self.message = None
        self.lock = rwlock.RWLockWriteD()

    def write(self, message):
        """Function to write message to bus"""

        with self.lock.gen_wlock():
            self.message = message

    def read(self):
        """Function to read message from bus"""

        with self.lock.gen_rlock():
            output = self.message

        return output