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
