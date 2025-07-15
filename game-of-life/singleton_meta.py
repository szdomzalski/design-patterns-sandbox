from threading import Lock


class SingletonMetaLazy(type):
    """
    Singleton metaclass that ensures only one instance of a class is created.
    This version creates the instance only when it is first accessed (lazy instantiation).
    This is useful for classes that may not be used immediately or at all.
    """
    __instances = {}
    __lock = Lock()

    def __call__(cls, *args, **kwargs):
        """
        This method is called when an instance of the class is requested.
        It checks if an instance already exists. If it does, it returns that
        instance. If not, it creates a new instance and stores it in the
        __instances dictionary.

        This method takes over the default __call__ method of the class - it means overriding __call__ method in the
        called cls will not work (that method will not be called).
        """
        with cls.__lock:  # Ensure thread safety
            if cls not in cls.__instances:
                # Invoking __call__ of "type" to create the instance like in the default __call__ method
                cls.__instances[cls] = super().__call__(*args, **kwargs)

        return cls.__instances[cls]