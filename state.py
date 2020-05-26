class BlendLoopState():
    # Make sure to set the initial state correctly here.
    # Otherwise, functions that depend on state may use wrong initial state.
    # For example, your error reporting modal might accidently take
    # a boolean field from the state instead of an empty string.
    # This would cause it to report endlessly and crash Blender.
    def __init__(self, state):
        self._state = state
        self.__task = None
        initial = [('is_running', 'b', False),
                   ('info', 's', ""),
                   ('error', 's', "")]
        for name, _type, value in initial:
            st_item = self._state.add()
            st_item.name = name
            self.__set_property(name, _type, value)

    def __get_property(self, prop, _type):
        for item in self._state:
            if item.name == prop:
                return getattr(item, _type)

    def __set_property(self,  prop, _type, value):
        for item in self._state:
            if item.name == prop:
                if _type == 'b':
                    item.b = value
                elif _type == 'i':
                    item.i = value
                elif _type == 's':
                    item.s = value
                else:
                    raise Exception(
                        f'Received invalid _type parameter: {_type}')

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
