# Lip flap utilities for Ren'py
# Copyright 2022 Soaria
#
# Inspired by https://www.renpy.org/wiki/renpy/doc/cookbook/Blink_And_Lip_Flap
#
# To use, do something like this:
#    define keia_callback = speaker("keia")
#    define keia = Character('Keia', color="#c8c8ff", image="keia", callback=keia_callback)
#
# And hook it into your side image's LayeredImage animations:
#    always WhileSpeaking("keia", "sidekeia speakingmouth", "keia-blank")
#
# This assumes usage of the tools in vox.rpy for vox_is_playing().

init -10 python:
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

    # Set to the name of the character that is speaking, or None.
    speaking_char = None
    texting_char = None

    # This returns the speaking displayable if the character is speaking,
    # and the idle displayable if they are not. The second tuple value is
    # how long to wait before checking again.
    def while_speaking(name, speaking_d, idle_d, _st, _at):
        if name == speaking_char and (name == texting_char or vox_is_playing()):
            return speaking_d, .1
        else:
            return idle_d, None

    # Convert to a curried function.
    c_while_speaking = renpy.curry(while_speaking)

    # Displayable that returns the correct displayable for a character
    # depending on whether they are speaking or not.
    def WhileSpeaking(name, speaking_d, idle_d = Null()):
        return DynamicDisplayable(c_while_speaking(name, speaking_d, idle_d))

    # Character callback maintains the speaking_char variable.
    def speaker_callback(name, event, **kwargs):
        global speaking_char, texting_char

        if event == "show":
            speaking_char = name
            texting_char = name
        elif event == "slow_done":
            texting_char = None
        elif event == "end":
            speaking_char = None


    # Make a curried version for building callbacks per character.
    speaker = renpy.curry(speaker_callback)