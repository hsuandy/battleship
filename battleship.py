import os
import pandas as pd
from random import randint, choice
from art import tprint
from rich import print as rprint

# ASCII art found at https://www.asciiart.eu/vehicles/navy, credit to Matthew Bace
ship = '''[red]
                                     |__
                                     |\/
                                     ---
                                     / | [
                              !      | |||
                            _/|     _/|-++'
                        +  +--|    |--|--|_ |-
                     { /|__|  |/\__|  |--- |||__/
                    +---------------___[}-_===_.'____
                ____`-' ||___-{]_| _[}-  |     |_[___\==--
 __..._____--==/___]_|__|_____________________________[___\==--____,------'-.
|                                                                          /
 \_________________________________________________________________________|
[/]'''

# Resize terminal
def initialize_terminal(height = 80, width = 35):
    cmd = f"printf '\e[8;{width};{height}t'"
    os.system(cmd)

# Generate a grid map for the game by creating a dataframe
def create_grid(row, col, sea_icon):
    init_col = [chr(ord('A') + num) for num in range(col)]
    init_row = [sea_icon for num in range(col)]
    grid = pd.DataFrame([init_row for num in range(row)], columns=init_col)
    return grid

# Populate a grid map with ships
def create_fleet_map(grid, fleet_data):
    map = grid.copy()
    occupied = {}

    # Initialize starting coordinate for a ship
    def initialize(ship_size):
        row = randint(0, grid.shape[0] - ship_size)
        col = randint(0, grid.shape[1] - ship_size)
        return row, col

    # Generate dictionary with grid coordinates as key and orientation icon as value for a ship based on size
    def map_ship(ship_size):
        start = initialize(ship_size)
        orientation = randint(0, 1) # Select orientation (0 = horizontal, 1 = vertical)
        coords = {}
        for i in range(ship_size):
            row = start[0]
            col = start[1]
            icon = ''
            if orientation == 0:
                col += i
                icon = '>'
            else:
                row += i
                icon = '^'
            coords[row, col] = icon
        return coords
    
    # Check that ship coordinates do not overlap with existing ship coordinates in occupied dictionary
    def validate_coords(coords, occupied):
        for coord in coords:
            if coord in occupied:
                return False
        return True

    # Populate occupied dictionary with validated ship coordinates
    for size in fleet_data.values():
        while True:
            coords = map_ship(size)
            if validate_coords(coords, occupied):
                for coord, icon in coords.items():
                    occupied[coord] = icon
                break

    # Map validated ship coordinates to fleet grid
    for coord, icon in occupied.items():
        map.iloc[coord] = icon
    return map

def update_fleet_map(fleet_map, fleet_display, target, sea_icon, hit_icon, miss_icon):
    if fleet_map.iloc[target] in (miss_icon, hit_icon):
        raise KeyError
    if fleet_map.iloc[target] == sea_icon:
        fleet_map.iloc[target] = miss_icon
        fleet_display.iloc[target] = miss_icon
        return False
    else:
        fleet_map.iloc[target] = hit_icon
        fleet_display.iloc[target] = hit_icon
        return True

def initialize_hitpoints(fleet):
    return sum([size for size in fleet.values()])

def check_game_state(player_life, opponent_life):
    state = 0
    if player_life == 0 and opponent_life == 0:
        state = 1 # Draw
    elif player_life == 0:
        state = 2 # Player loses
    elif opponent_life == 0:
        state = 3 # Player wins
    return state

def ai_target_selection(target_queue, player_fleet_map):
    if len(target_queue) > 0:
        player_target = choice(target_queue)
        target_queue.remove(player_target)
    else:
        player_row = randint(0, player_fleet_map.shape[0] - 1)
        player_col = randint(0, player_fleet_map.shape[1] - 1)
        player_target = player_row, player_col
    return player_target

def ai_targeting_update(target, p_row_max, p_col_max, targeted_list):
    target_queue = []
    # Check above and below target
    if target[0] + 1 < p_row_max and (target[0] + 1, target[1]) not in targeted_list:
        target_queue.append((target[0] + 1, target[1]))
    if target[0] - 1 >= 0 and (target[0] - 1, target[1]) not in targeted_list:
        target_queue.append((target[0] - 1, target[1]))
    # Check left and right of target
    if target[1] + 1 < p_col_max and (target[0], target[1] + 1) not in targeted_list:
        target_queue.append((target[0], target[1] + 1))
    if target[1] - 1 >= 0 and (target[0], target[1] - 1) not in targeted_list:
        target_queue.append((target[0], target[1] - 1))
    return target_queue

def game_over_screen(game_state):
    os.system('clear')
    if game_state == 1:
        tprint("DRAW")
        rprint("[bold yellow]Mutual destruction, both fleets have been sunk![/]", '\n')
    elif game_state == 2:
        tprint("YOU LOSE")
        rprint("[bold red1]Your opponent has sunk your fleet![/]", '\n')
    elif game_state == 3:
        tprint("YOU WIN")
        rprint(f"[bold green1]{player_name} has triumphed![/]", '\n')
    choice = input("Enter Y to play again, or any other key to quit: ")
    if choice.lower() == 'y':
        return True
    else:
        return False

# Draw UI
def draw_ui():
    print('\n')
    rprint(f'[bold green]{player_name}[/]')
    rprint(f'Damage Points Remaining: [orange1]{player_life}[/]', '\n')
    rprint(player_fleet_map,'\n\n')
    rprint('[bold red]Opponent[/]')
    rprint(f'Damage Points Remaining: [orange1]{opponent_life}[/]', '\n')
    rprint(opponent_fleet_map, '\n') # Print map with opponent fleet coordinates
    rprint(opponent_display, '\n')
    rprint(output_message, '\n')

retry = True

# External game loop for enabling a retry option when game ends
while retry:
    # Attempt to resize terminal (may not work with all terminal types)
    initialize_terminal()
    os.system('clear')

    # Initialize game data
    tprint("BATTLESHIP")
    rprint(ship, '\n')
    print("Welcome to the Naval Battle Simulator.", '\n')
    player_name = input('Enter your name: ') or 'Player'
    player_fleet = {'Carrier': 5, 'Battleship': 4, 'Cruiser': 3, 'Submarine':3, 'Destroyer': 2}
    #player_fleet = {'Cruiser': 3} # Test fleet data
    player_life = initialize_hitpoints(player_fleet)
    opponent_fleet = {'Carrier': 5, 'Battleship': 4, 'Cruiser': 3, 'Submarine':3, 'Destroyer': 2}
    #opponent_fleet = {'Cruiser': 3} # Test fleet data
    opponent_life = initialize_hitpoints(opponent_fleet)
    sea_icon = '·'
    hit_icon = '*'
    miss_icon = '+'
    output_message = ''
    player_display = create_grid(10, 10, sea_icon)
    player_fleet_map = create_fleet_map(player_display, player_fleet)
    opponent_display = create_grid(10, 10, sea_icon)
    opponent_fleet_map = create_fleet_map(opponent_display, opponent_fleet)
    p_row_max = player_fleet_map.shape[0]
    p_col_max = player_fleet_map.shape[1]
    o_row_max = opponent_fleet_map.shape[0]
    o_col_max = opponent_fleet_map.shape[1]
    target_queue = []
    targeted_list = []

    # Internal game loop for running the game
    while True:
        draw_ui()

        # Player turn
        try:
            opp_row = int(input(f'Enter target row value (0 - {o_row_max - 1}): '))
            opp_col = ord(input(f'Enter target column value (A - {chr(ord("@") + o_col_max)}): ').lower()) - 97
            opp_target = opp_row, opp_col
            opp_result = update_fleet_map(opponent_fleet_map, opponent_display, opp_target, sea_icon, hit_icon, miss_icon)
            if opp_result == True:
                output_message = "It's a [green1]hit[/]!"
                opponent_life -= 1
            else:
                output_message = "It's a [yellow]miss[/]!"
        except ValueError:
            output_message = "[red]TARGETING ERROR!\nValue entered is invalid.[/]"
        except TypeError:
            output_message = "[red]TARGETING ERROR!\nValue entered is invalid.[/]"
        except IndexError:
            output_message = "[red]TARGETING ERROR!\nCoordinate entered is out of range.[/]"
        except KeyError:
            output_message = "[yellow]This coordinate has already been targeted.[/]"

        draw_ui()
        input("Opponent's Turn (Press ENTER to continue)")

        # Opponent turn
        player_target = ai_target_selection(target_queue, player_fleet_map)
        while player_target in targeted_list:
            player_target = ai_target_selection(target_queue, player_fleet_map)
        targeted_list.append(player_target)
        player_result = update_fleet_map(player_fleet_map, player_display, player_target, sea_icon, hit_icon, miss_icon)
        if player_result == True:
            output_message = "You've been [red1]hit[/]!"
            player_life -= 1
            target_queue += ai_targeting_update(player_target, p_row_max, p_col_max, targeted_list)
        else:
            output_message = "Opponent [yellow]missed[/]!"

        # Check if there is a winner
        game_state = check_game_state(player_life, opponent_life)
        if game_state > 0:
            retry = game_over_screen(game_state)
            break

        draw_ui()
