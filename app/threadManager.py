"""
Context Manager for pausable threads.

Working
-------------

Creates an manager object that contains references to all the pausable threads.
Exposes a decorator to be used with functions meant to run in separate threads.
Use this in the service layer of the application.
"""
import threading

class RefObj:
    """
    This is the single point of communication to the external world
    for a pausable thread function.
    The function to be used must respect the status hooks:
    PAUSE: Temporarily dump variables and halt execution
    RUN: Run normally with args taken from ref.args
    TERM: Instantly terminate execution
    """
    #Abstract attributes to be overridden.
    manager = None
    function = None 
    opClass = None

    def __init__(self, name, *args):
        self._status = "PAUSE"
        self.output = self.opClass()
        self.args = args
        self.thread = threading.Thread(target=self.function, 
                                        args=(self,))
        self.manager.refs[name] = self

    @property
    def status(self):
        if self.thread.is_alive():
            return self._status
        else:
            self._status = "TERM"
            self.thread.join()
            return self._status
    
    @status.setter
    def status(self, newStatus):
        raise Exception

    def start(self):
        self._status = "RUN"
        self.thread.start()

    def pause(self):
        self._status = "PAUSE"
    
    def terminate(self):
        self._status = "TERM"
        self.thread.join()

    def resume(self):
        self._status = "RUN"

class ThreadManager:
    """
    ref attribute is the list of all pausable threads in context.
    Before declaring any function as pausableTask,
    create a class with attributes as the return values of the function.
    Pass the class directly to pausableTask parameter.
    Each function declared so, must have a single parameter ref 
    (type: RefObj).
    Access the actual arguments to the function in ref.args.
    Dump the outputs to ref.output. This is of type RefObj.
    Function must respect ref.status.

    For example see ../tests/threadManagerTest.py
    """
    def __init__(self):
        self.refs = dict()

    def __del__(self):
        for ref in self.refs:
            ref.terminate()

    def pausableTask(self, opClass):
        def wrapper(f):
            return type(f.__name__,
            (RefObj,),
            {
                "function": f,
                "opClass": opClass,
                "manager": self
            })
            
        return wrapper