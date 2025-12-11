from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.clock import Clock
from kivy.core.window import Window
import math
import json
import os
import random

CANVAS_WIDTH, CANVAS_HEIGHT = 600, 450
BOX_SIZE, INITIAL_SPEED = 40, 3
CORNER_DANGER_ZONE = 50
COLORS = [(0.86,0.15,0.15,1), (0.98,0.75,0.14,1), (0.09,0.64,0.29,1), (0.15,0.39,0.92,1)]

class Player:
    def __init__(self):
        self.name, self.avatar, self.level = 'Игрок', 0, 1
        self.experience, self.best_score = 0, 0
        self.games_played, self.total_play_time = 0, 0

    def save(self):
        with open('dvd_player.json', 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, ensure_ascii=False)

    @classmethod
    def load(cls):
        try:
            if os.path.exists('dvd_player.json'):
                with open('dvd_player.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    player = cls()
                    player.__dict__.update(data)
                    return player
        except: pass
        return cls()

def format_time(seconds):
    return f"{int(seconds//60)}:{int(seconds%60):02d}"

class GameCanvas(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_state = {'status': 'idle', 'score': 0, 'start_time': 0, 'box': {}}
        self.player = Player.load()
        Clock.schedule_interval(self.update, 1/60.)

    def start_game(self):
        angle = random.uniform(0, 2*math.pi)
        self.game_state = {
            'status': 'playing', 'score': 0, 'start_time': Clock.get_time(),
            'box': {
                'x': CANVAS_WIDTH/2-BOX_SIZE/2, 'y': CANVAS_HEIGHT/2-BOX_SIZE/2,
                'size': BOX_SIZE,
                'velocity_x': math.cos(angle)*INITIAL_SPEED,
                'velocity_y': math.sin(angle)*INITIAL_SPEED,
                'color_index': random.randint(0, 3)
            }
        }

    def check_corner(self, box):
        cx, cy = box['x']+box['size']/2, box['y']+box['size']/2
        for x, y in [(0,0), (CANVAS_WIDTH,0), (0,CANVAS_HEIGHT), (CANVAS_WIDTH,CANVAS_HEIGHT)]:
            if math.hypot(cx-x, cy-y) < CORNER_DANGER_ZONE: return True
        return False

    def update(self, dt):
        if self.game_state['status'] != 'playing': return
        
        self.game_state['score'] = Clock.get_time() - self.game_state['start_time']
        box = self.game_state['box']
        box['x'] += box['velocity_x']
        box['y'] += box['velocity_y']

        color_changed = False
        if box['x'] <= 0 or box['x'] + box['size'] >= CANVAS_WIDTH:
            box['velocity_x'] *= -1
            box['x'] = max(0, min(CANVAS_WIDTH-box['size'], box['x']))
            box['color_index'] = random.randint(0, 3)
            color_changed = True

        if box['y'] <= 0 or box['y'] + box['size'] >= CANVAS_HEIGHT:
            box['velocity_y'] *= -1
            box['y'] = max(0, min(CANVAS_HEIGHT-box['size'], box['y']))
            if not color_changed: box['color_index'] = random.randint(0, 3)

        if self.check_corner(box):
            self.game_over()

        self.canvas.ask_update()

    def game_over(self):
        final_score = self.game_state['score']
        self.player.games_played += 1
        self.player.total_play_time += final_score
        if final_score > self.player.best_score:
            self.player.best_score = final_score
        self.player.experience += int(final_score * 2)
        if self.player.experience >= self.player.level * 100:
            self.player.level += 1
            self.player.experience = 0
        self.player.save()
        App.get_running_app().root.current = 'gameover'

    def on_touch_down(self, touch):
        if self.game_state['status'] != 'playing': return False
        canvas_x = (touch.x - self.x) * CANVAS_WIDTH / self.width
        canvas_y = (touch.y - self.y) * CANVAS_HEIGHT / self.height
        box = self.game_state['box']
        if (canvas_x >= box['x'] and canvas_x <= box['x']+box['size'] and
            canvas_y >= box['y'] and canvas_y <= box['y']+box['size']):
            angle = random.uniform(0, 2*math.pi)
            speed = math.hypot(box['velocity_x'], box['velocity_y'])
            box['velocity_x'] = math.cos(angle) * speed
            box['velocity_y'] = math.sin(angle) * speed
            return True
        return super().on_touch_down(touch)

    def draw_game(self):
        self.canvas.clear()
        with self.canvas:
            Color(0.84, 0.78, 0.66, 1)
            Rectangle(pos=self.pos, size=self.size)
            for i in range(0, int(self.height), 20):
                Color(0.47, 0.39, 0.31, 0.08)
                Line(points=[self.x, self.y+i, self.x+self.width, self.y+i], width=1)

        if self.game_state['status'] == 'playing':
            box = self.game_state['box']
            scale_x, scale_y = self.width / CANVAS_WIDTH, self.height / CANVAS_HEIGHT

            # Углы опасности
            cx, cy = box['x']+box['size']/2, box['y']+box['size']/2
            for x, y in [(0,0), (CANVAS_WIDTH,0), (0,CANVAS_HEIGHT), (CANVAS_WIDTH,CANVAS_HEIGHT)]:
                dist = math.hypot(cx-x, cy-y)
                alpha = 0.25 if dist < CORNER_DANGER_ZONE else 0.08
                Color(0.6, 0.11, 0.11, alpha)
                r = CORNER_DANGER_ZONE * min(scale_x, scale_y)
                px = self.x + x*scale_x - r
                py = self.y + y*scale_y - r
                Ellipse(pos=(px, py), size=(r*2, r*2))

            # DVD коробка
            color = COLORS[box['color_index']]
            Color(*color)
            px = self.x + box['x'] * scale_x
            py = self.y + box['y'] * scale_y
            Rectangle(pos=(px, py), size=(box['size']*scale_x, box['size']*scale_y))
            Color(0,0,0,1)
            Line(rectangle=(px,py,box['size']*scale_x,box['size']*scale_y), width=2)

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player.load()
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Заголовок
        header = BoxLayout(size_hint_y=None, height=120, padding=[30,20], spacing=5)
        header.add_widget(Label(text='ФИЛИАЛ СКРЭНТОН', font_size=16, color=[0.47,0.44,0.42,1]))
        header.add_widget(Label(text='DVD ЗАСТАВКА', font_size=36, bold=True))
        header.add_widget(Label(text='Игра в конференц-зале', font_size=16, color=[0.47,0.44,0.42,1]))
        layout.add_widget(header)
        
        # Правила
        rules = BoxLayout(size_hint_y=None, height=180, padding=20)
        rules.add_widget(Label(
            text='ПРАВИЛА ИГРЫ\n\n• Не дай DVD достичь углов экрана!\n• Кликай по логотипу для смены направления\n• Цвет меняется при касании стен\n• Выживай как можно дольше!',
            font_size=18, halign='center', valign='middle'
        ))
        layout.add_widget(rules)
        
        # Инфо игрока
        player_box = BoxLayout(size_hint_y=None, height=60, padding=15, spacing=10)
        player_box.add_widget(Label(text='👨‍💼', font_size=28))
        player_box.add_widget(Label(text=self.player.name, font_size=20, bold=True))
        player_box.add_widget(Label(text=f'• Уровень {self.player.level}'))
        player_box.add_widget(Label(text=format_time(self.player.best_score), font_size=18))
        layout.add_widget(player_box)
        
        # Старт
        btn = Button(text='▶ НАЧАТЬ ИГРУ', size_hint_y=None, height=70, font_size=24, background_color=[0.34,0.32,0.30,1])
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'game'))
        layout.add_widget(btn)
        
        layout.add_widget(Label(text='Dunder Mifflin Paper Company', size_hint_y=None, font_size=14))
        self.add_widget(layout)

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Счетчики
        scores = BoxLayout(size_hint_y=None, height=70, spacing=30)
        scores.add_widget(Label(text='⏱', font_size=32))
        self.score_label = Label(text='0:00', font_size=28, bold=True)
        scores.add_widget(self.score_label)
        scores.add_widget(Label(text='🏆', font_size=32))
        self.best_label = Label(text='0:00', font_size=28, bold=True)
        scores.add_widget(self.best_label)
        layout.add_widget(scores)
        
        # Канвас
        self.game_canvas = GameCanvas(size_hint_y=0.7)
        layout.add_widget(self.game_canvas)
        
        # Пауза
        pause_btn = Button(text='⏸ ПАУЗА', size_hint_y=None, height=60, font_size=20)
        pause_btn.bind(on_press=self.on_pause)
        layout.add_widget(pause_btn)
        
        self.add_widget(layout)
        Clock.schedule_interval(self.update_display, 0.1)

    def on_pre_enter(self):
        self.player = Player.load()
        self.best_label.text = format_time(self.player.best_score)
        self.game_canvas.start_game()
        self.game_canvas.draw_game()

    def update_display(self, dt):
        if self.game_canvas.game_state['status'] == 'playing':
            self.score_label.text = format_time(self.game_canvas.game_state['score'])

    def on_pause(self, instance):
        if self.game_canvas.game_state['status'] == 'playing':
            self.game_canvas.game_state['status'] = 'paused'

class GameOverScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
        
        layout.add_widget(Label(text='КОНФЕРЕНЦ-ЗАЛ', font_size=18, color=[0.47,0.44,0.42,1]))
        layout.add_widget(Label(text='ИГРА ОКОНЧЕНА', font_size=36, bold=True))
        
        self.score_label = Label(text='0:00', font_size=28, bold=True)
        layout.add_widget(self.score_label)
        
        self.record_label = Label(text='0:00', font_size=24, bold=True)
        layout.add_widget(self.record_label)
        
        self.level_label = Label(text='Уровень 1', font_size=24, bold=True)
        layout.add_widget(self.level_label)
        
        again_btn = Button(text='🔄 ИГРАТЬ СНОВА', size_hint_y=None, height=70, font_size=22)
        again_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'game'))
        layout.add_widget(again_btn)
        
        menu_btn = Button(text='◀ ГЛАВНОЕ МЕНЮ', size_hint_y=None, height=60, font_size=20)
        menu_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'menu'))
        layout.add_widget(menu_btn)
        
        self.add_widget(layout)

    def on_pre_enter(self):
        game_screen = self.manager.get_screen('game')
        score = game_screen.game_canvas.game_state['score']
        player = game_screen.game_canvas.player
        
        self.score_label.text = format_time(score)
        self.record_label.text = format_time(player.best_score)
        self.level_label.text = f'Уровень {player.level}'

class DVDGameApp(App):
    def build(self):
        Window.size = (1000, 700)
        Window.clearcolor = (0.996, 0.953, 0.78, 1)
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(GameOverScreen(name='gameover'))
        return sm

DVDGameApp().run()
