# Benjamin Wang (hgf3jq) Thomas Nguyen (eep8uv)
# CS FINAL PROJECT
# PARTNERS:

# Benjamin "Ben" Wang @hgf3jq // High Score: 11120
# Thomas Nguyen @eep8uv

# GAME IDEA:
# Guy moves around in a fixed camera/map/boundaries while zombies/enemies try to attack the guy.
# The guy can shoot projectiles in any of the eight directions (up down left right and diagonals)
# CHANGED: Goal is now to just survive as long as possible
# NAME: Night of the Poorly Made Zombies

# Required:

# USER INPUT: wasd controls character, arrows control aiming/shooting
# START SCREEN: Displays names and instructions
# GAME OVER: Game is lost when the character's health is reduced to 0, game is won when timer ends
# WINDOW SIZE: 800 x 600
# Graphics/Images: Background Images/Character Image/Enemy Images

# Optional:

# Restart from Game Over: When game is lost, press space to restart.
# Enemies: They're the main obstacle and they chase down the players. They continuously spawn throughout the time.
# Sprites: Enemies/Player will have sprites
# Health Bar: Health bar is more like lives, and whenever enemy comes into contact with player, half a life is lost.
# Timer: Player tries to survive for as long as possible, with the timer keeping track for how long the player has been
# alive IN SECONDS

# ADDED SINCE CHECKPOINT 2:
# Game concept went from survive until timer to survive for as long as possible (was more fun that way)
# Code was cleaned up and a lot of functions were created so that the tick(keys) function is more readable
# Sprites for the background, zombies, and player were added
# Interface, Start Screen, and Restart Screen created
# No more collectibles, replaced with sprites

import gamebox
import pygame
import random  # Random number generation
import math  # for enemy algorithm, I'm sure it's fine we can clarify with TA if needed (I used for trig functions)

### DEFINE CAMERA ###
camera = gamebox.Camera(800, 600)

# ----- HELPER SWITCHES, Defaults: Similar to restart() function
game_on = False  # GAME ON: False
level_won = False  # LEVEL WON: False
start = True  # START SCREEN: True
cooldown_shoot = False  # Shooting Cooldown: False
oneshot = False


# ----- DEFINE ENTITIES

# TIMER
timer = 0  # if this is changed, restart function needs to be changed as well, how many seconds in the timer
tickCount = 0  # Helper variable for counting ticks
spawnTick = 10
level = 1

# --- PLAYER
player_speed = 7  # How fast player moves
player_health = 5  # How much health does the player have
lives_list = []  # <Helper array for health>
totalscore = 0  # Total score displayed at the end of the game
# Player sprite images / Taken from https://opengameart.org/content/animated-top-down-survivor-player
player_images = []  # <Helper array for player sprite>
p_image_num = 8
for i in range(p_image_num):
    player_images.append('images/topdown'+str(i)+'.png')
player = gamebox.from_image(400,300,player_images[0])
p_scale = 1/9
player.scale_by(p_scale)
# --- Helper booleans for player sprite
p_move_up = False
p_move_down = False
p_move_left = False
p_move_right = False
p_move_upleft = False
p_move_upright = False
p_move_downleft = False
p_move_downright = False

# --- ENEMIES
enemies = []  # <global enemy array>
enemy_speed = 1.5  # How fast enemies move
enemy_health = 1  # How much health enemies have
enemy_kills = 0  # How many enemies have been killed
wave_number = 2  # How many enemies spawn per wave (exponential)
difficulty_timer = 0  # <Helper Timer for wave spawn and level management>
current_frame = 1  # <Helper variable for zombie sprite>
special_number = wave_number

# --- BULLETS
bullets = []  # <global bullet array>
bullet_speed = 20  # How fast bullets move
bulletCD = 7  # bullet cool-down (in ticks)
CDcount = 0  # cool-down helper variable

# ----- PLAYER CONTROLS -----

# Player Movement
def player_movement(keys):
    '''
    CONTROLS THE PLAYER MOVEMENTS
    :param keys: Player inputs (for this specifically, only wasd will work)
    :return: Moves the player in x/y direction, a fixed distance (player_speed) based on input
    '''

    if pygame.K_w in keys:  # MOVE UP
        if player.y > 10:  # booleans keeps player in boundaries
            player.y -= player_speed
    if pygame.K_s in keys:  # MOVE DOWN
        if player.y < 590:
            player.y += player_speed
    if pygame.K_a in keys:  # MOVE LEFT
        if player.x > 10:
            player.x -= player_speed
    if pygame.K_d in keys:  # MOVE RIGHT
        if player.x < 790:
            player.x += player_speed
# Player Shooting
def player_shoot_commands(keys):
    global p_move_right,p_move_up,p_move_left,p_move_down, p_move_upleft, p_move_upright, p_move_downleft, \
        p_move_downright
    '''
    CONTROLS THE BULLET DIRECTION
    :param keys: Player inputs (for this specifically, only arrow keys will work)
    :return: Calls function 'make_bullet' and gives it a direction based on player input
    EDIT: Also now controls player sprite
    '''
    if pygame.K_UP in keys:
        if pygame.K_LEFT in keys:  # diagonal 'up-left'
            make_bullet(player.x, player.y, 'upleft')
            if not p_move_upleft:
                p_move_up = False
                p_move_down = False
                p_move_left = False
                p_move_right = False
                p_move_upleft = True
                p_move_upright = False
                p_move_downleft = False
                p_move_downright = False
                player.image = player_images[5]
                player.full_size()
                player.scale_by(p_scale)
        elif pygame.K_RIGHT in keys:  # diagonal 'up-right'
            make_bullet(player.x, player.y, 'upright')
            if not p_move_upright:
                p_move_up = False
                p_move_down = False
                p_move_left = False
                p_move_right = False
                p_move_upleft = False
                p_move_upright = True
                p_move_downleft = False
                p_move_downright = False
                player.image = player_images[4]
                player.full_size()
                player.scale_by(p_scale)
        else:
            make_bullet(player.x, player.y, 'up')
            if not p_move_up:  # vertical 'up'
                player.image = player_images[1]
                p_move_up = True
                p_move_down = False
                p_move_left = False
                p_move_right = False
                p_move_upleft = False
                p_move_upright = False
                p_move_downleft = False
                p_move_downright = False
                player.full_size()
                player.scale_by(p_scale)
    elif pygame.K_DOWN in keys:
        if pygame.K_LEFT in keys:  # diagonal 'down-left'
            make_bullet(player.x, player.y, 'downleft')
            p_move_up = False
            p_move_down = False
            p_move_left = False
            p_move_right = False
            p_move_upleft = False
            p_move_upright = False
            p_move_downleft = True
            p_move_downright = False
            player.image = player_images[6]
            player.full_size()
            player.scale_by(p_scale)
        elif pygame.K_RIGHT in keys:  # diagonal 'down-right'
            make_bullet(player.x, player.y, 'downright')
            p_move_up = False
            p_move_down = False
            p_move_left = False
            p_move_right = False
            p_move_upleft = False
            p_move_upright = False
            p_move_downleft = False
            p_move_downright = True
            player.image = player_images[7]
            player.full_size()
            player.scale_by(p_scale)
        else:
            make_bullet(player.x, player.y, 'down')
            if not p_move_down:  # vertical 'down'
                player.image = player_images[3]
                p_move_up = False
                p_move_down = True
                p_move_left = False
                p_move_right = False
                p_move_upleft = False
                p_move_upright = False
                p_move_downleft = False
                p_move_downright = False
                player.full_size()
                player.scale_by(p_scale)
    elif pygame.K_LEFT in keys:
        make_bullet(player.x, player.y, 'left')
        if not p_move_left:  # horizontal 'left'
            player.image = player_images[2]
            p_move_up = False
            p_move_down = False
            p_move_left = True
            p_move_right = False
            p_move_upleft = False
            p_move_upright = False
            p_move_downleft = False
            p_move_downright = False
            player.full_size()
            player.scale_by(p_scale)
    elif pygame.K_RIGHT in keys:  # horizontal 'right'
        make_bullet(player.x, player.y, 'right')
        if not p_move_right:
            p_move_up = False
            p_move_down = False
            p_move_left = False
            p_move_right = True
            p_move_upleft = False
            p_move_upright = False
            p_move_downleft = False
            p_move_downright = False
            player.image = player_images[0]
            player.full_size()
            player.scale_by(p_scale)

# ----- ENEMY HELPER FUNCTIONS -------

# Creates a single enemy, helper to 'make_wave' function
def make_enemy():
    '''
    Takes no input, is a helper function. Appends an array named 'entity' to the global enemies array.
    This array holds index[0] : <Sprite> and index[1] : <Health Num>.
    '''
    global enemies

    # Loads zombie sprite images // https://opengameart.org/content/animated-top-down-zombie
    enemy_images = []
    for i in range(16):
        file = 'images/skeleton-move_'+ str(i) + '.png'
        enemy_images.append(file)

    entity = []
    # Random Spawn Generation
    side = random.randint(1, 4)  # Random Side
    randomx = random.randint(0, 800)  # Random integer on x axis
    randomy = random.randint(0, 600)  # Random integer on y axis
    scale = 1/9
    if side == 1:  # spawn left
        enemy = gamebox.from_image(-100, randomy, enemy_images[-1])
        enemy.scale_by(scale)
    if side == 2:  # spawn bottom
        enemy = gamebox.from_image(randomx, -100, enemy_images[-1])
        enemy.scale_by(scale)
        # enemy.rotate(-90)  # flip facing towards center
    if side == 3:  # spawn right
        enemy = gamebox.from_image(900, randomy, enemy_images[-1])
        enemy.scale_by(scale)
        # enemy.flip()  # flip facing towards center
    if side == 4:  # spawn up
        enemy = gamebox.from_image(randomx, 900, enemy_images[-1])
        enemy.scale_by(scale)
        # enemy.rotate(90)  # flip facing towards center

    entity.append(enemy)  # index[0] = sprite
    entity.append(enemy_health)  # index[1] = health
    enemies.append(entity)  # appends array to global array


# Makes x enemies, default is the wave number
def make_wave(x=wave_number):
    '''
    Using the 'make_enemy' function, appends x entities to the global array 'enemies'
    :param x: The amount of enemies that wants to be created. If not specified, default is the global variable
    'wave_number'. However, can still be clarified to any amount.
    '''
    for i in range(x):
        make_enemy()
# Check Enemy Health; if = 0, enemy dies
def check_enemy_health():
    '''
    Helper Function, Checks every single entity in the global array 'enemies' and checks their index[1] (Health Num).
    If their Health Num = 0, they are 'dead' and are removed from 'enemies.' Whenever this function is
    called (an enemy 'dies'), 1 is added to the enemy killed count ('enemy_kills').
    '''
    global enemy_kills
    for entity in enemies:
        health = entity[1]
        if health <= 0:
            enemies.remove(entity)
            enemy_kills += 1
# Enemy Movement Algorithm
def move_enemies(enemies):
    '''
    Algorithm that calculates how enemies should move and then gives movement commands based on said calcs.
    :param enemies: Should be the global array 'enemies' or another array that holds other arrays with index[0] = shape,
    index[1] = some health number.
    '''
    global current_frame, special_number
    for entity in enemies:

        enemy_images = []
        for i in range(16):
            file = 'images/skeleton-move_' + str(i) + '.png'
            enemy_images.append(file)
        check_enemy_health()
        # enemy movement algorithm

        # EXPLANATION: Enemies move at a constant rate of four pixels, however, the angle at which they move is
        # optimized to change depending on the location of the player. Depending on the angle, the da (basically dx)
        # and db (basically dy) changes to accommodate the constant rate of movement of four pixels (dD).

        # TL;DR enemies move at a constant rate but calculate the shortest path to the player and move accordingly
        # Not the most clean algorithm but it gets the job done
        enemy = entity[0]
        distance_y = player.y - enemy.y
        distance_x = player.x - enemy.x
        if -5 < distance_y < 5:
            if player.x < enemy.x:
                theta = (3 * math.pi)
            else:
                theta = 2 * math.pi
        elif -5 < distance_x < 5:
            if player.y < enemy.y:
                theta = (3 * math.pi / 2)
            else:
                theta = (5 * math.pi / 2)
        else:
            theta = math.atan(distance_y / distance_x) + (2 * math.pi)
            if player.x < enemy.x:
                if player.y < enemy.y:
                    theta -= math.pi
                else:
                    theta += math.pi
        da = enemy_speed * math.cos(theta)
        db = enemy_speed * math.sin(theta)



        angle = theta * 180 / math.pi
        if (player.x <= enemy.x and da > 0) or (player.x > enemy.x and da < 0):
            da *= -1
            # angle *= -1
        if (player.y >= enemy.y and db > 0) or (player.y < enemy.y and db < 0):
            db *= -1
            # angle *= -1
        # if (player.x <= enemy.x )
        enemy.x += da
        enemy.y -= db
        enemy_move = True

        try:
            special_number = 0.5/len(enemies)
        except ZeroDivisionError:
            special_number = 0.5

        # whenever the zombie moves, increase the sprite loop by var, current_frame
        if enemy_move:
            current_frame += special_number
            if current_frame >= 16:
                current_frame = 1
            enemy.image = enemy_images[int(current_frame)]
            enemy.set_angle(angle)
        else:
            enemy.image = enemy_images[-1]

        # prevent enemy overlap
        for foe in enemies:  # NOTE: Probably needs more work because it looks kinda wacky
            if enemy.touches(foe[0]):
                enemy.move_both_to_stop_overlapping(foe[0])

# ------BULLET HELPER FUNCTIONS--------

# makes a bullet based on direction and player coordinates
def make_bullet(x, y, direction):
    '''
    Creates a bullet at the center of the player and gives a direction based on what command created the bullet.
    :param x: The player's x coordinate
    :param y: The player's y coordinate
    :param direction: The direction given when 'player_shoot_commands()' was called
    :return: Appends a 'bulletList' array which contains index[0] = <Shape>, index[1] = <direction> to the
    global array 'bullets'
    '''
    global bullets, cooldown_shoot
    if not cooldown_shoot:
        bulletList = []
        bullet = gamebox.from_color(x, y, 'white', 5, 5)
        bulletList.append(bullet)
        bulletList.append(direction)
        bullets.append(bulletList)
        cooldown_shoot = True
    # Each bullet is appended to the list,'Bullets' as a list, holding [shape, direction]
# bullet moves based on bullet array
def move_bullet(list):
    '''
    Moves each bullet shape in the global 'bullets' array based on their direction.
    :param list: The global 'bullets' array
    :return: Each bullet moves at a constant speed (bullet_speed) in a direction based on the make_bullet function.
    '''
    for bullet in list:
        shape = bullet[0]
        direction = bullet[1]
        dx = 0
        dy = 0
        # Based on direction, change dx and dy
        if direction == 'up':
            dy = bullet_speed
        elif direction == 'down':
            dy = -1 * bullet_speed
        elif direction == 'left':
            dx = -1 * bullet_speed
        elif direction == 'right':
            dx = bullet_speed
        elif direction == 'upleft':
            dx = -1 * bullet_speed
            dy = bullet_speed
        elif direction == 'downleft':
            dx = -1 * bullet_speed
            dy = -1 * bullet_speed
        elif direction == 'downright':
            dx = bullet_speed
            dy = -1 * bullet_speed
        elif direction == 'upright':
            dx = bullet_speed
            dy = bullet_speed
        # Updates bullet coordinates
        shape.x += dx
        shape.y -= dy
# Only allows bullets to be shot when off cool down
def cooldowncheck():
    '''
    The shooting commands have a default cool down of 7 ticks (or whatever value the default 'bulletCD' var is set to.
    Bullets can only be made 7 ticks after each other to make the game...harder?
    :return: turns on the helper switch "cooldown_shoot" which tells if the shooting is on cool down.
    '''
    global cooldown_shoot, CDcount
    if cooldown_shoot:  # Counts cooldown ticks
        CDcount += 1
        if CDcount == bulletCD:
            cooldown_shoot = False
            CDcount = 0
# Removes bullets if enemies are hit or out of bounds
def check_bullet(list):
    '''
    Checks if bullets either hit any entity in the 'enemies' array, or if they travel outside the game boundaries.
    :param list: Takes in the global array 'bullets'
    :return: If bullets meet the above conditions, they are removed from the global array 'bullets'
    '''
    for bullet in list:
        shape = bullet[0]
        # Hits Enemies
        for enemy in enemies:
            if shape.touches(enemy[0]):
                if bullet in bullets:
                    bullets.remove(bullet)
                    enemy[1] -= 1
        # Out of Bounds
        if shape.x > 800 or shape.x < 0 or shape.y > 600 or shape.y < 0:
            try:
                bullets.remove(bullet)
            except ValueError:
                return

# ----- Draw Commands -----

# Start Screen
def make_start_screen(): # START SCREEN, TEMP
    '''
    Helper function that creates the 'Start Screen'
    '''
    start_screen = gamebox.from_image(400, 300, 'images/start_screen.png')
    # start_screen made by Benjamin Wang (hgf3jq)
    camera.draw(start_screen)
    camera.display() #
# "You Lose" Screen
def make_restart_screen():
    '''
    Helper function that creates the text for the 'Game Over' Screen.
    Describes the player's stats (Level #, Enemies killed, Time survived, Total Score)
    '''
    camera.draw(gamebox.from_text(400, 300, 'GAME OVER!', 100, 'Dark Red', bold=True))
    camera.draw(gamebox.from_text(400, 525, 'Press SPACE to restart', 50, 'Dark Red'))
    camera.draw(gamebox.from_text(400,575, 'Press BACKSPACE to go to START', 25, 'Dark Red'))
    camera.draw(gamebox.from_text(400,375, 'You made it to Level '+str(level)+'!', 25, 'White'))
    camera.draw(gamebox.from_text(400, 400, 'You killed ' + str(enemy_kills) + ' enemies!', 25, 'White'))
    camera.draw(gamebox.from_text(400, 425, 'You survived ' + str(timer) + ' seconds!', 25, 'White'))
    camera.draw(gamebox.from_text(400, 450, 'Your score was: ' + str(totalscore), 25, 'White'))
    camera.display()
# "You Win" Screen
def make_winner_screen():
    '''
    Very rare instance but if you survive long enough, you can technically win. An easter egg if you will.
    Helper function that creates the text for a special 'You Win' screen.
    Describes the player's stats (Level #, Enemies killed, Time survived, Total Score)
    '''
    camera.draw(gamebox.from_text(400, 300, 'You Won...?', 100, 'Green', bold=True))
    camera.draw(gamebox.from_text(400, 525, 'Press SPACE to restart', 50, 'light green'))
    camera.draw(gamebox.from_text(400, 575, 'Press BACKSPACE to go to START', 25, 'light green'))
    camera.draw(gamebox.from_text(400, 400, 'Your killed ' + str(enemy_kills) + ' enemies!', 30, 'White'))
    camera.draw(gamebox.from_text(400, 425, 'You survived ' + str(timer) + ' seconds!', 30, 'White'))
    camera.draw(gamebox.from_text(400, 450, 'Your score was: ' + str(totalscore), 30, 'White'))
    camera.display()
# Top Interface (Shows Health, Timer, Score, Level Number)
def make_interface():
    '''
    Helper function that creates the text at the top of the game (the non-interactive interface)
    Draws text for : Score, Level #, Seconds Alive, Health.
    Also draws health shapes.
    '''
    global lives_list
    # Draw hearts
    for heart in lives_list:
        camera.draw(heart)
    # Draw Health Title
    camera.draw(gamebox.from_text(600, 25, 'Health', 25, 'pink', bold=True))
    # Draw Timer (Seconds Alive)
    camera.draw(gamebox.from_text(350, 25, 'Seconds Alive: ' + str(timer), 25, "white"))
    # Draw the Total Score
    camera.draw(gamebox.from_text(100, 25, 'Score: ' + str(totalscore), 25, 'Green', bold=True))
    # Changes the level color and name
    if level < 3:
        text = 'Daytime'
        color = 'Yellow'
    if 3 <= level < 5:
        text = 'Evening'
        color = 'Light Blue'
    if level == 5:
        text = 'Nighttime'
        color = 'Red'
    if 6 <= level < 10:
        text = 'Nighttime...?'
        color = 'Red'
    if 10 <= level < 15:
        text = 'Hazing Fog'
        color = 'Light Blue'
    if 15 <= level:
        text = 'Hell'
        color = 'Orange'
    # Draw Level Name
    camera.draw(gamebox.from_text(500, 25, text, 25, color))
    # Draw Level Number
    camera.draw(gamebox.from_text(200, 25, 'Level ' + str(level), 25, color))
    # Display everything.
    camera.display()
# Background
def make_background():
    '''
    Helper function that creates the background image.
    The background changes whenever the level increases.
    The series of images are in the directory and just change in color based on the level number.
    '''
    image_number = 15  # how many image sprites there are
    if level < image_number:
        level_time_sprite = level%image_number
    if level >= image_number:
        level_time_sprite = image_number
    if not game_on and not start:
        level_time_sprite = 0
    backgroundfile = 'images/b'+str(level_time_sprite)+'.png'  # The image must follow the format 'b<some_num>.png'
    # Background sprites are made by Benjamin Wang (hgf3jq)
    background_image = gamebox.from_image(400,300,backgroundfile) # Grabs the image from the directory
    background_image.scale_by(1/4)  # resizes it because for some reason all my images are too big.
    camera.draw(background_image) # Draw Command
# Draws Player, Bullets, and Enemies
def draw_entities_all():
    '''
    A helper function that draws all the entities in the game (player, enemies, bullets)
    For some reason also has a spawn condition (when no enemies are alive, spawn a wave).
    '''
    # Draw Player
    camera.draw(player)
    # Draw Enemies
    for enemy in enemies:
        camera.draw(enemy[0])
    # Wave Maker (Condition: No enemies alive)
    if enemies == []:
        make_wave(wave_number)
    # Draw Bullets
    for bullet in bullets:
        camera.draw(bullet[0])
# Draws Hearts in Interface visually representing player health
def draw_health():
    '''
    Draws x shapes based on the variable 'player_health'
    '''
    if player_health <= 5:
        for i in range(player_health):
            x = i*20 + 650
            y = 25
            # heart sprite from https://opengameart.org/content/heart-pixel-art
            heart = gamebox.from_image(x, y, 'images/heart.png')
            heart.scale_by(1/14)
            lives_list.append(heart)


# -----System Commands-----
# NOTE: Not really a restart, more like a "You lost" command...turns off the game.
def restart():
    '''
    Helper function that essentially turns the global 'game_on' variable to False
    It also does some fancy stuff that turns the background black and white
    '''
    global game_on
    game_on = False
    make_background()
    draw_entities_all()
# Sets values when game starts up. Should be very close to identical to the main default entities
def startup():
    '''
    A helper function that sets a bunch of global variables back to their original values.
    '''
    global game_on, level_won,level,timer,enemy_kills,start,totalscore, tickCount, cooldown_shoot, player_health
    global difficulty_timer,enemy_speed, CDcount, spawnTick, wave_number
    player.x = 400
    player.y = 300
    tickCount = 0
    cooldown_shoot = False
    enemies.clear()
    bullets.clear()
    player_health = 5
    CDcount = 0
    difficulty_timer = 0
    enemy_speed = 2
    wave_number = 2
    if not game_on:
        make_wave(wave_number)
        draw_health()
    if level_won:
        level_won = False
    game_on = True
    start = False
    enemy_kills = 0
    timer = 0
    level = 1
    totalscore = 0
    spawnTick = 10
    player.image = player_images[0]
    player.full_size()
    player.scale_by(p_scale)


# Checks if "you lose" conditions are met
def check_restart():
    '''
    Helper function that checks if the following conditions are met:
    - Enemy touches player.
    - Enemy touches player with no hearts.
    Whenever an enemy touches a player, they lose a heart.
    If an enemy touches a player with no hearts, the game ends and the restart() function is called.
    '''
    global player_health
    for entity in enemies:
        enemy = entity[0]
        if enemy.touches(player):  # if an enemy touches a player
            player_health -= 1  # player loses one heart
            if player_health == 0:
                restart()
            lives_list.pop()
            enemies.remove(entity)  # enemy dies
# Timer/Spawning/Level Granddaddy Function
def clock_stuff():
    '''
    A bunch of miscellaneous helper timer variables. Comments go more in depth of what exactly each thing does.
    Includes: Second Counter, Spawning Function, Level Function
    :return:
    '''
    global tickCount,spawnTick, timer, difficulty_timer, wave_number, enemy_speed, level
    # Second Counter
    tickCount += 1
    if tickCount == ticks_per_second:
        timer += 1 # Counts seconds
        tickCount = 0

        # SPAWNING FUNCTION
        if level % 5 == 0:
            spawnTick -= 1
            if spawnTick == 0:  # every five seconds, spawn a wave
                spawnTick = 10
                make_wave(int(wave_number/2))

        # LEVEL FUNCTION
        difficulty_timer += 1
        if difficulty_timer % 30 == 0: # Every 30 seconds
            level += 1 # increase the level
            if difficulty_timer % 60 == 0: # Every 60 seconds
                enemy_speed += 0.25 # Increase the enemy speeds
            else:
                wave_number += 4  # Increase the amount of enemies per spawn
                make_wave(wave_number)
# -----MAIN TICK FUNCTION------
def tick(keys):
    '''
    The main tick function. This is repeated thirty times per second and calls a bajillion other functions inside it.
    Goes more in depth of what everything in the function does in the comments.
    :param keys: Keys are what the player inputs (usually either space, WASD, or arrow keys)
    :return: A game hopefully lol
    '''

    # Globals woo hoo
    global game_on, enemies, tickCount, timer, level_won, start, enemy_kills, enemy_health, enemy_color
    global powerupCount, player_health, wave_number, enemy_speed, difficulty_timer, level, totalscore

    # ---- Game Off Screens ----
    if not game_on:
        if start:  # if it is the start of the game...
            make_start_screen()
        else:  # ... and if it is not the start of the game
            if not level_won:  # if the level is not won (i.e you lost)
                make_restart_screen()  # you get the "you lose, restart" screen
                if pygame.K_BACKSPACE in keys:
                    restart()
                    start = True
            if level_won:  # if the level is somehow won (timer reaches 999)
                make_winner_screen()  # you get the winner winner chicken dinner screen

    # ---- STARTUP FUNCTION ----
        if pygame.K_SPACE in keys:  # Space activates...
            startup()  # NOTE: this only activates if the game is not on
            game_on = True
    # ---- WHEN THE GAME IS ON ----
    if game_on:

        # System Stuff
        clock_stuff() # Works timers, difficulties and wave spawn
        if level == 1:
            totalscore = enemy_kills*10 # Calculate total score
        else:
            totalscore = enemy_kills*10 + level*100
        # -----DRAWING COMMANDS-----
        make_background()  # draws background
        draw_entities_all()  # draws player, enemies, and bullets
        make_interface()  # draws interface
        # Player Movement
        player_movement(keys)
        # Player Shooting Controls
        player_shoot_commands(keys)
        # -----Game End Functions-----
        check_restart()  # Checks losing conditions
        if timer == 999:  # Checks Hidden Win Condition
            restart()
            level_won = True
        # ----- Enemy Movement -----
        move_enemies(enemies)
        # ----- Bullet Movements -----
        move_bullet(bullets)  # Moves bullets based on directions
        cooldowncheck()  # Check if bullets are on cool-down
        check_bullet(bullets)  # Deletes bullets that hit enemies/out of bounds

ticks_per_second = 30
gamebox.timer_loop(ticks_per_second, tick)