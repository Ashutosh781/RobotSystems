# Purpose: Utility functions and classes for picarx

class Bus(object):
    """Simple class to act as Bus structure for communication between different modules"""

    def __init__(self):
        """Initialize the class"""

        self.message = None

    def write(self, message):
        """Function to write message to bus"""

        self.message = message

    def read(self):
        """Function to read message from bus"""

        return self.message