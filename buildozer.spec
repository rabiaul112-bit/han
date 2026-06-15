[app]
title = WPS PIN Generator
package.name = wpsgenerator
package.domain = com.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,pyperclip
orientation = portrait
android.permissions = INTERNET, ACCESS_WIFI_STATE, CHANGE_WIFI_STATE
android.api = 30
android.minapi = 21
android.ndk = 23b
android.gradle_dependencies =
android.entrypoint = org.kivy.android.PythonActivity
android.private_storage = True
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1