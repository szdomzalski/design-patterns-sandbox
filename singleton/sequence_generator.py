from threading import Lock, Thread

from meta import SingletonMetaLazy, SingletonMetaEager


class SequenceGeneratorLazy(metaclass=SingletonMetaLazy):
    """
    A class that generates a sequence of numbers.
    This class is a singleton, meaning only one instance of it can exist.
    The instance is created when the class is first time accessed.
    The sequence starts from a given number and increments by 1 each time
    the next number is requested.
    The class is thread-safe, meaning it can be used in a multi-threaded
    environment without causing data corruption.
    """

    def __init__(self, start: int = 0) -> None:
        """
        Initializes the sequence generator with a starting number. The initialization takes place only once,
        when the class is first accessed. Every subsequent access to the class will return the same instance, so the
        initialization will not be called again and the current number will not be reinitialized.

        :param start: The starting number of the sequence.
        :return: None
        """
        self.current = start
        self.__lock = Lock()

    def __new__(cls, *args, **kwargs):
        """
        This method is called when the class is first instantiated. This method is called with arguments from class call
        when requesting an instance in the metaclass but super().__new__ has to be called without arguments to work
        properly.
        This method has been overridden in this class just for showing the example of how to do it with singleton meta.
        :param args: Arguments passed to the class.
        :param kwargs: Keyword arguments passed to the class.
        :return: The instance of the class.
        """
        return super().__new__(cls)

    def __call__(cls, *args, **kwargs):
        """
        In current scenario this method is not used at all. It is overridden just as a demonstration that even "pass"
        won't break anything.
        """
        pass


    def get_next_number(self) -> int:
        """
        Returns the next number in the sequence.
        :return: The next number in the sequence.
        """
        with self.__lock:
            self.current += 1
            return self.current

class SequenceGeneratorEager(metaclass=SingletonMetaEager):
    """
    A class that generates a sequence of numbers.
    This class is a singleton, meaning only one instance of it can exist.
    The instance is created at the time of class definition.
    The sequence starts from a given number and increments by 1 each time
    the next number is requested.
    The class is thread-safe, meaning it can be used in a multi-threaded
    environment without causing data corruption.
    """

    def __init__(self, start: int = 0) -> None:
        """
        Initializes the sequence generator. The initialization takes place at the time of class definition because of
        eager instantiation. The current number is initialized to the starting number specified in the metaclass
        __new__ method so eager instantiation prefers no arguments to be passed in the class call.
        :param start: The starting number of the sequence.
        :return: None
        """
        self.current = start
        self.__lock = Lock()

    def __new__(cls, *args, **kwargs):
        """
        This method is called when the class is defined. This method is called with arguments from the metaclass call
        but super().__new__ has to be called without arguments to work properly.
        This method has been overridden in this class just for showing the example of how to do it with singleton meta.
        :param args: Arguments passed to the class.
        :param kwargs: Keyword arguments passed to the class.
        :return: The instance of the class.
        """
        return super().__new__(cls)

    def __call__(cls, *args, **kwargs):
        """
        In current scenario this method is not used at all. It is overridden just as a demonstration that even "pass"
        won't break anything.
        """
        pass

    def get_next_number(self) -> int:
        """
        Returns the next number in the sequence.
        :return: The next number in the sequence.
        """
        with self.__lock:
            self.current += 1
            return self.current


if __name__ == "__main__":
    # Example usage
    seq_gen = SequenceGeneratorLazy(start=10)
    print(seq_gen.get_next_number())  # Output: 11
    print(seq_gen.get_next_number())  # Output: 12

    # This is singleton, so it won't create a new instance and won't change the current value
    seq_gen2 = SequenceGeneratorLazy(start=20)
    print(id(seq_gen) == id(seq_gen2))  # Output: True
    print(seq_gen.get_next_number())  # Output: 13
    print(seq_gen.get_next_number())  # Output: 14

    # Keyword argument is ignored because of eager instatiation - it should be passed in the metaclass
    seq_gen_eager = SequenceGeneratorEager(start=10)
    print(seq_gen_eager.get_next_number())  # Output: 26
    print(seq_gen_eager.get_next_number())  # Output: 27

    # This is singleton, so it won't create a new instance and won't reinitialize the current value
    seq_gen_eager2 = SequenceGeneratorEager()
    print(id(seq_gen_eager) == id(seq_gen_eager2))  # Output: True
    print(seq_gen_eager.get_next_number())  # Output: 28
    print(seq_gen_eager.get_next_number())  # Output: 29

    # Multithreading example
    def generate_in_thead(sequence_generator: type[SequenceGeneratorLazy | SequenceGeneratorEager], idx: int) -> None:
        """
        This function generates a sequence of numbers in a separate thread.
        :param sequence_generator: The class of the sequence generator.
        :return: None
        """
        instance = sequence_generator()
        for i in range(5):
            print(f'Thread index: {idx}, Generator: {sequence_generator.__name__}, Iteration {i}: '
                  f'{instance.get_next_number()}')

    threads: list[Thread] = []
    for i in range(2):
        thread = Thread(target=generate_in_thead, args=(SequenceGeneratorLazy, i))
        threads.append(thread)
    for i in range(2):
        thread = Thread(target=generate_in_thead, args=(SequenceGeneratorEager, 2 + i))
        threads.append(thread)

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
