import pygame, os, sys, random, ballout_assets
from ast import literal_eval
from math import *


def get_screen(override=None):
    pygame.init()
    screen_info = pygame.display.Info()
    screen_l, screen_w = screen_info.current_w, screen_info.current_h
    return (screen_l, screen_w) if override == None else override


getTicksLastFrame = 0  #to not reset to 0 everytime the function is called


def get_delta_time() -> float:
    global getTicksLastFrame
    t = pygame.time.get_ticks()
    deltaTime = (t - getTicksLastFrame) / 1000.0
    getTicksLastFrame = t
    return deltaTime * 100


base_resolution = (1536, 864)


def scale_size(size: float, round_result=True):
    win = get_screen()
    scale_factor = min(win[0] / base_resolution[0],
                       win[1] / base_resolution[1])
    return round(size * scale_factor) if round_result else size * scale_factor


def scale_pos(self, pos: tuple, round_result=False):
    win = self.screen_size
    scale_factor = min(win[0] / self.base_resolution[0],
                       win[1] / self.base_resolution[1])
    x = pos[0] * scale_factor
    y = pos[1] * scale_factor
    return (round(x), round(y)) if round_result else (x, y)


def save(data, path="ballout_assets/save.txt"):
    with open(path, "w") as f:
        f.write(str(data))


def load(path="ballout_assets/save.txt"):
    try:
        with open(path, "r") as f:
            return literal_eval(f.read())
    except:
        return None


class Animation:
    """Animates frames from a spritesheet."""

    def __init__(self, spritesheet_path, frame_rects, size, flip=False):
        """
        :param spritesheet_path: Path to the spritesheet image
        :param frame_rects: List of (x, y, width, height) for each frame in the spritesheet
        :param size: Desired size to scale each frame to (width, height)
        :param animation_speed: Milliseconds between frames
        :param flip: Flip the frame horizontally if True
        """
        self.sprites = []
        self.current_sprite = 0
        self.last_update = 0
        # Load the spritesheet
        self.spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
        self.frame_rects = frame_rects
        self.flip = flip
        self.change_size(size)

    def change_size(self, size):
        # Extract each frame from the spritesheet
        for rect in self.frame_rects:
            frame = self.spritesheet.subsurface(pygame.Rect(rect))
            frame = pygame.transform.scale(frame, size)
            if self.flip:
                frame = pygame.transform.flip(frame, True, False)
            self.sprites.append(frame)

    def update(self, animation_speed: int = None, animate=True):
        now = pygame.time.get_ticks()
        if (now - self.last_update >= animation_speed) and animate:
            self.current_sprite = (self.current_sprite + 1) % len(self.sprites)
            self.last_update = now

        return self.sprites[self.current_sprite]

    def img_now(self, rotation=0, resized: tuple = False):
        img = self.sprites[self.current_sprite]

        # Resize the image if a size is given
        if resized:
            img = pygame.transform.scale(img, resized)

        # Rotate the image (rotate the resized image, not the original frame)
        img = pygame.transform.rotate(img, rotation)

        return img

    def find_hitrect(self, pos, inflate=(0, 0)):
        return self.sprites[self.current_sprite].get_rect(
            topleft=pos).inflate(inflate)


class buttons(pygame.sprite.Sprite):
    """Use to make it Simple buttons with Text"""

    def __init__(self,
                 x,
                 y,
                 font,
                 size,
                 text,
                 color,
                 txtcolor,
                 edge: str | tuple = None,
                 Invisable=False):
        super().__init__()
        self.x = int(x)
        self.y = int(y)
        self.font_name = font
        self.base_size = int(size)
        self.text = text
        self.color = color
        self.txtcolor = txtcolor
        self.edge = edge
        self.scale = 1.0
        self.target_scale = 1.0
        self.scale_speed = 0.05
        self.invisible = Invisable

        self.update_surface()

    def change_style(self, txt, color, txtcolor):
        self.color = color
        self.txtcolor = txtcolor
        self.text = txt
        self.update_surface()

    def update_surface(self):
        scaled_size = int(self.base_size * self.scale)
        self.font = pygame.font.Font(
            self.font_name,
            scaled_size) if self.font_name != "" else pygame.font.SysFont(
                self.font_name, scaled_size)
        self.text_surface = self.font.render(str(self.text), True,
                                             self.txtcolor)
        self.text_rect = self.text_surface.get_rect(center=(self.x, self.y))

        self.box_rect = pygame.Rect(self.text_rect.left - 20,
                                    self.text_rect.top - 10,
                                    self.text_rect.width + 40,
                                    self.text_rect.height + 20)

        self.image = pygame.Surface(
            (self.box_rect.width, self.box_rect.height), pygame.SRCALPHA)

        if not self.invisible:
            pygame.draw.rect(self.image,
                             self.color,
                             (0, 0, self.box_rect.width, self.box_rect.height),
                             border_radius=scale_size(10))

            self.image.blit(self.text_surface, (20, 10))
            if self.edge != None:
                pygame.draw.rect(
                    self.image,
                    self.edge,
                    (0, 0, self.box_rect.width, self.box_rect.height),
                    5,
                    border_radius=scale_size(10))
            self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, mouse_pos):
        # Check hover
        if self.box_rect.collidepoint(mouse_pos):
            self.target_scale = 1.2
        else:
            self.target_scale = 1.0

        # Smooth scale interpolation
        if abs(self.scale - self.target_scale) > 0.01:
            self.scale += (self.target_scale - self.scale) * self.scale_speed
            self.update_surface()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def get_rect(self, topleft=None):
        if topleft:
            temp_rect = self.box_rect.copy()
            temp_rect.topleft = topleft
            return temp_rect
        return self.box_rect



class ImageManager:
    """Mangages Images, make images button, helps with costumization"""

    def __init__(self,
                 image: pygame.surface,
                 size: tuple = (100, 100),
                 button=False,
                 big=0):
        #Initialize the ImageManager
        self.width, self.height = size
        self.image = pygame.transform.scale(
            image, (int(self.width), int(self.height)))
        self.button = button
        self.big = big
        self.rotation = 0

    def size_change(self, size: tuple = (100, 100)):
        self.width, self.height = size
        self.image = pygame.transform.scale(
            self.image, (int(self.width), int(self.height)))
        return self.image

    def Change_rotation(self, rotation: float):
        self.rotation = rotation

    def setting(self,
                surface: pygame.surface,
                location: float = (0.0, 0.0),
                draw=True):
        global x, y
        w, h = self.width, self.height
        x, y = location

        if self.button and pygame.Rect(x, y, w, h).collidepoint(
                pygame.mouse.get_pos()):
            w += self.big
            h += self.big
            y -= self.big / 2
            x -= self.big / 2

        # Resize
        self.image = pygame.transform.smoothscale(
            self.image, (int(w), int(h)))  # Directly update self.image

        # Rotate and re-center
        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        rect = rotated_image.get_rect(topleft=(x,
                                               y))  # Center the rotated image

        if draw:
            surface.blit(rotated_image, (x, y))

    def change_img(self, img: pygame.surface):
        self.image = pygame.transform.scale(
            img, (int(self.width), int(self.height)))

    def get_rect(self, inflate: int = (0, 0)):
        """Use this function to get the rectangle of a image(This is a Part of ImageManager)"""
        global x, y
        img = self.image
        inflate_w, inflate_h = inflate

        return img.get_rect(topleft=(x, y)).inflate(inflate_w, inflate_h)


class fonts:

    def __init__(self,
                 font: str = "",
                 screen: pygame.Surface = None,
                 size: int = 50) -> None:
        """
        font: Path to a .ttf font file or empty for default font.
        screen: The display Surface to draw on.
        size: Default font size.
        """
        self.display = screen
        self.size = size
        self.set_font(font)

    def set_font(self, font: str) -> None:
        """Sets the font path. Falls back to default if invalid."""
        if font and os.path.isfile(font):
            self.font_path = font
        else:
            self.font_path = None  # Use SysFont (default)

    def change_font(self, font: str) -> None:
        """Alias for set_font()."""
        self.set_font(font)

    def draw(self,
             pos,
             text: str,
             size: int = 30,
             color=(255, 255, 255),
             shadow=False,
             bg=False,
             bg_color="black",
             center=False,
             Italic=False,
             Bold=False):
        """Draws text with optional shadow/background and alignment."""

        if self.font_path:
            font = pygame.font.Font(self.font_path, size)
        else:
            font = pygame.font.SysFont(None, size)

        font.set_bold(Bold)
        font.set_italic(Italic)

        text_surface = font.render(text, True, color)

        if center:
            rect = text_surface.get_rect(center=pos)
        else:
            rect = text_surface.get_rect(topleft=pos)

        if shadow:
            shadow_surface = font.render(text, True, (0, 0, 0))
            shadow_pos = (rect.x + 2, rect.y + 2)
            self.display.blit(shadow_surface, shadow_pos)

        if bg:
            pygame.draw.rect(self.display, bg_color, rect)

        self.display.blit(text_surface, rect)


class timer:

    def __init__(self, screen, intervel, type="up", start_value=None):
        self.screen = screen
        self.intervel = intervel
        self.type = type
        self.start_value = start_value or 0
        self.time_left = start_value
        self.time_past = 0
        self.last = pygame.time.get_ticks()

    def step(self, increment: int | float = None) -> bool:
        now = pygame.time.get_ticks()
        interveal = self.intervel if increment is None else increment
        if now - self.last >= interveal:
            self.last = now
            if self.type == "down":
                if self.time_left > 0:
                    self.time_left -= 1
            elif self.type == "up":
                self.time_past += 1
            return True
        return False

    def show(self,
             pos: tuple,
             size: int = 50,
             color=(255, 255, 255),
             prefix=""):
        value = self.time_left if self.type == "down" else self.time_past
        self.txt.draw(scale_pos(pos, self.design_scale),
                      f"{prefix} {str(value)}",
                      size=scale_size(size, self.design_scale, True),
                      color=color)

    def __int__(self):
        return self.time_left if self.type == "down" else self.time_past

    def reset(self, intervel: float = 100, type="down", start_time: int = 0):
        """
        Reset the timer with the specified interval, type, and start time.
        """
        self.time_left = start_time  # Set the time_left to the start time
        self.time_past = 0  # Reset the time passed if counting up
        self.type = type  # Timer type ('up' or 'down')
        self.intervel = intervel  # Interval for timer updates (in milliseconds)
        self.last = pygame.time.get_ticks(
        )  # Current time to start the countdown/up
        self.time = self.last  # Save the current time


class MobileJoystick:

    def __init__(self,
                 center: tuple,
                 big_circle_radius: int,
                 small_circle_radius: int,
                 display,
                 side: str = "Right"):
        self.base_center = center
        self.center_x, self.center_y = center
        self.joy_pos_x, self.joy_pos_y = center
        self.big_radius = big_circle_radius
        self.small_radius = small_circle_radius
        self.screen = display
        self.mouse_down = False
        self.side = side
        self.rotation = 0

    def update(self) -> tuple:
        """Update joystick position and return (dx, dy), rotation, normalized (dx, dy)."""
        mouse_pos = pygame.mouse.get_pos()
        dx, dy = 0, 0

        # Check for events
        for event in pygame.event.get():
            if event.type in {pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN}:
                # Only allow touches/clicks on the right half
                if mouse_pos[0] > self.screen.get_width() / 2:
                    self.mouse_down = True
                    self.center_x, self.center_y = mouse_pos
            elif event.type in {pygame.MOUSEBUTTONUP, pygame.FINGERUP}:
                self.mouse_down = False

        # Update joystick position
        if self.mouse_down:
            dx = mouse_pos[0] - self.center_x
            dy = mouse_pos[1] - self.center_y
            dist = hypot(dx, dy)
            # Clamp to big circle
            factor = min(1, self.big_radius / dist) if dist != 0 else 1
            self.joy_pos_x = self.center_x + dx * factor
            self.joy_pos_y = self.center_y + dy * factor
        else:
            self.joy_pos_x, self.joy_pos_y = self.base_center

        # Calculate rotation
        dx_rel = self.joy_pos_x - self.center_x
        dy_rel = self.joy_pos_y - self.center_y
        if self.mouse_down:
            self.rotation = degrees(atan2(-dx_rel, -dy_rel))

        # Normalized joystick vector
        norm_dx = dx_rel / self.big_radius
        norm_dy = dy_rel / self.big_radius

        return ((0, 0) if not self.mouse_down else
                (dx_rel, dy_rel)), self.rotation, (norm_dx, norm_dy)

    def draw(self):
        if self.mouse_down:
            # Draw active joystick
            pygame.draw.circle(self.screen, "black",
                               (self.center_x, self.center_y), self.big_radius,
                               2)
            pygame.draw.circle(self.screen, "lightgray",
                               (int(self.joy_pos_x), int(self.joy_pos_y)),
                               self.small_radius)
        else:
            # Draw default joystick on base
            pygame.draw.circle(self.screen, "black", self.base_center,
                               self.big_radius, 2)
            pygame.draw.circle(self.screen, "lightgray", self.base_center,
                               self.small_radius)

