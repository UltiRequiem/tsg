import json
import os
import random
import sys
import time

from .assets import assets

# Must be set before importing Pygame
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
import pygame.locals


TITLE = "Typing speed test"


class Game:
    def __init__(self):
        self.width = 750
        self.height = 500

        self.reset = True
        self.active = False

        self.input_text = ""
        self.word = ""

        self.time_start = 0
        self.total_time = 0

        self.accuracy = "0%"
        self.results = "Time:0 Accuracy:0 % Wpm:0 "

        self.wpm = 0

        self.end = False

        self.HEAD_C = (255, 213, 102)
        self.TEXT_C = (240, 240, 240)
        self.RESULT_C = (255, 70, 70)

        pygame.init()

        self.cover = pygame.image.load(assets["cover"])
        self.cover = pygame.transform.scale(self.cover, (self.width, self.height))

        self.background = pygame.image.load(assets["background"])
        self.background = pygame.transform.scale(self.background, (self.width, self.height))

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(TITLE)

    def draw_text(self, screen, msg, y, fsize, color):
        font = pygame.font.Font(None, fsize)
        text = font.render(msg, True, color)
        text_rect = text.get_rect(center=(self.width / 2, y))
        screen.blit(text, text_rect)
        pygame.display.update()

    def get_sentence(self):
        with open(assets["sentences"]) as file:
            data = json.loads(file.read())
            return random.choice(data)

    def format_results(self,total_time:float, accuracy:float, wpm:float):
        return f"Time: {round(total_time)} seconds - Accuracy: {round(accuracy)} - WPM: {round(wpm)}"

    def show_results(self, screen):
        if not self.end:
            self.total_time = time.time() - self.time_start

            count = 0

            for index, char in enumerate(self.word):
                try:
                    if self.input_text[index] == char:
                        count += 1
                except:
                    pass
            self.accuracy = count / len(self.word) * 100

            self.wpm = len(self.input_text) * 60 / (5 * self.total_time)
            self.end = True

            self.results =  self.format_results(self.total_time, self.accuracy,self.wpm)

            self.time_img = pygame.image.load(assets["icon"])
            self.time_img = pygame.transform.scale(self.time_img, (150, 150))

            screen.blit(self.time_img, (self.width / 2 - 75, self.height - 140))
            self.draw_text(screen, "Reset", self.height - 70, 26, (100, 100, 100))

            pygame.display.update()

    def run(self):
        self.reset_game()

        self.running = True

        while self.running:
            clock = pygame.time.Clock()
            self.screen.fill((0, 0, 0), (50, 250, 650, 50))
            pygame.draw.rect(self.screen, self.HEAD_C, (50, 250, 650, 50), 2)

            self.draw_text(self.screen, self.input_text, 274, 26, (250, 250, 250))

            pygame.display.update()

            for event in pygame.event.get():
                # User closes the game
                if event.type == pygame.locals.QUIT:
                    self.running = False
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONUP:
                    x, y = pygame.mouse.get_pos()

                    # User starts writing
                    if x >= 50 and x <= 650 and y >= 250 and y <= 300:
                        self.active = True
                        self.input_text = ""
                        self.time_start = time.time()

                    if x >= 310 and x <= 510 and y >= 390 and self.end:
                        self.reset_game()
                        x, y = pygame.mouse.get_pos()

                elif event.type == pygame.KEYDOWN:
                    if self.active and not self.end:
                        if event.key == pygame.K_RETURN:
                            self.show_results(self.screen)

                            self.draw_text(
                                self.screen, self.results, 350, 28, self.RESULT_C
                            )

                            self.end = True

                        elif event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                        else:
                            try:
                                self.input_text += event.unicode
                            except:
                                pass

            pygame.display.update()

            clock.tick(60)

    def reset_game(self):
        self.screen.blit(self.cover, (0, 0))

        pygame.display.update()
        time.sleep(0.5)

        self.reset = False
        self.end = False

        self.input_text = ""
        self.word = ""
        self.time_start = 0
        self.total_time = 0
        self.wpm = 0

        self.word = self.get_sentence()

        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))

        msg = TITLE

        self.draw_text(self.screen, msg, 80, 80, self.HEAD_C)
        pygame.draw.rect(self.screen, (255, 192, 25), (50, 250, 650, 50), 2)
        self.draw_text(self.screen, self.word, 200, 28, self.TEXT_C)
        pygame.display.update()


def main():

    game = Game()

    game.run()


main()
