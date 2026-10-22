"""A short readiness arpeggio scheduled by the MIDI loop, without sleeping."""
class ReadyCue:
    def __init__(self, synth):
        self.synth = synth
        self.events = []
        self.active = set()
        self.started = 0.0

    def start(self, now):
        self.cancel()
        self.started = now
        # C major, played softly on MIDI channel 16. Duration: 0.72 seconds.
        self.events = sorted(
            [(i * 0.12, True, note) for i, note in enumerate((60, 64, 67, 72))]
            + [(i * 0.12 + 0.18, False, note) for i, note in enumerate((60, 64, 67))]
            + [(0.72, False, 72)]
        )

    def update(self, now):
        while self.events and now - self.started >= self.events[0][0]:
            _, on, note = self.events.pop(0)
            if on:
                self.synth.send("noteon", 15, note, 55)
                self.active.add(note)
            else:
                self.synth.send("noteoff", 15, note)
                self.active.discard(note)

    def cancel(self):
        self.events.clear()
        for note in sorted(self.active):
            self.synth.send("noteoff", 15, note)
        self.active.clear()
