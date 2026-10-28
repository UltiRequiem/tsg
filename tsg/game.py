"""The pygame window."""

from __future__ import annotations

import os
import time
from collections.abc import Sequence

# Must be set before importing pygame
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "hide")

import pygame  # noqa: E402

from .assets import assets  # noqa: E402
from .core import Session, pick_sentence  # noqa: E402

TITLE = "Typing speed test"

WIDTH, HEIGHT = 750, 500
INPUT_BOX = pygame.Rect(50, 250, 650, 50)
RESET_BOX = pygame.Rect(310, 390, 200, 110)

HEAD_COLOR = (255, 213, 102)
TEXT_COLOR = (240, 240, 240)
HINT_COLOR = (170, 170, 170)
RESULT_COLOR = (255, 70, 70)
WRONG_COLOR = (255, 90, 90)


class Game:
    def __init__(self, sentences: Sequence[str]) -> None:
        self.sentences = sentences

        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        self.background = self._load("background", (WIDTH, HEIGHT))
        self.reset_icon = self._load("icon", (150, 150))
        self.fonts: dict[int, pygame.font.Font] = {}

        self.session = Session(pick_sentence(sentences))
        self.running = False

    @staticmethod
    def _load(name: str, size: tuple[int, int]) -> pygame.Surface:
        return pygame.transform.smoothscale(pygame.image.load(assets[name]).convert(), size)

    def font(self, size: int) -> pygame.font.Font:
        if size not in self.fonts:
            self.fonts[size] = pygame.font.Font(None, size)
        return self.fonts[size]

    def draw_text(self, message: str, y: int, size: int, color: tuple[int, int, int]) -> None:
        text = self.font(size).render(message, True, color)
        self.screen.blit(text, text.get_rect(center=(WIDTH // 2, y)))

    def visible_typed_text(self) -> str:
        """The tail of what you typed, so a long line never leaves the box."""
        text = self.session.typed
        while text and self.font(26).size(text)[0] > INPUT_BOX.width - 20:
            text = text[1:]
        return text

    def render(self) -> None:
        session = self.session
        self.screen.blit(self.background, (0, 0))
        self.draw_text(TITLE, 80, 80, HEAD_COLOR)
        self.draw_text(session.target, 200, 28, TEXT_COLOR)

        self.screen.fill((0, 0, 0), INPUT_BOX)
        pygame.draw.rect(self.screen, HEAD_COLOR, INPUT_BOX, 2)
        self.draw_text(self.visible_typed_text(), INPUT_BOX.centery, 26, (250, 250, 250))

        if session.result:
            self.draw_text(str(session.result), 335, 28, RESULT_COLOR)
            self.screen.blit(self.reset_icon, (WIDTH // 2 - 75, HEIGHT - 140))
            self.draw_text("Reset", HEIGHT - 70, 26, (100, 100, 100))
        elif not session.active:
            self.draw_text("Start typing, press Enter when you are done", 350, 26, HINT_COLOR)
        else:
            self.draw_text("Enter: finish   Tab: new sentence   Esc: quit", 350, 22, HINT_COLOR)

    def new_round(self) -> None:
        self.session = Session(pick_sentence(self.sentences))

    def handle(self, event: pygame.event.Event) -> None:
        session = self.session
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            if session.finished and RESET_BOX.collidepoint(event.pos):
                self.new_round()
            elif INPUT_BOX.collidepoint(event.pos) and not session.finished:
                session.start(time.time())
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_TAB:
                self.new_round()
            elif session.finished:
                return
            elif event.key == pygame.K_RETURN:
                session.finish(time.time())
            elif event.key == pygame.K_BACKSPACE:
                session.backspace()
            elif event.unicode and event.unicode.isprintable():
                if not session.active:
                    session.start(time.time())
                session.type(event.unicode)

    def run(self) -> None:
        clock = pygame.time.Clock()
        self.running = True
        while self.running:
            for event in pygame.event.get():
                self.handle(event)
            self.render()
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()
