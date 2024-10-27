import pygame
import random
import pygame_gui
import math
from enum import Enum

WIDTH, HEIGHT = 800, 600
NUM_AGENTS = 1
VISION_RANGE = 200
ATTACK_RANGE = 50
HUNGER = 100
HUNGER_DRAIN_RATE = 8
POWER = 100
POWER_DRAIN_RATE = 5
FOOD_SIZE = 3
MAX_SPEED = 4
FOOD_POSITION = pygame.Vector2(200, 200)
BED_POSITION = pygame.Vector2(600, 200)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("State Machine")

# Load Orc Sprite Sheet
moodeng_sprite_sheet = pygame.image.load('./assets/MoodengSprite.png').convert_alpha()
banana_sprite = pygame.image.load('./assets/Banana.png').convert_alpha()
bed_sprite = pygame.image.load('./assets/Bed.png').convert_alpha()
moodeng_walk_animation = [moodeng_sprite_sheet.subsurface(pygame.Rect(x * 128, 0, 128, 128)) for x in range(2)]
moodeng_sleep = [moodeng_sprite_sheet.subsurface(pygame.Rect(x * 128, 1 * 128, 128, 128)) for x in range(2)]
moodeng_attack_animation = [moodeng_sprite_sheet.subsurface(pygame.Rect(x * 128, 2 * 128, 128, 128)) for x in range(5)]
moodeng_frames = moodeng_walk_animation
banana_frame = banana_sprite.subsurface(pygame.Rect(0, 0, 80, 80))
bed_frame = bed_sprite.subsurface(pygame.Rect(0, 0, 192, 192))

# Animation frame rate
FRAME_RATE = 0.4

# States------------
class AgentState(Enum):
    WANDERING_STATE = 0
    CHASE_STATE = 1
    WALK_TO_FOOD_STATE = 2
    WALK_TO_HOME_STATE = 3
    ATK_STATE = 4
    EAT_STATE = 5
    SLEEP_STATE = 6
#---------------------

class Agent:
    def __init__(self):
        self.position = pygame.Vector2(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * MAX_SPEED
        self.frame_index = 0
        
        self.power = POWER
        self.hunger = HUNGER
        
        self.current_state = AgentState.WANDERING_STATE
        self.current_animation = moodeng_walk_animation

    def update(self, target, food, home, time_detaTime):
        if self.current_state != AgentState.EAT_STATE and self.current_state != AgentState.SLEEP_STATE:
            self.hunger -= HUNGER_DRAIN_RATE * time_detaTime
            self.power -= POWER_DRAIN_RATE * time_detaTime
         
        if self.hunger <= 0:
            self.hunger = 0
            
        if self.power <= 0:
            self.power = 0
        
        print("State > " + str(self.current_state) + " : " + "Hunger = " + str(round(self.hunger)) + " : " + "Power = " + str(round(self.power)))
        
        a = pygame.Vector2(0,0)
        if self.current_state == AgentState.WANDERING_STATE:
            self.current_animation = moodeng_walk_animation
            self.velocity.x = random.randint(0, 600)
            self.velocity.y = random.randint(0, 600)
            if self.velocity.length() > MAX_SPEED:
                self.velocity.scale_to_length(MAX_SPEED)
            self.position += self.velocity

            # transition that could change to other stages
            dist = (target - self.position).length()
            if(self.power > 50 and self.hunger > 50):
                if dist < VISION_RANGE:
                    self.current_state = AgentState.CHASE_STATE
            elif(self.hunger < 50):
                self.current_state = AgentState.WALK_TO_FOOD_STATE
            elif(self.power < 50):
                self.current_state = AgentState.WALK_TO_HOME_STATE

        elif self.current_state == AgentState.CHASE_STATE:
            self.current_animation = moodeng_walk_animation
            a = (target - self.position).normalize() * 5
            self.velocity += a
            if self.velocity.length() > MAX_SPEED:
                self.velocity.scale_to_length(MAX_SPEED)
            self.position += self.velocity

            # transition that could change to other stages
            dist = (target - self.position).length()
            if self.hunger > 50 and self.power > 50:
                if dist >= VISION_RANGE:
                    self.current_state = AgentState.WANDERING_STATE
                if dist <= ATTACK_RANGE:
                    self.current_state = AgentState.ATK_STATE
            else:
                self.current_state = AgentState.WANDERING_STATE

        elif self.current_state == AgentState.ATK_STATE:
            self.current_animation = moodeng_attack_animation
            #self.velocity *= 0

            # transition that could change to other stages
            dist = (target - self.position).length()
            if self.hunger > 50 and self.power > 50:
                if dist > ATTACK_RANGE:
                    self.current_state = AgentState.CHASE_STATE
            else:
                self.current_state = AgentState.WANDERING_STATE
          
        elif self.current_state == AgentState.WALK_TO_FOOD_STATE:
            self.current_animation = moodeng_walk_animation
            a = (food - self.position).normalize() * 5
            self.velocity += a
            if self.velocity.length() > MAX_SPEED:
                self.velocity.scale_to_length(MAX_SPEED)
            self.position += self.velocity

            # transition that could change to other stages
            dist = (food - self.position).length()
            if dist <= ATTACK_RANGE:
                self.current_state = AgentState.EAT_STATE
                
        elif self.current_state == AgentState.EAT_STATE:
            self.current_animation = moodeng_attack_animation
            #self.velocity *= 0
            self.hunger += HUNGER_DRAIN_RATE * 5 * time_detaTime
            
            if self.hunger >= HUNGER:
                self.current_state = AgentState.WANDERING_STATE
        
        elif self.current_state == AgentState.WALK_TO_HOME_STATE:
            self.current_animation = moodeng_walk_animation
            a = (home - self.position).normalize() * 5
            self.velocity += a
            if self.velocity.length() > MAX_SPEED:
                self.velocity.scale_to_length(MAX_SPEED)
            self.position += self.velocity

            # transition that could change to other stages
            dist = (home - self.position).length()
            if dist <= 3:
                self.current_state = AgentState.SLEEP_STATE  
        
        elif self.current_state == AgentState.SLEEP_STATE:
            self.current_animation = moodeng_sleep
            #self.velocity *= 0
            self.power += POWER_DRAIN_RATE * 5 * time_detaTime
            
            if self.power >= POWER:
                self.current_state = AgentState.WANDERING_STATE
                
        a *= 0 # clear force

        # Warp around
        if self.position.x > WIDTH:
            self.position.x = 0
        elif self.position.x < 0:
            self.position.x = WIDTH
        if self.position.y > HEIGHT:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = HEIGHT

        return True


    def draw(self, screen, food_position, bed_position):
        # Update frame index for animation
        self.frame_index = (self.frame_index + FRAME_RATE) % len(self.current_animation)
        current_frame = self.current_animation[ int(self.frame_index) ]

        if self.velocity.x < 0:
            current_frame = pygame.transform.flip(current_frame, True, False)
        
        screen.blit(banana_frame, food_position - pygame.Vector2(40, 40))
        screen.blit(bed_frame, bed_position - pygame.Vector2(96, 96))
        screen.blit(current_frame, (int(self.position.x) - 64, int(self.position.y) - 64))
        

# ------------------------------------------------------------------------------------------------


def main():
    agents = [Agent() for _ in range(NUM_AGENTS)]

    clock = pygame.time.Clock()

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        screen.fill((190, 240, 200))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            target = pygame.Vector2(pygame.mouse.get_pos())

        agents = [moodeng for moodeng in agents if moodeng.update(target,FOOD_POSITION,BED_POSITION,time_delta)]
        for agent in agents:
            agent.draw(screen, FOOD_POSITION, BED_POSITION)

        pygame.draw.circle(screen, (255, 0, 0), (int(target.x), int(target.y)), FOOD_SIZE)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
