[app]
title = WPS PIN Generator
package.name = wpsgenerator
package.domain = com.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy==2.1.0,pyperclip
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_WIFI_STATE, CHANGE_WIFI_STATE
android.api = 31
android.minapi = 21
android.ndk = 25b
android.gradle_dependencies = 
android.entrypoint = org.kivy.android.PythonActivity
android.private_storage = True

[buildozer]
log_level = 2
warn_on_root = 1
