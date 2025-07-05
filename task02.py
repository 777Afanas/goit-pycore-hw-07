import re
from collections import UserDict
from datetime import datetime, timedelta
from functools import wraps

# ---------- Класи -----------------

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not re.match(r'^\d{10}$', value):
            raise ValueError("Phone number must be exactly 10 digits")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number):
        phone_to_remove = None
        for phone in self.phones:
            if phone.value == phone_number:
                phone_to_remove = phone
                break
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
        else:
            raise ValueError("Phone number not found")

    def edit_phone(self, old_phone_number, new_phone_number):
        for phone in self.phones:
            if phone.value == old_phone_number:
                phone.value = new_phone_number
                return
        raise ValueError("Phone number not found")

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        birthday_str = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Record not found")

    def get_upcoming_birthdays(self):
        congratulation_dates = []
        today = datetime.today().date()

        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value.date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday.replace(year=today.year + 1)

                if today <= birthday_this_year <= today + timedelta(days=6):
                    if birthday_this_year.weekday() in [5, 6]:
                        days_to_next_monday = 7 - birthday_this_year.weekday()
                        birthday_this_year += timedelta(days=days_to_next_monday)

                    congratulation_dates.append({
                        "name": record.name.value,
                        "congratulation_date": birthday_this_year.strftime("%Y.%m.%d")
                    })

        return congratulation_dates

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

# ---------- Декоратори та хелпери -----------------

def parse_input(user_input):
    cmd, *args = user_input.strip().split()
    cmd = cmd.lower()
    return cmd, args


def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Sorry, contact not found."
        except ValueError as e:
            return f"Value error: {e}"
        except IndexError:
            return "Enter all required parameters, please."
    return inner

# ---------- Команди -----------------

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    if len(args) != 3:
        raise IndexError
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."

@input_error
def show_phone(args, book):
    if len(args) != 1:
        raise IndexError
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    return f"{name}: {'; '.join(p.value for p in record.phones)}"

@input_error
def show_all(book):
    if not book.data:
        return "No contacts found."
    return str(book)

@input_error
def add_birthday(args, book):
    if len(args) != 2:
        raise IndexError
    name, birthday = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book):
    if len(args) != 1:
        raise IndexError
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    if not record.birthday:
        return "No birthday set for this contact."
    return f"{name}'s birthday: {record.birthday}"

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays this week."
    result = ["Upcoming birthdays:"]
    for item in upcoming:
        result.append(f"{item['name']} — {item['congratulation_date']}")
    return "\n".join(result)

# ---------- Головна функція -----------------

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()