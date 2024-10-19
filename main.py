import pygame
import math

# Initialisiere Pygame
pygame.init()

# Bildschirmgröße
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Raycasting mit Slider und FPS")

# Farben
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Slider-Parameter
slider_x = 100
slider_y = 10
slider_width = 440
slider_height = 20
slider_min_rays = 10
slider_max_rays = 800
slider_value = 10
slider_target_value = 150
slider_duration = 5.0
elapsed_time = 0.0

# Spielerattribute
player_x = 64  # Startet in der Mitte der Kachel (1, 1)
player_y = 64  # Kachel (1, 1)
player_angle = math.pi / 5  # Startet in Richtung 0 Grad (rechts)
player_speed = 120  # Geschwindigkeit in Pixeln pro Sekunde (nicht pro Frame)
rotation_speed = 2  # Drehgeschwindigkeit auf 20% reduziert (vorher 120)

# Labyrinth (1 = Wand, 0 = leerer Raum)
maze = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 1, 0, 1, 0, 1],
    [1, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]

# Gegner als Linienbuchstabe "B"
enemy_pos = {"x": 6 * 64, "y": 6 * 64}  # Gegner auf Kachel (6, 6)

# Maze-Parameter
TILE_SIZE = 64  # Größe einer Kachel (1 Einheit im Labyrinth)
PLAYER_RADIUS = 15  # Radius des Spielers für die Kollisionsprüfung

# FPS-Zähler
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Funktion für Raycasting
def cast_rays(num_rays):
    FOV = math.pi / 2  # 90 Grad Sichtfeld
    HALF_FOV = FOV / 2
    MAX_DEPTH = 800
    DISTANCE_TO_PROJECTION_PLANE = (WIDTH / 2) / math.tan(HALF_FOV)
    delta_angle = FOV / num_rays  # Der Winkel zwischen den einzelnen Strahlen bleibt abhängig vom FOV konstant
    current_angle = player_angle - HALF_FOV

    for ray in range(num_rays):
        for depth in range(MAX_DEPTH):
            target_x = player_x + depth * math.cos(current_angle)
            target_y = player_y + depth * math.sin(current_angle)

            col = int(target_x // TILE_SIZE)
            row = int(target_y // TILE_SIZE)

            # Verhindere Array-Index-Fehler, wenn die Koordinaten außerhalb des Labyrinths liegen
            if col < 0 or col >= len(maze[0]) or row < 0 or row >= len(maze):
                break

            if maze[row][col] == 1:
                wall_height = min(HEIGHT, int(TILE_SIZE / (depth + 0.0001) * DISTANCE_TO_PROJECTION_PLANE))
                # Verteilungsanpassung: Strahlen pixelgenau über die gesamte Bildschirmbreite verteilen
                ray_screen_x = int(ray * (WIDTH / num_rays))  # Strahlen werden über die gesamte Breite verteilt
                pygame.draw.line(screen, WHITE, (ray_screen_x, (HEIGHT // 2) - wall_height // 2),
                                 (ray_screen_x, (HEIGHT // 2) + wall_height // 2))
                break

        current_angle += delta_angle


# Funktion zum Zeichnen von horizontalen Linien (Boden)
def draw_horizontal_lines():
    # Höhe, bei der der Boden beginnt (untere Bildschirmhälfte)
    for y in range(HEIGHT // 2 + 1, HEIGHT, 5):  # Startet 1 Pixel unter der Mitte, um Division durch 0 zu vermeiden
        depth = HEIGHT / (2 * (y - HEIGHT // 2 + 0.0001))  # Simuliert die Entfernung, kleiner Offset hinzugefügt
        line_color = (100, 100, 100)  # Graue Linien für den Boden
        pygame.draw.line(screen, line_color, (0, y), (WIDTH, y))


# Kollisionserkennung zwischen Spieler und Wänden
def check_wall_collision(x, y):
    col = int(x // TILE_SIZE)
    row = int(y // TILE_SIZE)
    if maze[row][col] == 1:
        return True
    return False

# Funktion zur Bewegung des Spielers basierend auf Blickrichtung und Delta Time (dt)
def move_player(dt):
    global player_x, player_y
    move_x = player_speed * math.cos(player_angle) * dt  # Bewegung in x-Richtung basierend auf Blickwinkel und dt
    move_y = player_speed * math.sin(player_angle) * dt  # Bewegung in y-Richtung basierend auf Blickwinkel und dt

    new_x = player_x + move_x
    new_y = player_y + move_y

    # Nur bewegen, wenn keine Kollision mit einer Wand
    if not check_wall_collision(new_x, new_y):
        player_x = new_x
        player_y = new_y

# Funktion zum Zeichnen des Sliders
def draw_slider(value):
    # Slider-Hintergrund
    pygame.draw.rect(screen, WHITE, (slider_x, slider_y, slider_width, slider_height), 2)
    
    # Slider-Füllung (je nach Wert des Sliders)
    fill_width = (value - slider_min_rays) / (slider_max_rays - slider_min_rays) * slider_width
    pygame.draw.rect(screen, WHITE, (slider_x, slider_y, fill_width, slider_height))

# Funktion zur Abfrage des Sliders
def get_slider_value(mouse_x):
    if slider_x <= mouse_x <= slider_x + slider_width:
        # Berechne den Slider-Wert basierend auf der Mausposition
        value = slider_min_rays + (mouse_x - slider_x) / slider_width * (slider_max_rays - slider_min_rays)
        return int(value)
    return slider_value

def can_see_cube(cube_pos):
    dx = cube_pos["x"] - player_x
    dy = cube_pos["y"] - player_y
    distance = math.sqrt(dx ** 2 + dy ** 2)

    steps = int(distance / TILE_SIZE * 10)  # Verfeinerte Schritte zur genaueren Prüfung
    step_x = dx / steps
    step_y = dy / steps

    for step in range(steps):
        check_x = player_x + step_x * step
        check_y = player_y + step_y * step
        col = int(check_x // TILE_SIZE)
        row = int(check_y // TILE_SIZE)

        # Wenn eine Wand gefunden wird, ist die Sicht blockiert
        if maze[row][col] == 1:
            return False

    return True
# Funktion zur Projektion eines Würfels
def project_cube():
    # Würfelgröße (30x30 Pixel) und Position
    cube_size = 30
    cube_pos = {"x": 6 * TILE_SIZE, "y": 6 * TILE_SIZE}  # Position des Würfels auf Kachel (6, 6)

    # Berechne den Abstand zum Spieler
    dx = cube_pos["x"] - player_x
    dy = cube_pos["y"] - player_y
    distance = math.sqrt(dx ** 2 + dy ** 2)

    # Verhindere das Rendern, wenn der Würfel zu nah oder zu weit weg ist
    if distance < TILE_SIZE / 2 or distance > 800:
        return
    
    # Prüfe, ob der Spieler den Würfel sehen kann (Sichtlinie frei von Wänden)
    if not can_see_cube(cube_pos):
        return
    
    # Winkel zwischen Spieler und Würfel
    angle_to_cube = math.atan2(dy, dx)
    angle_diff = angle_to_cube - player_angle

    # Normalisierung des Winkels, damit er zwischen -π und π liegt
    angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

    # Würfel wird nur gerendert, wenn er im erweiterten Sichtfeld (90 Grad) ist
    if -math.pi / 4 < angle_diff < math.pi / 4:
        # Berechne die projizierte Position auf dem Bildschirm basierend auf dem Winkel
        projected_x = (WIDTH / 2) + math.tan(angle_diff) * (WIDTH / 2)
        cube_proj_size = cube_size / distance * 200  # Skalierung des Würfels basierend auf der Entfernung
        
        # Verhindere, dass der Würfel zu klein oder zu groß wird
        cube_proj_size = max(5, min(cube_proj_size, cube_size))
        
        # Zeichne den Würfel auf den Boden, projiziert auf den Bildschirm
        pygame.draw.rect(screen, WHITE, 
                         (projected_x - cube_proj_size // 2, HEIGHT // 2 + 50, cube_proj_size, cube_proj_size))
# Funktion zur Projektion eines Würfels auf dem Boden
# Funktion zur Projektion eines Würfels auf dem Boden
def project_cube_on_floor():
    # Würfelgröße (30x30 Pixel) und Position
    cube_size = 30
    cube_pos = {"x": 6 * TILE_SIZE, "y": 6 * TILE_SIZE}  # Position des Würfels auf Kachel (6, 6)

    # Berechne den Abstand zum Spieler
    dx = cube_pos["x"] - player_x
    dy = cube_pos["y"] - player_y
    distance = math.sqrt(dx ** 2 + dy ** 2)

    # Verhindere das Rendern, wenn der Würfel zu nah oder zu weit weg ist
    if distance < TILE_SIZE / 2 or distance > 800:
        return
    
    # Prüfe, ob der Spieler den Würfel sehen kann (Sichtlinie frei von Wänden)
    if not can_see_cube(cube_pos):
        return
    
    # Winkel zwischen Spieler und Würfel
    angle_to_cube = math.atan2(dy, dx)
    angle_diff = angle_to_cube - player_angle

    # Normalisierung des Winkels, damit er zwischen -π und π liegt
    angle_diff = (angle_diff + math.pi) % (2 * math.pi) - math.pi

    # Würfel wird nur gerendert, wenn er im erweiterten Sichtfeld (90 Grad) ist
    if -math.pi / 4 < angle_diff < math.pi / 4:
        # Berechne die projizierte Position auf dem Bildschirm basierend auf dem Winkel
        projected_x = (WIDTH / 2) + math.tan(angle_diff) * (WIDTH / 2)
        cube_proj_size = cube_size / distance * 200  # Skalierung des Würfels basierend auf der Entfernung
        
        # Verhindere, dass der Würfel zu klein oder zu groß wird
        cube_proj_size = max(5, min(cube_proj_size, cube_size))
        
        # Zeichne den Würfel am Boden, projiziert auf den Bildschirm (am unteren Rand der Mitte)
        pygame.draw.rect(screen, WHITE, 
                         (projected_x - cube_proj_size // 2, HEIGHT // 2 + 100 - cube_proj_size, 
                          cube_proj_size, cube_proj_size))



# Hauptspiel-Schleife
running = True

while running:
    dt = clock.tick(60) / 1000.0  # Delta Time in Sekunden
    elapsed_time += dt  # Aktualisiert die verstrichene Zeit

    # Berechne den Sliderwert basierend auf der Zeit (langsamer Anstieg)
    if slider_value < slider_target_value:
        # Berechne, wie viel der Slider innerhalb des Zeitintervalls ansteigen sollte
        slider_value = min(slider_target_value, 10 + (elapsed_time / slider_duration) * (slider_target_value - 10))

    screen.fill(BLACK)

    # Ereignisverarbeitung
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Slidersteuerung (manuelle Anpassung mit Maus, falls notwendig)
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:  # Linke Maustaste gedrückt
                mouse_x, _ = pygame.mouse.get_pos()
                slider_value = get_slider_value(mouse_x)

    # Steuerung für kontinuierliche Drehung und Bewegung
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_angle -= rotation_speed * dt  # Drehung abhängig von Delta Time (dt)
    if keys[pygame.K_RIGHT]:
        player_angle += rotation_speed * dt  # Drehung abhängig von Delta Time (dt)
    if keys[pygame.K_UP]:
        move_player(dt)

    # Zeichne den Boden (horizontale Linien)
    draw_horizontal_lines()

    # Projiziere den Würfel auf dem Boden
    #project_cube_on_floor()

    # Strahlen werfen (Raycasting) basierend auf dem aktuellen slider_value
    cast_rays(int(slider_value))

    # Zeichne den Slider
    draw_slider(int(slider_value))

    # FPS-Zähler anzeigen
    fps = int(clock.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, WHITE)
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()

