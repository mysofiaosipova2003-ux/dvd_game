from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle, Ellipse, Line, RoundedRectangle
from kivy.core.text import Label as CoreLabel
from kivy.clock import Clock
from kivy.core.window import Window
import math
import random
import json
import os
from datetime import datetime

# Константы (базовые размеры)
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
BOX_SIZE = 100
INITIAL_SPEED = 4.0
CORNER_DANGER_ZONE = 70
UPDATE_INTERVAL = 1/60  # 60 FPS

# Цвета (в формате 0-1) - только базовые
COLORS = [
    (1, 0, 0, 1),      # Красный
    (0, 1, 0, 1),      # Зелёный
    (0, 0, 1, 1),      # Синий
    (1, 1, 0, 1),      # Жёлтый
]

BG_CANVAS = (0.1, 0.1, 0.1, 1)
LINE_COLOR = (0.2, 0.2, 0.2, 1)
BORDER_COLOR = (1, 1, 1, 1)
DANGER_RED = (1, 0, 0, 0.3)
DANGER_GRAY = (0.5, 0.5, 0.5, 0.2)

# Цвета UI
AMBER_BG = (254/255, 243/255, 199/255, 1)
GRAY_DARK = (74/255, 74/255, 74/255, 1)
WHITE = (1, 1, 1, 1)
TV_FRAME_COLOR = (0.2, 0.2, 0.2, 1)
TV_SCREEN_COLOR = (0.15, 0.15, 0.15, 1)

# Персонажи (The Office) без смайликов
CHARACTERS = [
    "Майкл Скотт",
    "Дуайт Шрут",
    "Джим Халперт",
    "Пэм Бисли",
    "Райан Ховард",
    "Энди Бернард",
    "Кевин Малоун",
    "Анджела Мартин"
]

# Цвета персонажей (RGB 0-1)
CHARACTER_COLORS = {
    "Майкл Скотт": (0.2, 0.4, 0.8, 1),      # Синий
    "Дуайт Шрут": (0.6, 0.4, 0.2, 1),       # Коричневый
    "Джим Халперт": (0.2, 0.7, 0.3, 1),     # Зелёный
    "Пэм Бисли": (0.9, 0.4, 0.5, 1),        # Розовый
    "Райан Ховард": (0.6, 0.3, 0.7, 1),     # Фиолетовый
    "Энди Бернард": (0.9, 0.7, 0.2, 1),     # Жёлтый
    "Кевин Малоун": (0.9, 0.5, 0.2, 1),     # Оранжевый
    "Анджела Мартин": (0.5, 0.5, 0.5, 1)    # Серый
}

def get_scale():
    """Получить коэффициент масштабирования под размер экрана"""
    # Определяем ориентацию
    is_portrait = Window.height > Window.width
    
    if is_portrait:
        # Портретная ориентация - базовая ширина 1080px (Full HD портрет)
        base_width = 1080
        scale = Window.width / base_width
    else:
        # Ландшафтная ориентация - базовая ширина 1920px (Full HD ландшафт)
        base_width = 1920
        scale = Window.width / base_width
    
    # Ограничиваем масштаб от 0.7 до 1.3
    return max(0.7, min(scale, 1.3))

def sp(size):
    """Масштабируемые пиксели для размеров шрифта"""
    return int(size * get_scale())

def dp(size):
    """Масштабируемые пиксели для размеров элементов"""
    return int(size * get_scale())

class GameView(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Состояние квадрата
        self.box_x = (CANVAS_WIDTH - BOX_SIZE) / 2.0
        self.box_y = (CANVAS_HEIGHT - BOX_SIZE) / 2.0
        self.velocity_x = INITIAL_SPEED
        self.velocity_y = INITIAL_SPEED
        self.box_color_index = 0
        
        # Игровое состояние
        self.playing = False
        self.paused = False
        self.start_time = 0
        self.current_score = 0
        
        # Game loop
        self.game_loop_event = None
        
    def start(self):
        """Старт игры"""
        self.playing = True
        self.paused = False
        self.start_time = datetime.now()
        self.current_score = 0
        
        # Случайное направление
        angle = random.uniform(0, 2 * math.pi)
        self.velocity_x = math.cos(angle) * INITIAL_SPEED
        self.velocity_y = math.sin(angle) * INITIAL_SPEED
        
        # Центр экрана
        self.box_x = (CANVAS_WIDTH - BOX_SIZE) / 2.0
        self.box_y = (CANVAS_HEIGHT - BOX_SIZE) / 2.0
        
        self.box_color_index = random.randint(0, len(COLORS) - 1)
        
        # Запуск game loop
        self.game_loop_event = Clock.schedule_interval(self.update_game, UPDATE_INTERVAL)
        
        self.render()
    
    def pause(self):
        """Пауза"""
        self.paused = not self.paused
    
    def stop(self):
        """Стоп игры"""
        self.playing = False
        self.paused = False
        if self.game_loop_event:
            self.game_loop_event.cancel()
            self.game_loop_event = None
    
    def get_score(self):
        """Получить текущий счет (секунды)"""
        if not self.playing:
            return self.current_score
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed
    
    def is_running(self):
        """Проверка, идет ли игра"""
        return self.playing and not self.paused
    
    def check_corner_collision(self):
        """Проверка столкновения с углами"""
        box_center_x = self.box_x + BOX_SIZE / 2.0
        box_center_y = self.box_y + BOX_SIZE / 2.0
        
        corners = [
            (0, 0),
            (CANVAS_WIDTH, 0),
            (0, CANVAS_HEIGHT),
            (CANVAS_WIDTH, CANVAS_HEIGHT)
        ]
        
        for corner_x, corner_y in corners:
            distance = math.sqrt(
                (box_center_x - corner_x) ** 2 + 
                (box_center_y - corner_y) ** 2
            )
            if distance < CORNER_DANGER_ZONE:
                return True
        
        return False
    
    def update_game(self, dt):
        """Обновление состояния игры"""
        if not self.playing:
            return
        
        if not self.paused:
            # Движение квадрата
            self.box_x += self.velocity_x
            self.box_y += self.velocity_y
            
            color_changed = False
            
            # Отскок от стен
            if self.box_x <= 0 or self.box_x + BOX_SIZE >= CANVAS_WIDTH:
                self.velocity_x *= -1
                self.box_x = max(0, min(self.box_x, CANVAS_WIDTH - BOX_SIZE))
                self.box_color_index = random.randint(0, len(COLORS) - 1)
                color_changed = True
            
            if self.box_y <= 0 or self.box_y + BOX_SIZE >= CANVAS_HEIGHT:
                self.velocity_y *= -1
                self.box_y = max(0, min(self.box_y, CANVAS_HEIGHT - BOX_SIZE))
                if not color_changed:
                    self.box_color_index = random.randint(0, len(COLORS) - 1)
            
            # Проверка столкновения с углами
            if self.check_corner_collision():
                self.current_score = self.get_score()
                self.stop()
                App.get_running_app().game_over(self.current_score)
                return
        
        # Обновить счет
        score = self.get_score()
        App.get_running_app().update_score(score)
        
        # Отрисовка
        self.render()
    
    def render(self):
        """Отрисовка игры"""
        if not self.playing and self.current_score == 0:
            return
        
        self.canvas.clear()
        
        with self.canvas:
            # Фон canvas
            Color(*BG_CANVAS)
            Rectangle(pos=self.pos, size=self.size)
            
            # Линии текстуры
            Color(*LINE_COLOR)
            for i in range(0, int(CANVAS_HEIGHT), 30):
                Line(points=[self.pos[0], self.pos[1] + i, 
                           self.pos[0] + CANVAS_WIDTH, self.pos[1] + i], width=1)
            
            # Углы опасности
            box_center_x = self.box_x + BOX_SIZE / 2.0
            box_center_y = self.box_y + BOX_SIZE / 2.0
            
            corners = [
                (0, 0),
                (CANVAS_WIDTH, 0),
                (0, CANVAS_HEIGHT),
                (CANVAS_WIDTH, CANVAS_HEIGHT)
            ]
            
            for corner_x, corner_y in corners:
                distance = math.sqrt(
                    (box_center_x - corner_x) ** 2 + 
                    (box_center_y - corner_y) ** 2
                )
                is_dangerous = distance < CORNER_DANGER_ZONE
                
                if is_dangerous:
                    Color(*DANGER_RED)
                else:
                    Color(*DANGER_GRAY)
                
                Ellipse(
                    pos=(self.pos[0] + corner_x - CORNER_DANGER_ZONE,
                         self.pos[1] + corner_y - CORNER_DANGER_ZONE),
                    size=(CORNER_DANGER_ZONE * 2, CORNER_DANGER_ZONE * 2)
                )
            
            # DVD квадрат
            Color(*COLORS[self.box_color_index])
            Rectangle(
                pos=(self.pos[0] + self.box_x, self.pos[1] + self.box_y),
                size=(BOX_SIZE, BOX_SIZE)
            )
            
            # Рамка квадрата
            Color(*BORDER_COLOR)
            Line(
                rectangle=(self.pos[0] + self.box_x, self.pos[1] + self.box_y,
                          BOX_SIZE, BOX_SIZE),
                width=3
            )
        
        # Текст DVD внутри квадрата
        self.draw_text_on_box()
    
    def draw_text_on_box(self):
        """Отрисовка текста DVD на квадрате"""
        label = CoreLabel(text='DVD', font_size=48, bold=True)
        label.refresh()
        texture = label.texture
        
        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(
                texture=texture,
                pos=(self.pos[0] + self.box_x + BOX_SIZE/2 - texture.width/2,
                     self.pos[1] + self.box_y + BOX_SIZE/2 - texture.height/2),
                size=texture.size
            )
    
    def on_touch_down(self, touch):
        """Обработка нажатий на квадрат"""
        if not self.playing or self.paused:
            return False
        
        if not self.collide_point(*touch.pos):
            return False
        
        # Локальные координаты
        local_x = touch.pos[0] - self.pos[0]
        local_y = touch.pos[1] - self.pos[1]
        
        # Проверка попадания в квадрат
        if (self.box_x <= local_x <= self.box_x + BOX_SIZE and
            self.box_y <= local_y <= self.box_y + BOX_SIZE):
            
            # Случайное изменение направления
            angle = random.uniform(0, 2 * math.pi)
            speed = math.sqrt(self.velocity_x ** 2 + self.velocity_y ** 2)
            self.velocity_x = math.cos(angle) * speed
            self.velocity_y = math.sin(angle) * speed
            
            return True
        
        return False

class DVDScreensaverApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root_layout = None
        self.game_view = None
        self.player_data = self.load_player_data()
        self.score_label_texture = None
        self.best_label_texture = None
        self.score_rect = None
        self.best_rect = None
    
    def load_player_data(self):
        """Загрузка данных игрока"""
        if os.path.exists('player_data.json'):
            try:
                with open('player_data.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'name': 'Майкл Скотт',
            'best_score': 0,
            'games_played': 0,
            'total_time': 0,
            'sound_enabled': True,
            'speed': 1,
            'records': []
        }
    
    def save_player_data(self):
        """Сохранение данных игрока"""
        try:
            with open('player_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.player_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
    
    def format_time(self, seconds):
        """Форматирование времени"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"
    
    def build(self):
        """Построение интерфейса"""
        self.root_layout = FloatLayout()
        Window.clearcolor = AMBER_BG
        
        # Показать меню
        self.show_menu()
        
        # Обработка изменения размера окна
        Window.bind(on_resize=lambda *args: self.show_menu())
        
        return self.root_layout
    
    def draw_menu_text(self, widget, frame_x, frame_y, frame_width):
        """Отрисовка текста меню"""
        # Заголовок
        title_label = CoreLabel(
            text='DVD ЗАСТАВКА\nФИЛИАЛ СКРЭНТОН',
            font_size=sp(42),
            bold=True,
            halign='center'
        )
        title_label.refresh()
        title_texture = title_label.texture
        
        with widget.canvas:
            Color(1, 1, 1, 1)
            Rectangle(
                texture=title_texture,
                pos=(Window.width/2 - title_texture.width/2, frame_y + dp(560)),
                size=title_texture.size
            )
        
        # Описание
        desc_label = CoreLabel(
            text='Не дай логотипу DVD достичь углов экрана!\nТапай по логотипу, чтобы изменить его направление.',
            font_size=sp(22),
            halign='center'
        )
        desc_label.refresh()
        desc_texture = desc_label.texture
        
        with widget.canvas:
            Color(1, 1, 1, 1)
            Rectangle(
                texture=desc_texture,
                pos=(Window.width/2 - desc_texture.width/2, frame_y + dp(470)),
                size=desc_texture.size
            )
    
    def create_info_blocks(self, widget, frame_x, frame_y, frame_width):
        """Создание информационных блоков"""
        # Адаптивная ширина блоков
        total_spacing = dp(80)
        block_width = (frame_width - total_spacing) / 3
        block_height = dp(130)
        spacing = dp(20)
        start_x = frame_x + dp(40)
        start_y = frame_y + dp(300)
        
        # Блок Профиль
        profile_x = start_x
        with widget.canvas:
            Color(1, 1, 1, 0.7)
            RoundedRectangle(
                pos=(profile_x, start_y),
                size=(block_width, block_height),
                radius=[dp(12)]
            )
        
        profile_text = f"ПРОФИЛЬ\n{self.player_data['name']}\nИгр: {self.player_data['games_played']}"
        profile_label = CoreLabel(text=profile_text, font_size=sp(20), bold=True)
        profile_label.refresh()
        profile_texture = profile_label.texture
        
        with widget.canvas:
            Color(1, 1, 1, 1)
            Rectangle(
                texture=profile_texture,
                pos=(profile_x + block_width/2 - profile_texture.width/2,
                     start_y + block_height/2 - profile_texture.height/2),
                size=profile_texture.size
            )
        
        # Блок Рекорд
        record_x = start_x + block_width + spacing
        with widget.canvas:
            Color(1, 1, 1, 0.7)
            RoundedRectangle(
                pos=(record_x, start_y),
                size=(block_width, block_height),
                radius=[dp(12)]
            )
        
        record_text = f"РЕКОРД\n{self.format_time(self.player_data['best_score'])}\nОбщее: {self.format_time(self.player_data['total_time'])}"
        record_label = CoreLabel(
            text=record_text, 
            font_size=sp(20), 
            bold=True
        )
        record_label.refresh()
        record_texture = record_label.texture
        
        with widget.canvas:
            Color(1, 1, 1, 1)
            Rectangle(
                texture=record_texture,
                pos=(record_x + block_width/2 - record_texture.width/2,
                     start_y + block_height/2 - record_texture.height/2),
                size=record_texture.size
            )
        
        # Блок Настройки
        settings_x = start_x + (block_width + spacing) * 2
        with widget.canvas:
            Color(1, 1, 1, 0.7)
            RoundedRectangle(
                pos=(settings_x, start_y),
                size=(block_width, block_height),
                radius=[dp(12)]
            )
        
        sound_status = "ВКЛ" if self.player_data['sound_enabled'] else "ВЫКЛ"
        settings_text = f"НАСТРОЙКИ\nЗвук: {sound_status}\nСкорость: {self.player_data['speed']}"
        settings_label = CoreLabel(text=settings_text, font_size=sp(20), bold=True)
        settings_label.refresh()
        settings_texture = settings_label.texture
        
        with widget.canvas:
            Color(1, 1, 1, 1)
            Rectangle(
                texture=settings_texture,
                pos=(settings_x + block_width/2 - settings_texture.width/2,
                     start_y + block_height/2 - settings_texture.height/2),
                size=settings_texture.size
            )
        
        # Обработчики кликов на блоки
        def on_touch_down(instance, touch):
            # Профиль
            if (profile_x <= touch.pos[0] <= profile_x + block_width and
                start_y <= touch.pos[1] <= start_y + block_height):
                self.show_profile_selection()
                return True
            
            # Рекорд
            if (record_x <= touch.pos[0] <= record_x + block_width and
                start_y <= touch.pos[1] <= start_y + block_height):
                self.show_records()
                return True
            
            # Настройки
            if (settings_x <= touch.pos[0] <= settings_x + block_width and
                start_y <= touch.pos[1] <= start_y + block_height):
                self.show_settings()
                return True
            
            return False
        
        widget.bind(on_touch_down=on_touch_down)
    
    def show_menu(self):
        """Показать главное меню"""
        self.root_layout.clear_widgets()
        
        menu_widget = Widget()
        
        with menu_widget.canvas.before:
            Color(*AMBER_BG)
            Rectangle(pos=(0, 0), size=Window.size)
        
        # Рамка телевизора - увеличенные максимальные размеры для Full HD
        menu_width = min(Window.width - dp(100), dp(1000))
        menu_height = min(Window.height - dp(100), dp(900))
        frame_padding = dp(40)
        frame_width = menu_width
        frame_height = menu_height
        frame_x = Window.width/2 - frame_width/2
        frame_y = Window.height/2 - frame_height/2
        
        with menu_widget.canvas:
            # Внешняя темная рамка
            Color(*TV_FRAME_COLOR)
            RoundedRectangle(
                pos=(frame_x - dp(35), frame_y - dp(35)),
                size=(frame_width + dp(70), frame_height + dp(70)),
                radius=[dp(22)]
            )
            
            # Внутренняя рамка (экран)
            Color(*TV_SCREEN_COLOR)
            RoundedRectangle(
                pos=(frame_x, frame_y),
                size=(frame_width, frame_height),
                radius=[dp(18)]
            )
        
        # Текст меню
        self.draw_menu_text(menu_widget, frame_x, frame_y, frame_width)
        
        # Информационные блоки
        self.create_info_blocks(menu_widget, frame_x, frame_y, frame_width)
        
        # Кнопка старта
        self.create_start_button(menu_widget, frame_x, frame_y)
        
        self.root_layout.add_widget(menu_widget)
    
    def show_profile_selection(self):
        """Экран выбора персонажа"""
        self.root_layout.clear_widgets()
        
        profile_widget = Widget()
        
        with profile_widget.canvas.before:
            Color(*AMBER_BG)
            Rectangle(pos=(0, 0), size=Window.size)
        
        # Заголовок
        title_label = CoreLabel(text='ВЫБОР ПЕРСОНАЖА', font_size=sp(42), bold=True)
        title_label.refresh()
        title_texture = title_label.texture
        
        with profile_widget.canvas:
            Color(*GRAY_DARK)
            Rectangle(
                texture=title_texture,
                pos=(Window.width/2 - title_texture.width/2, Window.height - dp(150)),
                size=title_texture.size
            )
        
        # Список персонажей (2 колонки)
        char_width = dp(340)
        char_height = dp(85)
        spacing = dp(22)
        start_x = Window.width/2 - char_width - spacing/2
        start_y = Window.height - dp(260)
        
        for i, character in enumerate(CHARACTERS):
            col = i % 2
            row = i // 2
            
            char_x = start_x + col * (char_width + spacing)
            char_y = start_y - row * (char_height + spacing)
            
            # Проверка выбранного персонажа
            is_selected = self.player_data['name'] == character
            
            # Цвет кнопки - цвет персонажа
            bg_color = CHARACTER_COLORS[character]
            
            with profile_widget.canvas:
                Color(*bg_color)
                RoundedRectangle(
                    pos=(char_x, char_y),
                    size=(char_width, char_height),
                    radius=[dp(14)]
                )
            
            # Если выбран - рамка
            if is_selected:
                with profile_widget.canvas:
                    Color(1, 1, 1, 1)
                    Line(
                        rounded_rectangle=(char_x, char_y, char_width, char_height, dp(14)),
                        width=5
                    )
            
            char_label = CoreLabel(text=character, font_size=sp(24), bold=True)
            char_label.refresh()
            char_texture = char_label.texture
            
            with profile_widget.canvas:
                Color(1, 1, 1, 1)
                Rectangle(
                    texture=char_texture,
                    pos=(char_x + char_width/2 - char_texture.width/2,
                         char_y + char_height/2 - char_texture.height/2),
                    size=char_texture.size
                )
        
        # Обработчик кликов на персонажей
        def on_character_select(instance, touch):
            for i, character in enumerate(CHARACTERS):
                col = i % 2
                row = i // 2
                
                char_x = start_x + col * (char_width + spacing)
                char_y = start_y - row * (char_height + spacing)
                
                if (char_x <= touch.pos[0] <= char_x + char_width and
                    char_y <= touch.pos[1] <= char_y + char_height):
                    self.player_data['name'] = character
                    self.save_player_data()
                    self.show_profile_selection()
                    return True
            return False
        
        profile_widget.bind(on_touch_down=on_character_select)
        
        # Кнопка назад
        self.create_back_button(profile_widget)
        
        self.root_layout.add_widget(profile_widget)
    
    def show_settings(self):
        """Экран настроек"""
        self.root_layout.clear_widgets()
        
        settings_widget = Widget()
        
        with settings_widget.canvas.before:
            Color(*AMBER_BG)
            Rectangle(pos=(0, 0), size=Window.size)
        
        # Заголовок
        title_label = CoreLabel(text='НАСТРОЙКИ', font_size=sp(42), bold=True)
        title_label.refresh()
        title_texture = title_label.texture
        
        with settings_widget.canvas:
            Color(*GRAY_DARK)
            Rectangle(
                texture=title_texture,
                pos=(Window.width/2 - title_texture.width/2, Window.height - dp(150)),
                size=title_texture.size
            )
        
        # Блок звука
        sound_y = Window.height - dp(300)
        sound_label = CoreLabel(text='ЗВУК', font_size=sp(32), bold=True)
        sound_label.refresh()
        sound_texture = sound_label.texture
        
        with settings_widget.canvas:
            Color(*GRAY_DARK)
            Rectangle(
                texture=sound_texture,
                pos=(Window.width/2 - sound_texture.width/2, sound_y),
                size=sound_texture.size
            )
        
        # Кнопки ВКЛ/ВЫКЛ
        btn_width = dp(220)
        btn_height = dp(85)
        btn_spacing = dp(22)
        btn_y = sound_y - dp(150)
        
        # Кнопка ВКЛ
        on_btn_x = Window.width/2 - btn_width - btn_spacing/2
        on_bg_color = GRAY_DARK if self.player_data['sound_enabled'] else WHITE
        
        with settings_widget.canvas:
            Color(*on_bg_color)
            RoundedRectangle(
                pos=(on_btn_x, btn_y),
                size=(btn_width, btn_height),
                radius=[dp(14)]
            )
        
        on_label = CoreLabel(text='ВКЛ', font_size=sp(26), bold=True)
        on_label.refresh()
        on_texture = on_label.texture
        
        with settings_widget.canvas:
            Color(1, 1, 1, 1) if self.player_data['sound_enabled'] else Color(*GRAY_DARK)
            Rectangle(
                texture=on_texture,
                pos=(on_btn_x + btn_width/2 - on_texture.width/2,
                     btn_y + btn_height/2 - on_texture.height/2),
                size=on_texture.size
            )
        
        # Кнопка ВЫКЛ
        off_btn_x = Window.width/2 + btn_spacing/2
        off_bg_color = GRAY_DARK if not self.player_data['sound_enabled'] else WHITE
        
        with settings_widget.canvas:
            Color(*off_bg_color)
            RoundedRectangle(
                pos=(off_btn_x, btn_y),
                size=(btn_width, btn_height),
                radius=[dp(14)]
            )
        
        off_label = CoreLabel(text='ВЫКЛ', font_size=sp(26), bold=True)
        off_label.refresh()
        off_texture = off_label.texture
        
        with settings_widget.canvas:
            Color(1, 1, 1, 1) if not self.player_data['sound_enabled'] else Color(*GRAY_DARK)
            Rectangle(
                texture=off_texture,
                pos=(off_btn_x + btn_width/2 - off_texture.width/2,
                     btn_y + btn_height/2 - off_texture.height/2),
                size=off_texture.size
            )
        
        # Обработчик кликов
        def on_sound_toggle(instance, touch):
            if (on_btn_x <= touch.pos[0] <= on_btn_x + btn_width and
                btn_y <= touch.pos[1] <= btn_y + btn_height):
                self.player_data['sound_enabled'] = True
                self.save_player_data()
                self.show_settings()
                return True
            
            if (off_btn_x <= touch.pos[0] <= off_btn_x + btn_width and
                btn_y <= touch.pos[1] <= btn_y + btn_height):
                self.player_data['sound_enabled'] = False
                self.save_player_data()
                self.show_settings()
                return True
            
            return False
        
        settings_widget.bind(on_touch_down=on_sound_toggle)
        
        # Кнопка назад
        self.create_back_button(settings_widget)
        
        self.root_layout.add_widget(settings_widget)
    
    def show_records(self):
        """Экран таблицы рекордов"""
        self.root_layout.clear_widgets()
        
        records_widget = Widget()
        
        with records_widget.canvas.before:
            Color(*AMBER_BG)
            Rectangle(pos=(0, 0), size=Window.size)
        
        # Заголовок
        title_label = CoreLabel(text='ТАБЛИЦА РЕКОРДОВ', font_size=sp(42), bold=True)
        title_label.refresh()
        title_texture = title_label.texture
        
        with records_widget.canvas:
            Color(*GRAY_DARK)
            Rectangle(
                texture=title_texture,
                pos=(Window.width/2 - title_texture.width/2, Window.height - dp(150)),
                size=title_texture.size
            )
        
        # Таблица рекордов
        records = self.player_data.get('records', [])
        
        if not records:
            # Нет рекордов
            no_records_label = CoreLabel(
                text='Пока нет рекордов.\nСыграйте первую игру!',
                font_size=sp(26)
            )
            no_records_label.refresh()
            no_records_texture = no_records_label.texture
            
            with records_widget.canvas:
                Color(*GRAY_DARK)
                Rectangle(
                    texture=no_records_texture,
                    pos=(Window.width/2 - no_records_texture.width/2, Window.height/2),
                    size=no_records_texture.size
                )
        else:
            # Показываем топ-10
            start_y = Window.height - dp(240)
            row_height = dp(65)
            
            for i, record in enumerate(records[:10]):
                record_y = start_y - i * row_height
                
                # Получить цвет персонажа
                character_name = record.get('name', 'Майкл Скотт')
                character_color = CHARACTER_COLORS.get(character_name, (0.5, 0.5, 0.5, 1))
                
                # Фон строки - цвет персонажа
                with records_widget.canvas:
                    Color(*character_color)
                    RoundedRectangle(
                        pos=(dp(55), record_y),
                        size=(Window.width - dp(110), row_height - dp(10)),
                        radius=[dp(12)]
                    )
                
                # Текст записи
                record_text = f"{i+1}. {character_name} - {self.format_time(record['score'])} - {record['date']}"
                record_label = CoreLabel(text=record_text, font_size=sp(22))
                record_label.refresh()
                record_texture = record_label.texture
                
                with records_widget.canvas:
                    Color(1, 1, 1, 1)
                    Rectangle(
                        texture=record_texture,
                        pos=(dp(75), record_y + (row_height - record_texture.height)/2),
                        size=record_texture.size
                    )
        
        # Кнопка назад
        self.create_back_button(records_widget)
        
        self.root_layout.add_widget(records_widget)
    
    def create_back_button(self, widget):
        """Кнопка назад в меню"""
        btn_width = dp(340)
        btn_height = dp(85)
        btn_x = Window.width/2 - btn_width/2
        btn_y = dp(75)
        
        with widget.canvas:
            Color(*GRAY_DARK)
            RoundedRectangle(pos=(btn_x, btn_y), size=(btn_width, btn_height), radius=[dp(14)])
        
        btn_label = CoreLabel(text='НАЗАД', font_size=sp(26), bold=True)
        btn_label.refresh()
        btn_texture = btn_label.texture
        
        with widget.canvas:
            Color(1, 1, 1, 1)
            Rectangle(
                texture=btn_texture,
                pos=(btn_x + btn_width/2 - btn_texture.width/2,
                     btn_y + btn_height/2 - btn_texture.height/2),
                size=btn_texture.size
            )
        
        def on_back_click(w, touch):
            if btn_x <= touch.pos[0] <= btn_x + btn_width and \
               btn_y <= touch.pos[1] <= btn_y + btn_height:
                self.show_menu()
                return True
            return False
        
        widget.bind(on_touch_down=on_back_click)
    
    def create_start_button(self, widget, frame_x, frame_y):
        """Создание кнопки старта"""
        btn_width = dp(400)
        btn_height = dp(95)
        btn_x = Window.width/2 - btn_width/2
        btn_y = frame_y + dp(160)
        
        # Кнопка
        with widget.canvas:
            Color(*GRAY_DARK)
            RoundedRectangle(pos=(btn_x, btn_y), size=(btn_width, btn_height), radius=[dp(14)])
        
        # Текст кнопки
        btn_label = CoreLabel(text='НАЧАТЬ ИГРУ', font_size=sp(30), bold=True)
        btn_label.refresh()
        btn_texture = btn_label.texture
        
        with widget.canvas:
            Color(1, 1, 1, 1)
            Rectangle(
                texture=btn_texture,
                pos=(btn_x + btn_width/2 - btn_texture.width/2,
                     btn_y + btn_height/2 - btn_texture.height/2),
                size=btn_texture.size
            )
        
        def on_touch_down(w, touch):
            if btn_x <= touch.pos[0] <= btn_x + btn_width and \
               btn_y <= touch.pos[1] <= btn_y + btn_height:
                self.start_game()
                return True
            return False
        
        widget.bind(on_touch_down=on_touch_down)
    
    def start_game(self):
        """Запуск игры"""
        self.root_layout.clear_widgets()
        
        game_container = FloatLayout()
        
        # Фон
        game_bg = Widget()
        with game_bg.canvas.before:
            Color(*AMBER_BG)
            Rectangle(pos=(0, 0), size=Window.size)
        game_container.add_widget(game_bg)
        
        # Рамка телевизора
        tv_frame = Widget()
        frame_padding = dp(45)
        frame_width = CANVAS_WIDTH + frame_padding * 2
        frame_height = CANVAS_HEIGHT + frame_padding * 2
        frame_x = Window.width/2 - frame_width/2
        frame_y = Window.height/2 - frame_height/2
        
        with tv_frame.canvas:
            # Внешняя темная рамка
            Color(*TV_FRAME_COLOR)
            RoundedRectangle(
                pos=(frame_x - dp(35), frame_y - dp(35)),
                size=(frame_width + dp(70), frame_height + dp(70)),
                radius=[dp(22)]
            )
            
            # Внутренняя рамка (экран)
            Color(*TV_SCREEN_COLOR)
            RoundedRectangle(
                pos=(frame_x, frame_y),
                size=(frame_width, frame_height),
                radius=[dp(18)]
            )
        
        game_container.add_widget(tv_frame)
        
        # Игровое поле (внутри рамки)
        canvas_container = FloatLayout(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(None, None),
            size=(CANVAS_WIDTH, CANVAS_HEIGHT)
        )
        
        self.game_view = GameView(
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(None, None),
            size=(CANVAS_WIDTH, CANVAS_HEIGHT)
        )
        canvas_container.add_widget(self.game_view)
        game_container.add_widget(canvas_container)
        
        # UI элементы
        self.create_game_ui(game_container)
        self.create_game_buttons(game_container)
        
        self.root_layout.add_widget(game_container)
        
        # Старт игры
        self.game_view.start()
    
    def create_game_ui(self, container):
        """Создание UI игры"""
        # Счет слева вверху
        score_widget = Widget()
        score_label = CoreLabel(text='Время: 0:00', font_size=sp(26), bold=True)
        score_label.refresh()
        self.score_label_texture = score_label.texture
        
        with score_widget.canvas:
            Color(*GRAY_DARK)
            self.score_rect = Rectangle(
                texture=self.score_label_texture,
                pos=(dp(45), Window.height - dp(95)),
                size=self.score_label_texture.size
            )
        container.add_widget(score_widget)
        
        # Лучший счет справа вверху
        best_widget = Widget()
        best_label = CoreLabel(text=f"Рекорд: {self.format_time(self.player_data['best_score'])}", font_size=sp(26), bold=True)
        best_label.refresh()
        self.best_label_texture = best_label.texture
        
        with best_widget.canvas:
            Color(*GRAY_DARK)
            self.best_rect = Rectangle(
                texture=self.best_label_texture,
                pos=(Window.width - self.best_label_texture.width - dp(45), Window.height - dp(95)),
                size=self.best_label_texture.size
            )
        container.add_widget(best_widget)
    
    def create_game_buttons(self, container):
        """Создание кнопок паузы и выхода"""
        # Кнопка паузы (слева)
        pause_btn_width = dp(220)
        pause_btn_height = dp(85)
        pause_btn_x = Window.width/2 - pause_btn_width - dp(18)
        pause_btn_y = dp(55)
        
        pause_widget = Widget()
        
        with pause_widget.canvas:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=(pause_btn_x, pause_btn_y), size=(pause_btn_width, pause_btn_height), radius=[dp(14)])
        
        pause_label = CoreLabel(text='Пауза', font_size=sp(24), bold=True)
        pause_label.refresh()
        pause_texture = pause_label.texture
        
        with pause_widget.canvas:
            Color(*GRAY_DARK)
            Rectangle(
                texture=pause_texture,
                pos=(pause_btn_x + pause_btn_width/2 - pause_texture.width/2,
                     pause_btn_y + pause_btn_height/2 - pause_texture.height/2),
                size=pause_texture.size
            )
        
        def on_pause_touch(w, touch):
            if pause_btn_x <= touch.pos[0] <= pause_btn_x + pause_btn_width and \
               pause_btn_y <= touch.pos[1] <= pause_btn_y + pause_btn_height:
                self.game_view.pause()
                return True
            return False
        
        pause_widget.bind(on_touch_down=on_pause_touch)
        container.add_widget(pause_widget)
        
        # Кнопка выхода (справа)
        exit_btn_width = dp(220)
        exit_btn_height = dp(85)
        exit_btn_x = Window.width/2 + dp(18)
        exit_btn_y = dp(55)
        
        exit_widget = Widget()
        
        with exit_widget.canvas:
            Color(0.9, 0.9, 0.9, 1)
            RoundedRectangle(pos=(exit_btn_x, exit_btn_y), size=(exit_btn_width, exit_btn_height), radius=[dp(14)])
        
        exit_label = CoreLabel(text='Выйти', font_size=sp(24), bold=True)
        exit_label.refresh()
        exit_texture = exit_label.texture
        
        with exit_widget.canvas:
            Color(*GRAY_DARK)
            Rectangle(
                texture=exit_texture,
                pos=(exit_btn_x + exit_btn_width/2 - exit_texture.width/2,
                     exit_btn_y + exit_btn_height/2 - exit_texture.height/2),
                size=exit_texture.size
            )
        
        def on_exit_touch(w, touch):
            if exit_btn_x <= touch.pos[0] <= exit_btn_x + exit_btn_width and \
               exit_btn_y <= touch.pos[1] <= exit_btn_y + exit_btn_height:
                self.exit_game()
                return True
            return False
        
        exit_widget.bind(on_touch_down=on_exit_touch)
        container.add_widget(exit_widget)
    
    def exit_game(self):
        """Выход из игры"""
        if self.game_view:
            self.game_view.stop()
        self.show_menu()
    
    def update_score(self, score):
        """Обновление счета"""
        score_label = CoreLabel(text=f'Время: {self.format_time(score)}', font_size=sp(26), bold=True)
        score_label.refresh()
        self.score_label_texture = score_label.texture
        self.score_rect.texture = self.score_label_texture
        self.score_rect.size = self.score_label_texture.size
    
    def game_over(self, score):
        """Окончание игры"""
        # Обновить статистику
        self.player_data['games_played'] += 1
        self.player_data['total_time'] += score
        
        if score > self.player_data['best_score']:
            self.player_data['best_score'] = score
        
        # Добавить в таблицу рекордов
        record = {
            'name': self.player_data['name'],
            'score': score,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        if 'records' not in self.player_data:
            self.player_data['records'] = []
        
        self.player_data['records'].append(record)
        self.player_data['records'].sort(key=lambda x: x['score'], reverse=True)
        self.player_data['records'] = self.player_data['records'][:10]
        
        self.save_player_data()
        
        # Показать экран Game Over
        self.show_game_over(score)
    
    def show_game_over(self, score):
        """Экран Game Over"""
        self.root_layout.clear_widgets()
        
        gameover_widget = Widget()
        
        with gameover_widget.canvas.before:
            Color(254/255, 243/255, 199/255, 0.9)
            Rectangle(pos=(0, 0), size=Window.size)
        
        # Заголовок
        title_label = CoreLabel(text='ИГРА ОКОНЧЕНА', font_size=sp(46), bold=True)
        title_label.refresh()
        title_texture = title_label.texture
        
        with gameover_widget.canvas:
            Color(*GRAY_DARK)
            Rectangle(
                texture=title_texture,
                pos=(Window.width/2 - title_texture.width/2, Window.height - dp(230)),
                size=title_texture.size
            )
        
        # Счет
        score_label = CoreLabel(text=f'Время выживания: {self.format_time(score)}', font_size=sp(34))
        score_label.refresh()
        score_texture = score_label.texture
        
        with gameover_widget.canvas:
            Color(*GRAY_DARK)
            Rectangle(
                texture=score_texture,
                pos=(Window.width/2 - score_texture.width/2, Window.height - dp(330)),
                size=score_texture.size
            )
        
        # Лучший счет
        best_label = CoreLabel(text=f"Лучший рекорд: {self.format_time(self.player_data['best_score'])}", font_size=sp(26))
        best_label.refresh()
        best_texture = best_label.texture
        
        with gameover_widget.canvas:
            Color(*GRAY_DARK)
            Rectangle(
                texture=best_texture,
                pos=(Window.width/2 - best_texture.width/2, Window.height - dp(400)),
                size=best_texture.size
            )
        
        # Кнопка рестарта
        self.create_restart_button(gameover_widget)
        
        # Кнопка меню
        self.create_menu_button(gameover_widget)
        
        self.root_layout.add_widget(gameover_widget)
    
    def create_restart_button(self, widget):
        """Кнопка рестарта"""
        btn_width = dp(400)
        btn_height = dp(95)
        btn_x = Window.width/2 - btn_width/2
        btn_y = dp(250)
        
        with widget.canvas:
            Color(*GRAY_DARK)
            RoundedRectangle(pos=(btn_x, btn_y), size=(btn_width, btn_height), radius=[dp(14)])
        
        btn_label = CoreLabel(text='ИГРАТЬ СНОВА', font_size=sp(30), bold=True)
        btn_label.refresh()
        btn_texture = btn_label.texture
        
        with widget.canvas:
            Color(1, 1, 1, 1)
            Rectangle(
                texture=btn_texture,
                pos=(btn_x + btn_width/2 - btn_texture.width/2,
                     btn_y + btn_height/2 - btn_texture.height/2),
                size=btn_texture.size
            )
        
        def on_touch_down(w, touch):
            if btn_x <= touch.pos[0] <= btn_x + btn_width and \
               btn_y <= touch.pos[1] <= btn_y + btn_height:
                self.start_game()
                return True
            return False
        
        widget.bind(on_touch_down=on_touch_down)
    
    def create_menu_button(self, widget):
        """Кнопка меню"""
        btn_width = dp(400)
        btn_height = dp(85)
        btn_x = Window.width/2 - btn_width/2
        btn_y = dp(145)
        
        with widget.canvas:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=(btn_x, btn_y), size=(btn_width, btn_height), radius=[dp(14)])
        
        btn_label = CoreLabel(text='Главное меню', font_size=sp(24))
        btn_label.refresh()
        btn_texture = btn_label.texture
        
        with widget.canvas:
            Color(*GRAY_DARK)
            Rectangle(
                texture=btn_texture,
                pos=(btn_x + btn_width/2 - btn_texture.width/2,
                     btn_y + btn_height/2 - btn_texture.height/2),
                size=btn_texture.size
            )
        
        def on_touch_down(w, touch):
            if btn_x <= touch.pos[0] <= btn_x + btn_width and \
               btn_y <= touch.pos[1] <= btn_y + btn_height:
                self.show_menu()
                return True
            return False
        
        widget.bind(on_touch_down=on_touch_down)

if __name__ == '__main__':
    DVDScreensaverApp().run()
