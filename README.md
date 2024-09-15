# QQ

Tencent QQ (Chinese: 腾讯QQ), also known as QQ, is an instant messaging software service and web portal developed by the Chinese technology company Tencent.

[![Build flatpak manifest](https://github.com/arenekosreal/com.qq.QQ/actions/workflows/test.yaml/badge.svg)](https://github.com/arenekosreal/com.qq.QQ/actions/workflows/test.yaml)

## Features

### LiteLoaderQQNT

This is a third-party program which allows you load plugins to extend QQ and remove useless features as you need.

### Wayland

This package enables the flags to run on Wayland and it should work out-of-the-box.

This package also can fallback to X11 when Wayland is not available.

## For NixOS Users

As NixOS not obey FHS(Filesystem Hierarchy Standard), and this project require a FHS enviroment to finish some process.

A simple way is install a Steam (*unfree software*).

```nix
# configuration.nix

{
  pkgs,
  config,
  ...
}: {
  programs.steam = {
    enable = true;
    package = pkgs.steam;
  };
}
```

After rebuild, Steam provide `steam-run` that run a program in FHS enviroment.
Therefore, you could use `steam-run bash` to use this project.
Also, you could use another way to achieve this if you don't like unfree.

## Legality

The QQ app itself is **proprietary** (closed source).

This wrapper is not verified by, affiliated with, or supported by Tencent.
