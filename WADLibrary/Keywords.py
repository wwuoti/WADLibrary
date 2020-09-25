import json
from .Sessions import Sessions
from .common.keys import keys
from .common import execute
import time


class Keywords:
    def __init__(self, path, platform, device_name, timeout):
        self.__sessions = []
        self.__current_session = None
        self.__platform = platform
        self.path = path
        self.device_name = device_name
        self.timeout = timeout

    def set_up(self):
        """Sets up a new session for WinAppDriver.

        Starts by first defining the required capabilities, such as platform, device name
        or any experimental flags. Then, creates an initial session called Root for the main Desktop window.
        In WAD, sessions represent different application top-level windows.
        """
        desired_caps = dict()
        desired_caps["app"] = 'Root'
        desired_caps["platformName"] = self.__platform
        desired_caps["deviceName"] = self.device_name
        desired_caps["ms:experimental-webdriver"] = True

        execute.post(self.path + '/session/', json={'desiredCapabilities': desired_caps})

        res = execute.get(self.path + '/sessions')
        json_obj = json.loads(res.text)
        for session in json_obj['value']:
            cap = session['capabilities']
            session_id = session['id']
            if 'appTopLevelWindow' in cap:
                app_name = cap['appTopLevelWindow']
            elif 'app' in cap:
                app_name = cap['app']
            session_obj = Sessions(session_id=session_id, name=app_name, desired_caps=cap)
            self.__sessions.append(session_obj)
        ses = self.get_session('Root')
        self.__current_session = ses

    def clean_up(self):
        """Removes all sessions."""
        for_deletion = self.__sessions
        for session in self.__sessions:
            self.delete_session(session.get_id())
        for session in for_deletion:
            self.__sessions.remove(session)

    def clean_up_session(self, name):
        """Removes a specific session.

        Arguments detailed:
        | =Argument= | =Input=                            |
        | name       | Name of the session to be removed. |
        """
        session = self.get_session(name)
        self.delete_session(session.get_id())
        self.__sessions.remove(session)

    def get_sessions(self):
        """Returns all sessions."""
        return self.__sessions

    def get_current_session_id(self):
        """Returns currently active session."""
        return self.__current_session.get_id()

    def get_session_ids(self):
        """Returns identifiers for all sessions."""
        ids = []
        for session in self.__sessions:
            ids.append(session.get_id())
        return ids

    def get_session(self, name):
        """Returns session for specified name.

        Arguments detailed:
        | =Argument= | =Input=                              |
        | name       | Name of the session to be retrieved. |
        """
        for session in self.__sessions:
            if name == session.get_name():
                return session

    def get_session_by_id(self, session_id):
        """Returns session for specified id."""
        for session in self.__sessions:
            if session_id == session.get_id():
                return session

    def get_window_handle(self, using, value, session_id=None):
        """Searches for a window and returns a handle for it.

        Arguments detailed:
        | =Argument= | =Input=                                     |
        | using      | Locator strategy for window                 |
        | value      | Locator of window                           |
        | session_id | Session which contains the searched element |

        | =Return=   | Output                                      |
        | handle     | Memory address of window                    |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        elem = self.find_element(using=using, value=value, session_id=session_id)
        win = execute.get(self.path + '/session/' + session_id + '/element/' + elem + '/attribute/NativeWindowHandle')
        json_obj = json.loads(win.text)
        handle = hex(int(json_obj['value']))
        return handle

    def attach_to_window(self, value, name, using='name', session_id=None):
        """ Finds a window, creates a new session for it and sets the window to the foreground.

        Arguments detailed:
        | =Argument=  | =Input=                                          |
        | value       | Locator of window                                |
        | name        | Name of session which will be created for window |
        | using       | Locator strategy for window                      |
        | session_id  | Session which contains the searched element      |

        | =Return=    | =Output=                                         |
        | None        | None                                             |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        window_handle = self.get_window_handle(using=using, value=value, session_id=session_id)
        desired_caps = dict()
        desired_caps["appTopLevelWindow"] = window_handle
        desired_caps["platformName"] = self.__platform
        desired_caps["deviceName"] = self.device_name
        self.__current_session = self._create_session(desired_caps, name)
        self.get_sessions()

    def close_window(self, session_id=None):
        """Closes window of specified session.

        Arguments detailed:
        | =Argument=  | =Input=                             |
        | session_id  | Session which window will be closed |

        | =Return=    | =Output=                            |
        | None        | None                                |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        execute.delete(self.path + '/session/' + session_id + '/window')

    def maximize_window(self, session_id=None):
        """Maximizes window of specified session.

        Arguments detailed:
        | =Argument=  | =Input=                                   |
        | session_id  | Session which window will be maximized.   |

        | =Return=   | =Output=                                   |
        | None       | None                                       |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        execute.post(self.path + '/session/' + session_id + '/window/maximize')

    def minimize_window(self, session_id=None):
        """Minimizes window of specified session.

        Arguments detailed:
        | =Argument=  | =Input=                                |
        | session_id  | Session which window will be minimized |

        | =Return=   | =Output=                                |
        | None       | None                                    |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        execute.post(self.path + '/session/' + session_id + '/window/minimize')

    def delete_session(self, session_id):
        """Deletes specified session.

        Arguments detailed:
        | =Argument=  | =Input=                             |
        | session_id  | Session which window will be closed |

        | =Return=    | =Output=                            |
        | None        | None                                |
        """
        execute.delete(self.path + '/session/' + session_id)

    def set_current_session(self, name):
        """Sets specified session to active.

        Arguments detailed:
        | =Argument=  | =Input=                   |
        | name        | Session to be set active. |

        | =Return=   | =Output=                   |
        | None       | None                       |
        """
        self.__current_session = self.get_session(name)

    def set_focus(self, session_id=None):
        """Sets a session's window to the foreground
        Arguments detailed:
        | =Argument=   | =Input=                                        |
        | session_id   | Session which window will be set to foreground |

        | =Return=     | =Output=                                       |
        | None         |  None                                          |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        session = self.get_session_by_id(session_id)
        caps = session.get_desired_caps()
        if 'appTopLevelWindow' in caps:
            app_name = caps['appTopLevelWindow']
        elif 'app' in caps:
            app_name = caps['app']
        json_obj = {'name': app_name}
        execute.post(self.path + '/session/' + session_id + '/window', json=json_obj)

    def find_element(self, value, using='name', session_id=None):
        """Searches for element in the current session's window.

        Arguments detailed:
        | =Argument=   | =Input=                                |
        | value        | Value of element locator               |
        | using        | Type of element locator                |
        | session_id   | Session where element is searched from |

        | =Return=     | =Output=                               |
        | elem         | Element identifier                     |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        res = execute.post(self.path + '/session/' + session_id + '/element',
                           json={'using': using, 'sessionId': session_id, 'value': value})
        json_obj = json.loads(res.text)
        elem = json_obj['value']['ELEMENT']
        return elem

    def find_element_children(self, *args, session_id=None):
        """
        Finds all children for specified chain of elements.

        All positional arguments are given in the format "locator_type:locator". The element locators
        have to be given in a top-down order, meaning that the topmost element in the hierarchy is
        given as the first element.

        Arguments detailed:
        | =Argument=   | =Input=                                                                        |
        | *args        | All positional arguments, interpreted as locator_type:locator                  |
        | session_id   | Session where all elements are searched from                                   |

        | =Return=     | =Output=                                                                       |
        | children     | List of child elements from the last level of the hierarchy, matching criteria |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        parent_using, parent_value = args[0].split(":", 1)
        parent_elem = self.find_element(value=parent_value, using=parent_using, session_id=session_id)
        for i in range(1, len(args)):
            child_using, child_value = args[i].split(":", 1)
            res = execute.post(self.path + '/session/' + session_id + '/element/' +
                               parent_elem + '/elements/',
                               json={'using': child_using, 'sessionid': session_id, 'value': child_value})
        json_obj = json.loads(res.text)
        children = json_obj['value']
        return children

    def find_child_element(self, *args, session_id=None):
        """
        Finds first child for specified chain of elements.

        All positional arguments are given in the format "locator_type:locator". The element locators
        have to be given in a top-down order, meaning that the topmost element in the hierarchy is
        given as the first element.

        Arguments detailed:
        | =Argument= | =Input=                                                       |
        | *args      | All positional arguments, interpreted as locator_type:locator |
        | session_id | Session where all elements are searched from                  |

        | =Return=   | =Output=                                                      |
        | last_child | Element identifier                                            |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        parent_using, parent_value = args[0].split(":", 1)
        parent_elem = self.find_element(value=parent_value, using=parent_using, session_id=session_id)
        for i in range(1, len(args)):
            child_using, child_value = args[i].split(":", 1)
            res = execute.post(self.path + '/session/' + session_id + '/element/' +
                               parent_elem + '/element/',
                               json={'using': child_using, 'sessionid': session_id, 'value': child_value})

            json_obj = json.loads(res.text)
            parent_elem = json_obj['value']['ELEMENT']
        last_child = parent_elem
        return last_child

    def click_child_recursively(self, *args, button='left', session_id=None):
        """
        Clicks first child for specified chain of elements.

        All positional arguments are given in the format "locator_type:locator". The element locators
        have to be given in a top-down order, meaning that the topmost element in the hierarchy is
        given as the first element.

        Arguments detailed:
        | =Argument=  | =Input=                                                       |
        | *args       | All positional arguments, interpreted as locator_type:locator |
        | button      | Mouse button used                                             |
        | session_id  | Session where all elements are searched from                  |

        | =Return=    | =Output=                                                      |
        | None        | None                                                          |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        elem = self.find_child_element(*args, session_id=session_id)
        self._move_to_element(elem, session_id)
        self._mouse_click(button, session_id)

    def click_ith_child_element(self, *args, index=0, button='left', session_id=None):

        """
        Clicks the Ith child for a specified chain of elements.

        All positional arguments are given in the format "locator_type:locator". The element locators
        have to be given in a top-down order, meaning that the topmost element in the hierarchy is
        given as the first element. When the last child element in the chain is reached, its children
        are iterated through and the one corresponding to the specified index is clicked.

        | =Argument=  | =Input=                                                               |
        | *args       | All positional arguments, interpreted as locator_type:locator         |
        | index       | The index of the child element to be clicked (indexing starts from 0) |
        | button      | Mouse button used                                                     |
        | session_id  | Session where all elements are searched from                          |

        | =Return=    | =Output=                                                              |
        | None        | None                                                                  |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        children = self.find_element_children(*args, session_id=session_id)
        elem = children[index]['ELEMENT']
        self._move_to_element(elem, session_id)
        self._mouse_click(button, session_id)

    def double_click(self, session_id=None):
        """Double clicks the left mouse button.

        Arguments detailed:
        | =Argument=   | =Input=                                    |
        | session_id   | Session where mouse will be double clicked |

        | =Return=     | =Output=                                   |
        | None         |  None                                      |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        execute.post(self.path + '/session/' + session_id + '/doubleclick')

    def double_click_element(self, value, using='name', session_id=None):
        """Double clicks specified element.

        Arguments detailed:
        | =Argument= | =Input=                          |
        | value      |  Value of element locator        |
        | using      |  Type of element locator         |
        | session_id | Session where element is located |

        | =Return=   | =Output=                         |
        | None       | None                             |
        """

        if session_id is None:
            session_id = self.get_current_session_id()
        elem = self.find_element(value=value, using=using, session_id=session_id)
        self._move_to_element(elem=elem, session_id=session_id)
        self.double_click(session_id=session_id)

    def click_element(self, value, using='name', button='left', session_id=None):
        """Finds element and clicks on it.

        Arguments detailed:
        | =Argument=   | =Input=                          |
        | value        | Value of element locator         |
        | using        | Type of element locator          |
        | button       | Mouse button used                |
        | session_id   | Session where element is located |

        | =Return=     | =Output=                         |
        | None         | None                             |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        elem = self.find_element(value=value, using=using, session_id=session_id)
        self._move_to_element(elem=elem, session_id=session_id)
        self._mouse_click(button=button, session_id=session_id)

    def move_mouse_to_element(self, value, using='name', session_id=None):
        """Moves mouse to specified element.

        Arguments detailed:
        | =Argument=   | =Input=                          |
        | value        | Value of element locator         |
        | using        | Type of element locator          |
        | session_id   | Session where element is located |

        | =Return=     | =Output=                         |
        | None         | None                             |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        elem = self.find_element(value=value, using=using, session_id=session_id)
        self._move_to_element(elem=elem, session_id=session_id)

    def move_mouse_to_last_child(self, *args, session_id=None):
        """Moves mouse to last element specified in a chain of elements.

        All positional arguments are given in the format "locator_type:locator". The element locators
        have to be given in a top-down order, meaning that the topmost element in the hierarchy is
        given as the first element. When the last child element in the chain is reached, its children
        are iterated through and the one corresponding to the specified index is clicked.

        | =Argument=  | =Input=                                                               |
        | *args       | All positional arguments, interpreted as locator_type:locator         |
        | session_id  | Session where all elements are searched from                          |

        | =Return=    | =Output=                                                              |
        | None        | None                                                                  |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        child_elem = self.find_child_element(*args, session_id=session_id)
        self._move_to_element(elem=child_elem, session_id=session_id)

    def keyboard_keys(self, value, session_id=None):
        """Sends specified keys as keyboard input.

        Arguments detailed:
        | =Argument=   | =Input=                                    |
        | value        | Value of element locator                   |
        | session_id   | Session where key presses are sent         |

        | =Return=     | =Output=                                   |
        | None         | None                                       |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        execute.post(self.path + '/session/' + session_id + '/keys', json={'value': list(value)})

    def send_key(self, value, session_id=None):
        """Sends a single keyboard key.

        Arguments detailed:
        | =Argument=   | =Input=                                    |
        | value        | Keyboard key to send                       |
        | session_id   | Session where keyboard key is sent         |

        | =Return=     | =Output=                                   |
        | None         |  None                                      |
        """
        if session_id is None:
            session_id = self.get_current_session_id()

        key = keys(value)

        execute.post(self.path + '/session/' + session_id + '/keys', json={'value': [key]})

    def enter_value(self, value, locator, using='name', session_id=None):
        """Inputs value to specified input element

        Arguments detailed:
        | =Argument=   | =Input=                                    |
        | value        | Value to enter into element                |
        | locator      | Element locator                            |
        | using        | Type of element locator                    |
        | session_id   | Session which contains the element         |

        | =Return=     | =Output=                                   |
        | None         |  None                                      |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        elem = self.find_element(locator, using, session_id)
        execute.post(self.path + '/session/' + session_id + '/element/' + elem + '/value',
                     json={'value': list(value)})

    def is_element_enabled(self, value, using='name', session_id=None):
        """Checks whether or not an element is enabled.

        Arguments detailed:
        | =Argument=   | =Input=                                                    |
        | value        | Value of element locator                                   |
        | using        | Type of element locator                                    |

        | =Return=     | =Output=                                                   |
        | enabled      | Boolean value: True if element is enabled, false otherwise |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        try:
            elem = self.find_element(value=value, using=using, session_id=session_id)
        except:
            return
        res = execute.get(self.path + '/session/' + session_id + '/element/' + elem + '/enabled')
        json_obj = json.loads(res.text)
        enabled = json_obj['value']
        return enabled

    def get_element_attribute(self, locator, attribute='Name', using='name', session_id=None):
        """Retrieves the value of an element's attribute.

        Element is first found using the specified locator, after which the attribute is queried for it.
        The default attribute searched for is the object's name.

        Arguments detailed:
        | =Argument=  | =Input=                                |
        | locator     | Element locator                        |
        | attribute   | Attribute of element to be retrieved   |
        | using       | Type of element locator                |
        | session_id  | Session where element is searched from |

        | =Return=    | =Output=                               |
        | attribute   | Value of attribute as a string         |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        elem = self.find_element(value=locator, using=using, session_id=session_id)
        res = execute.get(self.path + '/session/' + session_id + '/element/' + elem +
                          '/attribute/' + attribute)
        json_obj = json.loads(res.text)
        attribute = json_obj['value']
        return attribute

    def get_element_value(self, locator, using='name', session_id=None):
        """Retrieves the value of an element.

        Arguments detailed:
        | =Argument=  | =Input=                                     |
        | locator     | Element locator                             |
        | using       | Type of element locator                     |
        | session_id  | Session where element is searched from      |

        | =Return=    | =Output=                                    |
        | value       | True if element is enabled, false otherwise |
        """
        value = self.get_element_attribute(locator=locator, attribute='Value.Value', using=using, session_id=session_id)
        return value

    def get_child_element_attribute(self, *args, child_attribute='Value.Value',
                                    session_id=None):
        """
        Finds attribute for last element in chain of elements.

        All positional arguments are given in the format "locator_type:locator". The element locators
        have to be given in a top-down order, meaning that the topmost element in the hierarchy is
        given as the first element.

        Arguments detailed:
        | =Argument=      | =Input=                                                       |
        | *args           | All positional arguments, interpreted as locator_type:locator |
        | child_attribute | Attribute of last element to be queried                       |
        | session_id      | Session where all elements are searched from                  |

        | =Return=        | =Output=                                                      |
        | attribute       | Attribute value                                               |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        child_elem = self.find_child_element(*args, session_id=session_id)
        attribute = self._get_attribute_for_elem(child_elem, child_attribute, session_id)
        return attribute

    ####################################################################################################################
    # Waiting functions
    ####################################################################################################################

    def wait_until_element_is_visible(self, locator, using='name', timeout=None, error=None, session_id=None):
        """Waits until element with specified locator is visible.

        Arguments detailed:
        | =Argument=  | =Input=                                       |
        | locator     | Element locator                               |
        | using       | Type of element locator                       |
        | timeout     | How long to wait until element is visible     |
        | error       | Error to show in case element is not visible  |
        | session_id  | Session where element is searched from        |

        | =Return=    | =Output=                                      |
        | error       | If element is not visible within timeout      |
        """
        if timeout is None:
            timeout = self.timeout

        def check_visibility():
            visible = self._is_visible(locator, using, session_id)
            if visible:
                return
            elif visible is None:
                return error or "Element locator '%s' did not match any elements after %s" % (
                    locator, timeout)
            else:
                return error or "Element '%s' was not visible in %s" % (locator, timeout)

        self._wait_until_no_error(timeout, check_visibility)

    def wait_until_element_is_not_visible(self, locator, using='name', timeout=None, error=None, session_id=None):
        """Waits until element with specified locator is not visible.

        Arguments detailed:
        | =Argument=  | =Input=                                         |
        | locator     | Element locator                                 |
        | using       | Type of element locator                         |
        | timeout     | How long to wait until element is not visible   |
        | error       | Error to show in case element is still visible  |
        | session_id  | Session where element is searched from          |

        | =Return=    | =Output=                                        |
        | error       | If element is visible within timeout            |
        """
        if timeout is None:
            timeout = self.timeout

        def check_visibility():
            visible = self._is_visible(locator, using, session_id)
            if visible:
                return error or "Element '%s' is still visible in %s" % (locator, timeout)
            elif visible is None:
                return error or "Element locator '%s' did not match any elements after %s" % (
                    locator, timeout)
            else:
                return

        self._wait_until_no_error(timeout, check_visibility)

    def wait_until_child_element_is_visible(self, *args, timeout=None, error=None, session_id=None):
        """Waits until element and all of its children are visible.

        All positional arguments are given in the format "locator_type:locator". The element locators
        have to be given in a top-down order, meaning that the topmost element in the hierarchy is
        given as the first element.

        Arguments detailed:
        | =Argument= | =Input=                                                        |
        | *args      | All positional arguments, interpreted as locator_type:locator  |
        | timeout    | How long to wait until all elements are visible                |
        | error      | Error to show in case element is not visible                   |
        | session_id | Session where all elements are searched from                   |

        | =Return=   | =Output=                                                       |
        | error      | If element is not visible within timeout                       |
        """
        if timeout is None:
            timeout = self.timeout

        def check_visibility():
            visible = self._is_child_element_visible(*args, session_id=session_id)
            locator = args[-1]
            if visible:
                return
            elif visible is None:
                return error or "Element locator '%s' did not match any elements after %s" % (
                    locator, timeout)
            else:
                return error or "Element '%s' was not visible in %s" % (locator, timeout)

        self._wait_until_no_error(timeout, check_visibility)

    def wait_until_child_element_is_not_visible(self, *args, timeout=None, error=None, session_id=None):
        """Waits until one of the specified elements in arguments is not visible.

        All positional arguments are given in the format "locator_type:locator". The element locators
        have to be given in a top-down order, meaning that the topmost element in the hierarchy is
        given as the first element.

        Arguments detailed:
        | =Argument= | =Input=                                                        |
        | *args      | All positional arguments, interpreted as locator_type:locator  |
        | timeout    | How long to wait until all elements are visible                |
        | error      | Error to show in case element is not visible                   |
        | session_id | Session where all elements are searched from                   |

        | =Return=   | =Output=                                                       |
        | error      | If element is not visible within timeout                       |
        """
        if timeout is None:
            timeout = self.timeout

        def check_visibility():
            visible = self._is_child_element_visible(*args, session_id=session_id)
            locator = args[-1]
            if visible:
                return error or "Element '%s' is still visible in %s" % (locator, timeout)
            elif visible is None:
                return error or "Element locator '%s' did not match any elements after %s" % (
                    locator, timeout)
            else:
                return

        self._wait_until_no_error(timeout, check_visibility)

    def wait_until_element_is_enabled(self, locator, using='name', timeout=None, error=None, session_id=None):
        """Waits until element with specified locator is found/visible and enabled.

        Arguments detailed:
        | =Argument= | =Input=                                      |
        | locator    | Element locator                              |
        | using      | Type of element locator                      |
        | timeout    | How long to wait until element is visible    |
        | error      | Error to show in case element is not visible |
        | session_id | Session where element is searched from       |

        | =Return=   | =Output=                                     |
        | error      | If element is not enabled within timeout     |
        """
        if timeout is None:
            timeout = self.timeout

        def check_enabled():
            enabled = self.is_element_enabled(value=locator, using=using, session_id=session_id)
            if enabled:
                return
            elif enabled is None:
                return error or "Element locator '%s' did not match any elements after %s" % (
                    locator, timeout)
            else:
                return error or "Element '%s' was not enabled in %s" % (locator, timeout)

        self._wait_until_no_error(timeout, check_enabled)

    def wait_until_element_is_not_enabled(self, locator, using='name', timeout=None, error=None, session_id=None):
        """Waits until element with specified locator is found/visible and not enabled.

        Arguments detailed:
        | =Argument= | =Input=                                      |
        | locator    | Element locator                              |
        | using      | Type of element locator                      |
        | timeout    | How long to wait until element is visible    |
        | error      | Error to show in case element is not visible |
        | session_id | Session where element is searched from       |

        | =Return=   | =Output=                                     |
        | error      | If element is not enabled within timeout     |
        """
        if timeout is None:
            timeout = self.timeout

        def check_enabled():
            enabled = self.is_element_enabled(value=locator, using=using, session_id=session_id)
            if enabled:
                return error or "Element '%s' was not enabled in %s" % (locator, timeout)
            elif enabled is None:
                return error or "Element locator '%s' did not match any elements after %s" % (
                    locator, timeout)
            else:
                return

        self._wait_until_no_error(timeout, check_enabled)

    def wait_until_element_has_value(self, locator, value, using='name', timeout=None, error=None, session_id=None):
        """Waits until element has a specific value.

        Arguments detailed:
        | =Argument= | =Input=                                                    |
        | locator    | Element locator                                            |
        | value      | Value of element                                           |
        | using      | Type of element locator                                    |
        | timeout    | How long to wait until element has specific value          |
        | error      | Error to show in case element is not visible               |
        | session_id | Session where element is searched from                     |

        | =Return=   | =Output=                                                   |
        | error      | If element is does not have specified value within timeout |
        """
        if timeout is None:
            timeout = self.timeout

        def check_value():
            element_value = self.get_element_value(locator, using, session_id)
            if element_value == value:
                return
            elif element_value is None:
                return error or "Element locator '%s' did not match any elements after %s" % (
                    locator, timeout)
            else:
                return error or "Element '%s' did not contain value '%s' in %s" % (locator, value, timeout)

        self._wait_until_no_error(timeout, check_value)

    def _create_session(self, desired_caps, name):
        """Creates a session with desired capabilities.

        Arguments detailed:
        | =Argument=   | =Input=                          |
        | desired_caps | Dict of capabilities for session |
        | name         | Name for session                 |

        | =Return=     | =Output=                         |
        | session_obj  | Created session                  |
        """
        res = execute.post(self.path + '/session/', json={'desiredCapabilities': desired_caps})
        json_obj = json.loads(res.text)
        session_id = json_obj['sessionId']
        session_obj = Sessions(session_id=session_id, name=name, desired_caps=desired_caps)
        self.__sessions.append(session_obj)
        return session_obj

    def _move_to_element(self, elem, session_id=None):
        """Moves mouse to specified element.

        Arguments detailed:
        | =Argument=   | =Input=                         |
        | elem         | Element identifier              |
        | session_id   | Session where mouse is moved in |

        | =Return=     | =Output=                        |
        | None         |  None                           |

        """
        if session_id is None:
            session_id = self.get_current_session_id()
        execute.post(self.path + '/session/' + session_id + '/moveto', json={'element': elem})

    def _mouse_click(self, button='left', session_id=None):
        """Clicks the mouse button.

        Arguments detailed:
        | =Argument=   | =Input=                                                    |
        | button       | Mouse button which will be clicked (left, right or middle) |
        | session_id   | Session where button will be clicked                       |

        | =Return=     | =Output=                                                   |
        | None         | None                                                       |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        buttons = {'left': 0, 'middle': 1, 'right': 2}
        execute.post(self.path + '/session/' + session_id + '/click', json={'button': buttons[button]})

    def _get_attribute_for_elem(self, elem, attribute='Name', session_id=None):
        """Retrieves the value of a specified attribute for element given as parameter.

        Arguments detailed:
        | =Argument=  | =Input=                                   |
        | elem        | Element identifier to query attribute for |
        | attribute   | Attribute to query for element            |
        | session_id  | Session where element is searched from    |

        | =Return=    | =Output=                                  |
        | attribute   | Value of queried attribute                |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        res = execute.get(self.path + '/session/' + session_id + '/element/' + elem +
                          '/attribute/' + attribute)
        json_obj = json.loads(res.text)
        attribute = json_obj['value']
        return attribute

    def _is_visible(self, value, using='name', session_id=None):
        """
        Checks whether or not an element is visible.

        Arguments detailed:
        | =Argument=    | =Input=                                     |
        | value         | Value of element locator                    |
        | using         | Type of element locator                     |
        | session_id    | Session where element is searched from      |

        | =Return=      | =Output=                                    |
        | Boolean value | True if element is visible, false otherwise |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        res = execute.post(self.path + '/session/' + session_id + '/element',
                           json={'using': using, 'sessionId': session_id, 'value': value},
                           catch_error=False)
        json_obj = json.loads(res.text)
        if json_obj['status'] == 0:
            return True
        elif json_obj['status'] == 7:
            return False
        else:
            execute.analyse(res, catch_error=True)

    def _is_child_element_visible(self, *args, session_id=None):
        """
        Checks whether or not the last element in the chain is visible.

        All positional arguments are given in the format "locator_type:locator". The element locators
        have to be given in a top-down order, meaning that the topmost element in the hierarchy is
        given as the first element.

        Arguments detailed:
        | =Argument=    | =Input=                                                       |
        | *args         | All positional arguments, interpreted as locator_type:locator |
        | session_id    | Session where all elements are searched from                  |

        | =Return=      | =Output=                                                      |
        | Boolean value | True if element is visible, false otherwise                   |
        """
        if session_id is None:
            session_id = self.get_current_session_id()
        parent_elem = None
        for i in range(len(args)):
            using, value = args[i].split(":", 1)
            if i == 0:
                res = execute.post(self.path + '/session/' + session_id + '/element',
                                   json={'using': using, 'sessionId': session_id, 'value': value},
                                   catch_error=False)
            else:
                res = execute.post(self.path + '/session/' + session_id + '/element/' +
                                   parent_elem + '/element/',
                                   json={'using': using, 'sessionId': session_id, 'value': value},
                                   catch_error=False)
            json_obj = json.loads(res.text)
            if json_obj['status'] == 7:
                return False
            parent_elem = json_obj['value']['ELEMENT']
        if json_obj['status'] == 0:
            return True
        elif json_obj['status'] == 7:
            return False
        else:
            execute.analyse(res, catch_error=True)

    def _wait_until(self, timeout, error, func, *args):
        """General purpose wait function, acts as a helper for other wait functions.

        Waits until the function given as parameter returns true or timeout has elapsed.

        Arguments detailed:
        | =Argument= | =Input=                                           |
        | timeout    | How long to wait until element has specific value |
        | error      | Error to show when timeout has elapsed            |
        | func       | Function to execute until timeout                 |
        | *args      | Arguments for func                                |

        | =Return=   | =Output=                                          |
        | None       | None                                              |
        """

        error = error.replace('<TIMEOUT>', self.timeout)

        def wait_func():
            return None if func(*args) else error

        self._wait_until_no_error(timeout, wait_func)

    def _wait_until_no_error(self, timeout, wait_func, *args):
        """General purpose wait function, acts as a helper for other wait functions.

        Waits until the function given as parameter returns true or timeout has elapsed.

        Arguments detailed:
        | =Argument= | =Input=                                 |
        | timeout    | How long to execute the function        |
        | wait_func  | Function to execute until timeout       |
        | *args      | Arguments for wait_func                 |

        | =Return=   | =Output=                                |
        | None       | None                                    |
        """
        timeout = self.timeout if timeout is None else timeout
        max_time = time.time() + timeout
        while True:
            timeout_error = wait_func(*args)
            if not timeout_error:
                return
            if time.time() > max_time:
                raise AssertionError(timeout_error)
            time.sleep(0.1)
