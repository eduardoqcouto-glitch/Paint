import random
import time
from collections import Counter

class Dice:
    def __init__(self, sides=6, valor=1):
        self.valor = valor
        self.sides = sides
        self.held = False

    def roll(self):
        if not self.held:
            self.valor = random.randint(1, self.sides)
        return self.valor

class Player:
    def __init__(self, name):
        self.name = name
        self.Yahtzee_bonus_count = 0
        self.scoreboard = {
            "Aces": None,
            "Twos": None,
            "Threes": None,
            "Fours": None,
            "Fives": None,
            "Sixes": None,
            "Three of a Kind": None,
            "Four of a Kind": None,
            "Full House": None,
            "Small Straight": None,
            "Large Straight": None,
            "Yahtzee": None,
            "Chance": None,
        }

    def available_categories(self):
        return [cat for cat, score in self.scoreboard.items() if score is None]

    def bonus(self):
        upper_section_score = sum(
            score for cat, score in self.scoreboard.items()
            if cat in ["Aces", "Twos", "Threes", "Fours", "Fives", "Sixes"] and score is not None
        )
        return 35 if upper_section_score >= 63 else 0

    def yahtzee_bonus_score(self):
        return self.Yahtzee_bonus_count * 100

    def print_scoreboard(self):
        print(f"\n========== {self.name.upper()} ==========")

        for category, score in self.scoreboard.items():
            shown_score = "-" if score is None else score
            print(f"{category:<20} {shown_score}")

        print(f"{'Upper Bonus':<20} {self.bonus()}")
        print(f"{'Yahtzee Bonus':<20} {self.yahtzee_bonus_score()}")

        total = sum(
            score for score in self.scoreboard.values()
            if score is not None
        )

        total += self.bonus()
        total += self.yahtzee_bonus_score()

        print("-" * 28)
        print(f"{'TOTAL':<20} {total}")
        print("=" * 28)

    def is_game_over(self):
        return all(score is not None for score in self.scoreboard.values())
    
class YahtzeeGame:
    def __init__(self, players):
        self.players = [Player(name) for name in players]
        self.dados = [Dice() for _ in range(5)]
        self.current_player_index = 0
        self.rounds_played = 0

    def print_dice(self):
        dice_art = {
            1: [
                "┌─────┐",
                "│     │",
                "│  ●  │",
                "│     │",
                "└─────┘"
            ],
            2: [
                "┌─────┐",
                "│ ●   │",
                "│     │",
                "│   ● │",
                "└─────┘"
            ],
            3: [
                "┌─────┐",
                "│ ●   │",
                "│  ●  │",
                "│   ● │",
                "└─────┘"
            ],
            4: [
                "┌─────┐",
                "│ ● ● │",
                "│     │",
                "│ ● ● │",
                "└─────┘"
            ],
            5: [
                "┌─────┐",
                "│ ● ● │",
                "│  ●  │",
                "│ ● ● │",
                "└─────┘"
            ],
            6: [
                "┌─────┐",
                "│ ● ● │",
                "│ ● ● │",
                "│ ● ● │",
                "└─────┘"
            ]
        }

        values = self.dice_values()

        for line in range(5):
            time.sleep(0.1)
            print("  ".join(dice_art[value][line] for value in values))

        print("   1        2        3        4        5")

    def roll_dice(self):
        for dado in self.dados:
            dado.roll()

    def hold_dice(self, indices):
        for i, dado in enumerate(self.dados):
            dado.held = i in indices

    def dice_values(self):
        return [d.valor for d in self.dados]

    def reset_dice(self):
        for dice in self.dados:
            dice.held = False
            dice.valor = None
    def play_turn(self, player):
        self.reset_dice()

        player.print_scoreboard()

        for roll in range(1, 4):
            self.roll_dice()
            print(f"\nRoll {roll}:")
            self.print_dice()
            if roll < 3:
                hold_input = input(
                    "Enter numbers of dice to hold (comma-separated), "
                    "or press Enter to roll all: "
                )
                if hold_input:
                    indices = [
                        int(i.strip()) - 1
                        for i in hold_input.split(",")
                        if i.strip().isdigit()
                    ]
                    indices = [i for i in indices if 0 <= i < 5]
                    self.hold_dice(indices)
                else:
                    self.hold_dice([])
            else:
                print("\nFinal roll:")
                self.print_dice()
        if (
            player.scoreboard["Yahtzee"] == 50
            and self.calculate_score("Yahtzee", self.dice_values()) == 50
        ):
            player.Yahtzee_bonus_count += 1
            print("Yahtzee bonus! You scored an additional 100 points.")


        categories = player.available_categories()

        print("\nAvailable categories:")
        for number, cat in enumerate(categories, start=1):
            print(f"{number} - {cat}")


        while True:
            category_input = input("Choose a category to score: ")
            if category_input.isdigit():
                category_number = int(category_input)
                if 1 <= category_number <= len(categories):
                    break
            print("Invalid category. Please choose from available categories.")

        category = categories[category_number - 1]
        score = self.calculate_score(category, self.dice_values())
        player.scoreboard[category] = score

        print(f"Scored {score} points in {category}")
    def calculate_score(self, category, dice_values):
        count = Counter(dice_values)
        if category == "Aces":
            return count[1] * 1
        elif category == "Twos":
            return count[2] * 2
        elif category == "Threes":
            return count[3] * 3
        elif category == "Fours":
            return count[4] * 4
        elif category == "Fives":
            return count[5] * 5
        elif category == "Sixes":
            return count[6] * 6
        elif category == "Three of a Kind":
            if any(v >= 3 for v in count.values()):
                return sum(dice_values)
            return 0
        elif category == "Four of a Kind":
            if any(v >= 4 for v in count.values()):
                return sum(dice_values)
            return 0
        elif category == "Full House":
            if sorted(count.values()) == [2, 3]:
                return 25
            return 0
        elif category == "Small Straight":
            if any(all(num in dice_values for num in seq) for seq in [[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6]]):
                return 30
            return 0
        elif category == "Large Straight":
            if any(all(num in dice_values for num in seq) for seq in [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]]):
                return 40
            return 0
        elif category == "Yahtzee":
            if any(v == 5 for v in count.values()):
                return 50
            return 0
        elif category == "Chance":
            return sum(dice_values)
        else:
            raise ValueError(f"Invalid category {category}")

    def play_game(self):
        while not all(player.is_game_over() for player in self.players):
            current_player = self.players[self.current_player_index]
            print(f"\n{current_player.name}'s turn:")
            self.play_turn(current_player)

            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            self.rounds_played += 1

        print("\nGame Over! Final Scores:")
        for player in self.players:
            total_score = sum(score for score in player.scoreboard.values() if score is not None)
            total_score += player.bonus()
            total_score += player.yahtzee_bonus_score()
            print(f"{player.name}: {total_score} points")

players = []
number_of_players = int(input("How many players are playing?\n>> "))
for i in range(number_of_players):
    player_name = input(f"Enter the name of player {i + 1}: ")
    players.append(player_name)
game = YahtzeeGame(players)
game.play_game()