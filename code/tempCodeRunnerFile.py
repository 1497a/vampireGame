from settings import *
from player import Player
from menu import Menu
        
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites

from random import randint, choice
class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Survivor')
        self.clock = pygame.time.Clock()
        self.running = True
        self.menu = Menu(self)
        self.menu.run()  # Chạy menu trước khi bắt đầu trò chơi
        # groups 
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        
        # gun timer
        self.can_shoot = True
        self.shoot_time = 0 
        self.gun_cooldown = 100  # thời gian hồi giữa mỗi lần bắn

        # count hit
        self.hit_count = 0  # Bộ đếm số lần trúng của bulle
        # tự động bắn
        self.auto_shoot_timer = 0  # Bộ đếm thời gian cho việc bắn tự động
        self.auto_shoot_interval = 800  # Tần suất bắn (ms)

        # enemy timer a
        self.enemy_event = pygame.event.custom_type()
        self.enemy_spawn_rate = 500  # Thời gian giữa mỗi lần sinh quái (ms)
        pygame.time.set_timer(self.enemy_event, 500)
        self.spawn_positions = []

        # audio 
        self.shoot_sound = pygame.mixer.Sound(join('audio', 'shoot.wav'))
        self.shoot_sound.set_volume(0.2)
        self.impact_sound = pygame.mixer.Sound(join('audio', 'impact.ogg'))
        self.music = pygame.mixer.Sound(join('audio', 'music.wav'))
        self.music.set_volume(0.5)
        # self.music.play(loops = -1)

        # setup
        self.load_images()
        self.setup()
        # trạng thái game
        self.game_over = False
        self.start_time = pygame.time.get_ticks()  # Lưu thời gian bắt đầu
        self.elapsed_time = 0  # Thời gian đã trôi qua
    def load_images(self):
        self.bullet_surf = pygame.image.load(join('images', 'gun', 'bullet.png')).convert_alpha()

        folders = list(walk(join('images', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('images', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)

    def auto_shoot(self):
        if self.game_over:  # Nếu game kết thúc, không bắn tự động
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.auto_shoot_timer >= self.auto_shoot_interval and self.can_shoot:
            self.shoot_sound.play()
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
            self.auto_shoot_timer = current_time

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def setup(self):
        map = load_pygame(join('data', 'maps', 'world.tmx'))

        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        
        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)

        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()
                    self.hit_count += len(collision_sprites)
                    for sprite in collision_sprites:
                        sprite.destroy()
                    bullet.kill()
                    if self.hit_count % 10 == 0:  # Cứ mỗi 10 quái bị giết
                        self.auto_shoot_interval = max(10, self.auto_shoot_interval -20)  # Giảm đến tối đa 200ms

    def player_collision(self):
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.game_over = True  # Khi va chạm, đặt game_over thành True
    def restart_game(self):
        if self.game_over:
            self.game_over = False
            self.auto_shoot_interval =600
            self.enemy_spawn_rate = 600  # Thời gian giữa mỗi lần sinh quái (ms)
            pygame.time.set_timer(self.enemy_event, 600)
            self.hit_count = 0  
            self.all_sprites.empty()
            self.collision_sprites.empty()
            self.bullet_sprites.empty()
            self.enemy_sprites.empty()
            self.start_time = pygame.time.get_ticks()
            self.setup()
    def run(self):
        while self.running:
            # dt 
            dt = self.clock.tick() / 1000
        
            if not self.game_over:
                        self.elapsed_time = pygame.time.get_ticks() - self.start_time
            # Tính số phút đã trôi qua
            minutes = self.elapsed_time // 60000

            if minutes > 0 and self.elapsed_time // 60000 == minutes:
            # Tăng tốc độ sinh quái sau mỗi phút
                self.enemy_spawn_rate = max(10, self.enemy_spawn_rate - 30)  # Đảm bảo tốc độ không quá thấp
                pygame.time.set_timer(self.enemy_event, self.enemy_spawn_rate)
    
            # event loop 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    # Xác định vùng camera
                    camera_rect = pygame.Rect(
                        self.player.rect.centerx - WINDOW_WIDTH // 2,
                        self.player.rect.centery - WINDOW_HEIGHT // 2,
                        WINDOW_WIDTH,
                        WINDOW_HEIGHT
                    )
                    
                    # Chọn vị trí spawn ngoài camera
                    valid_spawn_positions = [
                        pos for pos in self.spawn_positions if not camera_rect.collidepoint(pos)
                    ]
                    
                    # Nếu có vị trí spawn hợp lệ, tạo quái
                    if valid_spawn_positions:
                        spawn_position = choice(valid_spawn_positions)
                        Enemy(
                            spawn_position,
                            choice(list(self.enemy_frames.values())),
                            (self.all_sprites, self.enemy_sprites),
                            self.player,
                            self.collision_sprites
                        )
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Nhấn 'R' để chơi lại
                        self.restart_game()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:  # Thoát game
                        pygame.quit()
            # update 
           
            if not self.game_over:
                self.gun_timer()
                self.auto_shoot()  # Kích hoạt tự động bắn
                self.all_sprites.update(dt)
                self.bullet_collision()
                self.player_collision()
            # self.all_sprites.update(dt)
            # self.bullet_collision()
            # self.player_collision()


            # draw
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            self.display_time_and_hits()
            if self.game_over:
                self.display_game_over()  # Hiển thị màn hình kết thúc
            pygame.display.update()

        pygame.quit()
    def display_game_over(self):
        # Hiển thị màn hình kết thúc
        font = pygame.font.Font(None, 74)
        text = font.render('Game Over', True, (255, 0, 0))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.display_surface.blit(text, text_rect)

        restart_text = font.render('Press R to Restart', True, (255, 255, 255))
        restart_text_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.display_surface.blit(restart_text, restart_text_rect)

        # Thêm dòng "Press X to Exit"
        exit_text = font.render('Press X to Exit', True, (255, 255, 255))
        exit_text_rect = exit_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 120))
        self.display_surface.blit(exit_text, exit_text_rect)
    def display_time_and_hits(self):
        font = pygame.font.Font(None, 36)

        # Hiển thị thời gian
        time_text = font.render(f"Time: {self.elapsed_time // 1000}s", True, (255, 255, 255))
        self.display_surface.blit(time_text, (10, 10))

        # Hiển thị số lần trúng quái
        hit_count_text = font.render(f"Hits: {self.hit_count}", True, (255, 255, 255))
        self.display_surface.blit(hit_count_text, (10, 50))  # Hiển thị ngay bên dưới thời gian

if __name__ == '__main__':
    game = Game()
    game.run()
