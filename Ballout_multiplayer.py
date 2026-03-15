import pygame
import socket
import threading
import time
import sys
import pickle
import struct
import random

pygame.init()
WIDTH, HEIGHT = 600, 400
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("LAN Multiplayer (Dict Players)")
FONT = pygame.font.SysFont("Arial", 24)
FPS = 60

# -------------------- NETWORK HELPERS --------------------
def send_packet(sock, obj):
    """Send a pickled object with 4-byte length header."""
    data = pickle.dumps(obj)
    sock.sendall(struct.pack("!I", len(data)) + data)

def recv_packet(sock):
    """Receive full pickled object using header length."""
    header = sock.recv(4)
    if not header:
        return None
    (length,) = struct.unpack("!I", header)
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            return None
        data += chunk
    return pickle.loads(data)

# -------------------- HOST --------------------
class LANHost:
    def __init__(self, tcp_port=5000, udp_port=5001, broadcast_interval=0.1):
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.broadcast_interval = broadcast_interval
        self.running = False
        self.server_socket = None
        self.clients = []  # [(conn, id)]
        self.players = {}  # {id: {...}}
        self.players["host"] = {
            "pos": [100, 100],
            "color": (0, 255, 0),
            "name": "Host"
        }

    def start(self):
        self.running = True
        threading.Thread(target=self._broadcast_thread, daemon=True).start()
        threading.Thread(target=self._tcp_server_thread, daemon=True).start()

    def _broadcast_thread(self):
        """UDP broadcast for discovery."""
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        msg = f"GAME_HOST:{self.tcp_port}".encode()
        while self.running:
            udp.sendto(msg, ('<broadcast>', self.udp_port))
            time.sleep(self.broadcast_interval)

    def _tcp_server_thread(self):
        """Accept clients."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.tcp_port))
        self.server_socket.listen()
        print("[HOST] Listening for clients...")
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                player_id = f"client{len(self.clients)+1}"
                print(f"[HOST] {player_id} connected from {addr}")
                self.clients.append((conn, player_id))
                # Create player entry
                self.players[player_id] = {
                    "pos": [random.randint(150, WIDTH-100), random.randint(150, HEIGHT-100)],
                    "color": (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)),
                    "name": player_id
                }
                # Tell this client its ID
                send_packet(conn, {"assign_id": player_id})
                # Start thread for that client
                threading.Thread(target=self._handle_client, args=(conn, player_id), daemon=True).start()
                self._broadcast_all()
            except Exception as e:
                print("[HOST] Error accepting:", e)
                break

    def _handle_client(self, conn, player_id):
        """Handle a connected client."""
        while self.running:
            try:
                data = recv_packet(conn)
                if data is None:
                    break
                if "pos" in data:
                    self.players[player_id]["pos"] = data["pos"]
                if "color" in data:
                    self.players[player_id]["color"] = data["color"]
                self._broadcast_all()
            except:
                break
        print(f"[HOST] {player_id} disconnected.")
        if player_id in self.players:
            del self.players[player_id]
        conn.close()
        self.clients = [(c, pid) for c, pid in self.clients if pid != player_id]
        self._broadcast_all()

    def _broadcast_all(self):
        """Send all players to every client."""
        dead = []
        for conn, _ in self.clients:
            try:
                send_packet(conn, {"players": self.players})
            except:
                dead.append(conn)
        for conn in dead:
            self.clients = [(c, pid) for c, pid in self.clients if c != conn]
            conn.close()

    def stop(self):
        self.running = False
        for c, _ in self.clients:
            c.close()
        if self.server_socket:
            self.server_socket.close()
        print("[HOST] Server stopped")

# -------------------- CLIENT --------------------
class LANClient:
    def __init__(self, udp_port=5001):
        self.udp_port = udp_port
        self.found_host = None
        self.client_socket = None
        self.players = {}
        self.my_id = None
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    def start(self):
        threading.Thread(target=self._discover_thread, daemon=True).start()
        while self.found_host is None:
            time.sleep(0.1)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.found_host)
        print(f"[CLIENT] Connected to host at {self.found_host}")
        threading.Thread(target=self._receive_thread, daemon=True).start()

    def _discover_thread(self):
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp.bind(('', self.udp_port))
        while True:
            data, addr = udp.recvfrom(1024)
            msg = data.decode()
            if msg.startswith("GAME_HOST"):
                _, port = msg.split(":")
                self.found_host = (addr[0], int(port))
                print(f"[CLIENT] Found host at {addr[0]}:{port}")
                break

    def _receive_thread(self):
        while True:
            try:
                packet = recv_packet(self.client_socket)
                if not packet:
                    break
                # If host assigns an ID
                if "assign_id" in packet:
                    self.my_id = packet["assign_id"]
                    print(f"[CLIENT] Assigned ID: {self.my_id}")
                # If host sends world data
                elif "players" in packet:
                    self.players = packet["players"]
            except:
                break

    def send_pos(self, pos):
        """Send movement update."""
        if not self.my_id:
            return
        try:
            send_packet(self.client_socket, {
                "pos": pos,
                "color": self.color
            })
        except:
            pass

    def stop(self):
        if self.client_socket:
            self.client_socket.close()
            print("[CLIENT] Disconnected")

# -------------------- GAME LOOP --------------------
def main():
    clock = pygame.time.Clock()
    mode = None
    host = None
    client = None

    # --- MENU ---
    while True:
        WIN.fill((30, 30, 30))
        host_text = FONT.render("Host Game", True, (255, 255, 255))
        join_text = FONT.render("Join Game", True, (255, 255, 255))
        WIN.blit(host_text, (WIDTH//2 - host_text.get_width()//2, HEIGHT//2 - 50))
        WIN.blit(join_text, (WIDTH//2 - join_text.get_width()//2, HEIGHT//2 + 50))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if HEIGHT//2 - 50 < y < HEIGHT//2:
                    mode = "host"; host = LANHost(); host.start(); break
                elif HEIGHT//2 + 50 < y < HEIGHT//2 + 100:
                    mode = "client"; client = LANClient(); client.start(); break
        if mode:
            break

    move_speed = 5

    # --- GAMEPLAY ---
    while True:
        clock.tick(FPS)
        WIN.fill((50, 50, 100))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if host: host.stop()
                if client: client.stop()
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()

        # Host control
        if mode == "host":
            player = host.players["host"]
            moved = False
            if keys[pygame.K_w]: player["pos"][1] -= move_speed; moved = True
            if keys[pygame.K_s]: player["pos"][1] += move_speed; moved = True
            if keys[pygame.K_a]: player["pos"][0] -= move_speed; moved = True
            if keys[pygame.K_d]: player["pos"][0] += move_speed; moved = True
            if moved:
                host._broadcast_all()

        # Client control
        if mode == "client" and client.my_id in client.players:
            my_player = client.players[client.my_id]
            moved = False
            if keys[pygame.K_UP]: my_player["pos"][1] -= move_speed; moved = True
            if keys[pygame.K_DOWN]: my_player["pos"][1] += move_speed; moved = True
            if keys[pygame.K_LEFT]: my_player["pos"][0] -= move_speed; moved = True
            if keys[pygame.K_RIGHT]: my_player["pos"][0] += move_speed; moved = True
            if moved:
                client.send_pos(my_player["pos"])

        # Draw all players
        players = host.players if mode == "host" else client.players
        for pid, pdata in players.items():
            color = pdata.get("color", (255, 255, 255))
            pygame.draw.circle(WIN, color, pdata["pos"], 20)
            name_text = FONT.render(pdata.get("name", pid), True, (255, 255, 255))
            WIN.blit(name_text, (pdata["pos"][0] - name_text.get_width() // 2, pdata["pos"][1] - 35))

        pygame.display.update()

if __name__ == "__main__":
    main()
