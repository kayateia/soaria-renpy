# Music system for Ren'py
# Copyright 2022 Soaria

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
    import time

    # Implements a simple ping-pong buffer system for music channels. This
    # lets us flip from one slice of a song to another without clicking.
    class PingPongChannel:
        def __init__(self, root):
            self.root = root
            self.ppbs = ["{0}-ppb1".format(root), "{0}-ppb2".format(root)]
            for i in self.ppbs:
                renpy.music.register_channel(i, "music")
            self.last_use = { self.ppbs[0]: 0.0, self.ppbs[1]: 0.0 }

        def get_pos(self):
            # Figure out which channel we used most recently.
            last_used = self.get_last_used()
            if last_used is None:
                return 0.0
            else:
                pos = renpy.music.get_pos(last_used)

                # This can happen sometimes during rollback and load/save.
                if pos is None:
                    return 0.0
                else:
                    return pos

        def get_last_used(self):
            if self.last_use[self.ppbs[0]] > self.last_use[self.ppbs[1]]:
                return self.ppbs[0]
            else:
                return self.ppbs[1]


        def get_playing(self):
            # Figure out which channel we used most recently.
            if self.last_use[self.ppbs[0]] > self.last_use[self.ppbs[1]]:
                return renpy.music.get_playing(self.ppbs[0])
            else:
                return renpy.music.get_playing(self.ppbs[1])

        def play(self, fn, fadein = 0.3, loop = None):
            # Is either channel open?
            cur_bgm_1 = renpy.music.get_playing(self.ppbs[0])
            cur_bgm_2 = renpy.music.get_playing(self.ppbs[1])

            channels = self.ppbs
            if cur_bgm_1 is None:
                # Use ppb1 for new stuffs.
                pass
            elif cur_bgm_2 is None:
                # Use ppb2 for new stuffs.
                channels = [channels[1], channels[0]]
            else:
                # Oops, we ran out of buffer channels. Overwrite
                # the oldest one.
                if self.last_use[0] < self.last_use[1]:
                    # Use ppb2 for new stuffs.
                    pass
                else:
                    channels = [channels[1], channels[0]]
                print("Warning: Overwriting music on channel", channels[0])
            
            renpy.music.stop(channel = channels[1], fadeout = fadein)
            renpy.music.stop(channel = channels[0], fadeout = 0.0)
            renpy.music.play(fn, channel = channels[0], fadein = fadein, loop = loop)

            self.last_use[channels[0]] = time.time()

        def stop(self, fadeout = 1.0):
            # Stop all channels.
            for i in self.ppbs:
                renpy.music.stop(i, fadeout)
                self.last_use[i] = 0.0

        def set_volume(self, volume, delay = 0.0):
            for i in self.ppbs:
                renpy.music.set_volume(volume = volume, delay = delay, channel = i)

    # Aggregate user channel, covering all ping pong buffer channels for
    # a logical music stream.
    class AggregateChannel:
        def __init__(self, root):
            self.music = PingPongChannel("{0}-mus".format(root))
            self.reverb = PingPongChannel("{0}-rvb".format(root))

        def set_volume(self, volume, delay = 0.0):
            self.music.set_volume(volume, delay)
            self.reverb.set_volume(volume, delay)

        def stop(self, fadeout = 1.0):
            self.music.stop(fadeout = fadeout)
            self.reverb.stop(fadeout = fadeout)

    # This represents our default aggregate channel for background music.
    music_default = AggregateChannel("bgm")

    def between(val, first, last):
        return first <= val and val <= last

    # Find the next loop start and end, given the BGM and the current
    # offset in seconds (if any).
    #
    # Two basic cases:
    # - The ptr is already inside the loop:
    #       Just use the current ptr and wrap it in the loop.
    # - The ptr is before the loop:
    #       If force_next is True, use the next loop.
    #       If force_next is False, use the current ptr wrapped in the next loop.
    def music_next_loop(target_bgm, tag, cur_offset):
        ps = target_bgm.parts

        for i in range(0, len(ps)):
            if ps[i].tag == tag:
                if cur_offset is None:
                    return ps[i]

                if between(cur_offset, ps[i].section_start, ps[i].loop_end) or not ps[i].force_next:
                    return ps[i].with_offset(cur_offset)
                else:
                    return ps[i]

        print("WARNING: Invalid music tag:", tag, target_bgm.fn)
        return None

    def music_target_name(target_bgm, loop):
        targetfn = "audio/" + target_bgm.fn
        if loop.loop_end is not None:
            target = "<from {0} to {1} loop {2}>{3}".format(
                loop.start, loop.loop_end, loop.loop_start, targetfn
            )
        elif loop.loop_start is not None:
            target = "<from {0} loop {1}>{2}".format(
                loop.start, loop.loop_start, targetfn
            )
        else:
            target = "<from {0}>{1}".format(
                loop.start, targetfn
            )
        return target

    def reverb_target_name(target_bgm):
        if not target_bgm.bar_time or not target_bgm.reverb:
            return None

        targetfn = "audio/" + target_bgm.reverb
        cur_pos = target_bgm.channel.music.get_pos()
        if cur_pos is None:
            return None

        # Play one bar of reverb.
        bar_time = 4 / (target_bgm.bpm / 60.0)
        target = "<from {0} to {1}>{2}".format(
            cur_pos, cur_pos + target_bgm.bar_time, targetfn
        )

        return target

    # Start playback of an entirely new BGM.
    def music_start(target_bgm, tag, channel = music_default, fadein = 0.3):
        loop = music_next_loop(target_bgm, tag, None)
        if loop is None:
            return

        target_bgm.cur_loop = loop

        target = music_target_name(target_bgm, loop)
        print("starting up", target)
        if loop.loop_end is None:
            channel.music.play(target, fadein = fadein, loop = False)
        else:
            channel.music.play(target, fadein = fadein)

    # Calculates graceful music transition points.
    def cur_bar(bar_time, offset):
        bar_idx = int(offset / bar_time)
        bar_start = bar_idx * bar_time
        bar_offset = offset - bar_start
        bar_next = (bar_idx + 1) * bar_time
        return (bar_start, bar_offset, bar_next)

    # Transition to the next bit of music loop.
    def music_transition(target_bgm, tag, channel = music_default, fadein = 0.3):
        # Figure out how far we are to the next transition point.
        cur_offset = channel.music.get_pos()
        next_loop = music_next_loop(target_bgm, tag, cur_offset)
        if next_loop is None:
            return

        # If it's less than one bar away, wait out the transition.
        tp_wait = next_loop.section_start - cur_offset
        print("calculated wait", tp_wait)
        if target_bgm.bar_time and tp_wait <= target_bgm.bar_time:
            # Wait until the target time, then switch to the new track at
            # the matching transition point. If the user clicks through, that's
            # okay - just immediately transition it.
            print("pausing for", tp_wait)
            renpy.pause(tp_wait)

            # We skipped the intervening time.
            next_loop = next_loop.with_offset(next_loop.section_start)
        elif target_bgm.bar_time:
            # Wait until the next musical bar to try to be less jarring.
            bar_info = cur_bar(target_bgm.bar_time, cur_offset)
            tp_wait = bar_info[2] - cur_offset

            print("pausing for", tp_wait)
            renpy.pause(tp_wait)

            # We skipped the intervening time.
            next_loop = next_loop.with_offset(next_loop.section_start)

            # We'll play the reverb tail from the current position before starting
            # up the next section of the main music.
            reverb_target = reverb_target_name(target_bgm)
            if reverb_target:
                print("playing reverb tail", reverb_target)
                target_bgm.channel.reverb.play(reverb_target, loop = False)
        else:
            # Probably not music, just go.
            pass

        # Do the switch.
        target_bgm.cur_loop = next_loop
        target = music_target_name(target_bgm, next_loop)
        print("transitioning to", target)
        channel.music.play(target, fadein = fadein)

    # Switch to another loop with the same intra-loop offset. This is
    # useful for switching between two different flavours of the same track.
    def music_switch_to(target_bgm, tag, channel = music_default, fadein = 0.5):
        # Figure out where we are within the current loop.
        cur_pos = channel.music.get_pos()
        cur_loop = target_bgm.cur_loop

        # This can happen with rollback.
        if cur_pos is None:
            cur_pos = 0.0
        if cur_loop is None:
            offset_pos = 0.0
        else:
            offset_pos = cur_pos - cur_loop.section_start

        next_loop = music_next_loop(target_bgm, tag, None)
        if next_loop is None:
            return
        next_loop = next_loop.with_offset(next_loop.section_start + offset_pos)

        print("switching. current state: cur_pos", cur_pos, "cur_loop", cur_loop, "offset_pos", offset_pos, "next_loop", next_loop)

        # Wait until we're on an even bar boundary.
        if target_bgm.bar_time:
            # Wait until the next musical bar to try to be less jarring.
            bar_info = cur_bar(target_bgm.bar_time, cur_pos)
            tp_wait = bar_info[2] - cur_pos

            print("pausing for", tp_wait)
            renpy.pause(tp_wait)

            # We'll play the reverb tail from the current position before starting
            # up the next section of the main music.
            reverb_target = reverb_target_name(target_bgm)
            if reverb_target:
                print("playing reverb tail", reverb_target)
                target_bgm.channel.reverb.play(reverb_target, loop = False)

            # Also adjust the next loop point.
            next_loop = next_loop.with_offset(next_loop.start + tp_wait)

        # Do the switch.
        target_bgm.cur_loop = next_loop
        target = music_target_name(target_bgm, next_loop)
        print("switching to", target)
        channel.music.play(target, fadein = fadein)

    def music_stop(channel = music_default, fadeout = 1):
        channel.stop(fadeout = fadeout)

    def music_start_if_needed(bgm, tag, fadein, channel):
        cur_bgm = channel.music.get_playing()
        if cur_bgm is None:
            music_start(bgm, tag, fadein = fadein, channel = channel)
        elif cur_bgm.find(bgm.fn) >= 0:
            # We're already playing.
            return
        else:
            music_stop(channel, fadein)
            music_start(bgm, tag, fadein = fadein, channel = channel)

    def get_bar_time(bpm):
        return 4 / (bpm / 60.0)

    # One loop segment of a BGM specifier. If 'bars' is not None, then
    # it specifies an offset in seconds to start the song's bars, and
    # treats loop points as 1-based bar indices instead of seconds.
    class BgmLoop:
        def __init__(self, tag, start, loop_start, loop_end, force_next = False, bars = None):
            self.start = start
            self.tag = tag
            self.section_start = start
            self.loop_start = loop_start
            self.loop_end = loop_end
            self.force_next = force_next
            self.bars = bars

        def adjust_bars(self, bpm):
            if self.bars is not None:
                bar_time = get_bar_time(bpm)
                if self.start is not None:
                    self.start = (self.start-1) * bar_time + self.bars
                self.section_start = self.start
                if self.loop_start is not None:
                    self.loop_start = (self.loop_start-1) * bar_time + self.bars
                if self.loop_end is not None:
                    self.loop_end = (self.loop_end-1) * bar_time + self.bars

        # offset is always seconds, not bars.
        def with_offset(self, offset):
            new_item = BgmLoop(self.tag, self.start, self.loop_start, self.loop_end, self.force_next, self.bars)
            new_item.section_start = self.section_start
            new_item.start = offset
            return new_item

        def __str__(self):
            return "<loop: start {0}, tag {1}, section_start {2}, loop_start {3}, loop_end {4}, force_next {5}, bars {6}>".format(
                self.start, self.tag, self.section_start, self.loop_start, self.loop_end, self.force_next, self.bars
            )

    class Bgm:
        # fn = file name of the audio bgm in question
        # parts = array of offsets in seconds which represent
        #   parts of the music. Each part has a start point, and then
        #   a loop start and end point.
        def __init__(self, fn, parts, channel = music_default, bpm = None, reverb = None):
            self.fn = fn
            self.parts = parts
            if bpm is not None:
                for i in self.parts:
                    i.adjust_bars(bpm)
            self.channel = channel
            self.bpm = bpm
            if self.bpm:
                self.bar_time = get_bar_time(self.bpm)
            else:
                self.bar_time = None
            self.reverb = reverb
            self.cur_loop = None

        def start(self, tag, fadein = 1):
            music_start(self, tag, fadein = 1, channel = self.channel)

        def start_if_needed(self, tag, fadein = 0.5):
            music_start_if_needed(self, tag, fadein, channel = self.channel)

        def switch_to(self, tag, fadein = 0.5):
            music_switch_to(self, tag, fadein = fadein, channel = self.channel)

        def transition(self, tag):
            music_transition(self, tag, channel = self.channel)

        def stop(self, fadeout = 1):
            music_stop(self.channel, fadeout)
            self.cur_loop = None

        def volume(self, volume, delay = 1):
            self.channel.set_volume(volume, delay)
