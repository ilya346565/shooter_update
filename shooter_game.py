from pygame import *
from random import randint
from time import time as timer

# Инициализация игры
init()

# Настройки окна
win_width = 700
win_height = 500
window = display.set_mode((win_width, win_height))
display.set_caption("Дуэльный шутер")

# Загрузка изображений
img_back = "galaxy.jpg"  # Фон
img_player1 = "new2.jpg"  # Первый игрок
img_player2 = "new.jpg"   # Второй игрок
img_bullet = "Bullet.png" # Пуля

# Загрузка звуков
mixer.init()
mixer.music.load('track.mp3')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')

# Шрифты
font.init()
font1 = font.SysFont('Arial', 80)
font2 = font.SysFont('Arial', 36)

# Классы спрайтов
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
        self.size_x = size_x
        self.size_y = size_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Bullet(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed, direction):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.direction = direction  # 1 - вверх, -1 - вниз
    
    def update(self):
        self.rect.y -= self.speed * self.direction
        # Удаляем пулю, если она выходит за пределы экрана
        if self.rect.y < 0 or self.rect.y > win_height:
            self.kill()

class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed, player_num):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.player_num = player_num  # Номер игрока (1 или 2)
        self.health = 100
        self.reload_time = 0
        self.last_shot = 0
    
    def update(self):
        keys = key.get_pressed()
        if self.player_num == 1:
            # Управление для первого игрока (стрелки)
            if keys[K_LEFT] and self.rect.x > 5:
                self.rect.x -= self.speed
            if keys[K_RIGHT] and self.rect.x < win_width - self.size_x:
                self.rect.x += self.speed
            if keys[K_UP] and self.rect.y > 5:
                self.rect.y -= self.speed
            if keys[K_DOWN] and self.rect.y < win_height - self.size_y:
                self.rect.y += self.speed
        else:
            # Управление для второго игрока (WASD)
            if keys[K_a] and self.rect.x > 5:
                self.rect.x -= self.speed
            if keys[K_d] and self.rect.x < win_width - self.size_x:
                self.rect.x += self.speed
            if keys[K_w] and self.rect.y > 5:
                self.rect.y -= self.speed
            if keys[K_s] and self.rect.y < win_height - self.size_y:
                self.rect.y += self.speed
    
    def fire(self):
        now = timer()
        if now - self.last_shot > self.reload_time:
            self.last_shot = now
            if self.player_num == 1:
                bullet = Bullet(img_bullet, self.rect.centerx-7, self.rect.top, 15, 20, 15, 1)
            else:
                bullet = Bullet(img_bullet, self.rect.centerx-7, self.rect.bottom, 15, 20, 15, -1)
            bullets.add(bullet)
            fire_sound.play()
            return True
        return False

# Создание игроков
player1 = Player(img_player1, win_width//4, win_height//2, 80, 80, 5, 1)
player2 = Player(img_player2, 3*win_width//4, win_height//2, 80, 80, 5, 2)

# Группы спрайтов
bullets = sprite.Group()

# Фон
background = transform.scale(image.load(img_back), (win_width, win_height))

# Основной игровой цикл
run = True
finish = False
clock = time.Clock()

while run:
    # Обработка событий
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            # Стрельба для игрока 1 (пробел)
            if e.key == K_SPACE:
                player1.fire()
            # Стрельба для игрока 2 (F)
            if e.key == K_f:
                player2.fire()
            # Рестарт игры при нажатии R
            if e.key == K_r and finish:
                finish = False
                player1.health = 100
                player2.health = 100
                for bullet in bullets:
                    bullet.kill()
    
    if not finish:
        # Обновление фона
        window.blit(background, (0, 0))
        
        # Обновление и отрисовка игроков
        player1.update()
        player2.update()
        player1.reset()
        player2.reset()
        
        # Обновление и отрисовка пуль
        bullets.update()
        bullets.draw(window)
        
        # Проверка столкновений пуль с игроками
        for bullet in bullets:
            if sprite.collide_rect(bullet, player1) and bullet.direction == -1:
                player1.health -= 10
                bullet.kill()
            elif sprite.collide_rect(bullet, player2) and bullet.direction == 1:
                player2.health -= 10
                bullet.kill()
        
        # Проверка условий победы
        if player1.health <= 0 or player2.health <= 0:
            finish = True
            if player1.health <= 0 and player2.health <= 0:
                result_text = font1.render("НИЧЬЯ!", True, (255, 255, 255))
            elif player1.health <= 0:
                result_text = font1.render("Игрок 2 победил!", True, (255, 0, 0))
            else:
                result_text = font1.render("Игрок 1 победил!", True, (0, 0, 255))
            
            window.blit(result_text, (win_width//2 - result_text.get_width()//2, win_height//2 - 50))
            restart_text = font2.render("Нажмите R для рестарта", True, (255, 255, 255))
            window.blit(restart_text, (win_width//2 - restart_text.get_width()//2, win_height//2 + 50))
        
        # Отрисовка здоровья игроков
        health1_text = font2.render(f"P1: {player1.health}", True, (0, 0, 255))
        health2_text = font2.render(f"P2: {player2.health}", True, (255, 0, 0))
        
        window.blit(health1_text, (20, 20))
        window.blit(health2_text, (win_width - health2_text.get_width() - 20, 20))
    
    display.update()
    clock.tick(60)