from .Keywords import Keywords
from .Driver import Driver


class WADLibrary(Keywords, Driver):
    """WADLibrary provides keywords for interacting with Windows desktop application using Windows Application Driver.
    WADLibrary handles starting up Windows Application Driver and interacts with it using HTTP requests via Python's
    Requests-library.

    WADLibrary is based on the following structure:
    | File        | Description |
    | Driver.py   | Windows Application Driver startup and teardown keywords |
    | Keywords.py | The actual keywords provided for use in Robot tests |
    | Sessions.py | Internal session management keywords |
    
    """
    def __init__(self, path="http://127.0.0.1:4723", platform="Windows", device_name="my_machine", timeout=30,
                 driver_path="C:/Program Files (x86)/Windows Application Driver/WinAppDriver"):
        Keywords.__init__(self, path, platform, device_name, timeout)
        Driver.__init__(self, driver_path)

    def wadlibrary_set_up(self):
        """Starts the Windows Application Driver and creates a session for it.
        """
        self.set_up_driver()
        self.set_up()

    def wadlibrary_tear_down(self):
        """Removes all sessions and stops the Windows Application Driver.
        """
        self.clean_up()
        self.tear_down_driver()
