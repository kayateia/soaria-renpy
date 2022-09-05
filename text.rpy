# "Wiggle text" for Ren'py
# Copyright 2022 Soaria
#
# Use like so:
#    $ wiggle_text(0, "", "Interesting.", "")
#    tasha @raised surprised "You can see {i}that{/i} too? {image=wiggle0} Hmm. Unexpected..."

default wiggletexts = [
    ('', ''),
    ('', ''),
    ('', '')
]

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

    from itertools import zip_longest

    # Sets up "wiggle text". This is based on this idea:
    # https://lemmasoft.renai.us/forums/viewtopic.php?t=23852
    def wiggle_text(index, prefix, txt, postfix):
        global wiggletext1, wiggletext2

        letters = list(txt)
        letters1 = map(lambda l: l, letters[1::2])
        letters1_w = map(lambda l: "{size=-2}" + l + "{/size}", letters[::2])
        letters2 = map(lambda l: l, letters[::2])
        letters2_w = map(lambda l: "{size=-2}" + l + "{/size}", letters[1::2])
        
        wiggletexts[index] = (
            prefix + "".join(list([l[0]+l[1] for l in zip_longest(letters1_w, letters1, fillvalue='')])) + postfix,
            prefix + "".join(list([l[0]+l[1] for l in zip_longest(letters2, letters2_w, fillvalue='')])) + postfix
        )

image wiggle0:
    Text("[wiggletexts[0][0]]", substitute = True)
    pause .08
    Text("[wiggletexts[0][1]]", substitute = True)
    pause .08
    repeat

image wiggle1:
    Text("[wiggletexts[1][0]]", substitute = True)
    pause .09
    Text("[wiggletexts[1][1]]", substitute = True)
    pause .09
    repeat

image wiggle2:
    Text("[wiggletexts[2][0]]", substitute = True)
    pause .075
    Text("[wiggletexts[2][1]]", substitute = True)
    pause .075
    repeat
