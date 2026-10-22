import unittest
from unittest.mock import Mock
from types import SimpleNamespace
from ivorybox.app import dispatch
from ivorybox.engine import Synth

class PresetTests(unittest.TestCase):
    def test_program_selects_curated_voice(self):
        for program,preset in [(0,'piano'),(1,'byte'),(2,'nebula')]:
            synth=Mock()
            dispatch(synth,SimpleNamespace(type='program_change',program=program,channel=0))
            synth.select_preset.assert_called_once_with(preset)

    def test_switch_resets_notes_selects_all_channels_and_applies_effects(self):
        s=object.__new__(Synth)
        s.lib=Mock();s.lib.fluid_synth_program_select.return_value=0
        s.settings=1;s.synth=2;s.sfid=3;s.preset='piano'
        s.select_preset('nebula')
        self.assertEqual(s.lib.fluid_synth_program_select.call_count,16)
        s.lib.fluid_synth_program_select.assert_called_with(2,15,3,0,89)
        self.assertEqual(s.preset,'nebula')
        calls=s.lib.fluid_synth_cc.call_args_list
        self.assertTrue(any(c.args==(2,0,120,0) for c in calls))
        self.assertTrue(any(c.args==(2,0,91,110) for c in calls))
        s.panic()
        s.lib.fluid_synth_cc.assert_called_with(2,15,93,80)
