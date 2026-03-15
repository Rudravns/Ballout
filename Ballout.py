"""
This is the File for the game BAllOUT

To run call Ballout().main_menu() and ENJOY

"""

#Module Import
import pygame, os, math
from ballout_entities import *
from ballout_classes import *
#from Ballout_multiplayer.py import *
from math import *


class Ballout:

    def __init__(self, fps: int = 60, screen_size: tuple = (int, int)):
        pygame.init()
        # Base design resolution
        self.base_resolution = (1536, 864)
        # Actual screen size
        new = None
        #new = (600, 300)
        self.screen_size = get_screen(override=screen_size)
        self.screen = pygame.display.set_mode(self.screen_size)
        self.goal_height = 300
        self.tick = abs(fps)
        self.clock = pygame.time.Clock()
        self.txt = fonts(screen=self.screen)
        self.current_msg: list = []
        self.msg_queue: list = []
        # Load or initialize save data
        self.saved_data = self.data_handler()

        self.game_dur = 90
        w, h = self.base_resolution
        self.debug = self.saved_data['debug']
        self.mobile = self.saved_data['mobile']
        self.learn = self.saved_data['learn']
        self.player_mass = self.saved_data['player_mass']
        self.ball_mass = self.saved_data['ball_mass']
        self.ball_amt = 1
        self.single_for_single_player = self.saved_data['Single(SINGLEPLAYER)']


        # Boundaries

        self.boundries = [
            pygame.Rect(0, 0, w, 10),  # top
            pygame.Rect(0, h + 189, w, 10),  # bottom
            pygame.Rect(0, 0, 10, h + 30),  # left
            pygame.Rect(w - 10, 0, 10, h + 30)  # right
        ]
        # Player skins (scaled)
        skin_size = self.scale_size(50)
        self.player_skins = [
            Animation("ballout_assets/player_black.png", [(0, 0, 32, 32),
                                                          (0, 32, 32, 32),
                                                          (0, 64, 32, 32),
                                                          (0, 96, 32, 32)],
                      (skin_size, skin_size)),
            Animation("ballout_assets/player_eye.png", [(0, 0, 32, 32),
                                                        (0, 32, 32, 32),
                                                        (0, 64, 32, 32),
                                                        (0, 96, 32, 32)],
                      (skin_size, skin_size)),
            Animation("ballout_assets/player_cherry_blossom.png",
                      [(0, 0, 32, 32),
                       (0, 32, 32, 32)], (skin_size, skin_size)),

            Animation("ballout_assets/player_angry.png", [(0, 0, 64, 64),
                                                        (0, 64, 64, 64),
                                                        (0, 128,64,64),
                                                        (0, 192, 64, 64)],
                      (skin_size, skin_size)),

            Animation("ballout_assets/player_emerald.png", [(0, 0, 64, 64),
                                                        (0, 64, 64, 64),
                                                        (0, 128,64,64),
                                                        (0, 192, 64, 64)],
                      (skin_size, skin_size))
            
            
        ]
        self.player_skin = [
            self.saved_data["player1"], self.saved_data["player2"],
            self.saved_data["Bot_skin"], self.saved_data["LAN skin"],
            self.saved_data["Bot_skin2"]
        ]

        self.level = self.saved_data["bot_level"]  # base level
        self.level2 = self.saved_data["bot_level2"] #second bot level
        # Game timers
        self.game_duration = timer(self.screen, 1000, "up")
        self.goal_timer = timer(self.screen, 1000, "down", 5)

        # Goal triggers
        self.goal_trig = [
            pygame.Rect(w - 10, h / 3 - 30, 10, h),
            pygame.Rect(0, h / 3 - 30, 10, h)
        ]

        # Field background
        self.fields = [
            ImageManager(
                pygame.image.load(
                    "ballout_assets/field_1.png").convert_alpha(),
                self.screen_size),
            ImageManager(
                pygame.image.load(
                    "ballout_assets/Field_2.png").convert_alpha(),
                self.screen_size)
        ]
        self.field = 0

        self.joystick = MobileJoystick(self.scale_pos((w - 300, h - 150)),
                                       self.scale_size(80),
                                       self.scale_size(40), self.screen)
        self.MouseDown = False

        return None

    def data_handler(self, Save: bool = False):

        if Save:
            save({
                "player1": self.player_skin[0],
                "player2": self.player_skin[1],
                "Bot_skin": self.player_skin[2],
                "LAN skin": self.player_skin[3],
                "Bot_skin2": self.player_skin[4],
                "learn": self.learn,
                "debug": self.debug,
                "mobile": self.mobile,
                "bot_level": self.level,
                "bot_level2": self.level2,
                "player_mass": self.player_mass,
                "ball_mass": self.ball_mass,
                "Single(SINGLEPLAYER)": self.single_for_single_player,
            })
            return 0

        saving_data = load()

        saving_data_correct = {
            "player1": 2,
            "player2": 1,
            "Bot_skin": 3,
            "LAN skin": 4,
            "Bot_skin2": 0,
            "learn": False,
            "debug": False,
            "mobile": False,
            "bot_level": 3,
            "bot_level2": 3,
            "player_mass": 10,
            "ball_mass": 0.01,
            "Single(SINGLEPLAYER)": True,
        }

        saved_file = list(map(lambda x: x, saving_data))

        correct = list(map(lambda x: x, saving_data_correct))

        result_list = [item for item in correct if item not in saved_file]

        saving_data.update(
            {item: saving_data_correct[item]
             for item in result_list})

        save(saving_data)
        return saving_data

    # ------------------- SCALING HELPERS -------------------
    def scale_size(self, size: float, round_result=True):
        win = get_screen()
        scale_factor = min(win[0] / self.base_resolution[0],
                           win[1] / self.base_resolution[1])
        return round(size *
                     scale_factor) if round_result else size * scale_factor

    def scale_pos(self, pos: tuple, round_result=False):
        win = get_screen()
        scale_factor = min(win[0] / self.base_resolution[0],
                           win[1] / self.base_resolution[1])
        x = pos[0] * scale_factor
        y = pos[1] * scale_factor
        return (round(x), round(y)) if round_result else (x, y)

    def scale_rect(self, rect):
        """Scale a pygame.Rect from base resolution to current screen size"""

        scaled_pos = self.scale_pos((rect.x, rect.y))
        self.screen_size = get_screen()
        scaled_size = (self.scale_size(rect.width, False),
                       self.scale_size(rect.height, False))
        return pygame.Rect(scaled_pos[0], scaled_pos[1], scaled_size[0],
                           scaled_size[1])

    def get_scaled_boundaries(self):
        """Return scaled boundary rects with a goal hole on left/right sides"""
        w, h = get_screen()

        wall_thickness = self.scale_size(10)
        goal_height = self.scale_size(self.goal_height)  # height of the goal
        goal_y = (h - goal_height) // 2  # vertical start of goal

        # Horizontal boundaries
        top = pygame.Rect(0, 0, w, wall_thickness)
        bottom = pygame.Rect(0, h - wall_thickness, w, wall_thickness)

        # Vertical boundaries split around the goal
        left_top = pygame.Rect(0, 0, wall_thickness, goal_y)
        left_bottom = pygame.Rect(0, goal_y + goal_height, wall_thickness,
                                  h - (goal_y + goal_height))
        right_top = pygame.Rect(w - wall_thickness, 0, wall_thickness, goal_y)
        right_bottom = pygame.Rect(w - wall_thickness, goal_y + goal_height,
                                   wall_thickness, h - (goal_y + goal_height))

        return [top, bottom, left_top, left_bottom, right_top, right_bottom]

    def get_scaled_goal_triggers(self):
        """Return scaled goal trigger rects (left and right)"""
        w, h = get_screen()
        goal_width = self.scale_size(10)  # width of the goal
        goal_height = self.scale_size(self.goal_height)  # height of the goal
        goal_y = (h - goal_height) // 2

        left_goal = pygame.Rect(0, goal_y, goal_width, goal_height)
        right_goal = pygame.Rect(w - goal_width, goal_y, goal_width,
                                 goal_height)

        return left_goal, right_goal

    def generate_message(self,
                     text: str = None,
                     text_duration: float = 20.0,
                     size: int = 60):

        # Queue new message if provided
        if text:
            self.msg_queue.append((text, text_duration))

        # Start next message if none is active
        if not self.current_msg and self.msg_queue:
            msg_text, duration = self.msg_queue.pop(0)
            self.current_msg = [msg_text, duration, 0, self.scale_size(0)]  # [text, remaining_time, y_pos, ???]

        # If there’s no current message, exit
        if not self.current_msg:
            return

        # Unpack
        msg_text, remaining_time, y_pos, _ = self.current_msg
        target_y = self.scale_size(50)

        # Move down until target
        if y_pos < target_y:
            y_pos += 100 * self.dt

        # Decrease timer
        remaining_time -= self.dt
        if remaining_time <= 0:
            # Message done
            self.current_msg = None
            return

        # Alpha proportional to remaining time (fade out during last 0.5 seconds)
        fade_time = 0.5  # seconds to fade
        if remaining_time < fade_time:
            alpha = int(255 * (remaining_time / fade_time))
        else:
            alpha = 255

        alpha = max(0, min(255, alpha))

        # Draw message
        font = pygame.font.Font(None, self.scale_size(size))
        text_surf = font.render(msg_text, True, (255, 255, 255))
        text_surf.set_alpha(alpha)
        text_rect = text_surf.get_rect(center=(self.screen_size[0] // 2, int(y_pos)))
        self.screen.blit(text_surf, text_rect)

        # Update current message state
        self.current_msg[1] = remaining_time
        self.current_msg[2] = y_pos

    # ------------------- MAIN MENU -------------------
    def main_menu(self):
        w, h = self.base_resolution
        buttons_group = pygame.sprite.Group()
        Local = buttons(
            self.scale_pos((w // 2 + 20, h // 2 - 50), True)[0],
            self.scale_pos((w // 2 + 20, h // 2 - 50), True)[1], "",
            self.scale_size(50), "CO-OP", "#ad8fff", "black", "Black")
        Single = buttons(
            self.scale_pos((w // 2 + 20, h // 2 + 50), True)[0],
            self.scale_pos((w // 2 + 20, h // 2 + 50), True)[1], "",
            self.scale_size(50), "Singleplayer", "#ff6b6b", "black", "Black")

        LAN = buttons(
            self.scale_pos((w // 2 + 20, h // 2 + 150), True)[0],
            self.scale_pos((w // 2 + 20, h // 2 + 150), True)[1], "",
            self.scale_size(50), "LAN Multiplayer", "#4e4e4e", "white",
            "Black")

        setting = buttons(
            self.scale_pos((w // 2 + 20, h // 2 + 250), True)[0],
            self.scale_pos((w // 2 + 20, h // 2 + 250), True)[1], "",
            self.scale_size(50), "Settings", "#9e9e9e", "white", "Black")
        back_button = buttons(
            self.scale_pos((150, h // 2 + 370), True)[0],
            self.scale_pos((150, h // 2 + 370), True)[1], "",
            self.scale_size(50), "Exit Game", "#00a895", "red", "Black")
        buttons_group.add(Local)
        buttons_group.add(Single)
        buttons_group.add(LAN)
        buttons_group.add(setting)
        buttons_group.add(back_button)

        time.sleep(0.1)
        logo = ImageManager(
            pygame.image.load(
                "ballout_assets/Ballout_logo.png").convert_alpha(),
            (self.scale_size(600), self.scale_size(150)))

        # Use pygame's time functions for a reliable delay
        click_delay = 500  # milliseconds
        last_click_time = -click_delay  # Allow immediate click on first launch

        while True:
            self.clock.tick(self.tick)
            self.screen.fill("black")
            self.fields[self.field].setting(self.screen,
                                            self.scale_pos((10, 10)))
            logo.setting(self.screen, self.scale_pos((w // 2 + 20 - 300, 100)))

            for button in buttons_group:
                button.update(pygame.mouse.get_pos())
                button.draw(self.screen)

            # Draw boundaries & goal triggers (scaled)
            scaled_goals = self.get_scaled_goal_triggers()
            scaled_bounds = self.get_scaled_boundaries()
            pygame.draw.rect(self.screen, "Orange", scaled_goals[0])
            pygame.draw.rect(self.screen, "Blue", scaled_goals[1])
            for boundry in scaled_bounds:
                pygame.draw.rect(self.screen, "black", boundry)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN
                                                 and event.key
                                                 == pygame.K_ESCAPE):
                    self.data_handler(Save=True)
                    pygame.quit()
                    sys.exit()
                    return 0
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    current_time = pygame.time.get_ticks()
                    if current_time - last_click_time < click_delay:
                        continue  # Ignore click if it's too soon

                    elif Local.get_rect().collidepoint(pygame.mouse.get_pos()):
                        self.CO_OP_menu()
                        # After returning, clear events and reset the timer to prevent click-through
                        pygame.event.clear(pygame.MOUSEBUTTONDOWN)
                        last_click_time = pygame.time.get_ticks()
                    elif Single.get_rect().collidepoint(
                            pygame.mouse.get_pos()):
                        self.single_player_menu()
                        # After returning, clear events and reset the timer
                        pygame.event.clear(pygame.MOUSEBUTTONDOWN)
                        last_click_time = pygame.time.get_ticks()
                    elif LAN.get_rect().collidepoint(pygame.mouse.get_pos()):
                        self.LAN_menu()

                    elif setting.get_rect().collidepoint(
                            pygame.mouse.get_pos()):
                        self.settings()
                        continue
                    elif back_button.get_rect().collidepoint(
                            pygame.mouse.get_pos()):
                        self.data_handler(Save=True)
                        pygame.quit()
                        sys.exit()

                    last_click_time = current_time
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.MouseDown = False

            pygame.display.flip()

    # ------------------settings-------------
    def settings(self):
        w, h = self.base_resolution
        buttons_group = pygame.sprite.Group()
        back_button = buttons(
            self.scale_pos((w // 2 + 20, h // 2 + 300), True)[0],
            self.scale_pos((w // 2 + 20, h // 2 + 300), True)[1], "",
            self.scale_size(50), "BACK", "#00a895", "red", "Black")
        debug = buttons(
            self.scale_pos((w // 2 + 20, h // 2 - 50), True)[0],
            self.scale_pos((w // 2 + 20, h // 2 - 50), True)[1], "",
            self.scale_size(50), f"Debug: {self.debug}", "dark blue",
            "#008dff", "Black")
        bot_learn = buttons(
            self.scale_pos((w // 2 + 20, h // 2 + 50), True)[0],
            self.scale_pos((w // 2 + 20, h // 2 + 50), True)[1], "",
            self.scale_size(50), f"Bot Learning: {self.learn}", "dark red",
            "red", "Black")
        mobile = buttons(
            self.scale_pos((w // 2 + 20, h // 2 + 150), True)[0],
            self.scale_pos((w // 2 + 20, h // 2 + 150), True)[1], "",
            self.scale_size(50),
            f"Mobile Joystick(only single_player mode): {self.mobile}",
            "orange", "yellow", "Black")
        buttons_group.add(bot_learn)
        buttons_group.add(back_button)
        buttons_group.add(debug)
        buttons_group.add(mobile)

        while True:
            self.clock.tick(self.tick)
            self.screen.fill("black")
            self.fields[self.field].setting(self.screen,
                                            self.scale_pos((10, 10)))
            self.txt.draw(
                self.scale_pos(((w // 2 - 125, h // 2 - 270), True)[0],
                               self.scale_pos((w // 2 + 20, h // 2 - 100),
                                              True)[1]), "Settings",
                self.scale_size(100), "#6ebeff", True)

            for button in buttons_group:
                button.update(pygame.mouse.get_pos())
                button.draw(self.screen)

            # Draw boundaries & goal triggers (scaled)
            scaled_goals = self.get_scaled_goal_triggers()
            scaled_bounds = self.get_scaled_boundaries()
            pygame.draw.rect(self.screen, "Orange", scaled_goals[0])
            pygame.draw.rect(self.screen, "Blue", scaled_goals[1])
            for boundry in scaled_bounds:
                pygame.draw.rect(self.screen, "black", boundry)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN
                                                 and event.key
                                                 == pygame.K_ESCAPE):
                    return 0
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.get_rect().collidepoint(
                            pygame.mouse.get_pos()):
                        return 0
                    if debug.get_rect().collidepoint(pygame.mouse.get_pos()):
                        self.debug = not self.debug
                        debug.change_style(f"Debug: {self.debug}", "dark blue",
                                           "#008dff")
                    if bot_learn.get_rect().collidepoint(
                            pygame.mouse.get_pos()):
                        self.learn = not self.learn
                        bot_learn.change_style(f"Bot Learning: {self.learn}",
                                               "dark red", "red")
                    if mobile.get_rect().collidepoint(pygame.mouse.get_pos()):
                        self.mobile = not self.mobile
                        mobile.change_style(
                            f"Mobile Joystick(only single_player mode): {self.mobile}",
                            "orange", "yellow")

            pygame.display.flip()

    #--------------------Pause game_---------------

    def pause(self) -> bool:
        w, h = self.base_resolution
        buttons_group = pygame.sprite.Group()
        Resume = buttons(
            self.scale_pos((w // 2 + 20, h // 2 - 50), True)[0],
            self.scale_pos((w // 2 + 20, h // 2 - 50), True)[1], "",
            self.scale_size(50), "Resume", "#00a895", "#f0ad8f", "Black")

        exit = buttons(
            self.scale_pos((w // 2 + 20, h // 2 + 50), True)[0],
            self.scale_pos((w // 2 + 20, h // 2 + 50), True)[1], "",
            self.scale_size(50), "Exit", "Dark red", "red", "Black")

        buttons_group.add(Resume)
        buttons_group.add(exit)
        scaled_bounds = self.get_scaled_boundaries()
        scaled_goals = self.get_scaled_goal_triggers()

        while True:
            self.clock.tick(self.tick)
            self.screen.fill("black")
            self.fields[self.field].setting(self.screen, (10, 10))

            for button in buttons_group:
                button.update(pygame.mouse.get_pos())
                button.draw(self.screen)

            self.txt.draw(
                self.scale_pos(((w // 2 - 200, h // 2 - 270), True)[0],
                               self.scale_pos((w // 2 + 20, h // 2 - 100),
                                              True)[1]), "Game Paused",
                self.scale_size(100), "#6ebeff", True)
            scaled_bounds_with_holes = self.get_scaled_boundaries()
            if self.debug:
                pygame.draw.rect(self.screen, "Blue",
                                 self.get_scaled_goal_triggers()[0])
                pygame.draw.rect(self.screen, "Orange",
                                 self.get_scaled_goal_triggers()[1])
            else:
                pygame.draw.rect(self.screen, "Blue",
                                 self.get_scaled_goal_triggers()[0])
                pygame.draw.rect(self.screen, "Orange",
                                 self.get_scaled_goal_triggers()[1])

            for boundry in scaled_bounds_with_holes:
                pygame.draw.rect(self.screen, "black", boundry)
            for event in pygame.event.get():

                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN
                                                 and event.key
                                                 == pygame.K_ESCAPE):
                    return False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.MouseDown == True
                    if Resume.get_rect().collidepoint(pygame.mouse.get_pos()):
                        return False
                    if exit.get_rect().collidepoint(pygame.mouse.get_pos()):
                        return True
            pygame.display.flip()

    # ------------------- SINGLE PLAYER MENU -------------------
    def single_player_menu(self):
        w, h = self.base_resolution
        buttons_group = pygame.sprite.Group()

        # --- BUTTON COLORS ---
        button_bg = "#ff4c42"        
        button_text = "white"
        button_edge = "black"

        # --- PLAYER BUTTONS ---
        player1_ready_button = buttons(
            *self.scale_pos((300, 400), True),
            None,
            self.scale_size(50),
            "Not Ready",
            button_bg,
            button_text,
            button_edge
        )

        player1_r_change = buttons(
            *self.scale_pos((400, 300), True),
            None,
            self.scale_size(50),
            ">",
            button_bg,
            button_text,
            button_edge
        )

        player1_l_change = buttons(
            *self.scale_pos((200, 300), True),
            None,
            self.scale_size(50),
            "<",
            button_bg,
            button_text,
            button_edge
        )

        buttons_group.add(player1_ready_button, player1_r_change, player1_l_change)
        
        # --- PLAYER1 BUTTONS ---
        player2_ready_button = buttons(
            *self.scale_pos((300, 700), True),
            None,
            self.scale_size(50),
            "Not Ready",
            button_bg,
            button_text,
            button_edge
        )

        player2_r_change = buttons(
            *self.scale_pos((400, 600), True),
            None,
            self.scale_size(50),
            ">",
            button_bg,
            button_text,
            button_edge
        )

        player2_l_change = buttons(
            *self.scale_pos((200, 600), True),
            None,
            self.scale_size(50),
            "<",
            button_bg,
            button_text,
            button_edge
        )

        buttons_group.add(player2_ready_button, player2_r_change, player2_l_change)
        
        ready = (False, False) #player1, player 2

        # --- BOT LEVEL BUTTONS ---
        bot_level = buttons(
            *self.scale_pos((1200, 400), True),
            None,
            self.scale_size(50),
            f"Bot level: {self.level}",
            "#229c06",  # Green for bot level
            button_text,
            button_edge
        )

        bot_level_r_change = buttons(
            *self.scale_pos((1300, 300), True),
            None,
            self.scale_size(50),
            ">",
            button_bg,
            button_text,
            button_edge
        )

        bot_level_l_change = buttons(
            *self.scale_pos((1100, 300), True),
            None,
            self.scale_size(50),
            "<",
            button_bg,
            button_text,
            button_edge
        )

        buttons_group.add(bot_level, bot_level_r_change, bot_level_l_change)

        bot_level2 = buttons(
            *self.scale_pos((1200, 700), True),
            None,
            self.scale_size(50),
            f"Bot level: {self.level2}",
            "#229c06",  # Green for bot level
            button_text,
            button_edge
        )

        bot_level_r_change2 = buttons(
            *self.scale_pos((1300, 600), True),
            None,
            self.scale_size(50),
            ">",
            button_bg,
            button_text,
            button_edge
        )

        bot_level_l_change2 = buttons(
            *self.scale_pos((1100, 600), True),
            None,
            self.scale_size(50),
            "<",
            button_bg,
            button_text,
            button_edge
        )

        buttons_group.add(bot_level2, bot_level_r_change2, bot_level_l_change2)

        # Bot skin clickable area
        bot_img_change = pygame.Rect(*self.scale_pos((1150, 250)),
                                    *self.scale_pos((100, 100)))
        bot2_img_change = pygame.Rect(*self.scale_pos((1150, 550)),
                                    *self.scale_pos((100, 100)))
        singles_to_doubles_singleplayer = buttons(
            *self.scale_pos((w/2+20, 780), True),
            None,
            self.scale_size(50),
            f"Mode: {"Doubles" if not self.single_for_single_player else "Singles"}",
            "#b0a207",
            button_text,
            button_edge
        )
        buttons_group.add(singles_to_doubles_singleplayer)


        while True:
            self.dt = self.clock.tick(self.tick)/100
            self.screen.fill("black")

            # --- BACKGROUND ---
            self.fields[self.field].setting(self.screen, self.scale_pos((10, 10)))
            self.txt.draw(self.scale_pos((420, 110)), "SINGLEPLAYER MODE",
                        100, "black", Italic=True)

            # --- BUTTONS ---
            for button in buttons_group:
                button.update(pygame.mouse.get_pos())
                button.draw(self.screen)

            # --- SCALED GOALS & BOUNDARIES ---
            scaled_goals = self.get_scaled_goal_triggers()
            scaled_bounds = self.get_scaled_boundaries()
            pygame.draw.rect(self.screen, "orange", scaled_goals[0])
            pygame.draw.rect(self.screen, "blue", scaled_goals[1])
            for boundry in scaled_bounds:
                pygame.draw.rect(self.screen, "black", boundry)

            # --- PLAYER SKINS ---
            self.screen.blit(
                self.player_skins[self.player_skin[0]].img_now(
                    0, (self.scale_size(100), self.scale_size(100))),
                self.scale_pos((250, 250))
            )
            self.screen.blit(
                self.player_skins[self.player_skin[1]].img_now(
                    0, (self.scale_size(100), self.scale_size(100))),
                self.scale_pos((250, 550))
            )

            bot_skin_index = self.player_skin[2]
            self.screen.blit(
                self.player_skins[bot_skin_index].img_now(
                    0, (self.scale_size(100), self.scale_size(100))),
                self.scale_pos((1150, 250))
            )
            bot_skin_index = self.player_skin[4]
            self.screen.blit(
                self.player_skins[bot_skin_index].img_now(
                    0, (self.scale_size(100), self.scale_size(100))),
                self.scale_pos((1150, 550))
            )


            #---- Game Start -----
            if self.single_for_single_player and (ready[0] == True):
                enities = [
                    Player(self.scale_pos((w / 4, h / 2)), self.screen,
                        scaled_bounds, self.player_skins[self.player_skin[0]],
                        "First", self.player_mass),

                    bot(self.scale_pos((w * 3 / 4, h / 2)), self.screen,
                        scaled_bounds, self.player_skins[self.player_skin[2]],
                        1, scaled_goals, 0, difficulty=self.level,
                        ),
                    ]
                self.single_player(enities)
                return 0

            elif ready == (True, True):
                enities = [
                    Player(self.scale_pos((w / 4,  (h / 3.5))), self.screen,
                        scaled_bounds, self.player_skins[self.player_skin[0]],
                        "First", self.player_mass),

                    Player(self.scale_pos((w / 4, (h/5.5)+(h / 2))), self.screen,
                        scaled_bounds, self.player_skins[self.player_skin[1]],
                        "Second", self.player_mass),

                    bot(self.scale_pos((w * 3 / 4, h / 3.5)), self.screen,
                        scaled_bounds, self.player_skins[self.player_skin[2]],
                        1, scaled_goals, 0, difficulty=self.level,
                        ),

                    bot(self.scale_pos((w * 3 / 4,  (h/5.5)+(h / 2))), self.screen,
                        scaled_bounds, self.player_skins[self.player_skin[4]],
                        1, scaled_goals, 0, difficulty=self.level,
                        ),
                    ]
                self.single_player(enities)
                return 0

            #show msg if there are 
            self.generate_message()
            # --- EVENTS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN
                                                and event.key == pygame.K_ESCAPE):
                    return 0
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    # Mode change
                    if singles_to_doubles_singleplayer.get_rect().collidepoint(pos):
                        self.single_for_single_player = not self.single_for_single_player
                        singles_to_doubles_singleplayer.change_style(f"Mode: {'Doubles' if not self.single_for_single_player else 'Singles'}",
                        "#b0a207", button_text)
                        self.generate_message("Mode changed", 20)



                    # Change bot skin
                    if bot_img_change.collidepoint(pos):
                        self.player_skin[2] = (self.player_skin[2] + 1) % len(self.player_skins)
                    if bot2_img_change.collidepoint(pos):
                        self.player_skin[4] = (self.player_skin[4] + 1) % len(self.player_skins)


                    # Start game
                    if player1_ready_button.get_rect().collidepoint(pos):
                        ready = (True, ready[1]) 
                        player1_ready_button.change_style("Ready", "#00a895", button_text)
                    if player2_ready_button.get_rect().collidepoint(pos):
                        ready = (ready[0], True)
                        player2_ready_button.change_style("Ready", "#00a895", button_text)
                        if self.single_for_single_player:
                            self.generate_message("Turn on Doubles for this player to join", 20)
                    if bot_level.get_rect().collidepoint(pos):
                        self.generate_message("This bot is ready to Join", 20)
                    if bot_level2.get_rect().collidepoint(pos):
                        if not self.single_for_single_player:
                            self.generate_message("This bot is ready to Join", 20)
                        else:
                            self.generate_message("Turn on Doubles for this bot to join", 20)


                    # Change player skin
                    if player1_r_change.get_rect().collidepoint(pos):
                        self.player_skin[0] = (self.player_skin[0] + 1) % len(self.player_skins)
                    if player1_l_change.get_rect().collidepoint(pos):
                        self.player_skin[0] = (self.player_skin[0] - 1) % len(self.player_skins)
                    if player2_r_change.get_rect().collidepoint(pos):
                        self.player_skin[1] = (self.player_skin[1] + 1) % len(self.player_skins)
                    if player2_l_change.get_rect().collidepoint(pos):
                        self.player_skin[1] = (self.player_skin[1] - 1) % len(self.player_skins)

                    # Change bot level
                    if bot_level_r_change.get_rect().collidepoint(pos) and self.level < 30:
                        self.level += 1
                        bot_level.change_style(f"Bot level: {self.level}", "#229c06", button_text)
                    if bot_level_l_change.get_rect().collidepoint(pos) and self.level > 1:
                        self.level -= 1
                        bot_level.change_style(f"Bot level: {self.level}", "#229c06", button_text)
                    if bot_level_r_change2.get_rect().collidepoint(pos) and self.level2 < 30:
                        self.level2 += 1
                        bot_level2.change_style(f"Bot level: {self.level2}", "#229c06", button_text)
                    if bot_level_l_change2.get_rect().collidepoint(pos) and self.level2 > 1:
                        self.level2 -= 1
                        bot_level2.change_style(f"Bot level: {self.level2}", "#229c06", button_text)
                    

            #--------- BOT SKIN DEBUG ------
            if self.debug:
                pygame.draw.rect(self.screen, "blue", bot_img_change, 4)
                pygame.draw.rect(self.screen, "blue", bot2_img_change, 4)
                

            # -------single player restrictions-------------
            if self.single_for_single_player:
                ready = (ready[0], False)
                player2_ready_button.change_style("Singles | can not join", "#ff4c42", button_text)
                bot_level2.change_style(f"Singles | can not join", "#ff4c42", button_text)
            else:
                player2_ready_button.change_style("Not Ready", "#ff4c42", button_text) if not ready[1] else player2_ready_button.change_style("Ready", "#00a895", button_text)
                bot_level2.change_style(f"Bot level: {self.level2}", "#229c06", button_text)

            
            

            pygame.display.flip()

    # ------------------- SINGLE PLAYER GAME -------------------
    def single_player(self, entites:list = [Player | bot, bot | Player]):
        w, h = self.base_resolution
        # Players with scaled positions
        scaled_bounds = self.get_scaled_boundaries()
        scaled_goals = self.get_scaled_goal_triggers()

        # Player 1 (Human) on left, Bot on right
        players = entites
        
        player_start_positions = [p.pos.copy() for p in players]

        # Balls with scaled positions
        diameter = self.scale_size(25)*2
        balls = []
        top_y = h / 4
        bottom_y = 3 * h / 4

        for i in range(self.ball_amt):
            x = w / 2
            
            if self.ball_amt == 1:
                # If only one ball, put it in the middle
                y = h / 2
            else:
                # Evenly space multiple balls from top_y to bottom_y
                y = top_y + i * (bottom_y - top_y) / (self.ball_amt - 1)

            balls.append(
                Ball(
                    self.scale_pos((x, y)),
                    self.scale_size(25),
                    self.screen,
                    Animation(
                        "ballout_assets/Ball1.png",
                        [(0, 0, 32, 32)],
                        (self.scale_size(50), self.scale_size(50))
                    ),
                    scaled_bounds,
                    self.ball_mass,
                    players,
                    scaled_goals
                )
            )

        ball_start_positions = [(b.x, b.y) for b in balls]
        goal_speed = 0
        # Player hitboxes and bot ball tracking
        for i, player in enumerate(players):
            other_players = players.copy()
            other_players.pop(i)
            player.add_hbox(other_players)
            if str(player) == "BOT":
                player.add_ball(balls)
        # Balls for collisions
        for ball in balls:
            for other_ball in balls:
                ball.add_ball(other_ball)

        # Game state
        state = "playing"

        player_1_goals = 0
        player_2_goals = 0

        # Reset timers
        self.goal_timer.reset()
        self.game_duration.reset(1000, "up")

        while True:
            dt = self.clock.tick(self.tick) / 100
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN
                                                 and event.key
                                                 == pygame.K_ESCAPE):
                    res = self.pause()
                    if res: return 0
            keys = pygame.key.get_pressed()
            self.screen.fill("white") if self.debug else self.screen.fill(
                "black")
            self.fields[self.field].setting(self.screen,
                                            self.scale_pos((10, 10)))

            # Draw boundaries and goals
            scaled_bounds_with_holes = self.get_scaled_boundaries()
            if self.debug:
                pygame.draw.rect(self.screen, "Blue",
                                 self.get_scaled_goal_triggers()[0])
                pygame.draw.rect(self.screen, "Orange",
                                 self.get_scaled_goal_triggers()[1])
            else:
                pygame.draw.rect(self.screen, "Blue",
                                 self.get_scaled_goal_triggers()[0])
                pygame.draw.rect(self.screen, "Orange",
                                 self.get_scaled_goal_triggers()[1])

            for boundry in scaled_bounds_with_holes:
                pygame.draw.rect(self.screen, "black", boundry)
            # Display FPS and scores
            if self.debug:
                self.txt.draw(self.scale_pos((10, h - 100)),
                              f"FPS: {round(self.clock.get_fps())}",
                              size=self.scale_size(50),
                              color="black")

            self.txt.draw(self.scale_pos((10, 10)),
                          f"Player 1: {player_1_goals}",
                          size=self.scale_size(40),
                          color="black",
                          Italic=True,
                          Bold=True)
            self.txt.draw(self.scale_pos((w - 200, 10)),
                          f"Bot: {player_2_goals}",
                          size=self.scale_size(40),
                          color="black",
                          Italic=True,
                          Bold=True)
            output = self.joystick.update() if self.mobile else None

            self.generate_message()
            # Timer
            if state == "playing":
                self.game_duration.step()
                time_text = f"Time passed: {int(self.game_duration)}"
                self.txt.draw(self.scale_pos((w // 2, int(h * 0.05))),
                              time_text,
                              size=self.scale_size(36),
                              color="black",
                              center=True)

                # Update players

                for player in players:
                    player.update(keys, dt, output) if str(
                        player) != "BOT" else player.update(keys, dt)
                    player.draw(self.debug)

                # Update balls
                scored = False
                for ball in balls:
                    goal_scored = ball.update(dt)
                    ball.draw(self.debug)
                    if goal_scored:
                        if goal_scored == 1: player_1_goals += 1
                        elif goal_scored == 2: player_2_goals += 1
                        goal_speed = round((math.hypot(ball.vx, ball.vy))/2,2)
                        scored = True
                        break

                if scored:
                    state = "goal_pause"
                    self.goal_timer.reset(1000, "down", 5)

            elif state == "goal_pause":
                # Reset positions
                
                for bi, ball in enumerate(balls):
                    start_x, start_y = ball_start_positions[bi]
                    ball.x, ball.y = start_x, start_y
                    ball.vx = ball.vy = ball.ax = ball.ay = 0
                    ball.hit_box, ball.goal_hitbox = ball.update_hbox()

                for pi, player in enumerate(players):
                    player.pos = player_start_positions[pi].copy()
                    player.velocity = pygame.Vector2(0, 0)
                    player.hit_box = player.update_hbox()

                # Draw frozen
                for player in players:
                    player.draw(self.debug)
                for ball in balls:
                    ball.update(0)
                    ball.draw(self.debug)
                
                self.txt.draw(self.scale_pos((w // 2-150, h // 2-100)),
                                      f"Goal for {"Left Team" if goal_scored == 1 else "Right Team"}!",
                                      size=self.scale_size(50),
                                      color="black",
                                      Italic=True,
                                      Bold=True)

                if goal_speed > 0:self.txt.draw(self.scale_pos((10, h-50)),f"Goal Speed: {goal_speed}mph", 50, "black", Italic=True, Bold=True)

                restart_text = f"Resuming in: {int(self.goal_timer)}"
                self.txt.draw(self.scale_pos((w // 2, int(h * 0.05))),
                              restart_text,
                              size=self.scale_size(36),
                              color="red",
                              center=True)
                self.goal_timer.step()
                if int(self.goal_timer) <= 0:
                    state = "playing"


            # Game over condition
            if int(self.game_duration) >= self.game_dur:
                winner = "Player 1" if player_1_goals > player_2_goals else "Draw" if player_1_goals == player_2_goals else "Bot"
                self.txt.draw(self.scale_pos((600, 200)),
                              f"{winner} wins!",
                              size=100,
                              color="black",
                              Italic=True,
                              Bold=True)
                self.txt.draw(self.scale_pos((600, 500)),
                              "Click anywhere to exit",
                              size=50,
                              color="black",
                              Italic=True,
                              Bold=True)
                pygame.time.wait(1000)
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.game_duration.reset(1000, "up")
                        self.goal_timer.reset()
                        return 0
            # Quit

            if self.mobile: self.joystick.draw()
            pygame.display.flip()

    # ------------------- CO_OP MULTIPLAYER MENU -------------------
    def CO_OP_menu(self):
        buttons_group = pygame.sprite.Group()
        player1_ready = False
        player1_ready_button = buttons(
            self.scale_pos((300, 600), True)[0],
            self.scale_pos((300, 600), True)[1], "", self.scale_size(50),
            "Not Ready", "Red", "white", "Black")
        player1_r_change = buttons(
            self.scale_pos((400, 400), True)[0],
            self.scale_pos((400, 400), True)[1], "", self.scale_size(50), ">",
            "Black", "white", "Black")
        player1_l_change = buttons(
            self.scale_pos((200, 400), True)[0],
            self.scale_pos((200, 400), True)[1], "", self.scale_size(50), "<",
            "Black", "white", "Black")
        buttons_group.add(player1_ready_button)
        buttons_group.add(player1_r_change)
        buttons_group.add(player1_l_change)

        player2_ready = False
        player2_ready_button = buttons(
            self.scale_pos((1200, 600), True)[0],
            self.scale_pos((1200, 600), True)[1], "", self.scale_size(50),
            "Not Ready", "Red", "white", "Black")
        player2_r_change = buttons(
            self.scale_pos((1300, 400), True)[0],
            self.scale_pos((1300, 400), True)[1], "", self.scale_size(50), ">",
            "Black", "white", "Black")
        player2_l_change = buttons(
            self.scale_pos((1100, 400), True)[0],
            self.scale_pos((1100, 400), True)[1], "", self.scale_size(50), "<",
            "Black", "white", "Black")
        buttons_group.add(player2_ready_button)
        buttons_group.add(player2_r_change)
        buttons_group.add(player2_l_change)

        while True:
            self.clock.tick(self.tick)
            self.screen.fill("black")
            self.fields[self.field].setting(self.screen, (10, 10))
            self.txt.draw(self.scale_pos((570, 110)),
                          "CO-OP MODE",
                          100,
                          "black",
                          Italic=True)
            for button in buttons_group:
                button.update(pygame.mouse.get_pos())
                button.draw(self.screen)

            scaled_bounds_with_holes = self.get_scaled_boundaries()
            if self.debug:
                pygame.draw.rect(self.screen, "Blue",
                                 self.get_scaled_goal_triggers()[0])
                pygame.draw.rect(self.screen, "Orange",
                                 self.get_scaled_goal_triggers()[1])
            else:
                pygame.draw.rect(self.screen, "Blue",
                                 self.get_scaled_goal_triggers()[0])
                pygame.draw.rect(self.screen, "Orange",
                                 self.get_scaled_goal_triggers()[1])

            for boundry in scaled_bounds_with_holes:
                pygame.draw.rect(self.screen, "black", boundry)

            if player1_ready and player2_ready:
                self.CO_OP()
                return 1

            # Draw player skins
            self.screen.blit(
                self.player_skins[self.player_skin[0]].img_now(
                    0, self.scale_pos((100, 100))), self.scale_pos((250, 400)))
            self.screen.blit(
                self.player_skins[self.player_skin[1]].img_now(
                    0, self.scale_pos((100, 100))), self.scale_pos(
                        (1150, 400)))

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN
                                                 and event.key
                                                 == pygame.K_ESCAPE):
                    return 0

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if player1_ready_button.get_rect().collidepoint(
                            pygame.mouse.get_pos()):
                        player1_ready = True
                        player1_ready_button.change_style(
                            "Ready", "Green", "white")

                    if player2_ready_button.get_rect().collidepoint(
                            pygame.mouse.get_pos()):
                        player2_ready = True
                        player2_ready_button.change_style(
                            "Ready", "Green", "white")

                    # Skin change logic
                    if player1_r_change.get_rect().collidepoint(
                            pygame.mouse.get_pos()):
                        self.player_skin[0] = (self.player_skin[0] + 1) % len(
                            self.player_skins)  # Wrap around using modulo

                    if player1_l_change.get_rect().collidepoint(
                            pygame.mouse.get_pos()):
                        self.player_skin[0] = (self.player_skin[0] - 1) % len(
                            self.player_skins)  # Wrap around using modulo

                    if player2_r_change.get_rect().collidepoint(
                            pygame.mouse.get_pos()):
                        self.player_skin[1] = (self.player_skin[1] + 1) % len(
                            self.player_skins)  # Wrap around using modulo

                    if player2_l_change.get_rect().collidepoint(
                            pygame.mouse.get_pos()):
                        self.player_skin[1] = (self.player_skin[1] - 1) % len(
                            self.player_skins)  # Wrap around using modulo

            pygame.display.flip()

    # ------------------- CO_OP MULTIPLAYER-------------------
    def CO_OP(self):
        # === Setup Boundaries & Goals ===
        self.boundries = self.get_scaled_boundaries()
        self.goal_trig = self.get_scaled_goal_triggers()
        goal_speed = 0.0
        # === Setup Players ===
        players = [
            Player((self.screen_size[0] / 4, self.screen_size[1] / 2.5),
                   self.screen, self.boundries,
                   self.player_skins[self.player_skin[0]], "First", 0.233),
            Player((self.screen_size[0] * 3 / 4, self.screen_size[1] / 2.5),
                   self.screen, self.boundries,
                   self.player_skins[self.player_skin[1]], "Second", 1)
        ]

        player_start_positions = [p.pos.copy() for p in players]

        # === Setup Ball ===
        balls = [
            Ball((self.screen_size[0] / 2, self.screen_size[1] / 2), 25,
                 self.screen,
                 Animation("ballout_assets/Ball1.png", [(0, 0, 32, 32)],
                           (50, 50)), self.boundries, 0.002, players,
                 self.goal_trig)
        ]
        ball_start_positions = [(b.x, b.y) for b in balls]

        # Assign collisions between players
        for i, player in enumerate(players):
            others = players.copy()
            others.pop(i)
            player.add_hbox(others)

        # Assign collisions between balls
        for ball in balls:
            for other_ball in balls:
                ball.add_ball(other_ball)

        # === Game Variables ===
        state = "playing"
        player_1_goals = 0
        player_2_goals = 0
        self.goal_timer.reset()

        while True:
            dt = self.clock.tick(self.tick) / 100
            keys = pygame.key.get_pressed()
            self.screen.fill("black")
            self.fields[self.field].setting(self.screen, (10, 10))

            # --- Draw Goals ---
            pygame.draw.rect(self.screen, "Orange", self.goal_trig[0])
            pygame.draw.rect(self.screen, "Blue", self.goal_trig[1])

            # --- Draw Boundaries ---

            if self.debug:
                for bound in self.boundries:
                    pygame.draw.rect(self.screen, "red", bound, 2)
                pygame.draw.rect(self.screen, "green", self.goal_trig[0], 2)
                pygame.draw.rect(self.screen, "blue", self.goal_trig[1], 2)
                self.txt.draw(self.scale_pos((10, self.screen_size[1]-100)),
                              f"FPS: {round(self.clock.get_fps())}",
                              size=self.scale_size(50),
                              color="black")

            screen_w, screen_h = pygame.display.get_window_size()

            # --- Display Scores ---
            self.txt.draw(self.scale_pos((10, 10)),
                          f"Player 1: {player_1_goals}",
                          size=40,
                          color="black",
                          Italic=True,
                          Bold=True)
            self.txt.draw(self.scale_pos((1350, 10)),
                          f"Player 2: {player_2_goals}",
                          size=40,
                          color="black",
                          Italic=True,
                          Bold=True)
            for bound in self.boundries:
                pygame.draw.rect(self.screen, "black", bound)
            # ===== PLAYING STATE =====
            if state == "playing":
                self.game_duration.step()
                if int(self.game_duration) >= self.game_dur:
                    state = "game_over"

                self.txt.draw((screen_w // 2, int(screen_h * 0.05)),
                              f"Time passed: {int(self.game_duration)}",
                              size=self.scale_size(36),
                              color="black",
                              center=True)

                # --- Update Players ---
                for player in players:
                    player.update(keys, dt)
                    player.draw(self.debug)

                # --- Update Balls ---
                scored = False
                for ball in balls:
                    goal_scored = ball.update(dt)
                    ball.draw(self.debug)
                    if goal_scored:
                        if goal_scored == 1: player_1_goals += 1
                        elif goal_scored == 2: player_2_goals += 1
                        scored = True
                        goal_speed = round((math.hypot(ball.vx, ball.vy))/2,2)
                        break

                if scored:
                    state = "goal_pause"
                    self.goal_timer.reset(1000, "down", 5)

            # ===== GOAL PAUSE =====
            elif state == "goal_pause":
                # Reset positions
                for bi, ball in enumerate(balls):
                    start_x, start_y = ball_start_positions[bi]
                    ball.x, ball.y = start_x, start_y
                    ball.vx = ball.vy = ball.ax = ball.ay = 0
                    ball.hit_box, ball.goal_hitbox = ball.update_hbox()

                for pi, player in enumerate(players):
                    player.pos = player_start_positions[pi].copy()
                    player.velocity = pygame.Vector2(0, 0)
                    player.hit_box = player.update_hbox()

                # Draw frozen
                for player in players:
                    player.update(keys, 0)
                    player.draw(self.debug)
                for ball in balls:
                    ball.update(0)
                    ball.draw(self.debug)

                self.txt.draw(self.scale_pos((self.screen_size[0] // 2-150, self.screen_size[1] // 2-100)),
                                      f"Goal for {"Left Team" if goal_scored == 1 else "Right Team"}!",
                                      size=self.scale_size(50),
                                      color="black",
                                      Italic=True,
                                      Bold=True)

                if goal_speed > 0: self.txt.draw(self.scale_pos((10, self.screen_size[1]-50)),f"Goal Speed: {goal_speed}mph", 50, "black", Italic=True, Bold=True)
                self.txt.draw((screen_w // 2, int(screen_h * 0.05)),
                              f"Resuming in: {int(self.goal_timer)}",
                              size=self.scale_size(36),
                              color="red",
                              center=True)
                self.goal_timer.step()
                if int(self.goal_timer) <= 0:
                    state = "playing"

            # ===== GAME OVER =====
            elif state == "game_over":
                for bi, ball in enumerate(balls):
                    start_x, start_y = ball_start_positions[bi]
                    ball.x, ball.y = start_x, start_y
                    ball.vx = ball.vy = ball.ax = ball.ay = 0
                    ball.hit_box, ball.goal_hitbox = ball.update_hbox()

                for pi, player in enumerate(players):
                    player.pos = player_start_positions[pi].copy()
                    player.velocity = pygame.Vector2(0, 0)
                    player.hit_box = player.update_hbox()

                # Draw frozen
                for player in players:
                    player.update(keys, 0)
                    player.draw(self.debug)
                for ball in balls:
                    ball.update(0)
                    ball.draw(self.debug)

                if player_1_goals > player_2_goals: winner = "Player 1"
                elif player_2_goals > player_1_goals: winner = "Player 2"
                else: winner = "Draw"

                self.txt.draw(self.scale_pos((600, 200)),
                              f"{winner} wins!",
                              size=100,
                              color="black",
                              Italic=True,
                              Bold=True)
                self.txt.draw(self.scale_pos((600, 500)),
                              "Click anywhere to exit",
                              size=50,
                              color="black",
                              Italic=True,
                              Bold=True)

                pygame.time.wait(1000)
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        self.game_duration.reset(1000, "up")
                        self.goal_timer.reset()
                        return 0

            # ===== EVENTS =====
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN
                                                 and event.key
                                                 == pygame.K_ESCAPE):
                    res = self.pause()
                    if res: return 0
            pygame.display.flip()

    #--------------------LAN MULTIPLAYER MENU-----------------
    def LAN_menu(self):
        w, h = pygame.display.get_window_size()
        buttons_group = pygame.sprite.Group()

        player1_r_change = buttons(
            self.scale_pos((940, 700), True)[0],
            self.scale_pos((940, 700), True)[1], "", self.scale_size(50), ">",
            "Black", "white", "Black")
        player1_l_change = buttons(
            self.scale_pos((640, 700), True)[0],
            self.scale_pos((640, 700), True)[1], "", self.scale_size(50), "<",
            "Black", "white", "Black")

        buttons_group.add(player1_r_change)
        buttons_group.add(player1_l_change)

        Join_server = buttons(
            self.scale_pos((w // 2 + 20, h // 2 - 50), True)[0],
            self.scale_pos((w // 2 + 20, h // 2 - 50), True)[1], "",
            self.scale_size(50), "Join server", "#ad8fff", "black", "Black")

        create_server = buttons(
            self.scale_pos((w // 2 + 20, h // 2 + 50), True)[0],
            self.scale_pos((w // 2 + 20, h // 2 + 50), True)[1], "",
            self.scale_size(50), "Create server", "#ad8fff", "black", "Black")
        buttons_group.add(Join_server)
        buttons_group.add(create_server)

        client = None
        connect_thread = None
        connection_ready = False

        while True:
            self.dt = self.clock.tick(self.tick) / 1000
            self.screen.fill("black")
            self.fields[self.field].setting(self.screen, (10, 10))
            self.txt.draw(self.scale_pos((370, 110)),
                          "LAN MULTIPLAYER MODE",
                          100,
                          "black",
                          Italic=True)

            for button in buttons_group:
                button.update(pygame.mouse.get_pos())
                button.draw(self.screen)

            self.screen.blit(
                self.player_skins[self.player_skin[3]].img_now(
                    0, self.scale_pos((130, 130))), self.scale_pos((720, 620)))

            scaled_bounds_with_holes = self.get_scaled_boundaries()
            if self.debug:
                pygame.draw.rect(self.screen, "Blue",
                                 self.get_scaled_goal_triggers()[0])
                pygame.draw.rect(self.screen, "Orange",
                                 self.get_scaled_goal_triggers()[1])
            else:
                pygame.draw.rect(self.screen, "Blue",
                                 self.get_scaled_goal_triggers()[0])
                pygame.draw.rect(self.screen, "Orange",
                                 self.get_scaled_goal_triggers()[1])

            for boundry in scaled_bounds_with_holes:
                pygame.draw.rect(self.screen, "black", boundry)

            for event in pygame.event.get():
                pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN
                                                 and event.key
                                                 == pygame.K_ESCAPE):
                    return 0
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if player1_r_change.get_rect().collidepoint(pos):
                        self.player_skin[3] = (self.player_skin[3] + 1) % len(
                            self.player_skins)

                    if player1_l_change.get_rect().collidepoint(pos):
                        self.player_skin[3] = (self.player_skin[3] - 1) % len(
                            self.player_skins)
                        # In LAN_menu, replace synchronous client.start() with async check
                    if Join_server.get_rect().collidepoint(pos):
                        if not connect_thread:
                            client = LANClient()
                            Join_server.change_style("Finding Server...",
                                                     "#ad8fff", "black")

                            def try_connect():
                                nonlocal connection_ready
                                try:
                                    client.start(timeout=5)
                                    # Wait for ID assignment
                                    start_wait = time.time()
                                    while client.my_id is None and time.time() - start_wait < 5:
                                        time.sleep(0.1)
                                    if client.my_id:
                                        connection_ready = True
                                except TimeoutError:
                                    self.generate_message(
                                        "No Servers found", 20)
                                    Join_server.change_style(
                                        "Join server", "#ad8fff", "black")

                            connect_thread = threading.Thread(
                                target=try_connect, daemon=True)
                            connect_thread.start()
                    if create_server.get_rect().collidepoint(pos):
                        host = LANHost()
                        host.start()
                        self.LAN_game("host", host)
                        return 0
            if connection_ready:
                self.LAN_game("client", client)
                return 0
            self.generate_message(None)
            pygame.display.flip()

    def LAN_game(self, mode: str, host_or_client):
        """
        Starts a LAN game session with full multiplayer support.
        mode: "host" or "client"
        host_or_client: LANHost or LANClient instance
        """
        w, h = pygame.display.get_window_size()
        dt = 0
        run = True

        players = pygame.sprite.Group()
        remote_players = {}

        # -------------------- ID SETUP --------------------
        if mode == "host":
            local_player_id = "host"
        else:
            local_player_id = host_or_client.my_id
            if not local_player_id:
                return 0 # Error: No ID assigned

        # -------------------- LOCAL PLAYER --------------------       
        local_start_pos = pygame.Vector2(200, 200)

        local_player = LANPlayer(
            Start_pos=local_start_pos.copy(),
            display=self.screen,
            wall=self.get_scaled_boundaries(),
            skin=self.player_skins[self.player_skin[3]],
            key=None,
            mass=1,
            lan_client=host_or_client if mode == "client" else None,
            lan_host=host_or_client if mode == "host" else None,
            player_id=local_player_id,
            is_remote=False)
        players.add(local_player)

        # -------------------- BALLS --------------------
        balls = [
            Ball((w / 2, h / 2), 25, self.screen,
                 Animation("ballout_assets/Ball1.png",
                           [(0, 0, 32, 32)], (50, 50)),
                 self.get_scaled_boundaries(), 0.002, players,
                 self.get_scaled_goal_triggers())
        ]
        ball_start_positions = [(b.x, b.y) for b in balls]

        # -------------------- GAME VARIABLES --------------------
        player_1_goals = 0
        player_2_goals = 0
        state = "playing"
        self.goal_timer.reset()
        self.game_duration.reset()

        # -------------------- MAIN LOOP --------------------
        while run:
            dt = self.clock.tick(self.tick) / 100
            keys = pygame.key.get_pressed()
            self.screen.fill("black")
            self.fields[self.field].setting(self.screen, (10, 10))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    res = self.pause()
                    if res: return 0

            joystick = None

            # --- SYNC REMOTE PLAYERS ---
            # Fetch latest state from Host or Client object
            current_network_players = host_or_client.players.copy()
            
            # 1. Create/Update players
            for pid, state in current_network_players.items():
                if pid == local_player_id:
                    continue
                if pid not in remote_players:
                    # New player joined
                    rp = LANPlayer(
                        Start_pos=pygame.Vector2(state["pos"]),
                        display=self.screen,
                        wall=self.get_scaled_boundaries(),
                        skin=self.player_skins[3], # Default skin for network players
                        key=None,
                        mass=1,
                        player_id=pid,
                        lan_client=host_or_client if mode == "client" else None, # Pass client for interpolation
                        is_remote=True)
                    remote_players[pid] = rp
                    players.add(rp)
            
            # 2. Remove disconnected players
            for pid in list(remote_players.keys()):
                if pid not in current_network_players:
                    rp = remote_players.pop(pid)
                    rp.kill()

            # --- UPDATE PLAYERS ---
            for p in players:
                p.update(keys=keys, dt=dt, joystick=joystick)
                p.draw(self.debug)

            # --- UPDATE BALLS ---
            scored = False
            for bi, ball in enumerate(balls):
                goal_scored = ball.update(dt)
                if goal_scored:
                    if goal_scored == 1: player_1_goals += 1
                    elif goal_scored == 2: player_2_goals += 1
                    scored = True
                    break

            # --- HANDLE GOAL PAUSE ---
            if scored:
                state = "goal_pause"
                self.goal_timer.reset(1000, "down", 5)
                for bi, ball in enumerate(balls):
                    ball.x, ball.y = ball_start_positions[bi]
                    ball.vx = ball.vy = ball.ax = ball.ay = 0
                    ball.hit_box, ball.goal_hitbox = ball.update_hbox()
                for p in players:
                    if not p.is_remote:
                        p.pos = local_start_pos.copy()
                        p.velocity = pygame.Vector2(0, 0)
                        p.hit_box = p.update_hbox()

            if state == "goal_pause":
                self.goal_timer.step()
                if int(self.goal_timer) <= 0:
                    state = "playing"

            # --- DRAW EVERYTHING ---
            for ball in balls:
                ball.draw(self.debug)

            for p in players:
                self.screen.blit(
                    self.player_skins[self.player_skin[3]].img_now(
                        p.angle, self.scale_pos((p.size[0], p.size[1]))),
                    self.scale_pos((p.pos.x, p.pos.y)))

            for bound in self.get_scaled_boundaries():
                pygame.draw.rect(self.screen, "black", bound)
            pygame.draw.rect(self.screen, "Blue",
                             self.get_scaled_goal_triggers()[0])
            pygame.draw.rect(self.screen, "Orange",
                             self.get_scaled_goal_triggers()[1])

            self.txt.draw(self.scale_pos((10, 10)),
                          f"Player 1: {player_1_goals}",
                          size=40,
                          color="black")
            self.txt.draw(self.scale_pos((1350, 10)),
                          f"Player 2: {player_2_goals}",
                          size=40,
                          color="black")

            pygame.display.flip()

        # --- CLEANUP ---
        run = False
        host_or_client.stop()
        return 0


if __name__ == "__main__":
    os.system("cls") if os.name == "nt" else os.system("clear")
    fullscreen = (900, 600)
    fullscreen = get_screen()
    #print(fullscreen)
    pygame.display.init()
    game = Ballout(0, fullscreen).main_menu()
