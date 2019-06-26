import time
import pygame
from pygame.locals import *

from inputmanager import InputManager

# A simple player object. This only keeps track of position.  
class TestPlayer:
    def __init__(self):
        self.x = 320
        self.y = 240
        self.speed = 4
    
    def move_left(self):
        self.x -= self.speed
    def move_right(self):
        self.x += self.speed
    def move_up(self):
        self.y -= self.speed
    def move_down(self):
        self.y += self.speed

# The main method...duh! 
def main():
    
    fps = 30
    
    print("Plug in a USB gamepad. Do it! Do it now! Press enter after you have done this.")
    wait_for_enter()
    
    pygame.init()
    
    num_joysticks = pygame.joystick.get_count()
    if num_joysticks < 1:
        print("You didn't plug in a joystick. FORSHAME!")
        return
    
    input_manager = InputManager()
    
    screen = pygame.display.set_mode((640, 480))
    
    button_index = 0
    
    player = TestPlayer()
    
    
    # The main game loop 
    while not input_manager.quit_attempt:
        start = time.time()
        
        screen.fill((0,0,0))
        
        # There will be two phases to our "game". 
        is_configured = button_index >= len(input_manager.buttons)
        
        # In the first phase, the user will be prompted to configure the joystick by pressing
        # the key that is indicated on the screen 
        # You would probably do this in an input menu in your real game. 
        if not is_configured:
            success = configure_phase(screen, input_manager.buttons[button_index], input_manager)
            # if the user pressed a button and configured it... 
            if success:
                # move on to the next button that needs to be configured
                button_index += 1
        
        # In the second phase, the user will control a "character" on the screen (which will 
        # be represented by a simple blue ball) that obeys the directional commands, whether
        # it's from the joystick or the keyboard. 
        else:
            interaction_phase(screen, player, input_manager)
        
        pygame.display.flip()
        
        # maintain frame rate 
        difference = start - time.time()
        delay = 1.0 / fps - difference
        if delay > 0:
            time.sleep(delay)

def configure_phase(screen, button, input_manager):
    
    # need to pump windows events otherwise the window will lock up and die
    input_manager.get_events() 
    
    # configure_button looks at the state of ALL buttons pressed on the joystick
    # and will map the first pressed button it sees to the current button you pass
    # in here.  
    success = input_manager.configure_button(button)
    
    # tell user which button to configure 
    write_text(screen, "Press the " + button + " button", 100, 100)
    
    # If a joystick button was successfully configured, return True
    return success

def interaction_phase(screen, player, input_manager):
    # I dunno. This doesn't do anything. But this is how  
    # you would access key hit events and the like. 
    # Ideal for "shooting a weapon" or "jump" sort of events 
    for event in input_manager.get_events():
        if event.key == 'A' and event.down:
            pass # weeeeeeee 
        if event.key == 'X' and event.up:
            input_manager.quit_attempted = True
    
    # ...but for things like "move in this direction", you want 
    # to know if a button is pressed and held 
    
    if input_manager.is_pressed('left'):
        player.move_left()
    elif input_manager.is_pressed('right'):
        player.move_right()
    if input_manager.is_pressed('up'):
        player.move_up()
    elif input_manager.is_pressed('down'):
        player.move_down()
    
    # Draw the player 
    pygame.draw.circle(screen, (0, 0, 255), (player.x, player.y), 20)

# There was probably a more robust way of doing this. But 
# command line interaction was not the point of the tutorial. 
def wait_for_enter():
    try: input()
    except: pass

# This renders text on the game screen.  
# Also not the point of this tutorial. 
cached_text = {}
cached_font = None
def write_text(screen, text, x, y):
    global cached_text, cached_font
    image = cached_text.get(text)
    if image == None:
        if cached_font == None:
            cached_font = pygame.font.Font(pygame.font.get_default_font(), 12)
        image = cached_font.render(text, True, (255, 255, 255))
        cached_text[text] = image
    screen.blit(image, (x, y - image.get_height()))

# Kick things off.  
main()

# fin.