from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    '''
    User class representing a user with various read-only attributes.
    Attributes:
        first_name (str): The user's first name.
        last_name (str): The user's last name.
        email (str): The user's email address.
        age (int | None): The user's age, optional.
        phone (str | None): The user's phone number, optional.
        address (str | None): The user's address, optional.

    This class is immutable, meaning once an instance is created, its attributes cannot be modified.

    The User in this code is a "product" in the Builder pattern. I let myself to omit abstraction of the user as it is
    not needed for such a simple example.
    '''
    first_name: str
    last_name: str
    email: str
    age: int | None = None
    phone: str | None = None
    address: str | None = None

    def __str__(self) -> str:
        '''
        Returns a string representation of the User instance.
        '''
        user_str = f'{self.first_name} {self.last_name} <{self.email}>'
        if self.age is not None:
            user_str += f' (Age: {self.age})'
        if self.phone is not None:
            user_str += f' (Phone: {self.phone})'
        if self.address is not None:
            user_str += f' (Address: {self.address})'
        return user_str


class UserBuilder(ABC):
    '''
    Abstract UserBuilder class that defines the interface for building a User instance.
    This class provides methods to create a user and set various attributes.
    It is intended to be extended by concrete builder classes that implement the actual construction logic.
    '''

    @abstractmethod
    def create_user(self, first_name: str, last_name: str, email: str) -> None:
        pass

    @abstractmethod
    def set_age(self, age: int) -> None:
        pass

    @abstractmethod
    def set_phone(self, phone: str) -> None:
        pass

    @abstractmethod
    def set_address(self, address: str) -> None:
        pass

    @abstractmethod
    def get_user(self) -> User:
        pass


class ConcreteUserBuilder(UserBuilder):
    '''
    ConcreteUserBuilder class that constructs a User instance step by step.
    This class allows for the creation of a User with various attributes, some of which are optional.
    It follows the Builder design pattern, allowing for a flexible and readable way to create complex objects.

    Builder knows how to "build" the specific product (User) part by part but it has not idea about "order"'s specifics
    from client side. It is the responsibility of the director to call right methods in the right order.
    '''

    def create_user(self, first_name: str, last_name: str, email: str) -> None:
        '''
        Initializes the user data with mandatory fields: first name, last name, and email.
        :param first_name: The user's first name.
        :param last_name: The user's last name.
        :param email: The user's email address.
        :return: None
        '''
        self.__user_data = {'first_name': first_name, 'last_name': last_name, 'email': email}

    def set_age(self, age: int) -> None:
        '''
        Sets the user's age.
        :param age: The user's age.
        :return: None
        '''
        try:
            self.__user_data['age'] = age
        except KeyError:
            raise ValueError("User data not initialized. Call create_user first.")

    def set_phone(self, phone: str) -> None:
        '''
        Sets the user's phone number.
        :param phone: The user's phone number.
        :return: None
        '''
        try:
            self.__user_data['phone'] = phone
        except KeyError:
            raise ValueError("User data not initialized. Call create_user first.")

    def set_address(self, address: str) -> None:
        '''
        Sets the user's address.
        :param address: The user's address.
        :return: None
        '''
        try:
            self.__user_data['address'] = address
        except KeyError:
            raise ValueError("User data not initialized. Call create_user first.")

    def get_user(self) -> User:
        '''
        Returns the constructed User instance.
        :return: User instance with the data set in the builder.
        '''
        try:
            user = User(**self.__user_data)
        except KeyError:
            raise ValueError("User data not initialized. Call create_user first.")
        return user


class UserDirector:
    '''
    UserDirector class that orchestrates the user registration process using the UserBuilder.
    This class provides a high-level interface for registering a user, guiding the builder through the necessary steps.
    It collects user input and delegates the construction of the User object to the UserBuilder.

    Client provides information about its "order" - product type (which builder to use) and specifics (input data).
    Director is responsible for processing client input (prompt here but it can by anything in general) into a plan of
    actions for the builder. It does not create the user directly, but rather uses the builder to do so.
    '''

    def __init__(self, builder: UserBuilder) -> None:
        '''
        Initializes the UserDirector with a UserBuilder instance.
        :param builder: An instance extending UserBuilder that will be used to construct the User.
        :return: None
        '''
        self.__builder = builder

    def register_user(self) -> User:
        '''
        Collects user input to register a new user.
        Prompts the user for their first name, last name, email, and optional fields like age, phone, and address.
        :return: A User instance constructed with the provided input.
        '''
        print("Please provide the following user details:")
        self.__builder.create_user(
            input("Enter first name: "), input("Enter last name: "), input("Enter email: "))
        age_input = input("Enter age (optional, press Enter to skip): ")
        if age_input:
            self.__builder.set_age(int(age_input))
        phone_input = input("Enter phone (optional, press Enter to skip): ")
        if phone_input:
            self.__builder.set_phone(phone_input)
        address_input = input("Enter address (optional, press Enter to skip): ")
        if address_input:
            self.__builder.set_address(address_input)

        return self.__builder.get_user()


if __name__ == '__main__':
    user_builder = ConcreteUserBuilder()
    user_director = UserDirector(user_builder)
    user = user_director.register_user()
    print(f'Registered user: {user}')

    # Checking read access to user details
    print(f'User details: {user.first_name} {user.last_name}, Email: {user.email}, Age: {user.age}, '
          f'Phone: {user.phone}, Address: {user.address}')

    try:
        user.age = 100  # This will raise an error since User is frozen (immutable)
    except Exception:
        print("Cannot modify user age, User is immutable.")
