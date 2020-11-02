# Starts up WinAppDriver before the test
import subprocess
import os
import psutil


class Driver:
    def __init__(self, driver_path):
        self.f = open(os.devnull, 'w')
        self.process = None
        self.driver_path = driver_path

    def set_up_driver(self, path=None):
        """Starts the Windows Application Driver as a subprocess.

        Arguments detailed:
        | =Argument= | =Input=                                |
        | path       | Location of Windows Application Driver |

        | =Return=   | =Output=                               |  
        | None       | None                                   |
        """
        if path is None:
            path = self.driver_path
        si = subprocess.STARTUPINFO()
        si.dwFlags = subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0
        self.process = subprocess.Popen([path], startupinfo=si, creationflags=subprocess.CREATE_NEW_CONSOLE)

    def tear_down_driver(self):
        """Stops the Windows Application Driver."""
        process = psutil.Process(self.process.pid)
        for pro in process.children(recursive=True):
            pro.kill()
        process.kill()
