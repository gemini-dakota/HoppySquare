import pygame
import pygame.gfxdraw
import random
# import time

# Color Definitions
white = (255, 255, 255)
black = (1, 1, 1)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# Screen Definitions
screen_width = 500
screen_height = 500
fps = 30
dt_sec = 1.0/fps

# Rectangle is a wrapper for a pygame rect object
# Some extra Physics parameters are kept track of for movement
class Rectangle:
    def __init__(self, left_px=10, top_px=0, width_px=50, height_px=25, xvel_mps=1, color=red):

        # The pyGame rect we are wrapping
        self.rect = pygame.Rect(left_px, top_px, width_px, height_px)

        # Physics Related Parameters
        self.xvel_mps = xvel_mps  # velocity in the x direction
        self.yvel_mps = 0         # velocity in the y direction
        self.ya_mps2 = 0          # y plane gravity - 0 to disable

        self.y_remainder = 0.0    # fractions of a pixel to keep track of (due to gravity)

        # Other Parameters
        self.color = color

    def enableGravityY(self, gravity_mps2=9.8*35):
        ''' Enables gravity - an acceleration in the y direction '''
        self.ya_mps2 = gravity_mps2

    def move(self, x, y):
        ''' moves the rectangle by the specified (x,y) offset.
           The pygame library  returns a new rectangle that is moved by the offset '''
        self.rect = self.rect.move(x, y)

    def updateSpeedAndPosition(self):
        '''
        Updates the Car's (rects) position based on the Car's speed
        Contains logic to handle when the car gets to the edge of the screen
        '''

        # X Direction Movement - No Gravity
        x_m = self.xvel_mps * dt_sec

        # Y Direction Movement - Yes Gravity
        self.yvel_mps += self.ya_mps2 * dt_sec
        y_m = self.yvel_mps * dt_sec

        # move only allows 1 pixel or greater
        # Probably unnecessary to keep track up, but during slow moving games
        # this is noticable.
        if abs(y_m) < 1.0:
            self.y_remainder += y_m

        # X Direction - Move the Rectangle
        self.rect = self.rect.move(x_m, 0)

        # Y Direction - Move the Rectangle - Don't the tiny remainder movements
        if abs(y_m) < 1.0 and abs(self.y_remainder) >= 1.0:
            self.rect = self.rect.move(self.y_remainder, 0)
            if self.y_remainder > 0.0:
                self.y_remainder -= 1.0
            else:
                self.y_remainder += 1.0
        # Normal Case when move value is >=1 pixel
        else:
            self.rect = self.rect.move(0, y_m)

    def draw_rect(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.display.update()


def updateIfGoingOffScreen(r1, r2):
    '''
    Updates the Rectangle's position based on its speed
    Contains logic to handle when the car gets to the edge of the screen
    '''

    # Crappy way to do static vars in Python I guess?
    try:
        updateIfGoingOffScreen.gap_size_min += 0
        updateIfGoingOffScreen.gap_size_max += 0
    except AttributeError:
        updateIfGoingOffScreen.gap_size_min = 200
        updateIfGoingOffScreen.gap_size_max = 300

    # Check if the obstacle hits the wall
    if r1.xvel_mps<0:                     # moving left
        if r1.rect.left<=0:               # left edge hit wall

            # Gradually decrease gap size to increase difficulty
            updateIfGoingOffScreen.gap_size_min -= 10
            updateIfGoingOffScreen.gap_size_max -= 10
            if(updateIfGoingOffScreen.gap_size_min <= 100):
                updateIfGoingOffScreen.gap_size_min = 100
                updateIfGoingOffScreen.gap_size_max = 100

            gap_size = random.randint(updateIfGoingOffScreen.gap_size_min,
                                      updateIfGoingOffScreen.gap_size_max)
            gap_start = random.randint(60,375) # 0 - 500 total

            # Redraw new obstacles
            # TODO hard coded screen pixes
            # TODO bug when bottom rect goes down into floor?
            r1.rect.height = gap_start - 50
            r2.rect.height = 500-50-50-gap_size-r1.rect.height
            r2.rect.top = 50 + r1.rect.height + gap_size
            r1.rect = r1.rect.move(screen_width, 0)
            r2.rect = r2.rect.move(screen_width, 0)
            # print("gap_size: ", gap_size, "gap_start: ", gap_start, "h1: ", r1.rect.height, " h2: ", r2.rect.height)

            return True

    return False

def increaseSpeed(rect1, rect2):
    # Speed things up to gradually increase difficulty
    rect1.xvel_mps-=5    # reminder - negative is going left
    rect2.xvel_mps-=5
    if rect1.xvel_mps <= -200:
        rect1.xvel_mps = -200
        rect2.xvel_mps = -200

def checkForCollision(first, second):
    # Checks if two Rectangles crash. Returns True if crash, False otherwise
    # Check Top Right Corner
    if(first.rect.right > second.rect.left  and
       first.rect.right < second.rect.right and
       first.rect.top   > second.rect.top   and
       first.rect.top   < second.rect.bottom ):
        return True
    # Check Top Left Corner
    elif(first.rect.left > second.rect.left  and
         first.rect.left < second.rect.right and
         first.rect.top   > second.rect.top   and
         first.rect.top   < second.rect.bottom ):
        return True
    # Check Bottom Right Corner
    elif(first.rect.right > second.rect.left  and
         first.rect.right < second.rect.right and
         first.rect.bottom   > second.rect.top   and
         first.rect.bottom   < second.rect.bottom ):
        return True
    # Check Bottom Left Corner
    elif(first.rect.left > second.rect.left  and
         first.rect.left < second.rect.right and
         first.rect.bottom > second.rect.top   and
         first.rect.bottom < second.rect.bottom ):
        return True
    else:
        return False

# Initial Setup
pygame.init()
screen_surface = pygame.display.set_mode((screen_width, screen_height))
screen_surface.fill(black)
pygame.display.flip()
clock = pygame.time.Clock()

# Create some Rectangles (aka pyGame Rects)
border_height = 50
ceiling = Rectangle(0, 0,  screen_width, border_height, 0, red)
ground  = Rectangle(0,  screen_height-border_height,  screen_width, border_height, 0, red)

# Start Sizes
block_width = 20
block_height = 100
block_speed = -100

# Obstacle 1 - Pair of vertically aligned rectangles
lowBlock1  = Rectangle(screen_width - block_width,        # Left
                screen_height-border_height-block_height, # Top
                block_width,                              # Width
                block_height,                             # Height
                block_speed,                              # Speed
                green)                                    # Color
highBlock1 = Rectangle(screen_width - block_width,        # Left
                border_height,                            # Top
                block_width,                              # Width
                block_height,                             # Height
                block_speed,                              # Speed
                blue)                                     # Color

# Obstacle 2 - Pair of vertically aligned rectangles
lowBlock2  = Rectangle(screen_width - block_width+250,    # Left
                screen_height-border_height-block_height, # Top
                block_width,                              # Width
                block_height,                             # Height
                block_speed,                              # Speed
                green)                                    # Color
highBlock2 = Rectangle(screen_width - block_width+250,    # Left
                border_height,                            # Top
                block_width,                              # Width
                block_height,                             # Height
                block_speed,                              # Speed
                blue)                                     # Color

# The Game character that needs to flap between the obstacles
flappy =   Rectangle(100,   # Left
                     250,   # Top
                     20,    # Width
                     20,    # Height
                     0,     # Speed
                     white) # Color
flappy.enableGravityY()

score = 0
score_when_speed_increased = 0

# Main game loop
while True:
    clock.tick(fps)

    # Checks for pyGame events like keys pressed
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYDOWN:
            # Flap/Hop when space is pressed
            if event.key == pygame.K_SPACE:
                flappy.yvel_mps -= 250

                # Limit speed flappy can fly up
                if(flappy.yvel_mps <= -300):
                    flappy.yvel_mps = -300
    # Capture Exit Signal
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Clear Screen
    screen_surface.fill(black)

    # Re-Draw All Rectanges
    ceiling.updateSpeedAndPosition()
    ceiling.draw_rect(screen_surface)
    ground.updateSpeedAndPosition()
    ground.draw_rect(screen_surface)
    lowBlock1.updateSpeedAndPosition()
    lowBlock1.draw_rect(screen_surface)
    highBlock1.updateSpeedAndPosition()
    highBlock1.draw_rect(screen_surface)
    lowBlock2.updateSpeedAndPosition()
    lowBlock2.draw_rect(screen_surface)
    highBlock2.updateSpeedAndPosition()
    highBlock2.draw_rect(screen_surface)
    flappy.updateSpeedAndPosition()
    flappy.draw_rect(screen_surface)

    # Check if Blocks scrolled off screen and redraw
    if(updateIfGoingOffScreen(highBlock1, lowBlock1)):
        score += 1
        print("score: ", score)
    if(updateIfGoingOffScreen(highBlock2, lowBlock2)):
        score += 1
        print("score: ", score)

    # Slow increase speed of obstacles
    if(score != score_when_speed_increased):
        score_when_speed_increased = score
        increaseSpeed(lowBlock1, highBlock1)
        increaseSpeed(lowBlock2, highBlock2)

    # Check for collisions with obstacles
    crashed = False
    crashed |= checkForCollision(flappy, ground)
    crashed |= checkForCollision(flappy, ceiling)
    crashed |= checkForCollision(flappy, lowBlock1)
    crashed |= checkForCollision(flappy, highBlock1)
    crashed |= checkForCollision(flappy, lowBlock2)
    crashed |= checkForCollision(flappy, highBlock2)

    # Exit Game upon Crash
    if crashed == True:
        pygame.quit()
        quit()