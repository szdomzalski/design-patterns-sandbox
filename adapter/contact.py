from abc import ABC, abstractmethod
import csv
from dataclasses import dataclass
import json
import os
from typing import List, Any
import xml.etree.ElementTree as ET


@dataclass
class Contact:
    '''
    Contact class representing a contact with various attributes.
    Attributes:
        full_name (str): The contact's full name.
        email (str): The contact's email address.
        phone_number (str): The contact's phone number.
        is_friend (bool): Indicates if the contact is a friend.
    '''
    full_name: str
    email: str
    phone_number: str
    is_friend: bool

    def __str__(self):
        '''
        Returns a string representation of the Contact instance.
        The string includes the full name, email, phone number, and a note if the contact is a friend.
        '''
        return f"{self.full_name} ({self.email}) - {self.phone_number} {'(Friend)' if self.is_friend else ''}"


class Reader(ABC):
    '''
    Abstract base class defining interface for reading data from various sources.

    This class serves as a base for different types of readers that can read data
    from different sources like files, networks, or databases.
    '''
    def __init__(self, file_name: str) -> None:
        '''
        Initialize the reader with a file name.
        :param file_name: The name of the file to read data from.
        :return: None
        '''
        self.file_name = file_name

    @abstractmethod
    def read(self) -> str:
        '''
        Read and return the contents of the source.
        :return: The contents of the source as a string.
        '''
        pass

class ContactsAdapter(ABC):
    '''
    Abstract base class for adapting different data formats to Contact objects.

    This class defines the interface for converting various data formats
    into a list of Contact objects.
    '''
    def __init__(self, data_source: Reader) -> None:
        '''
        Initialize the adapter with a data source.
        :param data_source: An instance of Reader that provides the data to be converted.
        :return: None
        '''
        self.data_source = data_source

    @abstractmethod
    def get_contacts(self) -> List[Contact]:
        '''
        Convert source data into Contact objects.
        :return: A list of Contact objects created from the source data.
        '''
        pass

    def data_format(self) -> str:
        '''
        Return the format of the data being adapted.
        This method should be overridden in subclasses to return the specific data format.
        :return: str: The format of the data (e.g., 'XML', 'JSON', 'CSV').
        '''
        return self.__class__.__name__.replace('ContactsAdapter', '')


class XMLContactsAdapter(ContactsAdapter):
    '''Adapter for converting XML data into Contact objects.'''

    def get_contacts(self) -> List[Contact]:
        '''Convert XML data into Contact objects.

        Reads XML data from the source and converts it into a list of Contact objects.
        Expected XML format:
            <contacts>
                <contact>
                    <full_name>...</full_name>
                    <email>...</email>
                    <phone_number>...</phone_number>
                    <is_friend>true/false</is_friend>
                </contact>
            </contacts>

        :return: List[Contact]: A list of Contact objects created from the XML data.
        '''
        # Parse XML data into an ElementTree object
        root: ET.Element = ET.fromstring(self.data_source.read()) # Read XML data from a file
        # Extract contact information from the XML and create Contact objects
        contacts: List[Contact] = []
        for elem in root.iter():
            if elem.tag == 'contact':
                full_name = elem.find('full_name').text
                email = elem.find('email').text
                phone_number = elem.find('phone_number').text
                is_friend = elem.find('is_friend').text.lower() == 'true'
                contact = Contact(full_name, email, phone_number, is_friend)
                contacts.append(contact)
        return contacts

class JSONContactsAdapter(ContactsAdapter):
    '''Adapter for converting JSON data into Contact objects.'''

    def get_contacts(self) -> List[Contact]:
        '''Convert JSON data into Contact objects.

        Reads JSON data from the source and converts it into a list of Contact objects.
        Expected JSON format:
            {
                "contacts": [
                    {
                        "full_name": "...",
                        "email": "...",
                        "phone_number": "...",
                        "is_friend": true/false
                    }
                ]
            }

        :return: List[Contact]: A list of Contact objects created from the JSON data.
        '''
        # Parse JSON data into a dictionary
        data_dict: dict[str, Any] = json.loads(self.data_source.read()) # Read JSON data from a file
        # Extract contact information from the dictionary and create Contact objects
        contacts: List[Contact] = []
        for contact_data in data_dict['contacts']:
            full_name: str = contact_data['full_name']
            email: str = contact_data['email']
            phone_number: str = contact_data['phone_number']
            is_friend: bool = contact_data['is_friend']
            contact = Contact(full_name, email, phone_number, is_friend)
            contacts.append(contact)
        return contacts


class CSVContactsAdapter(ContactsAdapter):
    '''Adapter for converting CSV data into Contact objects.'''
    def get_contacts(self) -> List[Contact]:
        '''
        Convert CSV data into Contact objects.
        Reads CSV data from the source and converts it into a list of Contact objects.
        Expected CSV format:
            full_name,email,phone_number,is_friend

        :return: List[Contact]: A list of Contact objects created from the CSV data.
        '''
        csv_reader = csv.reader(self.data_source.read().splitlines(), delimiter=',')
        contacts: List[Contact] = []
        for row in csv_reader:
            try:
                full_name, email, phone_number, is_friend_str = row
                is_friend = is_friend_str.lower() == 'true'
                contact = Contact(full_name, email, phone_number, is_friend)
                contacts.append(contact)
            except ValueError:
                print(f"Skipping invalid row: {row}")
        return contacts


class FileReader(Reader):
    '''Concrete implementation of Reader that reads data from a file.'''
    def read(self) -> str:
        '''
        Read the contents of the file and return it as a string.
        :return: str: The contents of the file.
        '''
        with open(self.file_name, 'r') as f:
            return f.read()


class ContactsPrinter:
    '''Class to print contact data from a ContactsAdapter.'''

    def __init__(self, contacts_source: ContactsAdapter) -> None:
        '''
        Initialize the ContactsPrinter with a ContactsAdapter.
        :param contacts_source: An instance of ContactsAdapter that provides contact data.
        :return: None
        '''
        self.contacts_source = contacts_source

    def change_contacts_source(self, contacts_source: ContactsAdapter) -> None:
        '''
        Change the contacts source to a new ContactsAdapter.
        :param contacts_source: An instance of ContactsAdapter that provides contact data.
        :return: None
        '''
        self.contacts_source = contacts_source

    def print_contacts(self) -> None:
        '''
        Print the contact data from the provided ContactsAdapter.
        :return: None
        '''
        print(f"\nContacts from: {self.contacts_source.data_format()}")
        for contact in self.contacts_source.get_contacts():
            print(contact)


if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    printer = ContactsPrinter(None)

    # Example usage with paths relative to script location
    xml_reader = FileReader(os.path.join(script_dir, 'data', 'contacts.xml'))
    # Create an XML adapter and convert the data to a list of Contact objects
    xml_adapter = XMLContactsAdapter(xml_reader)
    # Print the Contact objects
    printer.change_contacts_source(xml_adapter)
    printer.print_contacts()

    json_reader = FileReader(os.path.join(script_dir, 'data', 'contacts.json'))
    # Create a JSON adapter and convert the data to a list of Contact objects
    json_adapter = JSONContactsAdapter(json_reader)
    # Print the Contact objects
    printer.change_contacts_source(json_adapter)
    printer.print_contacts()

    # Test CSV adapter
    csv_reader = FileReader(os.path.join(script_dir, 'data', 'contacts.csv'))
    csv_adapter = CSVContactsAdapter(csv_reader)
    printer.change_contacts_source(csv_adapter)
    printer.print_contacts()
