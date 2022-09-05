# Soaria scripty bits for Ren'py

Ren'py is a Python-based engine for visual and kinetic novel development.

These are a few scripts with common code pulled from our own VN work that might be useful to others. These are specifically for Ren'py 8.x, but may work with 7.x.

Everything in here is licenced under the Apache 2.0 licence. This means (non-binding simple English version) that you can more or less do what you want with it as long as you keep credits and don't try to sue over patents.

I doubt you can realistically drop any of this directly into your project, but maybe you'll find something useful. Very much expect it to be full of debug statements and bugs 😹

## Music system

Given Soaria's propensity toward musical endeavours, it probably shouldn't surprise anyone that we have a very complicated system for playing music, and transitioning to other variants and sections of music smoothly. This uses four separate channels to do click-free transitions plus reverb tails for continuity.

- music.rpy - the main music system
- foley.rpy - instantiates some channels to treat looping foley the same as music

## Vocal system

This mostly provides a way to reference deep pathed opus files by chapter, and also a `remaining_duration` method that you can use with a lip flap script to stop animations with audio stopping. (And also a much simpler `vox_is_playing`.)

## Sfx system

Not much here yet, it's just to make sure things end up in the proper channels.

## Lipflap helpers

Pulls together several different methods of tracking text and making quality lipflaps on your side images.

## nvl helpers

For making nvl mode more interesting with character portraits and such.
