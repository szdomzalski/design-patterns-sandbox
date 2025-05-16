from threading import Lock


class SingletonMetaLazy(type):
    """
    Singleton metaclass that ensures only one instance of a class is created.
    This version creates the instance only when it is first accessed.
    This is useful for classes that may not be used immediately or at all.
    """
    __instances = {}
    __lock = Lock()

    def __call__(cls, *args, **kwargs):
        """
        This method is called when an instance of the class is created.
        It checks if an instance already exists. If it does, it returns that
        instance. If not, it creates a new instance and stores it in the
        __instances dictionary.
        """
        with cls.__lock:  # Ensure thread safety
            if cls not in cls.__instances:
                cls.__instances[cls] = super().__call__(*args, **kwargs)
        
        return cls.__instances[cls]
    

class SingletonMetaEager(type):
    """
    Singleton metaclass that ensures only one instance of a class is created.
    This version creates the instance at the time of class definition.
    This is useful for classes that are always needed and should be created
    immediately.
    """
    __instances = {}

    def __init__(cls, *args, **kwargs):
        """
        This method is called when the class is defined. It creates an instance
        of the class and stores it in the __instances dictionary.
        """
        super().__init__(*args, **kwargs)
        cls.__instances[cls] = super().__call__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        """
        This method is called when an instance of the class is created.
        It returns the instance created at the time of
        class definition.
        """
        return cls.__instances[cls]