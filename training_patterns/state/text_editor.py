from __future__ import annotations
from abc import ABC, abstractmethod

'''
In fact, this example is not really the best fit for the State pattern,
as the text editor's states are not really distinct states but rather formatting options (strategy pattern).
However, for the sake of the exercise, I tried to implement it as a State pattern.
'''


class TextEditor:
    '''
    A simple text editor that can change its state.
    '''
    def __init__(self) -> None:
        self.__state: EditorState = DefaultState(self)
        self.__text_history: list[str] = []
        self.__redo_cache: list[str] = []

    def enter_text(self, text: str) -> None:
        '''
        Enter text into the editor.
        :param text: The text to enter.
        :return: None
        '''
        print(f"Entering text: {text}")
        formatted_text = self.__state.enter_text(text)
        print(f"Formatted text: {formatted_text}")
        self.__text_history.append(formatted_text)
        self.__redo_cache = []

    def apply_bold(self) -> None:
        '''
        Apply bold formatting to the text.
        :return: None
        '''
        print("Applying bold formatting.")
        self.__state.apply_bold()

    def apply_italic(self) -> None:
        '''
        Apply italic formatting to the text.
        :return: None
        '''
        print("Applying italic formatting.")
        self.__state.apply_italic()

    def apply_underline(self) -> None:
        '''
        Apply underline formatting to the text.
        :return: None
        '''
        print("Applying underline formatting.")
        self.__state.apply_underline()

    def set_formatting(self, state: EditorState) -> None:
        '''
        Set the current formatting state of the editor.
        :param state: The new state to set.
        :return: None
        '''
        print(f"Setting editor state to {state.__class__.__name__}.")
        self.__state = state

    def reset_formatting(self) -> None:
        '''
        Reset the editor to the default state.
        :return: None
        '''
        print("Resetting to default state.")
        self.__state.reset_formatting()

    def undo(self) -> None:
        '''
        Undo the last text entry.
        :return: None
        '''
        try:
            last_text = self.__text_history.pop()
            self.__redo_cache.append(last_text)
        except IndexError:
            print("No text to undo.")

    def redo(self) -> None:
        '''
        Redo the last undone text entry.
        :return: None
        '''
        try:
            last_redo = self.__redo_cache.pop()
            self.__text_history.append(last_redo)
        except IndexError:
            print("No text to redo.")

    def print_text(self) -> None:
        '''
        Print the current text in the editor.
        :return: None
        '''
        print("Current text in editor:")
        print(''.join(self.__text_history))


class EditorState(ABC):
    '''Abstract base class for text editor states.'''
    def __init__(self, editor: TextEditor) -> None:
        self.editor = editor

    @abstractmethod
    def enter_text(self, text: str) -> str:
        '''
        Enter text into the editor.
        :param text: The text to enter.
        :return: The formatted text.
        '''
        pass

    def apply_bold(self) -> None:
        '''
        Apply bold formatting to the text.
        :return: None
        '''
        self.editor.set_formatting(BoldState(self.editor))

    def apply_italic(self) -> None:
        '''
        Apply italic formatting to the text.
        :return: None
        '''
        self.editor.set_formatting(ItalicState(self.editor))

    def apply_underline(self) -> None:
        '''
        Apply underline formatting to the text.
        :return: None
        '''
        self.editor.set_formatting(UnderlineState(self.editor))

    def reset_formatting(self) -> None:
        '''
        Reset the editor to the default state.
        :return: None
        '''
        self.editor.set_formatting(DefaultState(self.editor))


class DefaultState(EditorState):
    '''Concrete state class for the default text editor state.'''

    def enter_text(self, text: str) -> str:
        '''
        Enter text in the default state.
        :param text: The text to enter.
        :return: The plain text.
        '''
        return text


class BoldState(EditorState):
    '''Concrete state class for the bold text editor state.'''

    def enter_text(self, text: str) -> str:
        '''
        Enter text in the bold state.
        :param text: The text to enter.
        :return: The bold formatted text.
        '''
        return f"\033[1m{text}\033[0m"


class ItalicState(EditorState):
    '''Concrete state class for the italic text editor state.'''

    def enter_text(self, text: str) -> str:
        '''
        Enter text in the italic state.
        :param text: The text to enter.
        :return: The italic formatted text.
        '''
        return f"\033[3m{text}\033[0m"


class UnderlineState(EditorState):
    '''Concrete state class for the underline text editor state.'''

    def enter_text(self, text: str) -> str:
        '''
        Enter text in the underline state.
        :param text: The text to enter.
        :return: The underlined formatted text.
        '''
        return f"\033[4m{text}\033[0m"


if __name__ == "__main__":
    editor = TextEditor()
    editor.enter_text("Hello, World!\n")
    editor.print_text()

    editor.apply_bold()
    editor.enter_text("This is bold text.\n")
    editor.print_text()

    editor.apply_italic()
    editor.enter_text("This is italic text.\n")
    editor.print_text()

    editor.apply_underline()
    editor.enter_text("This is underlined text.\n")
    editor.print_text()

    editor.reset_formatting()
    editor.enter_text("Back to default state.\n")
    editor.print_text()

    print("\nUndoing 3 last actions\n")
    editor.undo()
    editor.undo()
    editor.undo()
    editor.print_text()

    print("\nRedoing 1 last action\n")
    editor.redo()
    editor.print_text()

    print("\nUndoing 2 actions\n")
    editor.undo()
    editor.undo()
    editor.print_text()

    print("\nRedoing 3 actions\n")
    editor.redo()
    editor.redo()
    editor.redo()
    editor.print_text()
