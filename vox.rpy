# Vox system for Ren'py
# Copyright 2022 Soaria

init python:
    """
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    """

    renpy.music.register_channel("vox", "sound")
    renpy.music.register_channel("voxrvb", "sound")

    def vox_play_one(fn, rvbfn = None):
        fn = "audio/speech/" + fn
        print("Will play", fn)
        renpy.sound.stop(channel = "vox", fadeout = 0.3)
        renpy.sound.play(fn, channel = "vox")

        if rvbfn:
            rvbfn = "audio/speech/" + rvbfn
            print("Also playing", rvbfn)
            renpy.sound.stop(channel = "voxrvb", fadeout = 0.3)
            renpy.sound.play(rvbfn, channel = "voxrvb")

    def vox_is_playing():
        return renpy.sound.is_playing("vox")

    class VoxPlayer:
        def __init__(self, chapter_id):
            self.chapter_id = chapter_id
            self.basedir = "s-" + self.chapter_id + "/"
            self.playing = None
            self.playing_time = None

        def play(self, fn, rvbfn = None):
            if rvbfn:
                rvbfn = self.basedir + self.chapter_id + "-" + rvbfn + ".opus"
            vox_play_one(self.basedir + self.chapter_id + "-" + fn + ".opus", rvbfn = rvbfn)

        def remaining_duration(self):
            if not renpy.sound.is_playing("vox"):
                return 0.0
            dur = renpy.sound.get_duration("vox")
            # our files are 500ms padded.
            dur = dur - 0.5
            if dur < 0.0:
                dur = 0.0

            pos = renpy.sound.get_pos("vox")
            return dur - pos
