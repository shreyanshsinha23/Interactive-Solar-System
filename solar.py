import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1365, 780
SIDEBAR_WIDTH = 200
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Realistic Solar System with Sidebar and Expanding Planet View")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
HIGHLIGHT_COLOR = (100, 100, 255)
SIDEBAR_BG_COLOR = (74, 4, 4, 180)  # Acrylic effect (semi-transparent)
TOGGLE_BUTTON_COLOR = (74, 4, 4, 255)

# Clock
clock = pygame.time.Clock()

# Scaling factor for orbits
MAX_ORBIT_RADIUS = min(WIDTH - SIDEBAR_WIDTH, HEIGHT) // 2 - 40
ORBIT_SCALE = MAX_ORBIT_RADIUS / 850

# Planet Data
PLANETS = [
    ("Mercury", int(120 * ORBIT_SCALE), 10, 2.0, "Mercury.png", 4879, 0),
    ("Venus", int(200 * ORBIT_SCALE), 20, 1.5, "Venus.png", 12104, 0),
    ("Vulcan", int(280 * ORBIT_SCALE), 20, 1.3, "Vulcan.png", 5000, 0),
    ("Earth", int(360 * ORBIT_SCALE), 20, 1.0, "Earth.png", 12742, 1),
    ("Mars", int(450 * ORBIT_SCALE), 10, 0.8, "Mars.png", 6779, 2),
    ("Jupiter", int(550 * ORBIT_SCALE), 60, 0.5, "Jupiter.png", 139820, 79),
    ("Saturn", int(670 * ORBIT_SCALE), 50, 0.3, "Saturn.png", 116460, 82),
    ("Uranus", int(780 * ORBIT_SCALE), 40, 0.2, "Uranus.png", 50724, 27),
    ("Neptune", int(900 * ORBIT_SCALE), 40, 0.1, "Neptune.png", 49244, 14),
]

# Preload and cache scaled planet images
planet_images = {}
sidebar_icons = {}
expanded_images = {}
for planet in PLANETS:
    name, _, size, _, img_file, _, _ = planet
    img = pygame.image.load(img_file).convert_alpha()
    planet_images[name] = pygame.transform.smoothscale(img, (size, size))
    expanded_images[name] = pygame.transform.smoothscale(img, (HEIGHT * 4 // 5, HEIGHT * 4 // 5))
    sidebar_icons[name] = pygame.transform.smoothscale(img, (40, 40))

# Load Sun and background images
sun_image = pygame.image.load("Sun.png").convert_alpha()
sun_image = pygame.transform.smoothscale(sun_image, (90, 90))
bg_image = pygame.image.load("background.png").convert_alpha()
bg_image = pygame.transform.smoothscale(bg_image, (WIDTH, HEIGHT))

# Font
font = pygame.font.SysFont("Arial", 20)

# Sidebar state
sidebar_visible = True
selected_planet = None
expanding = False
expansion_progress = 0  # Progress of the planet expansion (0 to 1)

# Sidebar button dimensions
toggle_button_rect = pygame.Rect(10, 10, 50, 40)

# Functions to draw the sidebar and expanding planet...
def draw_sidebar():
    if not sidebar_visible:  # Skip drawing the sidebar if it is hidden
        return

    # Draw the acrylic effect for the sidebar
    sidebar_surface = pygame.Surface((SIDEBAR_WIDTH, HEIGHT), pygame.SRCALPHA)
    sidebar_surface.fill(SIDEBAR_BG_COLOR)
    screen.blit(sidebar_surface, (0, 0))

    # Draw planet names and icons in the sidebar
    y_offset = 80
    spacing = 60
    for planet in PLANETS:
        name, _, _, _, _, _, _ = planet

        # Draw planet icon
        screen.blit(sidebar_icons[name], (20, y_offset - 5))

        # Draw planet name
        text_surface = font.render(name, True, WHITE)
        text_rect = text_surface.get_rect(topleft=(70, y_offset))

        # Highlight the selected planet
        if selected_planet and selected_planet[0] == name:
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, (10, y_offset - 10, SIDEBAR_WIDTH - 20, 50), border_radius=10)

        screen.blit(text_surface, text_rect.topleft)
        y_offset += spacing

    # Draw information for the selected planet
    if selected_planet and not expanding:
        name, _, _, _, _, size_km, satellites = selected_planet
        text_y = 20
        line_spacing = 30
        name_text = font.render(f"Name: {name}", True, WHITE)
        size_text = font.render(f"Size: {size_km} km", True, WHITE)
        satellites_text = font.render(f"Satellites: {satellites}", True, WHITE)

        screen.blit(name_text, (10, text_y))
        screen.blit(size_text, (10, text_y + line_spacing))
        screen.blit(satellites_text, (10, text_y + 2 * line_spacing))


def draw_expanding_planet():
    global expansion_progress
    if selected_planet is None:
        return

    # Get planet details
    name, _, size, _, _, size_km, satellites = selected_planet
    planet_image = expanded_images[name]

    # Calculate size during expansion
    current_size = int(size + (planet_image.get_width() - size) * expansion_progress)
    if name == "Saturn":
        # Stretch Saturn horizontally by a factor of 2
        current_size_width = int(current_size * 2)
        resized_img = pygame.transform.smoothscale(planet_image, (current_size_width, current_size))
    else:
        resized_img = pygame.transform.smoothscale(planet_image, (current_size, current_size))

    # Draw the resized planet image at the center of the screen
    screen.blit(resized_img, resized_img.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    # Draw planet details on the right side
    details_x = WIDTH - SIDEBAR_WIDTH
    details_surface = pygame.Surface((SIDEBAR_WIDTH, HEIGHT), pygame.SRCALPHA)
    details_surface.fill(SIDEBAR_BG_COLOR)
    screen.blit(details_surface, (details_x, 0))

    text_y = 20
    line_spacing = 30
    name_text = font.render(f"Name: {name}", True, WHITE)
    size_text = font.render(f"Size: {size_km} km", True, WHITE)
    satellites_text = font.render(f"Satellites: {satellites}", True, WHITE)

    screen.blit(name_text, (details_x + 10, text_y))
    screen.blit(size_text, (details_x + 10, text_y + line_spacing))
    screen.blit(satellites_text, (details_x + 10, text_y + 2 * line_spacing))


# Add code for blinking stars
def generate_stars(num_stars):
    stars = []
    for _ in range(num_stars):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        brightness = random.uniform(0.2, 1.0)  # Initial brightness
        stars.append([x, y, brightness])
    return stars

def draw_blinking_stars(stars):
    for star in stars:
        # Adjust brightness with a sine wave function to create a blinking effect
        star[2] = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 500 + star[0] / 100)
        color = (255, 255, 255, int(star[2] * 255))  # Calculate the color based on brightness
        pygame.draw.circle(screen, color, (star[0], star[1]), random.randint(1, 2))


# Main loop
def main():
    global sidebar_visible, selected_planet, expanding, expansion_progress
    running = True
    angles = [random.uniform(0, 360) for _ in PLANETS]
    
    # Generate stars
    stars = generate_stars(200)  # Adjust the number of stars as desired

    while running:
        screen.blit(bg_image, (0, 0))

        # Draw blinking stars on the screen
        draw_blinking_stars(stars)

        # Draw the toggle button (always visible)
        pygame.draw.rect(screen, TOGGLE_BUTTON_COLOR, toggle_button_rect, border_radius=10)
        for i in range(3):
            pygame.draw.line(
                screen,
                WHITE,
                (toggle_button_rect.x + 15, toggle_button_rect.y + 12 + i * 8),
                (toggle_button_rect.x + 35, toggle_button_rect.y + 12 + i * 8),
                3,
            )

        # Handle planet expansion
        if expanding:
            if expansion_progress < 1:
                expansion_progress += 0.02
            else:
                expansion_progress = 1
            draw_expanding_planet()
        else:
            # Draw the sun and orbits
            screen.blit(sun_image, sun_image.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
            for planet in PLANETS:
                radius = planet[1]
                pygame.draw.circle(screen, WHITE, (WIDTH // 2, HEIGHT // 2), radius, 1)

            # Draw planets
            for i, planet in enumerate(PLANETS):
                name, distance, size, speed, _, _, _ = planet
                angles[i] = (angles[i] + speed) % 360
                x = WIDTH // 2 + math.cos(math.radians(angles[i])) * distance
                y = HEIGHT // 2 + math.sin(math.radians(angles[i])) * distance

                # Check if it's Saturn and stretch horizontally
                if name == "Saturn":
                    stretched_img = pygame.transform.smoothscale(planet_images[name], (int(size * 2), size))  # Stretch horizontally
                    screen.blit(stretched_img, stretched_img.get_rect(center=(int(x), int(y))))
                else:
                    screen.blit(planet_images[name], planet_images[name].get_rect(center=(int(x), int(y))))

            # Draw the sidebar
            draw_sidebar()

        # Handle events
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True

        # Handle sidebar toggle
        if toggle_button_rect.collidepoint(mouse_pos) and mouse_clicked:
            sidebar_visible = not sidebar_visible

        # Handle planet selection and return
        if expanding and mouse_clicked:
            expanding = False
            expansion_progress = 0
            selected_planet = None

        elif sidebar_visible and mouse_clicked and not expanding:
            y_offset = 80
            spacing = 60
            for planet in PLANETS:
                rect = pygame.Rect(10, y_offset - 10, SIDEBAR_WIDTH - 20, 50)
                if rect.collidepoint(mouse_pos):
                    selected_planet = planet
                    expanding = True
                    expansion_progress = 0
                y_offset += spacing

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
