# QQ

Tencent QQ (Chinese: 腾讯QQ), also known as QQ, is an instant messaging software service and web portal developed by the Chinese technology company Tencent.

## Help Wanted

We need replace [./patch/*.js](./patch) with geerated one, which requires unpacking application.asar and extract those files.

Thanks to [./extract-asar.py](./extract-asar.py), we can do extract job without nodejs installed. But the extracted JavaScript files are encrypted with unknown method.

What we need now is finding out how they encrypted those JavaScript files and decrypting them so we can generate patched script without distributing them in the repository. 

## Features

### LiteLoaderQQNT

This is a third-party program which allows you load plugins to extend QQ and remove useless features as you need.

### Wayland

This package enables the flags to run on Wayland and it should work out-of-the-box.

This package also can fallback to X11 when Wayland is not available.

## Legality

The QQ app itself is **proprietary** (closed source).

This wrapper is not verified by, affiliated with, or supported by Tencent.
