# implementation of Spaceship - program template for RiceRocks
import simplegui
import math
import random

# globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
started = False
rock_counter = 0
explosion_group = set([])
high_score = 0
level = 1

#variables to help adjust rock velocity to increase game difficulty
upper_bound = .3
lower_bound = -.3
range_width = upper_bound - lower_bound
temp_score = 20


class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2013.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
# .ogg versions of sounds are also available, just replace .mp3 by .ogg
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


# Ship class
class Ship:

    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0], self.image_center[1]] , self.image_size,
                              self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                              self.pos, self.image_size, self.angle)

    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT

        # update velocity
        if self.thrust:
            acc = angle_to_vector(self.angle)
            self.vel[0] += acc[0] * .1
            self.vel[1] += acc[1] * .1
            
        self.vel[0] *= .99
        self.vel[1] *= .99

    def set_thrust(self, on):
        self.thrust = on
        if on:
            ship_thrust_sound.rewind()
            ship_thrust_sound.play()
        else:
            ship_thrust_sound.pause()
       
    def increment_angle_vel(self):
        self.angle_vel += .05
        
    def decrement_angle_vel(self):
        self.angle_vel -= .05
        
    def shoot(self):
        global a_missile, missile_group
        forward = angle_to_vector(self.angle)
        missile_pos = [self.pos[0] + self.radius * forward[0], self.pos[1] + self.radius * forward[1]]
        missile_vel = [self.vel[0] + 6 * forward[0], self.vel[1] + 6 * forward[1]]
        missile_group.add(Sprite(missile_pos, missile_vel, self.angle, 0, missile_image, missile_info, missile_sound))

    #get position helper function
    def get_position(self):
        return self.pos
    
    #get radius helper function
    def get_radius(self):
        return self.radius
    
    
    
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        if self.animated:
            canvas.draw_image(explosion_image, [self.age * 64 + 64, 64], 
                              explosion_info.get_size(), self.pos, explosion_info.get_size())
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size,
                          self.pos, self.image_size, self.angle)
        
    def update(self):
        # update angle
        self.angle += self.angle_vel
        
        # update position
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        
        #increment age to give missile a lifespan
        self.age += 1
        #if age is less than the lifespan we want to keep missile
        #else the missile disappears
        if self.age < self.lifespan:
            return False
        else:
            return True
    
    #get position helper function
    def get_position(self):
        return self.pos
    
    #get radius helper function
    def get_radius(self):
        return self.radius
    
    def collide(self, other_object):
        if dist(self.pos, other_object.get_position()) < (self.radius + other_object.get_radius()):
            return True
        return False
        
# key handlers to control ship   
def keydown(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(True)
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot()
        
def keyup(key):
    if key == simplegui.KEY_MAP['left']:
        my_ship.increment_angle_vel()
    elif key == simplegui.KEY_MAP['right']:
        my_ship.decrement_angle_vel()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.set_thrust(False)
        
# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True

def draw(canvas):
    global time, started, lives, score, rock_counter, rock_group, level
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw UI
    canvas.draw_text("Lives", [50, 50], 22, "White")
    canvas.draw_text("Score", [680, 50], 22, "White")
    canvas.draw_text("High Score: ", [330, 50], 22, "White")
    canvas.draw_text("Level: ", [680, 550], 22, "White")
    canvas.draw_text(str(lives), [50, 80], 22, "White")
    canvas.draw_text(str(high_score), [440, 50], 22, "White")
    canvas.draw_text(str(score), [680, 80], 22, "White")
    canvas.draw_text(str(level), [750, 550], 22, "White")

    # draw ship and sprites
    my_ship.draw(canvas)
    
    # update ship and sprites
    my_ship.update()
    
    #check for collisions between rock and ship
    if group_collide(rock_group, my_ship):
        lives -= 1
        rock_counter -= 1
    
    #check for collisions between missiles and rocks
    group_group_collide(rock_group, missile_group)
    
    #update rocks
    process_sprite_group(canvas, rock_group)
    
    #update missiles
    process_sprite_group(canvas, missile_group)
    
    #process explosion grou
    process_sprite_group(canvas, explosion_group)
    #if lives = 0 end the game and start a new one
    if lives == 0:
        __init__game()
    
    if started:
        soundtrack.play()
        
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())
    
# timer handler that spawns a rock    
def rock_spawner():
    global rock_group, rock_counter, upper_bound, lower_bound, range_width, temp_score, level
    
    #adjust velocity of rocks based on the score to increase game difficulty
    if score == temp_score:
        upper_bound += .8
        lower_bound -= .8
        temp_score += 20
        level += 1
        #print temp_score

    #allow a max of 12 rocks
    max_rocks = 12
    
    #allow rocks to be spawned only if game is started
    if started:
        rock_pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
        
        #using this variables, increase the rock velocity as score increases
        rock_vel = [random.random() * range_width + lower_bound, random.random() * range_width + lower_bound]
        rock_avel = random.random() * .2 - .1
        
       
        #ignore if a spawned rock is initially too close to the ship
        if dist(rock_pos, my_ship.get_position()) < (asteroid_info.get_radius() + my_ship.get_radius()):
            return
        
        if rock_counter < max_rocks:
            rock_group.add(Sprite(rock_pos, rock_vel, 0, rock_avel, asteroid_image, asteroid_info))
            rock_counter += 1

# helper handler function that takes a set and a canvas and calls the update and 
#draw methods for each sprite in the group
def process_sprite_group(canvas, a_set):
    for sprite in a_set:
        sprite.draw(canvas)
        sprite.update()
        
    for sprite in set(a_set):
        if sprite.update():
            a_set.remove(sprite)

#group collide function
def group_collide(group, other_object):
    #introduce a flag to know what to return if there is a collision
    flag = False
    for item in set(group):
        if item.collide(other_object):
            group.remove(item)
            explosion_group.add(Sprite(item.get_position(), [0, 0], 0, 0, explosion_image, explosion_info, explosion_sound))
            if other_object == my_ship:
                explosion_group.add(Sprite(other_object.get_position(), [0, 0], 0, 0, explosion_image, explosion_info, explosion_sound))
            flag = True
    return flag

#helper function to check for collisions between two groups
def group_group_collide(group1, group2):
    global score, rock_counter
    for item in set(group1):
        if group_collide(group2, item):
            score += 1
            rock_counter -= 1
            group1.discard(item)
    return score

def __init__game():
    global lives, score, rock_counter, time, rock_group, started, high_score, level, upper_bound, lower_bound, range_width, temp_score
    
    #update high score
    if score > high_score:
        high_score = score
    
    #reset all global variables
    lives = 3    
    score = 0
    time = 0
    rock_counter = 0
    level = 1
    rock_group = set([])
    soundtrack.rewind()
    started = False
    
    upper_bound = .3
    lower_bound = -.3
    range_width = upper_bound - lower_bound
    temp_score = 20


# initialize stuff
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)
    
#draw instructions
intro = """This game is a variation of the popular game Asteroids (1979). 
           Asteroids is a relatively simple game by today's standards, but was 
           still immensely popular during its time.  Searching for 
           'asteroids arcade' yields links to multiple versions of Asteroids
           that are available on the web (including an updated version by Atari, 
           the original creator of Asteroids)."""

blank_line = " "

instruction_title = "INSTRUCTIONS:"

instruction_1 = "1. Use the left/right arrow keys to rotate your ship counterclockwise/clockwise (respectively)"
instruction_2 = "2. Use the forward button to accelerate your ship forwards"
instruction_3 = "3. Use the space button to fire missiles at asteroids"
goal = """GOAL: Destroy these asteroids before they strike your ship.
          You have three lives. Use them wisely """
level_up = "You level up in score increments of 20"

label = frame.add_label(intro)
label = frame.add_label(blank_line)
label = frame.add_label(instruction_title)
label = frame.add_label(instruction_1)
label = frame.add_label(instruction_2)
label = frame.add_label(instruction_3)
label = frame.add_label(blank_line)
label = frame.add_label(goal)
label = frame.add_label(level_up)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
rock_group = set([])
missile_group = set([])

# register handlers
frame.set_keyup_handler(keyup)
frame.set_keydown_handler(keydown)
frame.set_mouseclick_handler(click)
frame.set_draw_handler(draw)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
