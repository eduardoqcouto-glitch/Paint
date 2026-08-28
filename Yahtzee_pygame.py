"""
Yahtzee - pygame edition

A graphical version of the console Yahtzee.py game. Same rules and scoring
logic (upper-section bonus, Yahtzee bonus, five of a kind, etc.), driven by
mouse clicks instead of text input.

Controls:
  - Click "ROLL DICE" to roll (up to 3 rolls per turn).
  - Click a die to hold/unhold it between rolls.
  - Click a category on the scoreboard to score your turn with it
    (available as soon as you've rolled at least once).
""" 

import random
import sys
from collections import Counter

import pygame

# --------------------------------------------------------------------------
# Setup
# --------------------------------------------------------------------------

pygame.init()

WIDTH, HEIGHT = 1000, 650
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Yahtzee")
CLOCK = pygame.time.Clock()
FPS = 60

BG = (18, 87, 71)
PANEL = (245, 245, 240)
PANEL_ALT = (233, 233, 224)
PANEL_ROW_HOVER = (255, 244, 200)
TEXT = (25, 25, 25)
MUTED = (120, 120, 110)
ACCENT = (212, 175, 55)
HELD_COLOR = (212, 160, 20)
DICE_BG = (255, 255, 255)
DICE_HELD_BG = (255, 240, 176)
PIP = (35, 35, 35)
BUTTON = (34, 139, 87)
BUTTON_HOVER = (52, 168, 107)
BUTTON_DISABLED = (120, 120, 120)
WHITE = (255, 255, 255)
GOLD = (212, 175, 55)

FONT_TITLE = pygame.font.SysFont("georgia", 38, bold=True)
FONT_BIG = pygame.font.SysFont("georgia", 25, bold=True)
FONT_MED = pygame.font.SysFont("arial", 20, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 16)
FONT_TINY = pygame.font.SysFont("arial", 13)

CATEGORIES = [
    "Aces", "Twos", "Threes", "Fours", "Fives", "Sixes",
    "Three of a Kind", "Four of a Kind", "Full House",
    "Small Straight", "Large Straight", "Yahtzee", "Chance",
]
UPPER_CATEGORIES = {"Aces", "Twos", "Threes", "Fours", "Fives", "Sixes"}


# --------------------------------------------------------------------------
# Game rules (ported directly from Yahtzee.py)
# --------------------------------------------------------------------------

def calculate_score(category, dice_values):
    count = Counter(dice_values)
    if category == "Aces":
        return count[1] * 1
    if category == "Twos":
        return count[2] * 2
    if category == "Threes":
        return count[3] * 3
    if category == "Fours":
        return count[4] * 4
    if category == "Fives":
        return count[5] * 5
    if category == "Sixes":
        return count[6] * 6
    if category == "Three of a Kind":
        return sum(dice_values) if any(v >= 3 for v in count.values()) else 0
    if category == "Four of a Kind":
        return sum(dice_values) if any(v >= 4 for v in count.values()) else 0
    if category == "Full House":
        return 25 if sorted(count.values()) == [2, 3] else 0
    if category == "Small Straight":
        seqs = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
        return 30 if any(seq <= set(dice_values) for seq in seqs) else 0
    if category == "Large Straight":
        seqs = [{1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}]
        return 40 if any(seq <= set(dice_values) for seq in seqs) else 0
    if category == "Yahtzee":
        return 50 if any(v == 5 for v in count.values()) else 0
    if category == "Chance":
        return sum(dice_values)
    raise ValueError(f"Invalid category {category}")


class Die:
    def __init__(self):
        self.value = None
        self.held = False

    def roll(self):
        if not self.held:
            self.value = random.randint(1, 6)


class Player:
    def __init__(self, name):
        self.name = name
        self.yahtzee_bonus_count = 0
        self.scoreboard = {cat: None for cat in CATEGORIES}

    def available_categories(self):
        return [c for c in CATEGORIES if self.scoreboard[c] is None]

    def upper_total(self):
        return sum(
            score for cat, score in self.scoreboard.items()
            if cat in UPPER_CATEGORIES and score is not None
        )

    def bonus(self):
        return 35 if self.upper_total() >= 63 else 0

    def yahtzee_bonus_score(self):
        return self.yahtzee_bonus_count * 100

    def total(self):
        base = sum(s for s in self.scoreboard.values() if s is not None)
        return base + self.bonus() + self.yahtzee_bonus_score()

    def is_done(self):
        return all(s is not None for s in self.scoreboard.values())


# --------------------------------------------------------------------------
# UI helpers
# --------------------------------------------------------------------------

class Button:
    def __init__(self, rect, text, font=FONT_SMALL):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.enabled = True

    def draw(self, surface):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        if not self.enabled:
            color = BUTTON_DISABLED
        elif hover:
            color = BUTTON_HOVER
        else:
            color = BUTTON
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, TEXT, self.rect, 2, border_radius=10)
        label = self.font.render(self.text, True, WHITE)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, pos):
        return self.enabled and self.rect.collidepoint(pos)


class TextBox:
    def __init__(self, rect, placeholder=""):
        self.rect = pygame.Rect(rect)
        self.text = ""
        self.placeholder = placeholder

    def handle_key(self, event):
        """Returns True if Enter was pressed."""
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key == pygame.K_RETURN:
            return True
        elif event.unicode.isprintable() and len(self.text) < 18:
            self.text += event.unicode
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=8)
        pygame.draw.rect(surface, ACCENT, self.rect, 3, border_radius=8)
        shown = self.text if self.text else self.placeholder
        color = TEXT if self.text else MUTED
        label = FONT_MED.render(shown, True, color)
        surface.blit(label, (self.rect.x + 14, self.rect.y + (self.rect.height - label.get_height()) // 2))


PIP_LAYOUT = {
    1: [(1, 1)],
    2: [(0, 0), (2, 2)],
    3: [(0, 0), (1, 1), (2, 2)],
    4: [(0, 0), (0, 2), (2, 0), (2, 2)],
    5: [(0, 0), (0, 2), (1, 1), (2, 0), (2, 2)],
    6: [(0, 0), (0, 2), (1, 0), (1, 2), (2, 0), (2, 2)],
}


def draw_die(surface, rect, value, held):
    bg = DICE_HELD_BG if held else DICE_BG
    pygame.draw.rect(surface, bg, rect, border_radius=16)
    border_color = HELD_COLOR if held else TEXT
    pygame.draw.rect(surface, border_color, rect, 5 if held else 2, border_radius=16)

    if value is None:
        mark = FONT_BIG.render("?", True, MUTED)
        surface.blit(mark, mark.get_rect(center=rect.center))
        return

    cell = rect.width / 3
    r = max(7, int(rect.width * 0.09))
    for row, col in PIP_LAYOUT[value]:
        cx = rect.x + int(cell * (col + 0.5))
        cy = rect.y + int(cell * (row + 0.5))
        pygame.draw.circle(surface, PIP, (cx, cy), r)

    if held:
        tag = FONT_TINY.render("HELD", True, HELD_COLOR)
        surface.blit(tag, (rect.x + 6, rect.bottom - 20))


def draw_text(surface, text, font, color, pos, center=False):
    label = font.render(text, True, color)
    rect = label.get_rect(center=pos) if center else label.get_rect(topleft=pos)
    surface.blit(label, rect)
    return rect


# --------------------------------------------------------------------------
# Main game
# --------------------------------------------------------------------------

class YahtzeeGame:
    DICE_SIZE = 90
    DICE_GAP = 16

    def __init__(self):
        self.state = "COUNT"
        self.message = ""

        # Player-count screen
        self.count_box = TextBox((WIDTH // 2 - 110, 250, 220, 50), "e.g. 2")

        # Name-entry screen
        self.num_players = 0
        self.names_collected = []
        self.name_box = TextBox((WIDTH // 2 - 180, 250, 360, 50), "Player name")

        # Gameplay state
        self.players = []
        self.current_index = 0
        self.dice = [Die() for _ in range(5)]
        self.rolls_taken = 0
        self.round_number = 1
        self.bonus_applied_this_turn = False

        dice_row_left = 30
        dice_row_width = 560
        total_dice_width = 5 * self.DICE_SIZE + 4 * self.DICE_GAP
        self.dice_start_x = dice_row_left + (dice_row_width - total_dice_width) // 2
        self.dice_y = 160
        self.dice_rects = [
            pygame.Rect(self.dice_start_x + i * (self.DICE_SIZE + self.DICE_GAP), self.dice_y,
                        self.DICE_SIZE, self.DICE_SIZE)
            for i in range(5)
        ]

        roll_btn_w, roll_btn_h = 190, 50
        self.roll_button = Button(
            (self.dice_start_x + (total_dice_width - roll_btn_w) // 2, 280, roll_btn_w, roll_btn_h),
            "ROLL DICE", FONT_MED,
        )
        self.new_game_button = Button((WIDTH // 2 - 120, 500, 240, 54), "NEW GAME", FONT_MED)

        # Scoreboard panel geometry
        self.panel_x = 660
        self.panel_y = 120
        self.panel_w = WIDTH - self.panel_x - 30
        self.row_h = 26
        self.score_rows = {}  # category -> Rect
        self._build_score_rows()

    def _build_score_rows(self):
        y = self.panel_y
        for cat in CATEGORIES:
            self.score_rows[cat] = pygame.Rect(self.panel_x, y, self.panel_w, self.row_h)
            y += self.row_h
        self.bonus_row_y = y + 6
        self.yahtzee_bonus_row_y = self.bonus_row_y + self.row_h
        self.total_row_y = self.yahtzee_bonus_row_y + self.row_h + 8

    # ---- setup flow -----------------------------------------------------

    def start_new_game(self):
        self.state = "COUNT"
        self.message = ""
        self.count_box.text = ""
        self.num_players = 0
        self.names_collected = []
        self.name_box.text = ""
        self.players = []
        self.current_index = 0

    def confirm_player_count(self):
        text = self.count_box.text.strip()
        if text.isdigit() and 1 <= int(text) <= 6:
            self.num_players = int(text)
            self.names_collected = []
            self.name_box.text = ""
            self.state = "NAMES"
        else:
            self.message = "Enter a number of players from 1 to 6."

    def confirm_player_name(self):
        name = self.name_box.text.strip() or f"Player {len(self.names_collected) + 1}"
        self.names_collected.append(name)
        self.name_box.text = ""
        if len(self.names_collected) >= self.num_players:
            self.players = [Player(n) for n in self.names_collected]
            self.current_index = 0
            self.round_number = 1
            self.begin_turn()
            self.state = "PLAY"
        # else stay on NAMES for the next player

    def begin_turn(self):
        for die in self.dice:
            die.held = False
            die.value = None
        self.rolls_taken = 0
        self.bonus_applied_this_turn = False
        self.roll_button.enabled = True
        self.message = f"{self.current_player.name}'s turn - click ROLL DICE to begin."

    @property
    def current_player(self):
        return self.players[self.current_index]

    # ---- gameplay actions -------------------------------------------------

    def roll_dice(self):
        if self.rolls_taken >= 3:
            return
        for die in self.dice:
            die.roll()
        self.rolls_taken += 1
        if self.rolls_taken >= 3:
            self.roll_button.enabled = False
            self.message = "Final roll done. Choose a category to score."
        else:
            self.message = f"Roll {self.rolls_taken} of 3. Click dice to hold them, then roll again or score."

    def toggle_hold(self, index):
        if self.rolls_taken == 0:
            return
        die = self.dice[index]
        die.held = not die.held

    def dice_values(self):
        return [d.value for d in self.dice]

    def score_category(self, category):
        player = self.current_player
        if self.rolls_taken == 0 or player.scoreboard[category] is not None:
            return

        values = self.dice_values()

        if not self.bonus_applied_this_turn:
            if player.scoreboard.get("Yahtzee") == 50 and calculate_score("Yahtzee", values) == 50:
                player.yahtzee_bonus_count += 1
                self.message = "Yahtzee bonus! +100 points."
            self.bonus_applied_this_turn = True

        score = calculate_score(category, values)
        player.scoreboard[category] = score
        if not self.message.startswith("Yahtzee bonus"):
            self.message = f"{player.name} scored {score} points in {category}."

        self.advance_turn()

    def advance_turn(self):
        if all(p.is_done() for p in self.players):
            self.state = "GAMEOVER"
            return

        next_index = (self.current_index + 1) % len(self.players)
        if next_index <= self.current_index:
            self.round_number += 1
        self.current_index = next_index

        while self.current_player.is_done():
            next_index = (self.current_index + 1) % len(self.players)
            if next_index <= self.current_index:
                self.round_number += 1
            self.current_index = next_index

        self.begin_turn()

    # ---- event handling -----------------------------------------------

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        if self.state == "COUNT":
            if event.type == pygame.KEYDOWN:
                if self.count_box.handle_key(event):
                    self.confirm_player_count()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass

        elif self.state == "NAMES":
            if event.type == pygame.KEYDOWN:
                if self.name_box.handle_key(event):
                    self.confirm_player_name()

        elif self.state == "PLAY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if self.roll_button.clicked(pos):
                    self.roll_dice()
                    return
                for i, rect in enumerate(self.dice_rects):
                    if rect.collidepoint(pos):
                        self.toggle_hold(i)
                        return
                for cat, rect in self.score_rows.items():
                    if rect.collidepoint(pos) and self.current_player.scoreboard[cat] is None:
                        self.score_category(cat)
                        return

        elif self.state == "GAMEOVER":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.new_game_button.clicked(event.pos):
                    self.start_new_game()

    # ---- drawing ---------------------------------------------------------

    def draw(self, surface):
        surface.fill(BG)
        if self.state == "COUNT":
            self.draw_count_screen(surface)
        elif self.state == "NAMES":
            self.draw_names_screen(surface)
        elif self.state == "PLAY":
            self.draw_play_screen(surface)
        elif self.state == "GAMEOVER":
            self.draw_gameover_screen(surface)

    def draw_count_screen(self, surface):
        draw_text(surface, "YAHTZEE", FONT_TITLE, GOLD, (WIDTH // 2, 110), center=True)
        draw_text(surface, "How many players?", FONT_BIG, WHITE, (WIDTH // 2, 175), center=True)
        self.count_box.draw(surface)
        draw_text(surface, "Press ENTER to continue", FONT_SMALL, WHITE, (WIDTH // 2, 325), center=True)
        if self.message:
            draw_text(surface, self.message, FONT_SMALL, (255, 120, 120), (WIDTH // 2, 365), center=True)

    def draw_names_screen(self, surface):
        draw_text(surface, "YAHTZEE", FONT_TITLE, GOLD, (WIDTH // 2, 110), center=True)
        n = len(self.names_collected) + 1
        draw_text(surface, f"Enter name for Player {n} of {self.num_players}", FONT_BIG, WHITE,
                  (WIDTH // 2, 175), center=True)
        self.name_box.draw(surface)
        draw_text(surface, "Press ENTER to confirm", FONT_SMALL, WHITE, (WIDTH // 2, 325), center=True)
        if self.names_collected:
            joined = ", ".join(self.names_collected)
            draw_text(surface, f"So far: {joined}", FONT_TINY, WHITE, (WIDTH // 2, 360), center=True)

    def draw_play_screen(self, surface):
        # Title + round
        draw_text(surface, "YAHTZEE", FONT_BIG, GOLD, (30, 18))
        draw_text(surface, f"Round {self.round_number}", FONT_SMALL, WHITE, (30, 56))

        # Player list top-right
        list_x = WIDTH - 30
        y = 20
        for i, p in enumerate(self.players):
            color = GOLD if i == self.current_index else WHITE
            label = f"{'>' if i == self.current_index else ' '} {p.name}: {p.total()}"
            r = draw_text(surface, label, FONT_SMALL, color, (list_x, y))
            y += 20

        # Current turn banner
        draw_text(surface, f"{self.current_player.name}'s turn", FONT_MED, WHITE, (30, 96))

        # Dice
        values = self.dice_values()
        for i, rect in enumerate(self.dice_rects):
            draw_die(surface, rect, values[i], self.dice[i].held)

        # Roll button + rolls left
        self.roll_button.draw(surface)
        rolls_left = 3 - self.rolls_taken
        draw_text(surface, f"Rolls left: {rolls_left}", FONT_SMALL, WHITE,
                  (self.roll_button.rect.centerx, self.roll_button.rect.bottom + 20), center=True)
        draw_text(surface, "Click a die to hold/unhold it", FONT_TINY, WHITE,
                  (self.roll_button.rect.centerx, self.roll_button.rect.bottom + 40), center=True)

        # Message bar
        pygame.draw.rect(surface, PANEL_ALT, (20, 390, 590, 65), border_radius=10)
        draw_text(surface, self.message, FONT_SMALL, TEXT, (315, 422), center=True)

        # Scoreboard panel
        self.draw_scoreboard(surface)

    def draw_scoreboard(self, surface):
        player = self.current_player
        mouse_pos = pygame.mouse.get_pos()
        values = self.dice_values()
        can_preview = self.rolls_taken > 0

        panel_rect = pygame.Rect(self.panel_x - 10, self.panel_y - 40,
                                  self.panel_w + 20, self.total_row_y - self.panel_y + 80)
        pygame.draw.rect(surface, PANEL, panel_rect, border_radius=10)
        draw_text(surface, f"{player.name}'s Scoreboard", FONT_SMALL, TEXT,
                  (panel_rect.centerx, self.panel_y - 20), center=True)

        for i, cat in enumerate(CATEGORIES):
            rect = self.score_rows[cat]
            score = player.scoreboard[cat]
            available = score is None
            row_bg = PANEL_ALT if i % 2 == 0 else PANEL
            if available and can_preview and rect.collidepoint(mouse_pos):
                row_bg = PANEL_ROW_HOVER
            pygame.draw.rect(surface, row_bg, rect)

            draw_text(surface, cat, FONT_TINY, TEXT, (rect.x + 10, rect.y + 8))

            if score is not None:
                shown = str(score)
                color = TEXT
            elif can_preview:
                shown = str(calculate_score(cat, values))
                color = MUTED
            else:
                shown = "-"
                color = MUTED
            draw_text(surface, shown, FONT_TINY, color, (rect.right - 40, rect.y + 8))

        pygame.draw.rect(surface, PANEL_ALT, (self.panel_x, self.bonus_row_y, self.panel_w, self.row_h))
        draw_text(surface, "Upper Bonus (63+)", FONT_TINY, TEXT, (self.panel_x + 10, self.bonus_row_y + 8))
        draw_text(surface, str(player.bonus()), FONT_TINY, TEXT, (self.panel_x + self.panel_w - 40, self.bonus_row_y + 8))

        pygame.draw.rect(surface, PANEL_ALT, (self.panel_x, self.yahtzee_bonus_row_y, self.panel_w, self.row_h))
        draw_text(surface, "Yahtzee Bonus", FONT_TINY, TEXT, (self.panel_x + 10, self.yahtzee_bonus_row_y + 8))
        draw_text(surface, str(player.yahtzee_bonus_score()), FONT_TINY, TEXT,
                  (self.panel_x + self.panel_w - 40, self.yahtzee_bonus_row_y + 8))

        pygame.draw.rect(surface, GOLD, (self.panel_x, self.total_row_y, self.panel_w, self.row_h + 4), border_radius=4)
        draw_text(surface, "TOTAL", FONT_SMALL, TEXT, (self.panel_x + 10, self.total_row_y + 6))
        draw_text(surface, str(player.total()), FONT_SMALL, TEXT,
                  (self.panel_x + self.panel_w - 50, self.total_row_y + 6))

    def draw_gameover_screen(self, surface):
        draw_text(surface, "GAME OVER", FONT_TITLE, GOLD, (WIDTH // 2, 100), center=True)
        ranked = sorted(self.players, key=lambda p: p.total(), reverse=True)
        y = 170
        for rank, p in enumerate(ranked, start=1):
            color = GOLD if rank == 1 else WHITE
            draw_text(surface, f"{rank}. {p.name} - {p.total()} points", FONT_BIG, color,
                      (WIDTH // 2, y), center=True)
            y += 45
        self.new_game_button.draw(surface)

    def run(self):
        while True:
            for event in pygame.event.get():
                self.handle_event(event)
            self.draw(SCREEN)
            pygame.display.flip()
            CLOCK.tick(FPS)


if __name__ == "__main__":
    YahtzeeGame().run()
