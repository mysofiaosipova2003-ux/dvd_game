[app]
title = DVD Заставка
package.name = dvdgame
package.domain = ru.dvdgame

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1
requirements = python3,kivy

[buildozer]
log_level = 2

[app:android]
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 20
android.gradle_dependencies = 
android.enable_androidx = True
android.meta_data = ru.rustore.sdk.AppKey=ВАШ_КЛЮЧ_ОТ_RUSTORE

[app:android]
# ... существующие настройки ...

# ПОДПИСЬ APK ДЛЯ RUSTORE (ОБЯЗАТЕЛЬНО!)
android.release_artifact = bin/dvdgame-1.0-release.apk
android.add_src = dvdgame.keystore

# ДАННЫЕ КЛЮЧА (ВАШИ ПАРОЛИ)
android.release_keystore = dvdgame.keystore
android.release_keyalias = dvdgame
android.release_keystore_password = 123456
android.release_key_password = 123456
