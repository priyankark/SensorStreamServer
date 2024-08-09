import asyncio
import websockets
import socket
import json
import pygame
import random

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

class DinoGame:
    def __init__(self, width=800, height=400):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Dino Light Sensor Game")

        self.dino_rect = pygame.Rect(50, self.height - 100, 40, 60)
        self.dino_y = self.height - 100
        self.dino_velocity = 0
        self.jump_strength = -15
        self.gravity = 0.8

        self.obstacles = []
        self.obstacle_speed = 5
        self.obstacle_frequency = 1500  # milliseconds
        self.last_obstacle = pygame.time.get_ticks()

        self.score = 0
        self.font = pygame.font.Font(None, 36)

        self.game_over = False
        self.game_started = False

        self.light_levels = []
        self.max_light_history = 10
        self.change_threshold = 5.0  # Adjusted for illuminance values

    def create_obstacle(self):
        obstacle = pygame.Rect(self.width, self.height - 60, 30, 60)
        return obstacle

    def move_obstacles(self):
        for obstacle in self.obstacles:
            obstacle.x -= self.obstacle_speed
        self.obstacles = [obs for obs in self.obstacles if obs.right > 0]

    def check_collision(self):
        for obstacle in self.obstacles:
            if self.dino_rect.colliderect(obstacle):
                return True
        return False

    def update_score(self):
        self.score += 1

    def reset_game(self):
        self.dino_rect.y = self.height - 100
        self.dino_y = self.height - 100
        self.dino_velocity = 0
        self.obstacles.clear()
        self.score = 0
        self.game_over = False
        self.game_started = False
        self.light_levels.clear()

    def update(self):
        if not self.game_over and self.game_started:
            self.dino_velocity += self.gravity
            self.dino_y += self.dino_velocity
            self.dino_rect.y = int(self.dino_y)

            if self.dino_rect.bottom > self.height - 40:
                self.dino_rect.bottom = self.height - 40
                self.dino_y = self.dino_rect.y
                self.dino_velocity = 0

            self.move_obstacles()
            current_time = pygame.time.get_ticks()
            if current_time - self.last_obstacle > self.obstacle_frequency:
                self.obstacles.append(self.create_obstacle())
                self.last_obstacle = current_time

            self.update_score()

            if self.check_collision():
                self.game_over = True

    def draw(self):
        self.screen.fill((255, 255, 255))  # White background

        pygame.draw.rect(self.screen, (100, 100, 100), self.dino_rect)  # Gray dinosaur

        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, (0, 0, 0), obstacle)  # Black obstacles

        pygame.draw.line(self.screen, (0, 0, 0), (0, self.height - 40), (self.width, self.height - 40), 2)  # Ground line

        score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))

        if self.game_over:
            game_over_text = self.font.render("Game Over! Press SPACE to restart", True, (255, 0, 0))
            self.screen.blit(game_over_text, (self.width // 2 - 180, self.height // 2))
        elif not self.game_started:
            start_text = self.font.render("Change light level to start", True, (0, 0, 0))
            self.screen.blit(start_text, (self.width // 2 - 120, self.height // 2))

        pygame.display.flip()

    def control_dino(self, illuminance):
        self.light_levels.append(illuminance)
        if len(self.light_levels) > self.max_light_history:
            self.light_levels.pop(0)

        if len(self.light_levels) < 2:
            return

        recent_change = abs(self.light_levels[-1] - self.light_levels[-2])

        if not self.game_started:
            if recent_change > self.change_threshold:
                self.game_started = True
        
        if not self.game_over and self.game_started:
            if recent_change > self.change_threshold and self.dino_rect.bottom >= self.height - 40:
                self.dino_velocity = self.jump_strength

class LightSensorServer:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.ip_addr = get_ip()
        self.port = 8989
        self.game = DinoGame()

    async def handle_light_sensor(self, websocket, path):
        print(f"New connection from {websocket.remote_address}")
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    print(f"Received light sensor data: {data}")
                    
                    illuminance = float(data.get('illuminance', 0))
                    self.game.control_dino(illuminance)
                    
                except json.JSONDecodeError:
                    print(f"Error parsing JSON data: {message}")
        except websockets.exceptions.ConnectionClosed:
            print(f"Connection closed for {websocket.remote_address}")

    async def run_game(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if self.game.game_over:
                        self.game.reset_game()

            self.game.update()
            self.game.draw()
            clock.tick(60)
            await asyncio.sleep(0)

    async def main(self):
        print(f"Your Computer Name is: {self.hostname}")
        print(f"Your Computer IP Address is: {self.ip_addr}")
        print(f"* Enter {self.ip_addr}:{self.port} in the app.")
        print("* Press the 'Set IP Address' button.")
        print("* Select the light sensor to stream.")
        print("* Update the 'update interval' by entering a value in ms.")

        server = await websockets.serve(
            self.handle_light_sensor, 
            '0.0.0.0', 
            self.port, 
            max_size=1_000_000_000
        )
        game_task = asyncio.create_task(self.run_game())

        await asyncio.gather(server.wait_closed(), game_task)

if __name__ == "__main__":
    server = LightSensorServer()
    try:
        asyncio.run(server.main())
    except KeyboardInterrupt:
        print("Shutting down server...")
        pygame.quit()