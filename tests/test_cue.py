import unittest
from unittest.mock import Mock, patch, call
from ivorybox.cue import ReadyCue
from ivorybox.app import run

class ReadyCueTests(unittest.TestCase):
    def test_arpeggio_finishes_and_releases_every_note(self):
        synth = Mock()
        cue = ReadyCue(synth)
        cue.start(10)
        cue.update(9)
        synth.send.assert_not_called()
        cue.update(10)
        synth.send.assert_called_once_with('noteon', 15, 60, 55)
        cue.update(11)
        ons = [c.args[2] for c in synth.send.call_args_list if c.args[0] == 'noteon']
        offs = [c.args[2] for c in synth.send.call_args_list if c.args[0] == 'noteoff']
        self.assertEqual(ons, [60, 64, 67, 72])
        self.assertCountEqual(offs, ons)
        self.assertFalse(cue.active)
        self.assertFalse(cue.events)

    def test_cancel_releases_only_cue_notes_and_schedules_no_more(self):
        synth = Mock()
        cue = ReadyCue(synth)
        cue.start(0)
        cue.update(.13)
        cue.cancel()
        before = synth.send.call_count
        cue.update(100)
        self.assertEqual(synth.send.call_count, before)
        self.assertEqual(synth.send.call_args_list[-2:], [call('noteoff', 15, 60), call('noteoff', 15, 64)])

    def test_sound_waits_for_controller_and_runs_once_despite_reconnect(self):
        midi, synth, stop = Mock(), Mock(), Mock()
        midi.get_input_names.side_effect = [[], ['Q49'], [], ['Q49']]
        port = Mock()
        port.iter_pending.return_value = []
        midi.open_input.return_value = port
        stop.is_set.side_effect = [False] * 4 + [True]
        with patch('ivorybox.app.ReadyCue') as cue:
            run(midi, synth, stop, poll=0)
            cue.return_value.start.assert_called_once()
        self.assertEqual(midi.open_input.call_count, 2)

    def test_disabled_cue_never_starts(self):
        midi, synth, stop = Mock(), Mock(), Mock()
        midi.get_input_names.return_value = ['Q49']
        midi.open_input.return_value.iter_pending.return_value = []
        stop.is_set.side_effect = [False, True]
        with patch('ivorybox.app.ReadyCue') as cue:
            run(midi, synth, stop, ready_sound=False)
            cue.return_value.start.assert_not_called()

if __name__ == '__main__':
    unittest.main()
