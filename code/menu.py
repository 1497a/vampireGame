import pygame
import sys
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

class Menu:
    def __init__(self, game):
        self.display_surface = pygame.display.get_surface()
        self.game = game
        self.font = pygame.font.Font(None, 74)  # Font mặc định, có thể thay đổi

        # Màu sắc
        self.bg_color = (0, 0, 0)  # Màu nền đen
        self.text_color = (255, 255, 255)  # Màu chữ trắng

        # Các nút menu
        self.play_button = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50, 200, 50)
        self.quit_button = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 20, 200, 50)

    def run(self):
        # Vòng lặp màn hình menu
        while True:
            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_button.collidepoint(event.pos):
                        return  # Thoát khỏi menu và bắt đầu trò chơi
                    elif self.quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

            # Vẽ nền
            self.display_surface.fill(self.bg_color)

            # Vẽ các nút và chữ
            self.draw_text('Survivor Game', WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 150, self.font, self.text_color)
            self.draw_button(self.play_button, "Play")
            self.draw_button(self.quit_button, "Quit")

            # Cập nhật màn hình
            pygame.display.flip()

    def draw_text(self, text, x, y, font, color):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.display_surface.blit(text_surface, text_rect)

    def draw_button(self, rect, text):
        pygame.draw.rect(self.display_surface, (0, 128, 0), rect)  # Vẽ nút màu xanh lá cây
        font = pygame.font.Font(None, 50)
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        self.display_surface.blit(text_surface, text_rect)
