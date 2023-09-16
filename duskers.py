import argparse
import datetime
import json
import os
import random
import sys
import logging

DEBUG_MODE = False
cls_state = False
savedata = "save_file.json"

logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
log_format = '%(asctime)s %(levelname)s: %(message)s'
console_handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(console_handler)
#logger.info('App Starting')

shape1 = \
    ("\
░░░░░█▀▀█▄░░░░░\n\
░░░░█░░░▄██░░░░\n\
░░░█░░▐█░░░░░░░\n\
░░░█░░░░▀█░░░░░\n\
░░░░▀█▄▄▄▄█░░░░\
")

shape2 = \
    ("\
░░░░░░░▄░░░░░░░\n\
░░█░░░███░░░█░░\n\
░░░▀███░███▀░░░\n\
░░░░██░░░██░░░░\n\
░░░░███░███░░░░\
")

shape3 = \
    ("\
────▄▄────▄▄───\n\
▄▄▄─██▌──▐██──▄\n\
████────────███\n\
─████▄▄▄▄▄█████\n\
──███████████▀─\
")


class Robot:
    def __init__(self, name, shape):
        self.name = name
        self.shape = shape


robot1 = Robot("Pacman", shape1)
robot2 = Robot("Oogie Boogie", shape2)
robot3 = Robot("happy", shape3)
#logger.info('Robots initialized')


class LocationObj:
    def __init__(self, num, name, titanium):
        self.num = num
        self.name = name
        self.titanium = titanium


def cls():
    if cls_state:
        os.system('cls' if os.name == 'nt' else 'clear')
    else:
        pass


def print_robots(*robots):
    # Create a list of lines for each robot's shape
    lines = [robot.shape.split('\n') for robot in robots]

    # Check if all robots have the same number of lines
    num_lines = len(lines[0])
    for robot_lines in lines[1:]:
        if len(robot_lines) != num_lines:
            raise ValueError("All robots must have the same number of lines in their shapes")

    # Print the shapes side by side horizontally with " | " between them
    for i in range(num_lines):
        for j, robot_lines in enumerate(lines):
            print(robot_lines[i], end="")
            if j < len(lines) - 1:
                print(" | ", end="")
        print()  # Move to the next line for the next row


class Game:
    def __init__(self, seed, min_duration, max_duration, locations):
        self.last_save = None
        self.slot = 1
        self.num = 1
        self.debug = DEBUG_MODE
        self.game_state = True
        self.name = None
        self.titanium = 0
        self.robots = 3

        self.seed = seed
        self.min_duration = min_duration
        self.max_duration = max_duration

        # Get the list of locations, replace _ with space
        self.locations = list(locations.split(','))
        for i in range(len(self.locations)):
            self.locations[i] = self.locations[i].replace('_', ' ')

        # Initialize the random seed here
        random.seed(self.seed)

        # Initialize exploration-related variables
        self.explore_count = 0
        self.explored_locations = []
        self.place_dict = {}

    def main_menu(self):
        cls()
        while self.game_state:
            if self.debug:
                self.print_debug()
            print("+=======================================================================+")
            print("\
            ╭━━╮╭━━━┳╮╱╱╭┳━━━┳━╮╱╭╮╱╭╮╭╮╱╱╱╱╱╭━━━╮╱╱╱╱╱╭╮╱╱╱╱╱╱╭╮\n\
            ┃╭╮┃┃╭━╮┃╰╮╭╯┃╭━╮┃┃╰╮┃┃╭╯╰┫┃╱╱╱╱╱┃╭━╮┃╱╱╱╱╱┃┃╱╱╱╱╱╭╯╰╮\n\
            ┃╰╯╰┫┃╱┃┣╮╰╯╭┫┃╱┃┃╭╮╰╯┃╰╮╭┫╰━┳━━╮┃┃╱╰╋━━┳━━┫┃╭━━┳━┻╮╭╯\n\
            ┃╭━╮┃╰━╯┃╰╮╭╯┃╰━╯┃┃╰╮┃┃╱┃┃┃╭╮┃┃━┫┃┃╱╭┫╭╮┃╭╮┃┃┃┃━┫━━┫┃\n\
            ┃╰━╯┃╭━╮┃╱┃┃╱┃╭━╮┃┃╱┃┃┃╱┃╰┫┃┃┃┃━┫┃╰━╯┃╰╯┃╰╯┃╰┫┃━╋━━┃╰╮\n\
            ╰━━━┻╯╱╰╯╱╰╯╱╰╯╱╰┻╯╱╰━╯╱╰━┻╯╰┻━━╯╰━━━┻━━┻━━┻━┻━━┻━━┻━╯\n\
            \t\t(Survival ASCII Strategy Game)")
            print("+=======================================================================+")
            print("[New] Game")
            print("[Load] Game")
            print("[High] Scores")
            print("[Help]")
            print("[Exit]")

            command = (input("Your command:\n")).lower()

            if command == "new" or command == "n":
                self.name = None
                self.play_sub_menu()
            elif command == "load" or command == "l":
                self.load_menu()
            elif command == "high scores" or command == "high" or command == "hi" or command == "h":
                self.high_scores()
            elif command == "help" or command == "h":
                self.help_menu()
            elif command == "exit" or command == "e":
                print("Thanks for playing, bye!")
                sys.exit(0)

            else:
                print("Invalid input")
                command = (input("Your command:\n")).lower()

    def play_sub_menu(self):
        cls()
        if self.name is None:
            self.name = input("Enter your name:")
            print(f"Greetings, commander {self.name}!")
        else:
            print(f"Welcome back {self.name}!")
        print(f"Are you ready to begin?\n\t[Yes] [No] Return to Main[Menu]")
        begin = input("Your command:").lower()
        while begin not in ["yes", "no", "menu", "y", "n", "m"]:
            print("Invalid input. Please enter 'Yes' or 'No'.")
            begin = input("Your command: ").lower()
        while begin == "no" or begin == "n":
            print("How about now.\nAre you ready to begin?\n\t[Yes] [No] Return to Main[Menu]")
            begin = input("Your command: ").lower()
        if begin == "yes" or begin == "y":
            self.hub()
        elif begin == "menu" or begin == "m":
            self.main_menu()

    def high_scores(self):
        cls()
        print("There are no scores to display")
        print("\t[Back]")
        if input().lower() == "back":
            self.main_menu()

    def help_menu(self):
        cls()
        print("Coming SOON! Thanks for playing!")
        sys.exit(0)

    def hub_menu(self):
        cls()
        print("|==========================|")
        print("|            MENU          |")
        print("|                          |")
        print("| [Back] to game           |")
        print("| Return to [Main] Menu    |")
        print("| [Save] and exit          |")
        print("| [Exit] game              |")
        print("|==========================|")

        option = input("Your command:").lower()

        while option not in ["back", "b", "m", "menu", "s", "save", "e", "exit"]:
            print("Invalid input.")
            option = input("Your command: ").lower()
        if option == "back" or option == "b":
            self.hub()
        if option == "main" or option == "m":
            self.main_menu()
        if option == "save" or option == "s":
            self.save_menu()
        if option == "exit" or option == "e":
            print("Thanks for playing, bye!")
            sys.exit(0)

    def hub(self):
        cls()
        if self.debug:
            self.print_debug()
        print("\n+==============================================================================+")
        print_robots(robot1, robot2, robot3)
        print("+==============================================================================+")
        print(f"| Titanium: {self.titanium}\t\t\t\t\t\t\t\t       |")
        print("+==============================================================================+")
        print("| \t\t[Ex]plore\t\t\t[Up]grade\t\t       |")
        print("| \t\t[Save]\t\t\t\t[M]enu\t\t\t       |")
        print("+==============================================================================+")

        option = input("Your command:").lower()
        while option not in ["ex", "explore", "e", "up", "upgrade", "u", "save", "s", "m", "menu"]:
            print("Invalid input.")
            option = input("Your command: ").lower()
        if option == "ex" or option == "explore" or option == "e":
            self.explore()
        if option == "up" or option == "upgrade" or option == "u":
            print("Coming SOON! Thanks for playing!")
            sys.exit(0)
        if option == "save" or option == "s":
            self.save_menu()
        if option == "m" or option == "menu":
            self.hub_menu()

    def explore(self):
        cls()
        if self.debug:
            self.print_debug()

        # clear list of explored locations every time we enter explore()
        self.explored_locations.clear()
        self.num = 1

        print("Searching")

        # Generator object to give a random place from self.locations
        location_gen = self.location_generator(self.locations)

        # Adding the new place to the explored list
        self.explored_locations.append(next(location_gen))

        while True:

            for place in self.explored_locations:
                print(f"[{place.num}] {place.name}")
            print("[S] to continue searching")
            user_input = input("Your command: ")

            if user_input == "back":
                self.hub()

            if user_input == "s":
                try:
                    self.explored_locations.append(next(location_gen))
                    print("Searching")
                # When there are no more places in the list for the generator
                except StopIteration:
                    while user_input == "s":
                        print("Nothing more in sight.")
                        print("[Back]")
                        user_input = input("Your command: ")

                    # A valid place selected, deploy robots
                    if int(user_input) in [location.num for location in self.explored_locations]:
                        print("Deploying Robots")
                        print(f"{place.name} explored successfully, with no damage taken")
                        print(f"Acquired {place.titanium} lumps of titanium")
                        self.titanium += place.titanium
                        self.hub()

            try:
                if int(user_input) in [location.num for location in self.explored_locations]:
                    print("Deploying Robots")
                    print(f"{place.name} explored successfully, with no damage taken")
                    print(f"Acquired {place.titanium} lumps of titanium")
                    self.titanium += place.titanium
                    self.hub()
            except ValueError:
                print("Invalid input.")
                continue

    def location_generator(self, locations):
        num_locations = random.randint(1, 9)
        for name in range(num_locations):
            name = random.choice(locations)
            yield LocationObj(self.num, name, random.randint(10, 100))
            self.num += 1

    @staticmethod
    def are_all_numbers_int(locations):
        return all(isinstance(location.num, int) for location in locations)

    def load_menu(self):
        while True:

            self.pick_slot(savedata)
            print("Your Command:")
            slot = input("")

            if slot in ["1", "2", "3"]:
                while True:
                    if self.load(savedata, slot) == "Empty slot!":
                        break


                    else:
                        self.load(savedata, slot)
                        print("|==============================|")
                        print("|    GAME LOADED SUCCESSFULLY  |")
                        print("|==============================|")
                        print(f"Welcome back, commander {self.name}!")
                        self.hub()
            elif slot == "back":
                self.main_menu()

    def save_menu(self):
        while True:

            self.pick_slot(savedata)
            print("Your Command:")
            slot = input("")

            if slot in ["1", "2", "3"]:
                if self.load(savedata, slot) == "Empty slot!":
                    self.create_savedata(savedata)
                    self.save(savedata, slot)
                    print("|==============================|")
                    print("|    GAME SAVED SUCCESSFULLY   |")
                    print("|==============================|")
                    self.hub()
                else:
                    self.save(savedata,slot)
                    print("|==============================|")
                    print("|    GAME SAVED SUCCESSFULLY   |")
                    print("|==============================|")
                    self.hub()
            elif slot == "back":
                self.hub()
    def create_savedata(self, filename):
        blank_game_dict = {'slots': {'1': [{'Name': None, 'Titanium': None, 'Robots': None, 'Last Save': None}], '2': [{'Name': None, 'Titanium': None, 'Robots': None, 'Last Save': None}], '3': [{'Name': None, 'Titanium': None, 'Robots': None, 'Last Save': None}]}}

        with open(filename, 'w') as f:
            f.write((json.dumps(blank_game_dict, indent=2, default=str)))


    def pick_slot(self, filename):
        def printslots():
            with open(filename, 'r') as f:
                game_dict = json.load(f)
                print("\tSelect a save slot:")
                for slotnum in game_dict["slots"]:
                    for item in game_dict["slots"][slotnum]:
                        if item['Name'] is None:
                            print(f"\t[{slotnum}] empty")
                        else:
                            print(f"\t[{slotnum}] {item['Name']} Titanium: {item['Titanium']} Robots: {item['Robots']} Last Save: {item['Last Save']}")

        try:
            printslots()
        except json.decoder.JSONDecodeError:
            self.create_savedata(savedata)
            printslots()
        except FileNotFoundError:
            #print("Empty slot!")
            self.create_savedata(savedata)
            printslots()




    def save(self, filename, slotnum):
        last_save = datetime.datetime.now()
        formatted_dt = last_save.strftime('%Y-%m-%d %H:%M')

        with open(filename, 'r') as f:
            game_dict = json.load(f)

            for item in game_dict["slots"][slotnum]:
                item["Name"] = self.name
                item["Titanium"] = self.titanium
                item["Robots"] = self.robots
                item["Last Save"] = formatted_dt

        with open(filename, 'w') as f:
            f.write((json.dumps(game_dict, indent=2, default=str)))

    def load(self, filename, slotnum):
        try:
            with open(filename, 'r') as f:
                game_dict = json.load(f)

                for item in game_dict["slots"][slotnum]:
                    if item['Name'] is None:
                        print(f"Empty slot!")
                        return "Empty slot!"

                    else:
                        self.name = item["Name"]
                        self.titanium = item["Titanium"]
                        self.robots = item["Robots"]
                        self.last_save = item["Last Save"]
        except json.decoder.JSONDecodeError:
            print("Empty slot!")
            return "Empty slot!"




    def print_debug(self):
        logger.info("***********************************")
        logger.info(f"Debug: {self.debug}")
        logger.info(f"Game State: {self.game_state}")
        logger.info(f"Player Name: {self.name}")
        logger.info(f"Seed: {self.seed}")
        logger.info(f"Min_Duration: {self.min_duration}")
        logger.info(f"Max_duration: {self.max_duration}")
        logger.info(f"Locations: {self.locations}")
        logger.info(f"Titanium: {self.titanium}")
        logger.info(f"Robots: {self.robots}")
        logger.info(f"Last save: {self.last_save}")
        logger.info("***********************************")



parser = argparse.ArgumentParser(description="Welcome to Bayan The Coolest, the coolest game ever")

parser.add_argument("seed", type=str, nargs='?', default=69, help="Random seed (default: 69)")
parser.add_argument("min_duration", type=int, nargs='?', default=0, help="Minimum animation duration (default: 0)")
parser.add_argument("max_duration", type=int, nargs='?', default=0, help="Maximum animation duration (default: 0)")
parser.add_argument("locations", type=str, nargs='?', default="Place_A,Place_B,Place_C",
                    help="List of locations, enter as a string separated by commas, such as  High_street,Green_park,Destroyed_Arch")

args = parser.parse_args()

game = Game(
    seed=args.seed,
    min_duration=args.min_duration,
    max_duration=args.max_duration,
    locations=args.locations
)

game.main_menu()
