import pygame
import random
import pygame_gui
import math

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
orc_frames = [orc_sprite_sheet.subsurface(pygame.Rect(x * 100, 100, 100, 100)) for x in range(6)]

# Animation frame rate
FRAME_RATE = 0.4

class Agent:
    def __init__(self):
        self.hungriness = 100
        self.position = pygame.Vector2(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * MAX_SPEED
        self.frame_index = 0

    def update(self, target):

        a = (target - self.position).normalize() * 5
        self.velocity += a

        # Limit speed
        if self.velocity.length() > MAX_SPEED:
            self.velocity.scale_to_length(MAX_SPEED)

        # Update position
        self.position += self.velocity

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
