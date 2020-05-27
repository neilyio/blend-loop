class BlendLoopState():
    # Make sure to set the initial state correctly here.
    # Otherwise, functions that depend on state may use wrong initial state.
    # For example, your error reporting modal might accidently take
    # a boolean field from the state instead of an empty string.
    # This would cause it to report endlessly and crash Blender.
    def __init__(self):
        self._state = {'is_running': False,
                       'info': "",
                       'error': "",
                       'directory': ""}
        self.__task = None
        self.__subscriber = None

    def __get_property(self, prop, _type):
        return self._state[prop]

    def __set_property(self,  prop, _type, value):
        self._state = {**self._state, prop: value}

    @property
    def subscriber(self):
        return self.__subscriber

    @subscriber.setter
    def subscriber(self, value):
        self.__subscriber = value

    def subscriber_clear(self):
        del self.__subscriber

    @property
    def task(self):
        return self.__task

    @task.setter
    def task(self, value):
        self.__task = value

    @property
    def is_running(self):
        return self.__get_property('is_running', 'b')

    @is_running.setter
    def is_running(self, value):
        return self.__set_property('is_running', 'b', value)

    @property
    def info(self):
        return self.__get_property('info', 's')

    @info.setter
    def info(self, value):
        return self.__set_property('info', 's', value)

    @property
    def error(self):
        return self.__get_property('error', 's')

    @error.setter
    def error(self, value):
        return self.__set_property('error', 's', value)

    @property
    def directory(self):
        return self.__get_property('directory', 's')

    @directory.setter
    def directory(self, value):
        return self.__set_property('directory', 's', value)
