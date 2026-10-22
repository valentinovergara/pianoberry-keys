import unittest
from types import SimpleNamespace as Message
from unittest.mock import Mock
from ivorybox.app import choose_port, dispatch, run

class PianoTests(unittest.TestCase):
    def test_q49_preferred_and_through_excluded(self):
        self.assertEqual(choose_port(['Other 1', 'Midi Through Port-0', 'Alesis Q49 20:0']), 'Alesis Q49 20:0')
        self.assertIsNone(choose_port(['Midi Through Port-0']))
        self.assertIsNone(choose_port(['Other'], 'Q49'))
        self.assertEqual(choose_port(['Other'], 'other'), 'Other')

    def test_velocity_zero_is_note_off(self):
        synth = Mock()
        dispatch(synth, Message(type='note_on', channel=2, note=60, velocity=0))
        synth.send.assert_called_once_with('noteoff', 2, 60)

    def test_expression_and_piano_lock(self):
        synth = Mock()
        for msg in [Message(type='program_change', channel=0, program=20),
                    Message(type='control_change', channel=0, control=0, value=1),
                    Message(type='control_change', channel=0, control=32, value=2)]:
            dispatch(synth, msg)
        synth.send.assert_not_called()
        dispatch(synth, Message(type='control_change', channel=0, control=64, value=127))
        synth.send.assert_called_with('cc', 0, 64, 127)
        dispatch(synth, Message(type='pitchwheel', channel=0, pitch=-8192))
        synth.send.assert_called_with('pitch_bend', 0, 0)
        dispatch(synth, Message(type='note_on', channel=0, note=64, velocity=93))
        synth.send.assert_called_with('noteon', 0, 64, 93)

    def test_hotplug_disconnect_reconnect_and_cleanup(self):
        midi, synth, stop = Mock(), Mock(), Mock()
        first, second = Mock(), Mock()
        first.iter_pending.return_value = [Message(type='note_on', channel=0, note=60, velocity=100)]
        second.iter_pending.return_value = []
        midi.get_input_names.side_effect = [[], ['Q49'], [], ['Q49']]
        midi.open_input.side_effect = [first, second]
        stop.is_set.side_effect = [False, False, False, False, True]
        run(midi, synth, stop, poll=0, ready_sound=False)
        self.assertEqual(midi.open_input.call_count, 2)
        first.close.assert_called_once()
        second.close.assert_called_once()
        self.assertGreaterEqual(synth.panic.call_count, 4)
        synth.send.assert_called_with('noteon', 0, 60, 100)

    def test_open_failure_retries(self):
        midi, synth, stop = Mock(), Mock(), Mock()
        midi.get_input_names.return_value = ['Q49']
        stop.is_set.side_effect = [False, False, True]
        port = Mock()
        port.iter_pending.return_value = []
        midi.open_input.side_effect = [OSError('removed'), port]
        with self.assertLogs('ivorybox', level='ERROR'):
            run(midi, synth, stop, poll=0, ready_sound=False)
        self.assertEqual(midi.open_input.call_count, 2)
        port.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
