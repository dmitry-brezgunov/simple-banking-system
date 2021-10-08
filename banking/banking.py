import random
import sqlite3

conn = sqlite3.connect('card.s3db')
cur = conn.cursor()


class Card:
    inn = '400000'

    def __init__(self, card_number, pin, balance=0):
        self.card_number = card_number
        self.pin = pin
        self.balance = balance

    @classmethod
    def generate_number(cls):
        number = cls.inn + str(random.randint(100000000, 999999999))
        number_list = [int(x) for x in number]
        for i in range(len(number_list)):
            if (i + 1) % 2 != 0:
                number_list[i] *= 2
            if number_list[i] > 9:
                number_list[i] -= 9

        for i in range(10):
            if (i + sum(number_list)) % 10 == 0:
                number += str(i)
                break
        return number

    @staticmethod
    def generate_pin():
        pin = str(random.randint(1, 9999))
        if len(pin) < 4:
            pin = ('0' * (4 - len(pin))) + pin
        return pin

    @classmethod
    def create_card(cls):
        card_number = cls.generate_number()
        pin = cls.generate_pin()
        cur.execute(
            '''INSERT INTO card (number, pin) VALUES (?, ?)''',
            (card_number, pin)
        )
        conn.commit()
        return cls(card_number, pin)

    def add_income(self, value):
        self.balance += value
        cur.execute(
            '''UPDATE card SET balance = ? 
            WHERE number = ? AND pin = ?''',
            (self.balance, self.card_number, self.pin)
        )
        conn.commit()

    @staticmethod
    def check_luhn(card_number):
        number_list = [int(x) for x in card_number]
        for i in range(len(number_list) - 1):
            if (i + 1) % 2 != 0:
                number_list[i] *= 2
            if number_list[i] > 9:
                number_list[i] -= 9
        if sum(number_list) % 10 != 0:
            return False
        return True

    @classmethod
    def get_card_from_db(cls, card_number):
        cur.execute(
            '''SELECT number, pin, balance FROM card 
            WHERE number = ?''', [card_number]
        )
        entry = cur.fetchone()
        if entry:
            return cls(*entry)

    def do_transfer(self, card_number):
        if not self.check_luhn(card_number):
            return "Probably you made a mistake in the card number. Please try again!"
        other_card = self.get_card_from_db(card_number)
        if not other_card:
            return "Such a card does not exist."
        print("Enter how much money you want to transfer:")
        value = int(input())
        if value > self.balance:
            return "Not enough money!"
        self.balance -= value
        other_card.balance += value
        cur.execute(
            '''UPDATE card SET balance = ? 
            WHERE number = ? AND pin = ?''',
            (self.balance, self.card_number, self.pin)
        )
        cur.execute(
            '''UPDATE card SET balance = ? 
            WHERE number = ? AND pin = ?''',
            (other_card.balance, other_card.card_number, other_card.pin)
        )
        conn.commit()
        return "Success!"

    def delete_card(self):
        cur.execute(
            '''DELETE FROM card WHERE number = ?''',
            [self.card_number]
        )
        conn.commit()


def create_account():
    card = Card.create_card()
    print("Your card has been created")
    print("Your card number:")
    print(card.card_number)
    print("Your card PIN:")
    print(card.pin)


def log_in():
    print("Enter your card number:")
    card_number = input()
    print("Enter your PIN:")
    pin = input()
    card = Card.get_card_from_db(card_number)
    if not card or card.pin == pin:
        return card


def run():
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS card
            (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, 
            balance INTEGER DEFAULT 0)'''
    )
    conn.commit()
    while True:
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        command = input()

        if command == "1":
            create_account()

        if command == "2":
            card = log_in()
            if not card:
                print("Wrong card number or PIN!")
                continue
            print("You have successfully logged in!")

            while True:
                print("1. Balance")
                print("2. Add income")
                print("3. Do transfer")
                print("4. Close account")
                print("5. Log out")
                print("0. Exit")
                command = input()
                if command == "1":
                    print(f"Balance: {card.balance}")
                if command == "2":
                    print("Enter income:")
                    income = int(input())
                    card.add_income(income)
                    print("Income was added!")
                if command == "3":
                    print("Transfer")
                    print("Enter card number:")
                    card_number = input()
                    print(card.do_transfer(card_number))
                if command == "4":
                    card.delete_card()
                    print("The account has been closed!")
                    break
                if command == "5":
                    print("You have successfully logged out!")
                    break
                if command == "0":
                    print("Bye!")
                    exit()

        if command == "0":
            print("Bye!")
            exit()


if __name__ == "__main__":
    run()

conn.close()
