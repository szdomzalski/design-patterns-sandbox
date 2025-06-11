from abc import ABC, abstractmethod


class Operation(ABC):
    '''
    Abstract base class for text processing operations.
    This class defines the interface for text processing operations, which includes a method to process text.
    '''
    @abstractmethod
    def process(self, text: str) -> str:
        """
        Process the input text and return the modified text.
        :param text: Input text to be processed.
        :return: Processed text as a string.
        """
        pass


class UpperCaseOperation(Operation):
    def process(self, text: str) -> str:
        """
        Convert the input text to uppercase.
        :param text: Input text to be converted.
        :return: Uppercase text as a string.
        """
        return text.upper()


class LowerCaseOperation(Operation):
    def process(self, text: str) -> str:
        """
        Convert the input text to lowercase.
        :param text: Input text to be converted.
        :return: Lowercase text as a string.
        """
        return text.lower()


class CapitalizeOperation(Operation):
    def process(self, text: str) -> str:
        """
        Capitalize the first letter of the input text.
        :param text: Input text to be capitalized.
        :return: Capitalized text as a string.
        """
        return text.capitalize()

class NoOperation(Operation):
    def process(self, text: str) -> str:
        """
        Return the input text unchanged.
        :param text: Input text to be returned.
        :return: Unchanged text as a string.
        """
        return text


class TextProcessor:
    def __init__(self, operation: Operation):
        """
        Initialize the TextProcessor with a specific operation.
        :param operation: An instance of an Operation subclass.
        """
        self.operation = operation

    def process(self, text: str) -> str:
        """
        Process the input text using the specified operation.
        :param text: Input text to be processed.
        :return: Processed text as a string.
        """
        return self.operation.process(text)


TEXT_OPERATIONS = {
    0: NoOperation(),
    1: UpperCaseOperation(),
    2: LowerCaseOperation(),
    3: CapitalizeOperation(),
}


if __name__ == "__main__":
    print("Welcome to the Text Processor!")
    print("Select a text operation:")
    print("0. No Operation")
    print("1. Uppercase")
    print("2. Lowercase")
    print("3. Capitalize")

    choice = int(input("Enter the number corresponding to your choice: "))
    input_text = input("Enter the text to be processed: ")

    operation = TEXT_OPERATIONS[choice]
    processor = TextProcessor(operation)

    output_text = processor.process(input_text)
    print(f"Processed text: {output_text}")
