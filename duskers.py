import argparse
import datetime
import json
import os
import random
import sys
import logging
from dataclasses import dataclass
from typing import List


DEBUG_MODE = False
cls_state = False
savedata = "save_file.json"
high_scores_data = "high_score.json"


logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
log_format = '%(asctime)s %(levelname)s: %(message)s'
console_handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(console_handler)

if DEBUG_MODE:
    logger.info('App Starting')

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

    def __repr__(self):
        class_name = type(self).__name__
        return f"{class_name}(name={self.name})"


if DEBUG_MODE:
    logger.info('Robots initialized')


class LocationObj:
    def __init__(self, num, name, titanium, encounter_rate):
        self.num = num
        self.name = name
        self.titanium = titanium
        self.enc_rate = encounter_rate


if DEBUG_MODE:
    logger.info('Locations initialized')


@dataclass
class HighScore:
    name: str
    titanium: int


@dataclass
class HighScoreList:
    scores: List[HighScore]

    def __init__(self, scores: List[HighScore] = None):
        if scores is None:
            self.scores = []
        else:
            self.scores = scores

    def __iter__(self):
        # Return an iterator that iterates over the scores list
        return iter(self.scores)

    def append_to_high_score(self, name: str, titanium: int):
        # Create a new HighScore object and add it to the scores list
        new_score = HighScore(name, titanium)
        self.scores.append(new_score)
        # Sort the scores list in descending order by titanium values
        self.scores = sorted(self.scores, key=lambda score: score.titanium, reverse=True)

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
        self.num = 1
        self.debug = DEBUG_MODE
        self.game_state = True
        self.name = None
        self.titanium = 0
        self.robots = 0
        self.robot_list = []

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
        self.explored_locations = []

        # Initialize upgrade state:
        self. titanium_visible = False
        self.encounter_rate_visible = False

        self.game_dict = {}
        self.high_scores_obj = HighScoreList([])

        if DEBUG_MODE:
            logger.info('Game State initialized')
    def create_new_robot(self):
        # Create a new robot with a name based on the current count of robot objects
        if DEBUG_MODE:
            logger.info('New Robot Created')
        new_robot = Robot(f"Robot{self.robots}", random.choice([shape1, shape2, shape3]))
        self.robots += 1
        return new_robot

    def print_robot_list(self):
        print(self.robot_list)
    def main_menu(self):
        # Model While() loop for validating user input, should refactor all the other sub-menus to read like this.
        cls()
        self.LoadHighScore()

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
                self.titanium = 0
                self.robots = 0
                self.robot_list = [self.create_new_robot(), self.create_new_robot(), self.create_new_robot()]
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
                #command = (input("Your command:\n")).lower()

    def play_sub_menu(self):
        # Trying a different way of validating and catching invalid user input to see if I like it better.
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
        count = 0
        print("\tHIGH SCORES\n")

        # Sort the high scores in descending order by titanium values
        sorted_scores = sorted(self.high_scores_obj, key=lambda score: score.titanium, reverse=True)

        # Determine the minimum score (if any)
        min_score = min(sorted_scores, key=lambda score: score.titanium).titanium if sorted_scores else 0
        min_score_name = next((score.name for score in sorted_scores if score.titanium == min_score), "")

        # Ensure there are at least 10 high scores by padding with the minimum score
        while len(sorted_scores) < 10:
            sorted_scores.append(HighScore(min_score_name, min_score))

        # Print the top 10 high scores
        for count, jawn in enumerate(sorted_scores[:10], start=1):
            print(f"({count}) {jawn.name} {jawn.titanium}")

        print("\n\t[Back]")
        if input().lower() == "back" :
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
            sys.exit(0)
        if option == "exit" or option == "e":
            print("Thanks for playing, bye!")
            sys.exit(0)

    def hub(self):
        cls()
        if self.debug:
            self.print_debug()
        print("+==============================================================================+")
        print_robots(*self.robot_list)
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
            self.upgrade()
        if option == "save" or option == "s":
            self.save_menu()
        if option == "m" or option == "menu":
            self.hub_menu()

    def explore(self):
        if DEBUG_MODE:
            logger.info('Calling explore()')
        def deploy():
            print("Deploying Robots")
            second_rand = random.random()
            if DEBUG_MODE:
                logger.info(f'second_rand = {second_rand}')
            if second_rand < place.enc_rate:
                print("Enemy robots...")
                self.robots -= 1
                self.robot_list.pop()
                if self.robots == 0:
                    self.high_scores_obj.append_to_high_score(self.name, self.titanium)
                    self.SaveHighScore()
                    print("Mission aborted, the last robot lost...")
                    print("|==============================|")
                    print("|          GAME OVER!          |")
                    print("|==============================|")

                    self.main_menu()
                else:
                    print(f"{place.name} explored successfully, 1 robot lost...")
                    print(f"Acquired {place.titanium} lumps of titanium")
                    self.titanium += place.titanium
                    self.hub()
            else:
                print(f"{place.name} explored successfully, with no damage taken")
                print(f"Acquired {place.titanium} lumps of titanium")
                self.titanium += place.titanium
                self.hub()

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
            output_string = ""
            for place in self.explored_locations:
                place_info = f"[{place.num}] {place.name}"

                if self.titanium_visible:
                    place_info += f" Titanium: {place.titanium}"

                if self. encounter_rate_visible:
                    place_info += f" Encounter rate: {round(place.enc_rate*100)}%"

                output_string += place_info + "\n"

            print(output_string)

            print("[S] to continue searching")
            user_input = input("Your command: ")

            if user_input == "back" or user_input == "back":
                self.hub()

            elif user_input == "s":
                try:
                    self.explored_locations.append(next(location_gen))
                    print("Searching")
                # When there are no more places in the list for the generator
                except StopIteration:
                    if DEBUG_MODE:
                        logger.info('Reached end of places')
                    while True:

                        if user_input == "s":
                            print("Nothing more in sight.")
                            print("[Back]")
                            user_input = input("Your command: ")

                        # A valid place selected, deploy robots
                        elif user_input in [str(location.num) for location in self.explored_locations]:
                            deploy()
                        elif user_input == "back" or user_input == "back":
                            self.hub()
                        else:
                            print("Invalid input.")
                            break

            elif user_input in [str(location.num) for location in self.explored_locations]:
                deploy()
            else:
                print("Invalid input.")
                continue

    def location_generator(self, locations):
        num_locations = random.randint(1, 9)
        for name in range(num_locations):
            name = random.choice(locations)
            titanium = random.randint(10, 100)
            enc_rate = random.random()
            yield LocationObj(self.num, name, titanium, enc_rate)
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
                        if DEBUG_MODE:
                            self.print_debug()
                        self.hub()
            elif slot == "back":
                self.main_menu()

    def save_menu(self):
        while True:

            self.pick_slot(savedata)
            print("Your Command:")
            slot = input("")

            if slot in ["1", "2", "3"]:
                self.save(savedata,slot)
                print("|==============================|")
                print("|    GAME SAVED SUCCESSFULLY   |")
                print("|==============================|")
                self.hub()
            elif slot == "back":
                self.hub()
            else:
                print("Invalid slot number, choose 1, 2, or 3")
    def create_savedata(self, filename):
        blank_game_dict = {'slots': {'1': [{'Name': None, 'Titanium': None, 'Robots': None, 'Last Save': None, "titanium_visible": False, "encounter_rate_visible": False}], '2': [{'Name': None, 'Titanium': None, 'Robots': None, 'Last Save': None, "titanium_visible": False, "encounter_rate_visible": False}], '3': [{'Name': None, 'Titanium': None, 'Robots': None, 'Last Save': None, "titanium_visible": False, "encounter_rate_visible": False}]}}

        with open(filename, 'w') as f:
            f.write((json.dumps(blank_game_dict, indent=2, default=str)))


    def pick_slot(self, filename):
        def printslots():
            with open(filename, 'r') as f:
                self.game_dict = json.load(f)
                print("\tSelect a save slot:")
                for slotnum in self.game_dict["slots"]:
                    for item in self.game_dict["slots"][slotnum]:
                        if item['Name'] is None:
                            print(f"\t[{slotnum}] empty")
                        else:
                            print(f"\t[{slotnum}] {item['Name']} Titanium: {item['Titanium']} Robots: {item['Robots']} Last Save: {item['Last Save']} Upgrades: ", end='')
                            print("Titanium_visible" if item['titanium_visible'] else "", end=" ")
                            print("Enemy_info" if item['encounter_rate_visible'] else "",)

        try:
            printslots()
        except json.decoder.JSONDecodeError:
            if DEBUG_MODE:
                logger.info('hit json.decoder.JSONDecodeError, creating savedata JSON')
            self.create_savedata(savedata)
            printslots()
        except FileNotFoundError:
            if DEBUG_MODE:
                logger.info('hit FileNotFoundError, creating savedata JSON')
            self.create_savedata(savedata)
            printslots()




    def save(self, filename, slotnum):
        last_save = datetime.datetime.now()
        formatted_dt = last_save.strftime('%Y-%m-%d %H:%M')

        with open(filename, 'r') as f:
            self.game_dict = json.load(f)

            for item in self.game_dict["slots"][slotnum]:
                item["Name"] = self.name
                item["Titanium"] = self.titanium
                item["Robots"] = self.robots
                item["Last Save"] = formatted_dt
                item["titanium_visible"] = self.titanium_visible
                item["encounter_rate_visible"] = self.encounter_rate_visible

        with open(filename, 'w') as f:
            f.write((json.dumps(self.game_dict, indent=2, default=str)))

    def load(self, filename, slotnum):
        try:
            with open(filename, 'r') as f:
                self.game_dict = json.load(f)

                for item in self.game_dict["slots"][slotnum]:
                    if item['Name'] is None:
                        print(f"Empty slot!")
                        return "Empty slot!"

                    else:
                        self.name = item["Name"]
                        self.titanium = item["Titanium"]
                        self.robots = 0
                        self.last_save = item["Last Save"]
                        self.titanium_visible = item["titanium_visible"]
                        self.encounter_rate_visible = item["encounter_rate_visible"]
                        self.robot_list = []
                        for bot in range(1, item["Robots"]+1):
                            self.robot_list.append(self.create_new_robot())

        except json.decoder.JSONDecodeError:
            print("Empty slot!")
            return "Empty slot!"

    def upgrade(self):
        cls()
        print("|================================|")
        print("|          UPGRADE STORE         |")
        print("|                         Price  |")
        print("| [1] Titanium Scan         250  |")
        print("| [2] Enemy Encounter Scan  500  |")
        print("| [3] New Robot            1000  |")
        print("|                                |")
        print("| [Back]                         |")
        print("|================================|")

        while True:
            choice = input("Your command:")

            if choice =="1":
                if self.titanium < 250:
                    print("Not enough titanium!")
                else:
                    self.titanium_visible = True
                    self.titanium -= 250
                    print("Purchase successful. You can now see how much titanium you can get from each found location.")
                    self.hub()

            elif choice == "2":
                if self.titanium < 500:
                    print("Not enough titanium!")
                else:
                    self.encounter_rate_visible = True
                    self.titanium -= 500
                    print("Purchase successful. You will now see how likely you will encounter an enemy at each found location.")
                    self.hub()

            elif choice == "3":
                if self.titanium < 1000:
                    print("Not enough titanium!")
                else:
                    self.titanium -= 1000
                    self.robot_list.append(self.create_new_robot())
                    print("Purchase successful. You now have an additional robot")
                    self.hub()

            elif choice.lower() == "back" or choice.lower() == "b":
                self.hub()
            else:
                print("Invalid input.")


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
        logger.info(f"Number of Robots: {self.robots}")
        logger.info(f"Robots List: {self.robot_list}")
        logger.info(f"titanium_visible: {self.titanium_visible}")
        logger.info(f"encounter_rate_visible: {self.encounter_rate_visible}")
        logger.info(f"Last save: {self.last_save}")
        logger.info("***********************************")

    def SaveHighScore(self):
        jsonified_highscores = json.dumps(self.high_scores_obj, default=lambda o: o.__dict__, indent=4)
        with open(high_scores_data, "w") as f:
            f.write(jsonified_highscores)

    def LoadHighScore(self):
        try:
            with open(high_scores_data, "r") as f:
                json_data = json.load(f)
                score_dicts = json_data['scores']
                hslist = [HighScore(**score_dict) for score_dict in score_dicts]
                #self.high_scores_obj = sorted(hslist, key=lambda score: score.titanium, reverse=True)
                self.high_scores_obj = HighScoreList(hslist)
        except json.decoder.JSONDecodeError:
            if DEBUG_MODE:
                logger.info('hit json.decoder.JSONDecodeError for HighScores, using empty High Score Obj')
                self.high_scores_obj = HighScoreList([])
        except FileNotFoundError:
            if DEBUG_MODE:
                logger.info('hit FileNothFoundError for HighScores, using empty High Score Obj')
                self.high_scores_obj = HighScoreList([])

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

# hs1 = HighScore("Bayan1", 11)
# hs2 = HighScore("bayan2", 22)
# hs3 = HighScore("bayan3", 33)
# hslist = HighScoreList([hs1, hs2, hs3])
# game.high_scores_obj = hslist
# game.SaveHighScore()

#game.LoadHighScore()
#print(game.high_scores_obj)