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

class FlappyBird:
    def __init__(self, width=400, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Flappy Bird - Accelerometer Control")

        self.bird_y = height // 2
        self.bird_velocity = 0
        self.bird_rect = pygame.Rect(50, self.bird_y, 40, 40)

        self.pipes = []
        self.pipe_speed = 2
        self.pipe_frequency = 1500  # milliseconds
        self.last_pipe = pygame.time.get_ticks() + 2000  # Delay first pipe by 2 seconds

        self.score = 0
        self.font = pygame.font.Font(None, 36)

        self.game_over = False
        self.game_started = False

        self.jump_strength = -7  # Strength of the jump
        self.gravity = 0.4  # Gravity effect

    def create_pipe(self):
        gap = 200
        pipe_height = random.randint(100, self.height - gap - 100)
        bottom_pipe = pygame.Rect(self.width, pipe_height, 50, self.height - pipe_height)
        top_pipe = pygame.Rect(self.width, 0, 50, pipe_height - gap)
        return [bottom_pipe, top_pipe]

    def move_pipes(self):
        for pipe_pair in self.pipes:
            pipe_pair[0].x -= self.pipe_speed
            pipe_pair[1].x -= self.pipe_speed
        self.pipes = [pipe for pipe in self.pipes if pipe[0].right > 0]

    def check_collision(self):
        for pipe_pair in self.pipes:
            if self.bird_rect.colliderect(pipe_pair[0]) or self.bird_rect.colliderect(pipe_pair[1]):
                return True
        if self.bird_rect.top <= 0 or self.bird_rect.bottom >= self.height:
            return True
        return False

    def update_score(self):
        for pipe_pair in self.pipes:
            if 48 <= pipe_pair[0].x <= 52:
                self.score += 1

    def reset_game(self):
        self.bird_y = self.height // 2
        self.bird_velocity = 0
        self.bird_rect.y = self.bird_y
        self.pipes.clear()
        self.score = 0
        self.game_over = False
        self.game_started = False
        self.last_pipe = pygame.time.get_ticks() + 2000

    def update(self):
        if not self.game_over and self.game_started:
            # Apply gravity
            self.bird_velocity += self.gravity
            self.bird_y += self.bird_velocity
            self.bird_rect.y = int(self.bird_y)

            self.move_pipes()
            current_time = pygame.time.get_ticks()
            if current_time - self.last_pipe > self.pipe_frequency:
                self.pipes.append(self.create_pipe())
                self.last_pipe = current_time

            self.update_score()

            if self.check_collision():
                self.game_over = True

    def draw(self):
        self.screen.fill((135, 206, 250))  # Sky blue background

        for pipe in self.pipes:
            pygame.draw.rect(self.screen, (0, 255, 0), pipe[0])
            pygame.draw.rect(self.screen, (0, 255, 0), pipe[1])

        pygame.draw.rect(self.screen, (255, 255, 0), self.bird_rect)

        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        if self.game_over:
            game_over_text = self.font.render("Game Over! Press SPACE to restart", True, (255, 255, 255))
            self.screen.blit(game_over_text, (self.width // 2 - 180, self.height // 2))
        elif not self.game_started:
            start_text = self.font.render("Tilt to Start", True, (255, 255, 255))
            self.screen.blit(start_text, (self.width // 2 - 70, self.height // 2))

        pygame.display.flip()

    def control_bird(self, acceleration):
        if not self.game_started:
            if abs(acceleration) > 1:  # Start the game if there's significant tilt
                self.game_started = True
        
        if not self.game_over and self.game_started:
            # Jump when there's a significant positive z-acceleration (tilting left)
            if acceleration > 2:  # You can adjust this threshold
                self.bird_velocity = self.jump_strength

class AccelerometerServer:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.ip_addr = get_ip()
        self.port = 8989
        self.game = FlappyBird()

    async def handle_accelerometer(self, websocket, path):
        print(f"New connection from {websocket.remote_address}")
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    print(f"Received accelerometer data: {data}")
                    
                    # Use 'z' axis for jump control
                    acceleration = float(data.get('z', 0))
                    self.game.control_bird(acceleration)
                    
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
        print("* Select the accelerometer to stream.")
        print("* Update the 'update interval' by entering a value in ms.")

        server = await websockets.serve(
            self.handle_accelerometer, 
            '0.0.0.0', 
            self.port, 
            max_size=1_000_000_000
        )
        game_task = asyncio.create_task(self.run_game())

        await asyncio.gather(server.wait_closed(), game_task)

if __name__ == "__main__":
    server = AccelerometerServer()
    try:
        asyncio.run(server.main())
    except KeyboardInterrupt:
        print("Shutting down server...")
        pygame.quit()