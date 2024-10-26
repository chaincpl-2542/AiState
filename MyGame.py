import pygame
import random
import pygame_gui
import math
from enum import Enum

WIDTH, HEIGHT = 800, 600
NUM_AGENTS = 1
VISION_RANGE = 100
HUNGER = 100
HUNGER_DRAIN_RATE = 6
POWER = 100
POWER_DRAIN_RATE = 4
FOOD_SIZE = 3
MAX_SPEED = 2


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
manager = pygame_gui.UIManager((WIDTH, HEIGHT))
food_rate_slider = pygame_gui.elements.UIHorizontalSlider(
    relative_rect=pygame.Rect((10, 10), (200, 20)),
    start_value=500,
    value_range=(100, 2000),
    manager=manager
)
pygame.display.set_caption("State Machine")

# Load Orc Sprite Sheet
orc_sprite_sheet = pygame.image.load('./assets/Orc.png').convert_alpha()
orc_walk_animation = [orc_sprite_sheet.subsurface(pygame.Rect(x * 100, 100, 100, 100)) for x in range(6)]
orc_attack_animation = [orc_sprite_sheet.subsurface(pygame.Rect(x * 100, 2 * 100, 100, 100)) for x in range(6)]
orc_frames = orc_walk_animation

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
        self.current_animation = orc_walk_animation

    def update(self, target, food, home, time_detaTime):
        if self.current_state != AgentState.EAT_STATE and self.current_state != AgentState.SLEEP_STATE:
            self.hunger -= HUNGER_DRAIN_RATE * time_detaTime
            self.power -= POWER_DRAIN_RATE * time_detaTime
         
        print("State > " + str(self.current_state) + " : " + "Hunger > " + str(round(self.hunger)) + " : " + "Power > " + str(round(self.power)))
        
        a = pygame.Vector2(0,0)
        if self.current_state == AgentState.WANDERING_STATE:
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
            a = (target - self.position).normalize() * 5
            self.velocity += a
            if self.velocity.length() > MAX_SPEED:
                self.velocity.scale_to_length(MAX_SPEED)
            self.position += self.velocity

            # transition that could change to other stages
            dist = (target - self.position).length()
            if dist >= 100:
                self.current_state = AgentState.WANDERING_STATE
            if dist <= 10:
                self.current_state = AgentState.ATK_STATE

        elif self.current_state == AgentState.ATK_STATE:
            self.velocity *= 0

            # transition that could change to other stages
            dist = (target - self.position).length()
            if dist > 10:
                self.current_state = AgentState.CHASE_STATE
          
        elif self.current_state == AgentState.WALK_TO_FOOD_STATE:
            a = (food - self.position).normalize() * 5
            self.velocity += a
            if self.velocity.length() > MAX_SPEED:
                self.velocity.scale_to_length(MAX_SPEED)
            self.position += self.velocity

            # transition that could change to other stages
            dist = (food - self.position).length()
            if dist <= 10:
                self.current_state = AgentState.EAT_STATE
                
        elif self.current_state == AgentState.EAT_STATE:
            self.velocity *= 0
            self.hunger += HUNGER_DRAIN_RATE * 5 * time_detaTime
            
            if self.hunger >= 100:
                self.current_state = AgentState.WANDERING_STATE
        
        elif self.current_state == AgentState.WALK_TO_HOME_STATE:
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
            self.velocity *= 0
            self.power += POWER_DRAIN_RATE * 5 * time_detaTime
            
            if self.power >= 100:
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


    def draw(self, screen):
        # Update frame index for animation
        self.frame_index = (self.frame_index + FRAME_RATE) % len(orc_frames)
        current_frame = orc_frames[ int(self.frame_index) ]

        if self.velocity.x < 0:
            current_frame = pygame.transform.flip(current_frame, True, False)

        if self.current_state == AgentState.WANDERING_STATE:
            pygame.draw.circle(screen, (0,0,255), self.position, 10 )
        elif self.current_state == AgentState.CHASE_STATE:
            pygame.draw.circle(screen, (255, 255, 0 ), self.position, 10)
        elif self.current_state == AgentState.ATK_STATE:
            pygame.draw.circle(screen, (255, 0, 0 ), self.position, 10)
        
        screen.blit(current_frame, (int(self.position.x) - 50, int(self.position.y) - 50))


# ------------------------------------------------------------------------------------------------


def main():
    agents = [Agent() for _ in range(NUM_AGENTS)]

    clock = pygame.time.Clock()

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        screen.fill((100, 100, 100))
        manager.update(time_delta)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.process_events(event)

            target = pygame.Vector2(pygame.mouse.get_pos())
            food = pygame.Vector2(pygame.mouse.get_pos())
            home = pygame.Vector2(pygame.mouse.get_pos())

        agents = [moodeng for moodeng in agents if moodeng.update(target,food,home,time_delta)]
        for agent in agents:
            agent.draw(screen)

        pygame.draw.circle(screen, (255, 0, 0), (int(target.x), int(target.y)), FOOD_SIZE)

        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()