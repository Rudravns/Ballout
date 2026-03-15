import pygame, os, sys, random, ballout_assets, math, time
from ballout_classes import *
import socket, threading, pickle


class Player(pygame.sprite.Sprite):

    def __init__(self, Start_pos, display, wall, skin, key, mass):
        super().__init__()
        self.x, self.y = Start_pos
        self.display_width, self.display_height = pygame.display.get_window_size(
        )
        self.key = key
        self.mass = mass

        self.player = skin
        self.size = skin.sprites[0].get_size()
        self.angle = 0

        self.pos = pygame.Vector2(self.x, self.y)  # Position
        self.velocity = pygame.Vector2(0, 0)  # Velocity
        self.acceleration = pygame.Vector2(0, 0)  # Acceleration
        self.last_pos = self.pos.copy()  # Save last position

        self.speed = 15
        self.friction = -0.15
        self.surface = display
        self.wall = wall
        self.hit_box = self.update_hbox()

    def add_hbox(self, players):
        self.other_players = players

    def update_hbox(self):
        # Use proportional padding (40% of sprite size) instead of fixed 20px
        padding = self.size[0] * 0.4
        size = (self.size[0] - padding, self.size[1] - padding)
        pos = (self.pos[0] + padding / 2, self.pos[1] + padding / 2)
        return pygame.Rect(pos[0], pos[1], size[0], size[1])

    def draw(self, debug=False):
        self.surface.blit(self.player.img_now(self.angle), self.pos)
        if debug:
            pygame.draw.rect(self.surface, "red", self.hit_box, 2)

    def collision_momentum(self, other):
        diff = self.pos - other.pos
        dist = diff.length()

        if dist == 0:
            diff = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            dist = diff.length()

        # Radii approximation (using hit_box width)
        min_dist = (self.hit_box.width + other.hit_box.width) / 2

        if dist < min_dist:  # collision
            # Normalize collision normal
            normal = diff.normalize()

            # Push them apart to remove overlap
            overlap = min_dist - dist
            total_mass = self.mass + other.mass
            if total_mass == 0: total_mass = 1

            self.pos += normal * (overlap * (other.mass / total_mass))
            other.pos -= normal * (overlap * (self.mass / total_mass))

            # --- Velocity exchange ---
            # Project velocities onto normal
            v1n = self.velocity.dot(normal)
            v2n = other.velocity.dot(normal)

            # Tangential components (unchanged)
            v1t = self.velocity - v1n * normal
            v2t = other.velocity - v2n * normal

            # Elastic collision 1D formula for normal components
            new_v1n = (v1n * (self.mass - other.mass) +
                       2 * other.mass * v2n) / total_mass
            new_v2n = (v2n * (other.mass - self.mass) +
                       2 * self.mass * v1n) / total_mass

            self.velocity = v1t + new_v1n * normal
            other.velocity = v2t + new_v2n * normal

    def update(self, keys, dt, joystick: tuple = None):
        self.last_pos = self.pos.copy()
        self.acceleration = pygame.Vector2(0, 0)

        self.player_keys(keys)
        if joystick is not None:
            self.acceleration += pygame.Vector2(*joystick[0])

        if self.acceleration.length_squared() > 0:
            self.acceleration = self.acceleration.normalize() * self.speed
        self.acceleration += self.velocity * self.friction

        self.velocity += self.acceleration * dt

        self.pos.x += self.velocity.x * dt
        self.hit_box = self.update_hbox()
        self.check_collision("horizontal")

        self.pos.y += self.velocity.y * dt
        self.hit_box = self.update_hbox()
        self.check_collision("vertical")

        # Clamp to screen
        self.pos.x = self.clamp((self.display_width - self.size[0], 0),
                                self.pos.x)
        self.pos.y = self.clamp((self.display_height - self.size[1], 0),
                                self.pos.y)

        # Rotate toward velocity
        if self.velocity.length_squared() > 0.5:
            target_angle = math.degrees(
                math.atan2(-self.velocity.x, -self.velocity.y))
            angle_diff = (target_angle - self.angle + 180) % 360 - 180
            self.angle += angle_diff * 0.2

        self.hit_box = self.update_hbox()
        self.animate()

    def animate(self):
        animation_speed = self.clamp((200, 0), self.velocity.length_squared())
        animation_speed = abs(-animation_speed + 200)

        if animation_speed <= 192:
            self.player.update(animation_speed * 10)
        else:
            self.player.update(0, False)

    def player_keys(self, keys):
        if self.key == "First":
            if keys[pygame.K_w]: self.acceleration.y = -1
            if keys[pygame.K_s]: self.acceleration.y = 1
            if keys[pygame.K_a]: self.acceleration.x = -1
            if keys[pygame.K_d]: self.acceleration.x = 1
            self.animate()
        elif self.key == "Second":
            if keys[pygame.K_UP]: self.acceleration.y = -1
            if keys[pygame.K_DOWN]: self.acceleration.y = 1
            if keys[pygame.K_LEFT]: self.acceleration.x = -1
            if keys[pygame.K_RIGHT]: self.acceleration.x = 1
            self.animate()
        elif self.key == "Third":
            if keys[pygame.K_t]: self.acceleration.y = -1
            if keys[pygame.K_g]: self.acceleration.y = 1
            if keys[pygame.K_f]: self.acceleration.x = -1
            if keys[pygame.K_h]: self.acceleration.x = 1
            self.animate()
        elif self.key == "Fourth":
            if keys[pygame.K_i]: self.acceleration.y = -1
            if keys[pygame.K_k]: self.acceleration.y = 1
            if keys[pygame.K_j]: self.acceleration.x = -1
            if keys[pygame.K_l]: self.acceleration.x = 1
            self.animate()

    def check_collision(self, direction):
        for wall in self.wall:
            if self.hit_box.colliderect(wall):
                if direction == "horizontal":
                    self.pos.x = self.last_pos.x
                    self.velocity.x = 0
                elif direction == "vertical":
                    self.pos.y = self.last_pos.y
                    self.velocity.y = 0

        if hasattr(self, "other_players"):
            for other in self.other_players:
                if self.hit_box.colliderect(other.hit_box):
                    self.collision_momentum(other)

    def change_skin(self, skin):
        self.player = skin.update()
        self.hit_box = self.update_hbox()

    @staticmethod
    def clamp(boundary, value):
        max_val, min_val = boundary
        return min(max_val, max(min_val, value))


class Ball(pygame.sprite.Sprite):

    def __init__(self,
                 pos,
                 radius,
                 display,
                 ball,
                 wall,
                 mass=1,
                 players=[],
                 goaltrig=[]):
        super().__init__()
        self.x, self.y = pos
        self.radius = radius
        self.mass = mass
        self.surface = display
        self.ball = ball
        self.balls = []  # Other balls
        self.wall = wall
        self.players = players
        self.goal_trig = goaltrig

        # Physics
        self.vx = 0.0
        self.vy = 0.0
        self.ax = 0.0
        self.ay = 0.0
        self.last_x, self.last_y = self.x, self.y
        self.friction = -0.05
        self.rotation = 0

        # Collision
        self.width = radius * 2
        self.height = radius * 2
        self.hit_box, self.goal_hitbox = self.update_hbox()

    def update_hbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height), [
            pygame.Rect(self.x - self.width, self.y, self.width, self.height),
            pygame.Rect(self.x + self.width, self.y, self.width, self.height)
        ]

    def draw(self, debug=False):
        if debug:
            pygame.draw.rect(self.surface, "red", self.hit_box, 1)
            pygame.draw.rect(self.surface, "green", self.goal_hitbox[0], 1)
            pygame.draw.rect(self.surface, "blue", self.goal_hitbox[1], 1)
        ball_img = self.ball.img_now()
        ball_img = pygame.transform.scale(ball_img, (self.width, self.height))
        ball_img = pygame.transform.rotate(ball_img, self.rotation)
        self.surface.blit(ball_img, (self.x, self.y))

    def add_ball(self, other_ball):
        if other_ball != self and other_ball not in self.balls:
            self.balls.append(other_ball)

    def goal(self) -> int:
        screen_width = pygame.display.get_window_size()[0]

        # Left goal
        if self.x + self.width < 0:
            return 2  # goal on left side

        # Right goal
        elif self.x > screen_width:
            return 1  # goal on right side

        # No goal
        return 0

    def in_goal_gap(self):
        """Check if ball is inside left or right goal opening (ignore clamp)."""
        screen_w, screen_h = pygame.display.get_window_size()
        top_gap = screen_h / 3
        bottom_gap = screen_h * 2 / 3
        cx = self.x + self.radius
        cy = self.y + self.radius
        if cx <= self.radius + 15 and top_gap <= cy <= bottom_gap:
            return True
        if cx >= screen_w - self.radius - 15 and top_gap <= cy <= bottom_gap:
            return True
        return False

    # ===== WALL COLLISION WITH REFLECT =====
    def wall_collision(self):
        """Clamp to walls and bounce off corners properly."""
        vel = pygame.Vector2(self.vx, self.vy)
        normal = pygame.Vector2(0, 0)
        collided = False

        for wall in self.wall:
            # Horizontal collisions (top/bottom)
            if self.hit_box.colliderect(wall):
                if self.vy > 0 and self.y + self.height > wall.top and self.y < wall.top:  # moving down
                    self.y = wall.top - self.height
                    normal.y = -1
                    collided = True
                elif self.vy < 0 and self.y < wall.bottom and self.y + self.height > wall.bottom:  # moving up
                    self.y = wall.bottom
                    normal.y = 1
                    collided = True

                # Vertical collisions (left/right)
                if self.vx > 0 and self.x + self.width > wall.left and self.x < wall.left:  # moving right
                    self.x = wall.left - self.width
                    normal.x = -1
                    collided = True
                elif self.vx < 0 and self.x < wall.right and self.x + self.width > wall.right:  # moving left
                    self.x = wall.right
                    normal.x = 1
                    collided = True

        if collided:
            # Reflect velocity along the collision normal
            vel = vel.reflect(normal) * 0.7
            self.vx, self.vy = vel.x, vel.y

        self.hit_box, self.goal_hitbox = self.update_hbox()

    def player_collision(self, player):
        player_center = player.pos + pygame.Vector2(player.size) / 2
        ball_center = pygame.Vector2(self.x + self.radius,
                                     self.y + self.radius)
        diff = ball_center - player_center
        dist = diff.length()
        if dist == 0:
            diff = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            dist = diff.length()
        normal = diff / dist

        # Push the ball out of the player
        min_dist = self.radius + max(player.size) / 2
        overlap = max(0, min_dist - dist)
        if overlap > 0:
            total_mass = self.mass + player.mass
            self.x += normal.x * overlap * (player.mass / total_mass)
            self.y += normal.y * overlap * (player.mass / total_mass)
            player.pos.x -= normal.x * overlap * (self.mass / total_mass)
            player.pos.y -= normal.y * overlap * (self.mass / total_mass)

        # Relative velocity along the normal
        rel_vel = (self.vx - player.velocity.x) * normal.x + (
            self.vy - player.velocity.y) * normal.y

        # If already moving apart, do nothing
        if rel_vel > 0:
            return

        # Elastic collision impulse
        e = 0.8  # energy retention factor
        j = -(1 + e) * rel_vel
        j /= (1 / self.mass) + (1 / player.mass)

        # Apply impulse
        self.vx += (j * normal.x) / self.mass
        self.vy += (j * normal.y) / self.mass
        player.velocity.x -= (j * normal.x) / player.mass
        player.velocity.y -= (j * normal.y) / player.mass

        # Reflect ball slightly more to make it feel bouncy
        self.vx += normal.x * 0.5
        self.vy += normal.y * 0.5

    def ball_collision(self, other):
        diff = pygame.Vector2((self.x + self.radius, self.y + self.radius)) - \
               pygame.Vector2((other.x + other.radius, other.y + other.radius))
        dist = diff.length()
        if dist == 0:
            diff = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
            dist = diff.length()
        normal = diff / dist

        min_dist = self.radius + other.radius
        overlap = max(0, min_dist - dist)
        if overlap > 0:
            total_mass = self.mass + other.mass
            self_move = normal * (overlap * (other.mass / total_mass))
            other_move = normal * (overlap * (self.mass / total_mass))

            other_candidate_pos = pygame.Rect(other.x - other_move.x,
                                              other.y - other_move.y,
                                              other.width, other.height)
            if not any(other_candidate_pos.colliderect(w) for w in other.wall):
                other.x -= other_move.x
                other.y -= other_move.y
            else:
                other.vx = 0
                other.vy = 0

            self.x += self_move.x
            self.y += self_move.y

        rel_vel = (self.vx - other.vx) * normal.x + (self.vy -
                                                     other.vy) * normal.y
        if rel_vel > 0:
            return

        e = 0.8
        j = -(1 + e) * rel_vel
        j /= (1 / self.mass) + (1 / other.mass)

        self.vx += (j * normal.x) / self.mass
        self.vy += (j * normal.y) / self.mass
        if not any(other.hit_box.colliderect(w) for w in other.wall):
            other.vx -= (j * normal.x) / other.mass
            other.vy -= (j * normal.y) / other.mass

    def check_collision(self):
        """Wrapper: handle walls, players, and other balls."""
        self.wall_collision()

        # Players
        for player in self.players:
            if self.hit_box.colliderect(player.hit_box):
                self.player_collision(player)

        # Other balls
        for other in self.balls:
            if other != self and self.hit_box.colliderect(other.hit_box):
                self.ball_collision(other)

    # ===== MAIN UPDATE =====
    def update(self, dt) -> bool:
        self.last_x, self.last_y = self.x, self.y

        # Apply friction
        self.ax += self.vx * self.friction
        self.ay += self.vy * self.friction

        # Update velocity
        self.vx += self.ax * dt
        self.vy += self.ay * dt

        # Move ball
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Update hitboxes
        self.hit_box, self.goal_hitbox = self.update_hbox()

        # Check collisions with walls, players, balls
        self.check_collision()

        # Clamp inside screen as safety
        if not self.in_goal_gap():
            screen_w, screen_h = pygame.display.get_window_size()
            self.x = max(0, min(screen_w - self.width, self.x))
            self.y = max(0, min(screen_h - self.height, self.y))
            self.hit_box, self.goal_hitbox = self.update_hbox()

        # Rotation for visual effect
        if math.hypot(self.vx, self.vy) > 0.5:
            target_angle = math.degrees(math.atan2(-self.vx, -self.vy))
            angle_diff = (target_angle - self.rotation + 180) % 360 - 180
            self.rotation += angle_diff * 0.2

        self.ax = 0
        self.ay = 0
        return self.goal()

    @staticmethod
    def clamp(boundary, value):
        max_val, min_val = boundary
        return min(max_val, max(min_val, value))

class bot(Player):
    def __init__(self,
                 Start_pos,
                 display,
                 wall,
                 skin,
                 mass,
                 goals,
                 side,
                 difficulty=3
                 ):
        super().__init__(Start_pos, display, wall, skin, 0, mass)
        self.pos = pygame.Vector2(self.x, self.y)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = pygame.Vector2(0, 0)
        self.friction = 0.85
        self.surface = display
        self.wall = wall
        self.hit_box = self.update_hbox()

        # Clamp difficulty between 1 and 30
        self.difficulty = max(1, min(30, difficulty))

        # Linear scaling for slower movement
        def linear_scale(start, end):
            return start + (end - start) * (self.difficulty - 1) / 29

        self.speed = linear_scale(6, 25)  # slower
        self.kick_accuracy = linear_scale(0.2, 1.0)
        self.aggressiveness = linear_scale(0.1, 0.7)
        self.goal_chance = linear_scale(0.12, 1.0)

        # Ball tracking
        self.ball = []
        self.closest_ball = None

        # Goal info
        self.goal = None
        self.goal_y = 0
        self.add_goal(goals, side)

    # ======================== UPDATE ========================
    def update(self, keys, dt):
        # Find closest ball
        closest = None
        min_dist_sq = float('inf')
        bot_x, bot_y = self.pos.x, self.pos.y

        for b in self.ball:
            if not hasattr(b, "x"):
                continue
            bx, by = b.x + b.radius, b.y + b.radius
            dist_sq = (bx - bot_x) ** 2 + (by - bot_y) ** 2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest = b

        self.closest_ball = closest
        if not self.closest_ball:
            super().update(keys, dt)
            return

        # Move toward closest ball
        ball_center = pygame.Vector2(self.closest_ball.x + self.closest_ball.radius,
                                     self.closest_ball.y + self.closest_ball.radius)
        to_ball = ball_center - self.pos
        if to_ball.length_squared() > 0:
            to_ball.normalize_ip()
        self.acceleration = to_ball * self.speed * self.aggressiveness

        # Apply friction + update velocity
        self.velocity *= self.friction
        self.velocity += self.acceleration * dt

        # Clamp velocity
        if self.velocity.length_squared() > self.speed ** 2:
            self.velocity.scale_to_length(self.speed)

        # Update position
        self.pos += self.velocity
        self.x, self.y = self.pos.x, self.pos.y

        # Kick the ball if close
        max_dist = self.closest_ball.radius + max(self.size) / 2 + 10
        if (ball_center - self.pos).length_squared() <= max_dist ** 2:
            # Kick only 50% after level 25
            if self.difficulty > 25 and random.random() > 0.5:
                self.kick_ball()
            elif self.difficulty <= 25:
                self.kick_ball()

        super().update(keys, dt)

    # ======================== KICK BALL ========================
    def kick_ball(self):
        if not self.closest_ball or not self.goal:
            return

        ball_center = pygame.Vector2(
            self.closest_ball.x + self.closest_ball.radius,
            self.closest_ball.y + self.closest_ball.radius)
        goal_center = pygame.Vector2(self.goal[0], self.goal_y)

        # Decide if aiming for goal
        if random.random() <= self.goal_chance:
            target = goal_center
        else:
            angle = random.uniform(-135, 135) * math.pi / 180
            target = ball_center + pygame.Vector2(math.cos(angle), math.sin(angle)) * 200

        to_target = target - ball_center
        if to_target.length_squared() == 0:
            return

        # Apply random deviation
        angle_offset = random.uniform(-0.2, 0.2) * self.kick_accuracy
        cos_a = math.cos(angle_offset)
        sin_a = math.sin(angle_offset)
        new_x = to_target.x * cos_a - to_target.y * sin_a
        new_y = to_target.x * sin_a + to_target.y * cos_a
        angled_vec = pygame.Vector2(new_x, new_y)
        angled_vec.normalize_ip()

        power = 10 * self.aggressiveness + 5
        self.closest_ball.vx += angled_vec.x * power
        self.closest_ball.vy += angled_vec.y * power

    # ======================== OTHER ========================
    def add_goal(self, goal, side=0):
        self.goal = goal[side]
        self.owngoal = goal[0] if side == 1 else goal[1]
        self.goal_y = self.random_point()

    def random_point(self, offset: float = 0.0) -> float:
        return random.uniform(self.goal[1] - offset,
                              (self.goal[1] + self.goal[3] + offset))

    def add_ball(self, other_ball):
        if isinstance(other_ball, list):
            for b in other_ball:
                if b not in self.ball:
                    self.ball.append(b)
        else:
            if other_ball not in self.ball:
                self.ball.append(other_ball)

    def draw(self, debug=False):
        if debug and self.closest_ball and self.goal:
            pygame.draw.line(self.surface, "green", self.pos,
                             (0, self.goal[1]), 2)
            pygame.draw.line(self.surface, "green", self.pos,
                             (0, self.goal[1] + self.goal[3]), 2)
            ball_center = pygame.Vector2(
                self.closest_ball.x + self.closest_ball.radius,
                self.closest_ball.y + self.closest_ball.radius)
            pygame.draw.line(self.surface, "red", self.pos, ball_center, 2)
            pygame.draw.line(self.surface, "blue", self.pos,
                             (self.goal[0], self.goal_y), 2)
        super().draw(debug)

    def __str__(self):
        return "BOT"

# ================= LAN NETWORK CLASSES =================


def send_packet(sock, data):
    try:
        sock.sendall(pickle.dumps(data))
    except:
        pass


def recv_packet(sock):
    try:
        data = sock.recv(4096)
        if not data:
            return None
        return pickle.loads(data)
    except:
        return None


# ----------------- LANHost -----------------
class LANHost:

    def __init__(self, tcp_port=5000, udp_port=5001, broadcast_interval=0.1):
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.broadcast_interval = broadcast_interval
        self.running = False
        self.server_socket = None
        self.clients = []
        self.players = {}
        self.lock = threading.Lock()

    def update_player(self, player_id, state):
        """Update a specific player's state safely."""
        with self.lock:
            if player_id not in self.players:
                self.players[player_id] = {}
            self.players[player_id].update(state)

    def start(self):
        self.running = True
        threading.Thread(target=self._udp_broadcast_thread,
                         daemon=True).start()
        threading.Thread(target=self._tcp_server_thread, daemon=True).start()
        threading.Thread(target=self._continuous_broadcast_thread,
                         daemon=True).start()

    def _udp_broadcast_thread(self):
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        msg = f"GAME_HOST:{self.tcp_port}".encode()
        while self.running:
            try:
                udp.sendto(msg, ('<broadcast>', self.udp_port))
            except:
                pass
            time.sleep(self.broadcast_interval)

    def _tcp_server_thread(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.tcp_port))
        self.server_socket.listen()
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                player_id = f"client{len(self.clients)+1}"
                player_data = {
                    "pos":
                    [random.randint(100, 200),
                     random.randint(100, 200)],
                    "vel": [0, 0],
                    "angle":
                    0,
                    "color": (random.randint(50, 255), random.randint(50, 255),
                              random.randint(50, 255)),
                    "name":
                    player_id
                }
                with self.lock:
                    self.players[player_id] = player_data
                    self.clients.append(conn)
                send_packet(conn, {"assign_id": player_id})
                threading.Thread(target=self._handle_client,
                                 args=(conn, player_id),
                                 daemon=True).start()
            except:
                break

    def _handle_client(self, conn, player_id):
        while self.running:
            data = recv_packet(conn)
            if data is None: break
            with self.lock:
                if player_id in self.players:
                    self.players[player_id]["pos"] = data.get(
                        "pos", self.players[player_id]["pos"])
                    self.players[player_id]["vel"] = data.get(
                        "vel", self.players[player_id]["vel"])
                    self.players[player_id]["angle"] = data.get(
                        "angle", self.players[player_id]["angle"])
        with self.lock:
            self.players.pop(player_id, None)
            if conn in self.clients: self.clients.remove(conn)
        conn.close()

    def _continuous_broadcast_thread(self):
        while self.running:
            with self.lock:
                state = self.players.copy()
            self.broadcast_state(state)
            time.sleep(self.broadcast_interval)

    def broadcast_state(self, state_dict):
        dead = []
        with self.lock:
            for conn in self.clients:
                try:
                    send_packet(conn, {"players": state_dict})
                except:
                    dead.append(conn)
            for conn in dead:
                if conn in self.clients:
                    self.clients.remove(conn)
                    conn.close()

    def stop(self):
        self.running = False
        for c in self.clients:
            c.close()
        if self.server_socket: self.server_socket.close()


# ----------------- LANClient -----------------
class LANClient:

    def __init__(self, udp_port=5001):
        self.udp_port = udp_port
        self.found_host = None
        self.client_socket = None
        self.players = {}
        self.my_id = None
        self.connected = False
        self._receive_thread_running = False

    def start(self, timeout=5):
        threading.Thread(target=self._discover_thread, daemon=True).start()
        start_time = time.time()
        while self.found_host is None:
            if time.time() - start_time > timeout:
                raise TimeoutError("No host found")
            time.sleep(0.05)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.found_host)
        self.connected = True
        self._receive_thread_running = True
        threading.Thread(target=self._receive_thread, daemon=True).start()
        return self.client_socket

    def _discover_thread(self):
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp.bind(('', self.udp_port))
        while self.found_host is None:
            try:
                data, addr = udp.recvfrom(1024)
                msg = data.decode()
                if msg.startswith("GAME_HOST"):
                    parts = msg.split(":")
                    if len(parts) == 2 and parts[1].isdigit():
                        self.found_host = (addr[0], int(parts[1]))
            except:
                pass
        udp.close()

    def _receive_thread(self):
        while self._receive_thread_running:
            packet = recv_packet(self.client_socket)
            if not packet: continue
            if "assign_id" in packet: self.my_id = packet["assign_id"]
            elif "players" in packet: self.players = packet["players"]

    def send_pos(self, data):
        if not self.my_id or not self.client_socket: return
        state = {
            "pos": data.get("pos", data),
            "vel": data.get("vel", [0, 0]),
            "angle": data.get("angle", 0)
        }
        send_packet(self.client_socket, state)

    def stop(self):
        self._receive_thread_running = False
        if self.client_socket: self.client_socket.close()
        self.connected = False


class LANPlayer(Player):
    """
    Player subclass that syncs over LAN.
    - Local players handle input + physics + collisions.
    - Remote players are interpolated smoothly.
    - Works with LANClient or LANHost.
    """

    def __init__(self,
                 Start_pos,
                 display,
                 wall,
                 skin,
                 key=None,
                 mass=1,
                 lan_client: LANClient = None,
                 lan_host: LANHost = None,
                 player_id=None,
                 send_rate=0.05,
                 is_remote=False):
        super().__init__(Start_pos, display, wall, skin, key, mass)

        self.lan_client = lan_client
        self.lan_host = lan_host
        self.player_id = player_id
        self.send_rate = send_rate
        self._last_send = 0
        self.is_remote = is_remote

        # Interpolation
        self.network_pos = self.pos.copy()
        self.network_velocity = self.velocity.copy()
        self.network_angle = self.angle

    # ---------------- NETWORK ----------------
    def send_state(self):
        """Send this player's state to host or client."""
        if self.is_remote:
            return  # remote players don't send

        now = time.time()
        if now - self._last_send < self.send_rate:
            return
        self._last_send = now

        state = {
            "pos": (self.pos.x, self.pos.y),
            "vel": (self.velocity.x, self.velocity.y),
            "angle": self.angle
        }

        if self.lan_host:
            self.lan_host.update_player(self.player_id, state)
        elif self.lan_client:
            self.lan_client.send_pos(state)

    # ---------------- APPLY REMOTE STATES ----------------
    def apply_remote_states(self):
        """Automatically interpolate all remote players."""
        if not self.lan_client:
            return

        for pid, pdata in self.lan_client.players.items():
            if pid == self.player_id:
                continue  # skip self

            remote_pos = pygame.Vector2(*pdata["pos"])
            remote_vel = pygame.Vector2(*pdata.get("vel", (0, 0)))
            remote_angle = pdata.get("angle", self.angle)

            # Smooth interpolation
            lerp_t = min(1,
                         0.1 * pygame.time.get_ticks() / 16)  # adjust for dt
            self.network_pos += (remote_pos - self.network_pos) * lerp_t
            self.network_velocity += (remote_vel -
                                      self.network_velocity) * lerp_t
            angle_diff = (remote_angle - self.network_angle + 180) % 360 - 180
            self.network_angle += angle_diff * lerp_t

            # Apply interpolated values
            self.pos = self.network_pos.copy()
            self.velocity = self.network_velocity.copy()
            self.angle = self.network_angle
            self.hit_box = self.update_hbox()

    # ---------------- UPDATE ----------------
    def update(self, keys=None, dt=1, joystick=None):
        self.last_pos = self.pos.copy()
        self.acceleration = pygame.Vector2(0, 0)

        if not self.is_remote:
            # ---- Handle input ----
            if keys:
                if keys[pygame.K_w]: self.acceleration.y = -1
                if keys[pygame.K_s]: self.acceleration.y = 1
                if keys[pygame.K_a]: self.acceleration.x = -1
                if keys[pygame.K_d]: self.acceleration.x = 1
                if keys[pygame.K_UP]: self.acceleration.y = -1
                if keys[pygame.K_DOWN]: self.acceleration.y = 1
                if keys[pygame.K_LEFT]: self.acceleration.x = -1
                if keys[pygame.K_RIGHT]: self.acceleration.x = 1

            if joystick:
                self.acceleration += pygame.Vector2(*joystick)

            if self.acceleration.length_squared() > 0:
                self.acceleration = self.acceleration.normalize() * self.speed
            self.acceleration += self.velocity * self.friction
            self.velocity += self.acceleration * dt

            # Move & collision
            self.pos.x += self.velocity.x * dt
            self.hit_box = self.update_hbox()
            self.check_collision("horizontal")

            self.pos.y += self.velocity.y * dt
            self.hit_box = self.update_hbox()
            self.check_collision("vertical")

            # Clamp to screen
            self.pos.x = self.clamp((self.display_width - self.size[0], 0),
                                    self.pos.x)
            self.pos.y = self.clamp((self.display_height - self.size[1], 0),
                                    self.pos.y)

            # Rotate toward movement
            if self.velocity.length_squared() > 0.5:
                target_angle = math.degrees(
                    math.atan2(-self.velocity.x, -self.velocity.y))
                angle_diff = (target_angle - self.angle + 180) % 360 - 180
                self.angle += angle_diff * 0.2

            self.hit_box = self.update_hbox()
            self.send_state()
        else:
            # ---- Remote player interpolation ----
            self.apply_remote_states()

    # ---------------- DRAW ----------------
    def draw(self, debug=False):
        self.surface.blit(self.player.img_now(self.angle), self.pos)
        if debug:
            pygame.draw.rect(self.surface, "red", self.hit_box, 2)


pass
