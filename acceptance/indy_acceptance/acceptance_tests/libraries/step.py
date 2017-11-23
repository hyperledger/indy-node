"""
Created on Nov 20, 2017

@author: khoi.ngo


"""


class Steps:
    """
    Class manage list of step.
    """
    __steps = []

    def __init__(self):
        pass

    def get_last_step(self):
        """
        :return the last item of step.
        """
        if len(self.__steps) != 0:
            return self.__steps[-1]

    def get_list_step(self):
        """
        :return the list of step.
        """
        return self.__steps

    def add_step(self, name):
        """
        Add a new step to list step.
        :param name: variable hold the step name. Using to report.
        """
        from libraries.constant import Colors
        step_id = len(self.__steps)
        print(Colors.HEADER + "\n{0}. {1}\n".format(step_id, name) + Colors.ENDC)
        new_step = Step(step_id + 1, name)
        self.__steps.append(new_step)


class Step:
    """
    Class manage information of a test step.
    """
    from libraries.result import Status

    def __init__(self, step_id, name, status=Status.FAILED, message=""):
        self.__id = step_id
        self.__name = name
        self.__status = status
        self.__message = message

    def get_id(self):
        """
        :return: step's id.
        """
        return self.__id

    def get_name(self):
        """
        :return: step's name.
        """
        return self.__name

    def get_status(self):
        """
        :return: step's status.
        """
        return self.__status

    def get_message(self):
        """
        :return: return step's message.
        """
        return self.__message

    def set_status(self, status):
        self.__status = status

    def set_message(self, message):
        self.__message = message
