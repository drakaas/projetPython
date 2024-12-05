from getkey import getkey
from sys import argv


def parse_game(game_file_path: str) -> dict:
     width: int = 0
     height: int = 0
     data: list[str] = []

     try:
          with open(game_file_path, 'r') as file:
               data = [line.strip() for line in file]

          width = len(data[0].split('+')[1])
          height = len(data) - 3
          max_moves: int = int(data[-1])

          #recuperation de notre liste de voitures a partir de la chaine recupérée du fichier 
          car_list: list[list[tuple[int, int], str, int]] = parse_cars(data)

          return {
               'width': width,
               'height': height,
               'cars': car_list,
               'max_moves': max_moves
          }

     except FileNotFoundError:
          print(f"Erreur: Le fichier '{game_file_path}' n'existe pas.")
          exit(1)
     except IOError as e:
          print(f"Erreur : Une erreur  I/O est survenue'{game_file_path}': {e}")
          exit(1)





def parse_cars(data: list[str]) -> list[list[tuple[int, int], str, int]]:
     cars = [line[1:-1] for line in data[1:-2]]
     car_dict: dict[str, list[tuple[int, int], str, int]] = {}


     for row_index, row in enumerate(cars):
          previous = ''
          for col_index, char in enumerate(row):#
               if char == '.':
                    previous = '.'
                    continue
               if char in car_dict:
                    if not car_dict[char][1]:  
                         car_dict[char][1] = 'h' if previous == char else 'v'
                    car_dict[char][2] += 1  
               else:
                    car_dict[char] = [(col_index, row_index), '', 1]  

               previous = char
     #on elimine la lettre liée a chaque voiture et on garde uniquement la liste [(x,y),direction,taille]
     return [value for key, value in sorted(car_dict.items(), key=lambda item: item[0])]



def game_board(game: dict) -> list[list[str]]:
     #initialisation du plateau vide avec la largeur,hauteur
     board: list[list[str]] = [
          ["." for _ in range(game['width'])] for _ in range(game['height'])
     ]    
     colors: list = [
          '\u001b[41m', '\u001b[42m', '\u001b[43m',
          '\u001b[44m', '\u001b[45m', '\u001b[46m'
     ]


     for car_index, car in enumerate(game['cars']):
          #si notre voiture est differente de la lettre A on lui affecte uen des couleurs 'colors' d'une maniere cyclique
          color = colors[(car_index - 1) % len(colors)] if car_index != 0 else '\u001b[47m'
          (col, row) = car[0]
          for _ in range(car[2]):
               board[row][col] = color + chr(ord('A') + car_index) + '\u001b[0m'
               if car[1] == 'v':
                    row += 1
               else:
                    col += 1

     return board



def get_game_str(game: dict, current_move_number: int) -> str:
    game_str: list[list[str]] = game_board(game)
    result = '\n'.join([' '.join(row) for row in game_str])
    return (
        f"Le nombre de mouvements maximal = {game['max_moves']}\n"
        f"Nombre de mouvements restants = {current_move_number}\n"
        f"Mouvements Effectués = {game['max_moves'] - current_move_number}\n{result}"
    )


def validate_move(game: dict, car: list, direction: str) -> tuple[bool, list[int]]:
     width, height = game['width'], game['height']
     (col, row) = car[0]
     orientation = car[1]
     length = car[2]
     directions = ['LEFT', 'RIGHT', 'UP', 'DOWN']

     if direction not in directions:
          return False, []
     
     if (orientation == 'h' and direction not in directions[:2]) or \
          (orientation == 'v' and direction not in directions[2:]):
          return False, []

     if orientation == 'h':#calcule de la distance vers les bord du plateau pour la voiture A 
          car_extent = [col, col + length - 1]
          free_space = [col, width - col - length]
     else:
          car_extent = [row, row + length - 1]
          free_space = [row, height - row - length]

     

     for other in game['cars']:
          if other != car:
               (other_col, other_row) = other[0]
               #si une des voitures passe par le chemin de la voiture A 
               if orientation == 'h' and (other_row == row or (other[1] == 'v' and other_row <= row <= other_row + other[2] - 1)):
                    if other_col < col:#on verifie de quel coté cette voiture passe pour recalculer les mouvements possibles de ce coté
                         free_space[0] = min(free_space[0], col - other_col - 1)
                    else:
                         free_space[1] = min(free_space[1], other_col - car_extent[1] - 1)
               elif orientation == 'v' and (other_col == col or (other[1] == 'h' and other_col <= col <= other_col + other[2] - 1)):
                    if other_row < row:
                         free_space[0] = min(free_space[0], row - other_row - 1)
                    else:
                         free_space[1] = min(free_space[1], other_row - car_extent[1] - 1)
     #la fonction retourne s'il y a un mouvement incoherent ainsi que les cases libres de chaque coté de la voiture A
     return True, free_space



def move_car(game: dict, car_index: int, direction: str) -> bool:
     car: list = game['cars'][car_index]

     valid, free_space = validate_move(game, car, direction)
     directions = ['LEFT', 'RIGHT', 'UP', 'DOWN']

     if not valid:
          return False

     (row, col) = car[0]
     width: int = game['width']
     #si la voiture selectionnée est la voiture A qui se trouve au bord droit du plateau le mouvement est possible
     if direction == 'RIGHT' and car_index == 0 and free_space[1] == 0 and (car[0][0] + car[2] - 1) == (width - 1):
          game['cars'][car_index][0] = (row + 1, col)
          return True

     direction_index: int = directions.index(direction)
     border = direction_index % 2
     #s'il n y a aucune case libre de ce coté on retourne faux
     if free_space[border] == 0:
          return False
     else:
          possible_moves = {
          'LEFT': (-1, 0),
          'RIGHT': (1, 0),
          'UP': (0, -1),
          'DOWN': (0, 1),
     }
          move_row, move_col = possible_moves[direction]
          game['cars'][car_index][0] = (row + move_row, col + move_col)

          return True


def is_win(game: dict) -> bool:
     car_a: list = game['cars'][0]
     width: int = game['width']

     if (car_a[0][0] + car_a[2]) >= width:
          return True
     return False


def play_game(game: dict) -> int:
     cars = [chr(e + ord('A')) for e in range(len(game['cars']))]
     car: str = ''
     turns_left: int = game['max_moves']
     playing: bool = turns_left > 0

     print(get_game_str(game, turns_left))
     while playing:
          key = getkey()

          if key.upper() in cars:
               car = key.upper()
               print(f"Selected car: {car}")

          elif key in ["UP", "DOWN", "LEFT", "RIGHT"]:
               moved = False
               if car != '':
                    moved = move_car(game, cars.index(car.upper()), key)
                    if moved:
                         turns_left -= 1
                    if is_win(game):
                         print(get_game_str(game, turns_left))
                         return 0
                    elif turns_left == 0:
                         return 1
               else:
                    print('Mouvement impossible veuillez choisir une voiture !')
               print(get_game_str(game, turns_left))

          elif key == "ESCAPE":
               print("Exiting...")
               return 2

          else:
               print(f"Invalid input: {key}. Please select a car [{cars[0]}-{cars[-1]}] or a direction.")

     return 1

def show_game(game, moves)->None:
     print(get_game_str(game, moves))


if __name__ == '__main__':
     file_path = argv[1]
     try:
          if not file_path:
               print("erreur fichier manquant")
               exit(1)
          game_dict = parse_game(file_path)
          result = play_game(game_dict)
          if result == 0:
               print("Vous avez gagné")
          elif result == 1:
               print("Vous avez perdu")
          else:
               print("Vous avez abandonné")
     except Exception as e:
          exit(1)
