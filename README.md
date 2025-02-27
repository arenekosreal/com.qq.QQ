# QQ

Tencent QQ (Chinese: 腾讯QQ), also known as QQ, is an instant messaging software service and web portal developed by the Chinese technology company Tencent.

[![Build flatpak manifest](https://github.com/arenekosreal/com.qq.QQ/actions/workflows/test.yaml/badge.svg)](https://github.com/arenekosreal/com.qq.QQ/actions/workflows/test.yaml)

## Features

### LiteLoaderQQNT

This is a third-party program which allows you load plugins to extend QQ and remove useless features as you need.

### Freedesktop Runtime

This may save some space especially when you are not using other gnome applications in flatpak.

### Unsafe permissions removed

Unsafe permissions like accessing `/tmp` of host, or using `--device=all` are removed.
Most of those should be performed through xdg-desktop-portal instead using those permissions.

## Disadvantages

### Screenshot

Due to that QQ uses `gjs` to talk to dbus name `org.gnome.Shell.Screencast`, 
while `gjs` is not available with freedesktop runtime, permission to talk to `org.gnome.Shell.Screencast` is removed.
This should not have influence to KDE users, as screenshotting on KDE has been broken for a long perid of time 
according to [this](https://github.com/flathub/com.qq.QQ/pull/19).

Using system screenshot tools is recommended for better privacy. If you still want to use QQ's screenshot function, 
you can revert [4828897](https://github.com/arenekosreal/com.qq.QQ/commit/482889777bd8d1c93e52bd5db70c2ec9c79f487f), 
[2cb7b57](https://github.com/arenekosreal/com.qq.QQ/commit/2cb7b5762c8a2e85966ef1aab10a3655ad964c01) and 
[1b2cc88](https://github.com/arenekosreal/com.qq.QQ/commit/1b2cc880b0913bbfa7a9b99f46698cd8724961f9) and rebuild 
the modified manifest with flatpak-builder.

There maybe another solution that you can build gjs and its dependencies yourself. 
But that is going to be a hard story because you have to build mozjs, which build workflow is similar to firefox.

### Camera

Due to that QQ access camera devices directly and we only expose `--device=dri`, QQ will not find your camera devices.
We will test adding `--device=usb` as many of those camera devices are connected to host through USB bus, 
even integrated one. But `--device=usb` is only available since flatpak version 1.15.11 so you have to wait for some time.
If you still want to use camera, you can revert 
[1b4f106](https://github.com/arenekosreal/com.qq.QQ/commit/1b4f1062bc786f4dbc34f0d11667d4ad7a91456f) and rebuild 
the modified manifest with flatpak-builder.

Update: We found that QQ still cannot found integrated camera even `--device=usb` is added. What's more, 
according to [here](https://github.com/flatpak/flatpak/issues/1715), using pipewire is prefered to access
video devices. So we think if you still want to using camera, you have to revert commit mentioned above.

P.S: You can check [here](https://github.com/electron/electron/issues/42608) for more info.

## Legality

The QQ app itself is **proprietary** (closed source).

This wrapper is not verified by, affiliated with, or supported by Tencent.
