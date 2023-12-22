import pygame
import sys
import random
import tkinter as tk
from tkinter import filedialog

# Initializing Pygame
pygame.init()
pygame.mixer.init() # Initialize the mixer module for sound effects

# Load and play background music
pygame.mixer.music.load('background.mp3')
# Load block removal sound
block_remove_sound = pygame.mixer.Sound('effect.mp3')
pygame.mixer.music.play(-1)  # The -1 means to loop the music indefinitely

# Load sound button images
play_button_image = pygame.image.load('play_button.png')
mute_button_image = pygame.image.load('mute_button.png')

#scale the sound button images
play_button_image = pygame.transform.scale(play_button_image, (50, 50))
mute_button_image = pygame.transform.scale(mute_button_image, (50, 50))

# Boolean to keep track of music state
music_playing = True

# Position of the sound button
sound_button_pos = (710, 75)  # Example position
button_image = mute_button_image  # Start with music playing

# Screen dimensions
win_width, win_height = 800, 600

# Colors
GREEN, RED, BLACK, WHITE= (0, 255, 0), (255, 0, 0), (0, 0, 0), (255, 255, 255)

# Font
font = pygame.font.Font(None, 36)

# Block
class Block:
    DEFAULT_COLOR = WHITE  # White
    BLACK = BLACK  # Black

    def __init__(self, rect, word, color=None,floating=False):
        self.rect = rect
        self.word = word
        self.color = color if color else self.DEFAULT_COLOR
        self.floating = floating
        self.velocity = [-1, -1]  # Add this line

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        word_rendered = font.render(self.word, True, self.BLACK)
        screen.blit(word_rendered, (self.rect.x + (self.rect.width - word_rendered.get_width()) // 2, 
                                     self.rect.y + (self.rect.height - word_rendered.get_height()) // 2))
        
# Button
class Button:
    def __init__(self, rect, text, color, text_color=BLACK):
        self.rect = rect
        self.text = text
        self.color = color
        self.text_color = text_color
        self.is_visible = True  # to hide the button when it is not needed
    def draw(self, screen):
        if self.is_visible:  
            pygame.draw.rect(screen, self.color, self.rect)
            text_rendered = font.render(self.text, True, self.text_color)
            screen.blit(text_rendered, (self.rect.x + (self.rect.width - text_rendered.get_width()) // 2, 
                                        self.rect.y + (self.rect.height - text_rendered.get_height()) // 2))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Game:
    def __init__(self,start_button, next_level_button, exit_button, load_button):
        self.start_button = start_button
        self.next_level_button = next_level_button
        self.exit_button = exit_button
        self.load_button = load_button
        self.game_over = False
        self.running = True
        self.menu = True
        self.game = False
        self.words = []
        self.blocks = []
        self.block_height = 60
        self.block_width = 120
        self.block_spacing = 10
        self.user_input = ""
        self.score = 0
        self.start_ticks = pygame.time.get_ticks()
        self.level = 0
        self.blocks_popped_this_level = 0  # Track the number of popped blocks for the current level
        self.remaining_floaters = 0  # Track the number of floating blocks remaining
        self.countdown = 45 # Countdown timer for each level
        self.screen = pygame.display.set_mode((win_width, win_height))
        self.background_image = pygame.image.load('background_image.jpg').convert()#background image
        self.file_path = "words.txt"#default file path
        self.initialize_blocks()
        

    def initialize_blocks(self):
        self.blocks_popped_this_level = 0
        self.remaining_floaters = 0
        self.countdown = 45  # Reset the countdown for the new level
        rows = [5, 3, 2, 1]
        self.words = self.load_words_from_file(self.file_path)
        print(self.words)
        random.shuffle(self.words)
        #this is the part where  blocks are initialized with the words
        self.blocks = [Block(pygame.Rect(win_width // 2 - ((row * (self.block_width + self.block_spacing) - self.block_spacing) // 2) + j * (self.block_width + self.block_spacing), 
                                             win_height - 10 - i * (self.block_height + self.block_spacing) - self.block_height, self.block_width, self.block_height), 
                                self.words.pop(0), color=(255, 0, 0) if i % 2 == 0 else (0, 255, 0)) for i, row in enumerate(rows) for j in range(row)]
        
    def remove_block(self,block):       
        self.blocks.remove(block)
        play_block_remove_sound()
        self.blocks_popped_this_level += 1
        self.score += 10
        if self.blocks_popped_this_level == self.level:
            self.remaining_floaters = self.level
            self.add_floating_blocks() 
        if block.floating:
            self.add_floating_blocks() 

    def add_floating_blocks(self):
    # Number of floating blocks should match the current level number
        if self.remaining_floaters > 0:
            # Calculate a position for the new floating block
            x = random.randint(0, win_width - self.block_width)
            y = random.randint(0, win_height / 2)  # Make sure it's in the upper half of the screen
            # Get a word for the block
            word = self.words.pop(0) if self.words else "NoMoreWords" # If there are no more words, use a placeholder
            # Create and append the new block
            if word == "NoMoreWords": #to be able to see the whole word for the placeholder 
                new_block = Block(pygame.Rect(x, y, self.block_width+45, self.block_height), word, color=GREEN, floating=True)
            else:    
                new_block = Block(pygame.Rect(x, y, self.block_width, self.block_height), word, color=GREEN, floating=True)
            self.blocks.append(new_block) 
            self.remaining_floaters -= 1
        
    def update_floating_blocks(self):
        for block in self.blocks:
            if block.floating:
                # Move the block
                block.rect.x += block.velocity[0]
                block.rect.y += block.velocity[1]
                # If the block touches the left or right edge, invert its x velocity
                if block.rect.x < 0 or block.rect.x > win_width - block.rect.width:
                    block.velocity[0] *= -1
                    block.color = RED if block.color == GREEN else GREEN
                # If the block touches the top or goes past the middle of the screen, invert its y velocity
                if block.rect.y < 0 or block.rect.y > win_height / 2:
                    block.velocity[1] *= -1
                    block.color = RED if block.color == GREEN else GREEN
        
    
    def load_words_from_file(self, filename):
        #expect at least 25 words in the file or else ask the user to choose another file
        fitting_words = []
        try:
            with open(filename, 'r') as f:
                for line in f:
                    for word in line.strip().split():
                        word_surface = font.render(word, True, BLACK)
                        if word_surface.get_width() < self.block_width: #only accept words that are not longer than the block width
                            fitting_words.append(word)
        except FileNotFoundError:
            print(f"The file {filename} was not found.")
        return fitting_words


        
    def draw_menu(self):
        if len(self.blocks) == 0:
            self.next_level_button.draw(self.screen)
            
        else:
            self.start_button.draw(self.screen)

        if self.level == 0:
            self.load_button.draw(self.screen)      
        
        self.exit_button.draw(self.screen)

    def draw_game(self):
        for block in self.blocks:
            block.draw(self.screen)

        user_text = font.render(self.user_input, True, WHITE)
        self.screen.blit(user_text, (20, win_height - 60))

        seconds = (pygame.time.get_ticks() - self.start_ticks) // 1000
        timer_text = font.render("Time: " + str(seconds), True, WHITE)
        #self.screen.blit(timer_text, (win_width - timer_text.get_width() - 20, 20))

        score_text = font.render("Score: " + str(self.score), True, WHITE)
        self.screen.blit(score_text, (win_width - score_text.get_width() - 20, timer_text.get_height() + 30))

        # Update the countdown timer
        
        seconds_passed = (pygame.time.get_ticks() - self.start_ticks) // 1000
        self.countdown = max(45 - seconds_passed, 0)  # Countdown from 45 to 0
    
        # Draw the countdown timer
        timer_text = font.render("Time: " + str(self.countdown), True, WHITE)
        self.screen.blit(timer_text, (win_width - timer_text.get_width() - 20, 20))

        # Check if the countdown has reached 0, if so, end the game
        if self.countdown == 0:
            self.game = False
            self.menu = False
            self.game_over = True

        if len(self.blocks) == 0:  
            self.menu = True
            self.game = False

    def draw_game_over(self):
        #draw game over
        game_over_text = font.render("Game Over", True, WHITE)
        self.screen.blit(game_over_text, (win_width/2 - game_over_text.get_width()/2, win_height/2 - game_over_text.get_height()/2 - 100))
        #draw level reached
        level_text = font.render("Level Reached: " + str(self.level), True, WHITE)
        self.screen.blit(level_text, (win_width/2 - level_text.get_width()/2, win_height/2 - level_text.get_height()/2 - 50))
        #draw total score between game over and exit button
        score_text = font.render("Total Score: " + str(self.score), True, WHITE)
        self.screen.blit(score_text, (win_width/2 - score_text.get_width()/2, win_height/2 - score_text.get_height()/2 ))
        #draw exit button
        self.exit_button.draw(self.screen)
        self.menu = False
        self.game = False
        self.play_again_button = Button(pygame.Rect(win_width/2 - 62, win_height/2 + 110, 125, 50), "Play Again", GREEN)
        self.play_again_button.draw(self.screen)

    def handle_menu_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.start_button.is_visible and self.start_button.is_clicked(event.pos):
                self.start_ticks = pygame.time.get_ticks() # Reset the start ticks when blocks are initialized for a new level
                self.level += 1  
                print(self.level) 
                self.menu = False
                self.game = True
                self.start_button.is_visible = False
                self.next_level_button.is_visible = True
            elif self.next_level_button.is_visible and self.next_level_button.is_clicked(event.pos):
                self.start_ticks = pygame.time.get_ticks() # Reset the start ticks when blocks are initialized for a new level
                self.level += 1
                print(self.level) 
                self.initialize_blocks()
                self.menu = False
                self.game = True   
            elif self.exit_button.is_visible and self.exit_button.is_clicked(event.pos):
                self.running = False
                pygame.mixer.music.stop()  # Stop the music before quitting
                pygame.quit()
                sys.exit()
            elif self.load_button.is_visible and self.load_button.is_clicked(event.pos) and self.level == 0:
                self.file_path = open_file_dialog()
                if self.file_path != "words.txt":
                    self.initialize_blocks()
                print("Load button clicked")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.next_level_button.is_visible:
                    self.level += 1
                    print(self.level) 
                    self.initialize_blocks()
                    self.menu = False
                    self.game = True     

    def handle_game_events(self, event): 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                for block in self.blocks:
                    if block.word == self.user_input:
                        self.remove_block(block)
                        break
                    if self.user_input == "OVER":
                        self.game = False
                        self.menu = False
                        self.game_over = True
                        break
                self.user_input = ""
                
            elif event.key == pygame.K_BACKSPACE:
                self.user_input = self.user_input[:-1]
            else:
                self.user_input += event.unicode


    def handle_game_over_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.exit_button.is_clicked(event.pos):
                #close the game
                self.running = False
                pygame.mixer.music.stop()  # Stop the music before quitting
                pygame.quit()
                sys.exit()
            elif self.play_again_button.is_clicked(event.pos) and self.play_again_button.is_visible:
                #reset the game
                self.initialize_blocks()
                self.start_ticks = pygame.time.get_ticks() # Reset the start ticks when blocks are initialized for a new level
                self.game_over = False
                self.level = 1  
                self.score = 0
                print(self.level) 
                self.menu = False
                self.game = True
                self.start_button.is_visible = False
                self.next_level_button.is_visible = True 
                self.play_again_button.is_visible = False  

    def handle_sound_button(self, event):
        global music_playing, button_image
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            button_rect = button_image.get_rect(topleft=sound_button_pos)
            if button_rect.collidepoint(mouse_pos):
                toggle_music()

def open_file_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window
    
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")], title="Choose a .txt file") 

    if not file_path:
        file_path = "words.txt"
    #if the file has less than 25 words, ask them to choose another file
    try:
        with open(file_path, 'r') as f:
            word_count = 0
            for line in f:
                for word in line.strip().split():
                    word_count += 1
            if word_count < 25:
                file_path = open_file_dialog()
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        file_path = open_file_dialog()
     
    return file_path

def draw_button(surface, pos, playing):
    surface.blit(button_image, pos)
    if not playing:
        # Draw a vertical line (making it 'mute' visually)
        pygame.draw.line(surface, (255, 0, 0), (pos[0] + button_image.get_width() // 2, pos[1]), 
                         (pos[0] + button_image.get_width() // 2, pos[1] + button_image.get_height()), 5)
# Function to toggle music
def toggle_music():
    global music_playing, button_image
    if music_playing:
        pygame.mixer.music.pause()
        button_image = play_button_image
    else:
        pygame.mixer.music.unpause()
        button_image = mute_button_image
    music_playing = not music_playing

# Function to play the block removal sound
def play_block_remove_sound():
    block_remove_sound.play()

def main():     
    start_button = Button(pygame.Rect(win_width/2 - 50, win_height/2 - 25, 100, 50), "Start", GREEN)
    next_level_button = Button(pygame.Rect(win_width/2 - 75, win_height/2 - 25, 150, 50), "Next Level", GREEN)
    next_level_button.is_visible = False
    exit_button = Button(pygame.Rect(win_width/2 - 50, win_height/2 + 50, 100, 50), "Exit", RED)
    load_button = Button(pygame.Rect(win_width/2 - 50, win_height/2 + 125, 100, 50), "Load", GREEN)
    
    # Initialize the clock
    clock = pygame.time.Clock()
     # Set the frame rate ( 60 frames per second)
    fps = 60
    game = Game(start_button, next_level_button, exit_button, load_button)
    game.background_image = pygame.transform.scale(game.background_image, (win_width, win_height))
    while game.running:
        # Draw the background
        game.screen.blit(game.background_image, (0, 0))
        for event in pygame.event.get():
            game.handle_sound_button(event)
            if event.type == pygame.QUIT:
                game.running = False
            elif game.menu:
                game.handle_menu_events(event)
            elif game.game:
                game.handle_game_events(event) 
            elif game.game_over:
                game.handle_game_over_events(event)     
        game.screen.blit(button_image, sound_button_pos)
        
        if game.menu:
            game.draw_menu()
        elif game.game:
            game.update_floating_blocks()
            game.draw_game()
        elif game.game_over:
            game.draw_game_over()   

        pygame.display.flip()
        clock.tick(fps)
if __name__ == "__main__":
    main()
