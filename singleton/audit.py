from datetime import datetime
import os
from threading import Lock, Thread
import time

from meta import SingletonMetaLazy, SingletonMetaEager


class FileAuditManagerLazy(metaclass=SingletonMetaLazy):
    """
    A class that manages file audit.
    This class is a singleton, meaning only one instance of it can exist.
    The instance is created when the class is first time accessed.
    """

    def __init__(self, filename: str) -> None:
        """
        Initializes the file audit manager with a filename. The initialization takes place only once,
        when the class is first accessed. Every subsequent access to the class will return the same instance, so the
        initialization will not be called again and the current number will not be reinitialized.

        :param filename: The name of the file to be audited.
        :return: None
        """
        self.filename = filename
        self.__lock = Lock()
        self.__fd = os.open(filename, os.O_WRONLY | os.O_CREAT)
        self.__counter = 0

    def audit(self, message: str) -> None:
        """
        Audits a message to the file.
        :param message: The message to be audited.
        :return: None
        """
        with self.__lock:
            # Get the current timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.__counter += 1
            os.write(self.__fd, f'{timestamp}: {message}; counter: {self.__counter}\n'.encode())
            os.fsync(self.__fd)

    def __del__(self):
        """
        Destructor for the file audit manager. Closes the file descriptor when the instance is deleted.
        :return: None
        """
        os.close(self.__fd)
        self.__fd = None


class FileAuditManagerEager(metaclass=SingletonMetaEager):
    """
    A class that manages file audit.
    This class is a singleton, meaning only one instance of it can exist.
    The instance is created when the class is defined (eager instantiation).
    """

    def __init__(self, filename: str = 'audit_eager.log') -> None:
        """
        Initializes the file audit manager with a filename. The initialization takes place at the time of class
        definition. The instance is created immediately.

        :param filename: The name of the file to be audited. Eager instantiation is used, so the filename is set at the
        time of class definition and cannot be changed later (default value used).
        :return: None
        """
        self.filename = filename
        self.__lock = Lock()
        self.__fd = os.open(filename, os.O_WRONLY | os.O_CREAT)
        self.__counter = 0

    def audit(self, message: str) -> None:
        """
        Audits a message to the file.
        :param message: The message to be audited.
        :return: None
        """
        with self.__lock:
            # Get the current timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.__counter += 1
            os.write(self.__fd, f'{timestamp}: {message}; counter: {self.__counter}\n'.encode())
            os.fsync(self.__fd)

    def __del__(self):
        """
        Destructor for the file audit manager. Closes the file descriptor when the instance is deleted.
        :return: None
        """
        os.close(self.__fd)
        self.__fd = None


if __name__ == '__main__':
    # Example usage
    audit_manager_lazy = FileAuditManagerLazy('audit_lazy.log')
    audit_manager_lazy.audit('This is a test message.')
    time.sleep(1)
    audit_manager_lazy.audit('This is another test message.')

    audit_manager_eager = FileAuditManagerEager()
    audit_manager_eager.audit('This is a test message from eager instance.')
    time.sleep(1)
    audit_manager_eager.audit('This is another test message from eager instance.')

    # Multithreading example
    def auditing_in_thread(audit_manager_type: type[FileAuditManagerLazy | FileAuditManagerEager], idx: int) -> None:
        """
        Function to be run in a thread. Audits a message to the file.
        :param audit_manager: The audit manager to be used.
        :param idx: The thread index.
        :return: None
        """
        audit_manager = audit_manager_type()
        for i in range(5):
            audit_manager.audit(f'Thread index: {idx}, Auditor: {audit_manager_type.__name__}, Message: {i}')
            time.sleep(0.2)

    threads: list[Thread] = []
    threads_num_per_auditor = 4
    for i in range(threads_num_per_auditor):
        thread = Thread(target=auditing_in_thread, args=(FileAuditManagerLazy, i))
        threads.append(thread)
    for i in range(threads_num_per_auditor):
        thread = Thread(target=auditing_in_thread, args=(FileAuditManagerEager, threads_num_per_auditor + i))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()