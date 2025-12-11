[app]

# Название и пакет
title = DVD Заставка
package.name = dvdgame
package.domain = ru.scranton.dvd

# Исходники
source.dir = .
source.main = main.py
# Все нужные файлы для игры
source.include_exts = py,png,jpg,jpeg,JPG,PNG,kv,atlas,ttf,otf,json,txt,xml,wav,mp3
version = 1.0

# Требования (только Kivy)
requirements = python3,kivy==2.3.0

# Иконка (добавьте icon512.png 512x512)
icon.filename = icon.png

# Экран загрузки (DVD стиль)
presplash.filename = dvd_logo.jpg
android.presplash_color = #996633

# Ориентация (вертикальная для телефона)
orientation = portrait
fullscreen = 0

# Разрешения Android
android.permissions = INTERNET,VIBRATE

# Версии Android API
android.api = 33
android.minapi = 21

# Автоматически принимать лицензии
android.accept_sdk_license = True

# Архитектуры процессора (современные телефоны)
android.archs = arm64-v8a

# Формат сборки
android.release_artifact = apk

# Бекап
android.allow_backup = True

# Настройки Python for Android
p4a.branch = master
p4a.bootstrap = sdl2

# ВАШИ КЛЮЧИ ПОДПИСИ (из шага 4)
p4a.release_keystore = dvdgame.keystore
p4a.release_keyalias = dvdgame

[buildozer]

# Уровень логов
log_level = 2

# Не предупреждать при запуске от root
warn_on_root = 0
