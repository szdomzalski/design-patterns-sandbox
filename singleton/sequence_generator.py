from threading import Lock

from meta import SingletonMetaLazy, SingletonMetaEager


class SequenceGeneratorLazy(metaclass=SingletonMetaLazy):
    """
    A class that generates a sequence of numbers.
    This class is a singleton, meaning only one instance of it can exist.
    The instance is created when the class is first accessed.
    This is useful for classes that may not be used immediately or at all.
    The sequence starts from a given number and increments by 1 each time
    the next number is requested.
    The class is thread-safe, meaning it can be used in a multi-threaded
    environment without causing data corruption.
    """

    def __init__(self, start: int = 0) -> None:
        """
        Initializes the sequence generator with a starting number.
        :param start: The starting number of the sequence.
        """
        self.current = start
        self.__lock = Lock()


    def get_next_number(self) -> int:
        """
        Returns the next number in the sequence.
        :return: The next number in the sequence.
        """
        with self.__lock:  # Ensure thread safety
            # Increment the current number and return it
            ret = self.current
            self.current += 1
            return ret
        

class SequenceGeneratorEager(metaclass=SingletonMetaEager):
    """
    A class that generates a sequence of numbers.
    This class is a singleton, meaning only one instance of it can exist.
    The instance is created at the time of class definition.
    This is useful for classes that are always needed and should be created
    immediately.
    The sequence starts from a given number and increments by 1 each time
    the next number is requested.
    The class is thread-safe, meaning it can be used in a multi-threaded
    environment without causing data corruption.
    """

    def __init__(self, start: int = 0) -> None:
        """
        Initializes the sequence generator.
        """
        self.current = start
        self.__lock = Lock()

    def get_next_number(self) -> int:
        """
        Returns the next number in the sequence.
        :return: The next number in the sequence.
        """
        with self.__lock:
            # Increment the current number and return it
            ret = self.current
            self.current += 1
            return ret
        
        
if __name__ == "__main__":
    # Example usage
    seq_gen = SequenceGeneratorLazy(start=10)
    print(seq_gen.get_next_number())  # Output: 10
    print(seq_gen.get_next_number())  # Output: 11

    seq_gen2 = SequenceGeneratorLazy()  # This is singleton, so it won't create a new instance and won't change the current value
    print(id(seq_gen) == id(seq_gen2))  # Output: True
    print(seq_gen.get_next_number()) 
    print(seq_gen.get_next_number())  

    seq_gen_eager = SequenceGeneratorEager(start=20)
    print(seq_gen_eager.get_next_number())  # Output: 20
    print(seq_gen_eager.get_next_number())  # Output: 21

    seq_gen_eager2 = SequenceGeneratorEager() # This is singleton, so it won't create a new instance and won't change the current value
    print(id(seq_gen_eager) == id(seq_gen_eager2))  # Output: True
    print(seq_gen_eager.get_next_number()) 
    print(seq_gen_eager.get_next_number())