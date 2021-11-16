'''
Windows API wrapper code, from based on StackOverflow answer.
https://stackoverflow.com/questions/2090464/python-window-activation
Author: luc, Thomas Aiman
License: CC BY-SA 2.5 https://creativecommons.org/licenses/by-sa/2.5/
'''
import win32gui
import re


class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""

    def __init__ (self, wildcard):
        """Constructor"""
        self._handle = None
        self.find_window_wildcard(wildcard)
        if self._handle is None:
            raise ValueError(f"No window matching '{wildcard}' found")
        
    def find_window(self, class_name, window_name=None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        win32gui.SetForegroundWindow(self._handle)
    
    def is_foreground(self):
        return self._handle == win32gui.GetForegroundWindow()


def main():
    w = WindowMgr()
    w.find_window_wildcard(".*Hello.*")
    w.set_foreground()