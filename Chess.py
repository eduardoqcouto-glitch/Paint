import pygame

pygame.init()

tela = pygame.display.set_mode((960, 600))

BOARD_X = 180
BOARD_Y = 0

SQUARE_SIZE = 64

# Board image has 7px padding originally
BOARD_PADDING = 7 * 4

# WHITE PIECES

W_Pawn = pygame.image.load("Peças/W_Pawn.png")
W_Pawn = pygame.transform.scale_by(W_Pawn, 3.0)

W_Bishop = pygame.image.load("Peças/W_Bishop.png")
W_Bishop = pygame.transform.scale_by(W_Bishop, 3.0) 

W_Rook = pygame.image.load("Peças/W_Rook.png")
W_Rook = pygame.transform.scale_by(W_Rook, 3.0)

W_Queen = pygame.image.load("Peças/W_Queen.png")
W_Queen = pygame.transform.scale_by(W_Queen, 3.0) 

W_Knight = pygame.image.load("Peças/W_Knight.png")
W_Knight = pygame.transform.scale_by(W_Knight, 3.0)

W_King = pygame.image.load("Peças/W_King.png")
W_King = pygame.transform.scale_by(W_King, 3.0) 

# BLACK PIECES

B_Pawn = pygame.image.load("Peças/B_Pawn.png")
B_Pawn = pygame.transform.scale_by(B_Pawn, 3.0)

B_Bishop = pygame.image.load("Peças/B_Bishop.png")
B_Bishop = pygame.transform.scale_by(B_Bishop, 3.0) 

B_Rook = pygame.image.load("Peças/B_Rook.png")
B_Rook = pygame.transform.scale_by(B_Rook, 3.0)

B_Queen = pygame.image.load("Peças/B_Queen.png")
B_Queen = pygame.transform.scale_by(B_Queen, 3.0) 

B_Knight = pygame.image.load("Peças/B_Knight.png")
B_Knight = pygame.transform.scale_by(B_Knight, 3.0)

B_King = pygame.image.load("Peças/B_King.png")
B_King = pygame.transform.scale_by(B_King, 3.0) 

board_image = pygame.image.load("Peças/board_plain_05.png")
board_image = pygame.transform.scale_by(board_image, 4.0)

class Piece:
    name: str
    def __init__(self, color, position):
        if color not in "WB":
            raise ValueError("Escolha uma cor válida")
        self.color = color
        if position[0] not in "ABCDEFGH" or position[1] not in "12345678":
            raise ValueError("Escolha uma posição válida")
        self.position = position
    
        self.image = pygame.transform.scale_by(pygame.image.load(f"Peças/{self.color}_{self.name}.png"), 3.0)

    
class Pawn(Piece):
    name = "Pawn"

    def __init__(self, color, position):
        super().__init__(color, position)
        self.en_passant_possible = False

    def attacked_squares(self):
        attacks = []
        file = self.position[0]
        rank = int(self.position[1])
        next_rank = rank + 1 if self.color == "W" else rank - 1

        if not 1 <= next_rank <= 8:
            return attacks

        if file != "H":
            attacks.append(f"{chr(ord(file) + 1)}{next_rank}")
        if file != "A":
            attacks.append(f"{chr(ord(file) - 1)}{next_rank}")

        return attacks

    def valid_moves(self):
        moves = []
        file = self.position[0]
        rank = int(self.position[1])

#       WHITE PAWNS

        if self.color == "W":
            if rank < 8:
                forward_move = f"{file}{rank + 1}"

                if file != "H":
                    right = f"{chr(ord(file) + 1)}{rank + 1}"
                    if right in game_board.peças and game_board.peças[right].color == "B":
                            moves.append(right)

                if file != "A":
                    left = f"{chr(ord(file) - 1)}{rank + 1}"
                    if left in game_board.peças and game_board.peças[left].color == "B":
                        moves.append(left)

                if forward_move not in game_board.peças:
                    moves.append(forward_move)

                if rank == 2:
                    forward_move_2 = f"{file}{rank + 2}"
                    if forward_move_2 not in game_board.peças and forward_move not in game_board.peças:
                        moves.append(forward_move_2)

                if rank == 5:
                    for adjacent_file in [chr(ord(file) - 1), chr(ord(file) + 1)]:
                        if adjacent_file in "ABCDEFGH":
                            adjacent_square = f"{adjacent_file}{rank}"
                            if adjacent_square in game_board.peças:
                                adjacent_piece = game_board.peças[adjacent_square]
                                if isinstance(adjacent_piece, Pawn) and adjacent_piece.color == "B" and adjacent_piece.en_passant_possible:
                                    moves.append(f"{adjacent_file}{rank + 1}")

#       BLACK PAWNS

        else:
            if rank > 1:

                forward_move = f"{file}{rank - 1}"

                if file != "H":
                    right = f"{chr(ord(file) + 1)}{rank - 1}"
                    if right in game_board.peças and game_board.peças[right].color == "W":
                        moves.append(right)

                if file != "A":
                    left = f"{chr(ord(file) - 1)}{rank - 1}"
                    if left in game_board.peças and game_board.peças[left].color == "W":
                        moves.append(left)

                if forward_move not in game_board.peças:
                    moves.append(forward_move)

                if rank == 7:
                    forward_move_2 = f"{file}{rank - 2}"
                    if forward_move_2 not in game_board.peças and forward_move not in game_board.peças:
                        moves.append(forward_move_2)

                if rank == 4:
                    for adjacent_file in [chr(ord(file) - 1), chr(ord(file) + 1)]:
                        if adjacent_file in "ABCDEFGH":
                            adjacent_square = f"{adjacent_file}{rank}"
                            if adjacent_square in game_board.peças:
                                adjacent_piece = game_board.peças[adjacent_square]
                                if isinstance(adjacent_piece, Pawn) and adjacent_piece.color == "W" and adjacent_piece.en_passant_possible:
                                    moves.append(f"{adjacent_file}{rank - 1}")

        return moves

class Knight(Piece):
    name = "Knight"

    def attacked_squares(self):
        attacks = []
        file = self.position[0]
        rank = int(self.position[1])

        potential_attacks = [
            (chr(ord(file) + 1), rank + 2),
            (chr(ord(file) + 2), rank + 1),
            (chr(ord(file) + 2), rank - 1),
            (chr(ord(file) + 1), rank - 2),
            (chr(ord(file) - 1), rank - 2),
            (chr(ord(file) - 2), rank - 1),
            (chr(ord(file) - 2), rank + 1),
            (chr(ord(file) - 1), rank + 2)
        ]

        for attack in potential_attacks:
            if attack[0] in "ABCDEFGH" and 1 <= attack[1] <= 8:
                attacks.append(f"{attack[0]}{attack[1]}")

        return attacks

    def valid_moves(self):
        moves = []
        file = self.position[0]
        rank = int(self.position[1])

        potential_moves = [
            (chr(ord(file) + 1), rank + 2),
            (chr(ord(file) + 2), rank + 1),
            (chr(ord(file) + 2), rank - 1),
            (chr(ord(file) + 1), rank - 2),

            (chr(ord(file) - 1), rank - 2),
            (chr(ord(file) - 2), rank - 1),
            (chr(ord(file) - 2), rank + 1),
            (chr(ord(file) - 1), rank + 2)
        ]

        for move in potential_moves:
            if move[0] in "ABCDEFGH" and 1 <= move[1] <= 8:
                target_square = f"{move[0]}{move[1]}"

                if target_square not in game_board.peças or game_board.peças[target_square].color != self.color:
                    moves.append(target_square)

        return moves

class Bishop(Piece):
    name = "Bishop"

    def attacked_squares(self):
        attacks = []
        file = self.position[0]
        rank = int(self.position[1])
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for direction in directions:
            new_file = file
            new_rank = rank

            while True:
                new_file = chr(ord(new_file) + direction[0])
                new_rank += direction[1]

                if new_file not in "ABCDEFGH" or not 1 <= new_rank <= 8:
                    break

                target_square = f"{new_file}{new_rank}"
                attacks.append(target_square)

                if target_square in game_board.peças:
                    break

        return attacks

    def valid_moves(self):
        moves = []
        file = self.position[0]
        rank = int(self.position[1])

        directions = [
            (1, 1),   # Diagonal up-right
            (1, -1),  # Diagonal down-right
            (-1, 1),  # Diagonal up-left
            (-1, -1)  # Diagonal down-left
        ]

        for square in directions:
            new_rank = rank
            new_file = file

            while True:
                new_file = chr(ord(new_file) + square[0])
                new_rank = new_rank + square[1]
                # Empty
                if new_file in "ABCDEFGH" and 1 <= new_rank <= 8:
                    target_square = f"{new_file}{new_rank}"
                    if target_square not in game_board.peças:
                        moves.append(target_square)
                    elif target_square in game_board.peças and game_board.peças[target_square].color != self.color:
                        moves.append(target_square)
                        break
                    else:
                        break
                else:
                    break

        return moves
class Rook(Piece):
    name = "Rook"

    def __init__(self, color, position):
        super().__init__(color, position)
        self.has_moved = False

    def attacked_squares(self):
        attacks = []
        file = self.position[0]
        rank = int(self.position[1])
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for direction in directions:
            new_file = file
            new_rank = rank

            while True:
                new_file = chr(ord(new_file) + direction[0])
                new_rank += direction[1]

                if new_file not in "ABCDEFGH" or not 1 <= new_rank <= 8:
                    break

                target_square = f"{new_file}{new_rank}"
                attacks.append(target_square)

                if target_square in game_board.peças:
                    break

        return attacks

    def valid_moves(self):
        moves = []
        file = self.position[0]
        rank = int(self.position[1])

        directions = [
            (1, 0),   # Right
            (-1, 0),  # Left
            (0, 1),   # Up
            (0, -1)   # Down
        ]

        for square in directions:
            new_rank = rank
            new_file = file

            while True:
                new_file = chr(ord(new_file) + square[0])
                new_rank = new_rank + square[1]
                # Empty
                if new_file in "ABCDEFGH" and 1 <= new_rank <= 8:
                    target_square = f"{new_file}{new_rank}"
                    if target_square not in game_board.peças:
                        moves.append(target_square)
                    elif target_square in game_board.peças and game_board.peças[target_square].color != self.color:
                        moves.append(target_square)
                        break
                    else:
                        break
                else:
                    break

        return moves

class Queen(Piece):
    name = "Queen"

    def attacked_squares(self):
        attacks = []
        file = self.position[0]
        rank = int(self.position[1])
        directions = [
            (1, 1), (1, -1), (-1, 1), (-1, -1),
            (1, 0), (-1, 0), (0, 1), (0, -1)
        ]

        for direction in directions:
            new_file = file
            new_rank = rank

            while True:
                new_file = chr(ord(new_file) + direction[0])
                new_rank += direction[1]

                if new_file not in "ABCDEFGH" or not 1 <= new_rank <= 8:
                    break

                target_square = f"{new_file}{new_rank}"
                attacks.append(target_square)

                if target_square in game_board.peças:
                    break

        return attacks

    def valid_moves(self):
        moves = []
        file = self.position[0]
        rank = int(self.position[1])

        directions = [
            (1, 1),   # Diagonal up-right
            (1, -1),  # Diagonal down-right
            (-1, 1),  # Diagonal up-left
            (-1, -1),  # Diagonal down-left

            (1, 0),   # Right
            (-1, 0),  # Left
            (0, 1),   # Up
            (0, -1)   # Down
        ]

        for square in directions:
            new_rank = rank
            new_file = file

            while True:
                new_file = chr(ord(new_file) + square[0])
                new_rank = new_rank + square[1]
                # Empty
                if new_file in "ABCDEFGH" and 1 <= new_rank <= 8:
                    target_square = f"{new_file}{new_rank}"
                    if target_square not in game_board.peças:
                        moves.append(target_square)
                    elif target_square in game_board.peças and game_board.peças[target_square].color != self.color:
                        moves.append(target_square)
                        break
                    else:
                        break
                else:
                    break

        return moves

class King(Piece):
    name = "King"

    def __init__(self, color, position):
        super().__init__(color, position)
        self.has_moved = False

    def attacked_squares(self):
        attacks = []
        file = self.position[0]
        rank = int(self.position[1])
        directions = [
            (1, 1), (1, -1), (-1, 1), (-1, -1),
            (1, 0), (-1, 0), (0, 1), (0, -1)
        ]

        for direction in directions:
            new_file = chr(ord(file) + direction[0])
            new_rank = rank + direction[1]

            if new_file in "ABCDEFGH" and 1 <= new_rank <= 8:
                attacks.append(f"{new_file}{new_rank}")

        return attacks

    def valid_moves(self):
        moves = []
        file = self.position[0]
        rank = int(self.position[1])
        directions = [
            (1, 1), (1, -1), (-1, 1), (-1, -1),
            (1, 0), (-1, 0), (0, 1), (0, -1)
        ]

        # CASTLE

        if not self.has_moved and not game_board.still_in_check(self.color):
            # Kingside castle
            kingside_rook_square = f"H{rank}"
            if kingside_rook_square in game_board.peças:
                kingside_rook = game_board.peças[kingside_rook_square]
                if isinstance(kingside_rook, Rook) and not kingside_rook.has_moved:
                    squares_between = [f"F{rank}", f"G{rank}"]
                    if all(square not in game_board.peças for square in squares_between):
                        if not any(game_board.is_square_attacked_by(square, "B" if self.color == "W" else "W") for square in squares_between):
                            moves.append(f"G{rank}-O-O")

            # Queenside castle
            queenside_rook_square = f"A{rank}"
            if queenside_rook_square in game_board.peças:
                queenside_rook = game_board.peças[queenside_rook_square]
                if isinstance(queenside_rook, Rook) and not queenside_rook.has_moved:
                    squares_between = [f"B{rank}", f"C{rank}", f"D{rank}"]
                    if all(square not in game_board.peças for square in squares_between):
                        if not any(game_board.is_square_attacked_by(square, "B" if self.color == "W" else "W") for square in [f"C{rank}", f"D{rank}"]):
                            moves.append(f"C{rank}-O-O-O")


        for direction in directions:
            new_file = chr(ord(file) + direction[0])
            new_rank = rank + direction[1]

            if new_file not in "ABCDEFGH" or not 1 <= new_rank <= 8:
                continue

            target_square = f"{new_file}{new_rank}"

            if target_square not in game_board.peças:
                moves.append(target_square)
            elif game_board.peças[target_square].color != self.color:
                moves.append(target_square)

        return moves

class Board:

    def __init__(self):
        self.peças = {
            # Peças brancas (linha 1)
            "A1": Rook("W", "A1"),
            "B1": Knight("W", "B1"),
            "C1": Bishop("W", "C1"),
            "D1": Queen("W", "D1"),
            "E1": King("W", "E1"),
            "F1": Bishop("W", "F1"),
            "G1": Knight("W", "G1"),
            "H1": Rook("W", "H1"),

            # Peões brancos (linha 2)
            "A2": Pawn("W", "A2"),
            "B2": Pawn("W", "B2"),
            "C2": Pawn("W", "C2"),
            "D2": Pawn("W", "D2"),
            "E2": Pawn("W", "E2"),
            "F2": Pawn("W", "F2"),
            "G2": Pawn("W", "G2"),
            "H2": Pawn("W", "H2"),

            # Peões pretos (linha 7)
            "A7": Pawn("B", "A7"),
            "B7": Pawn("B", "B7"),
            "C7": Pawn("B", "C7"),
            "D7": Pawn("B", "D7"),
            "E7": Pawn("B", "E7"),
            "F7": Pawn("B", "F7"),
            "G7": Pawn("B", "G7"),
            "H7": Pawn("B", "H7"),

            # Peças pretas (linha 8)
            "A8": Rook("B", "A8"),
            "B8": Knight("B", "B8"),
            "C8": Bishop("B", "C8"),
            "D8": Queen("B", "D8"),
            "E8": King("B", "E8"),
            "F8": Bishop("B", "F8"),
            "G8": Knight("B", "G8"),
            "H8": Rook("B", "H8"),
        }

    def stalemate(self, color):
        valid_moves = []

        if self.still_in_check(color):
            return False

        for piece in self.peças.copy().values():
            if piece.color == color:
                valid_moves += self.legal_moves_for(piece)

        if not valid_moves:
            return True
        
        return False

    def is_square_attacked_by(self, square, by_color):
        for piece in self.peças.values():
            if piece.color == by_color and square in piece.attacked_squares():
                return True
        return False

    def still_in_check(self, color):
        king_position = None

        for position, piece in self.peças.items():
            if piece.color == color and isinstance(piece, King):
                king_position = position
                break

        if king_position is None:
            return True

        opponent_color = "B" if color == "W" else "W"
        return self.is_square_attacked_by(king_position, opponent_color)

    def legal_moves_for(self, piece):
        legal_moves = []
        old_position = piece.position

        for move in piece.valid_moves():
            # An en passant capture lands on an empty square, and the pawn
            # it captures sits beside the mover rather than on that square.
            is_en_passant = (
                isinstance(piece, Pawn)
                and move[0] != old_position[0]
                and move not in self.peças
            )
            capture_square = f"{move[0]}{old_position[1]}" if is_en_passant else move
            captured_piece = self.peças.get(capture_square)

            # Kings are never captured in chess.
            if isinstance(captured_piece, King):
                continue

            del self.peças[old_position]
            if is_en_passant:
                del self.peças[capture_square]
            self.peças[move] = piece
            piece.position = move

            still_in_check = self.still_in_check(piece.color)

            del self.peças[move]
            self.peças[old_position] = piece
            piece.position = old_position

            if captured_piece is not None:
                self.peças[capture_square] = captured_piece

            if not still_in_check:
                legal_moves.append(move)

        return legal_moves

    def check_move(self, color):
        # True means checkmate; False means either not in check or there is an escape.
        if not self.still_in_check(color):
            return False

        for piece in self.peças.copy().values():
            if piece.color == color and self.legal_moves_for(piece):
                return False

        return True


def get_square_rect(position):
    
    file = position[0]
    rank = int(position[1])

    column = ord(file) - ord("A")
    row = 8 - rank

    x = BOARD_X + BOARD_PADDING + column * SQUARE_SIZE
    y = BOARD_Y + BOARD_PADDING + row * SQUARE_SIZE

    return pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)

def mouse_to_square(mouse_pos):
    x, y = mouse_pos
    column = (x - BOARD_X - BOARD_PADDING) // SQUARE_SIZE
    row = (y - BOARD_Y - BOARD_PADDING) // SQUARE_SIZE

    if 0 <= column < 8 and 0 <= row < 8:
        file = chr(ord("A") + column)
        rank = str(8 - row)
        return f"{file}{rank}"
    return None

running = True
game_board = Board()

turn = "W"

clock = pygame.time.Clock()

selected_piece = None
selected_square = None
valid_moves = []

while running:
    tela.fill((30, 34, 42))

    tela.blit(board_image, (BOARD_X, BOARD_Y))

    for move in valid_moves:
        square = get_square_rect(move)

        pygame.draw.circle(
            tela,
            (80, 80, 80),
            square.center,
            10
        )

    stalemate = game_board.stalemate(turn)

    if stalemate:
        print("STALEMATE!")
        running = False
    

    for position, piece in game_board.peças.items():
        square = get_square_rect(position)

        piece_rect = piece.image.get_rect()
        piece_rect.midbottom = square.midbottom

        tela.blit(piece.image, piece_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                square = mouse_to_square(event.pos)

                if selected_piece and square in valid_moves:
                    # Move or capture
                    is_en_passant = (
                        isinstance(selected_piece, Pawn)
                        and square[0] != selected_square[0]
                        and square not in game_board.peças
                    )
                    if is_en_passant:
                        captured_pawn_square = f"{square[0]}{selected_square[1]}"
                        del game_board.peças[captured_pawn_square]

                    game_board.peças[square] = selected_piece
                    del game_board.peças[selected_square]
                    selected_piece.position = square

                    if isinstance(selected_piece, (King, Rook)):
                        selected_piece.has_moved = True

                    # A pawn can only be captured en passant on the move right
                    # after it double-steps, so clear the flag on every pawn
                    # before possibly setting it again on this move's pawn.
                    for other_piece in game_board.peças.values():
                        if isinstance(other_piece, Pawn):
                            other_piece.en_passant_possible = False

                    if isinstance(selected_piece, Pawn) and abs(int(square[1]) - int(selected_square[1])) == 2:
                        selected_piece.en_passant_possible = True

                    selected_piece = None
                    selected_square = None
                    valid_moves = []
                    turn = "B" if turn == "W" else "W"

                    if game_board.check_move(turn):
                        print("CHECKMATE!", "White wins!" if turn == "B" else "Black wins!")
                    elif game_board.still_in_check(turn):
                        print("CHECK!")
                elif selected_piece and square in [m[:2] for m in valid_moves if "-O-O" in m]:
                    # Handle castling
                    matching_move = next(m for m in valid_moves if m[:2] == square and "-O-O" in m)

                    if "-O-O-O" in matching_move:
                        # Queenside castle
                        rank = selected_piece.position[1]
                        new_king_square = f"C{rank}"
                        new_rook_square = f"D{rank}"
                        rook_square = f"A{rank}"

                        game_board.peças[new_king_square] = selected_piece
                        del game_board.peças[selected_square]
                        selected_piece.position = new_king_square

                        rook_piece = game_board.peças[rook_square]
                        game_board.peças[new_rook_square] = rook_piece
                        del game_board.peças[rook_square]
                        rook_piece.position = new_rook_square

                    else:
                        # Kingside castle
                        rank = selected_piece.position[1]
                        new_king_square = f"G{rank}"
                        new_rook_square = f"F{rank}"
                        rook_square = f"H{rank}"

                        game_board.peças[new_king_square] = selected_piece
                        del game_board.peças[selected_square]
                        selected_piece.position = new_king_square

                        rook_piece = game_board.peças[rook_square]
                        game_board.peças[new_rook_square] = rook_piece
                        del game_board.peças[rook_square]
                        rook_piece.position = new_rook_square

                    selected_piece.has_moved = True
                    rook_piece.has_moved = True

                    for other_piece in game_board.peças.values():
                        if isinstance(other_piece, Pawn):
                            other_piece.en_passant_possible = False

                    selected_piece = None
                    selected_square = None
                    valid_moves = []
                    turn = "B" if turn == "W" else "W"

                    if game_board.check_move(turn):
                        print("CHECKMATE!", "White wins!" if turn == "B" else "Black wins!")
                    elif game_board.still_in_check(turn):
                        print("CHECK!")

                elif square in game_board.peças:
                    if game_board.peças[square].color == turn:
                        selected_piece = game_board.peças[square]
                        selected_square = square
                        valid_moves = game_board.legal_moves_for(selected_piece)

                else:
                    selected_piece = None
                    selected_square = None
                    valid_moves = []
    pygame.display.flip()
    clock.tick(183248328831482843)

pygame.quit()