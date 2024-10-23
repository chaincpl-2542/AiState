import pygame
import random
import pygame_gui
import math
from enum import Enum
from abc import ABC, abstractmethod

WIDTH, HEIGHT = 800, 600
NUM_AGENTS = 1
FISH_SIZE = 5
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
    PATROL_STATE = 0
    CHASE_STATE = 1
    ATK_STATE = 2
#---------------------
class StateMachine():
    def __init__(self) -> None:
        self.states = {
            'patrol': PatrolState(),
            'chase': ChaseState(),
            'attack': AtkState()
        }
        self.curret_state = 'patrol'

    def update(self, agent, target):
        new_state = self.states[self.curret_state].update(agent, target)
        if new_state:
            self.transition_to(agent, new_state)

    def transition_to(self, agent, new_state):
        self.states[self.curret_state].exit(agent)
        self.curret_state = new_state
        self.states[self.curret_state].enter(agent)



class State(ABC):
    @abstractmethod
    def enter(self, agent):
        pass

    @abstractmethod
    def update(self, agent, target):
        pass
    
    @abstractmethod
    def exit(self, agent):
        pass

class PatrolState(State):
    def enter(self, agent):
        pass

    def update(self, agent, target):
        agent.velocity.x = random.randint(0, 600)
        agent.velocity.y = random.randint(0, 600)
        if agent.velocity.length() > MAX_SPEED:
            agent.velocity.scale_to_length(MAX_SPEED)
        agent.position += agent.velocity

        # transition that could change to other stages
        dist = (target - agent.position).length()
        if dist < 100:
            return 'chase'

    def exit(self, agent):
        pass

class ChaseState(State):
    def enter(self, agent):
        pass

    def update(self, agent, target):
        a = (target - agent.position).normalize() * 5
        agent.velocity += a
        if agent.velocity.length() > MAX_SPEED:
            agent.velocity.scale_to_length(MAX_SPEED)
        agent.position += agent.velocity

        # transition that could change to other stages
        dist = (target - agent.position).length()
        if dist >= 100:
            return 'patrol'
        if dist <= 10:
            return 'attack'

    def exit(self, agent):
        pass


class AtkState(State):
    def enter(self, agent):
        agent.velocity *= 0

    def update(self, agent, target):
        
        # transition that could change to other stages
        dist = (target - agent.position).length()
        if dist > 10:
            return 'chase'

    def exit(self, agent):
        pass


class Agent:
    def __init__(self):
        self.position = pygame.Vector2(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * MAX_SPEED
        self.frame_index = 0
        
        self.state_machine = StateMachine()

        self.current_animation = orc_walk_animation

    def update(self, target):

        self.state_machine.update(self, target)

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

        if self.state_machine.curret_state == 'patrol':
            pygame.draw.circle(screen, (0,0,255), self.position, 10 )
        elif self.state_machine.curret_state == 'chase':
            pygame.draw.circle(screen, (255, 255, 0 ), self.position, 10)
        elif self.state_machine.curret_state == 'attack':
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

        agents = [fish for fish in agents if fish.update(target)]
        for agent in agents:
            agent.draw(screen)

        pygame.draw.circle(screen, (255, 0, 0), (int(target.x), int(target.y)), FOOD_SIZE)

        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
