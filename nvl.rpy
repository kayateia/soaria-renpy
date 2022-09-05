# nvl mode utilities for Ren'py
# Copyright 2022 Soaria
#
# Some utilities to make nvl-mode dialogue less painful.

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

    # Generates a dynamic character object for nvl based on the passed image tags.
    # tags. This simplifies (a tiny bit) making dynamic faces in nvl. e.g.:
    #    define keia_callback = speaker("keia")
    #    define keia = Character('Keia', color="#c8c8ff", image="keia", callback=keia_callback)
    #    define keia_nvl = Character('{image=side keia_nvl} Keia', color="#c8c8ff", what_prefix="{i}", what_suffix="{/i}", kind = nvl, callback=keia_callback)
    #    define keia_thought_nvl_dyn = nvl_dynamic(keia_thought_nvl, "(Keia)", "keia_nvl greyed")
    # ...
    #    $ keia_though_nvl_dyn("raised surprised")("Whoa... Incredible...")

    def character_nvl_dynamic(kind, name, base_d, tags):
        fullname = '{image=side ' + base_d + ' ' + tags + '} ' + name
        return Character(fullname, kind=kind)

    nvl_dynamic = renpy.curry(character_nvl_dynamic)
