import unittest
from unittest.mock import Mock, call
from types import SimpleNamespace
from ivorybox.app import dispatch
from ivorybox.engine import Synth
from ivorybox.presets import PRESETS, PROGRAM_PRESETS, FILTER, GENERATORS

class PresetTests(unittest.TestCase):
    def synth(self):
        s=object.__new__(Synth)
        s.lib=Mock();s.lib.fluid_synth_program_select.return_value=0
        s.settings=1;s.synth=2;s.sfid=3;s.preset='piano';s.layered=False
        return s

    def test_program_selects_curated_voice(self):
        self.assertEqual(list(PROGRAM_PRESETS),list(range(7)))
        self.assertEqual([PROGRAM_PRESETS[i] for i in range(3)],['piano','byte','nebula'])
        for program,preset in PROGRAM_PRESETS.items():
            synth=Mock()
            dispatch(synth,SimpleNamespace(type='program_change',program=program,channel=0))
            synth.select_preset.assert_called_once_with(preset)

    def test_switch_resets_notes_selects_all_channels_and_applies_effects(self):
        s=self.synth()
        s.select_preset('nebula')
        self.assertEqual(s.lib.fluid_synth_program_select.call_count,16)
        s.lib.fluid_synth_program_select.assert_called_with(2,15,3,0,89)
        self.assertEqual(s.preset,'nebula')
        calls=s.lib.fluid_synth_cc.call_args_list
        self.assertTrue(any(c.args==(2,0,120,0) for c in calls))
        self.assertTrue(any(c.args==(2,0,91,110) for c in calls))
        s.panic()
        s.lib.fluid_synth_cc.assert_called_with(2,15,93,80)

    def test_layer_receives_notes_sustain_and_expression_once(self):
        s=self.synth();s.select_preset('abyss');s.lib.reset_mock()
        for method,args in [('noteon',(0,60,80)),('noteoff',(0,60)),('cc',(0,64,127)),('pitch_bend',(0,9000))]:
            s.send(method,*args)
            fn=getattr(s.lib,'fluid_synth_'+method)
            self.assertEqual(fn.call_args_list,[call(2,*args),call(2,16,*args[1:])])

    def test_leaving_layered_mode_clears_secondary_voices_and_filter(self):
        s=self.synth();s.select_preset('abyss');s.lib.reset_mock()
        s.select_preset('piano')
        self.assertFalse(s.layered)
        self.assertIn(call(2,31,120,0),s.lib.fluid_synth_cc.call_args_list)
        for generator in GENERATORS:
            self.assertIn(call(2,0,generator,0.0),s.lib.fluid_synth_set_gen.call_args_list)
        s.lib.reset_mock();s.send('noteon',0,60,90)
        s.lib.fluid_synth_noteon.assert_called_once_with(2,0,60,90)

    def test_pulse_lead_is_monophonic_per_channel_only(self):
        s=self.synth();s.select_preset('pixel-quest');s.lib.reset_mock()
        s.send('noteon',2,60,80)
        self.assertEqual(s.lib.mock_calls,[call.fluid_synth_all_sounds_off(2,2),call.fluid_synth_noteon(2,2,60,80)])
        s.lib.reset_mock();s.send('noteoff',2,60)
        s.lib.fluid_synth_all_sounds_off.assert_not_called()

    def test_panic_restores_offsets_for_both_layers(self):
        s=self.synth();s.select_preset('abyss');s.lib.reset_mock();s.panic()
        calls=s.lib.fluid_synth_set_gen.call_args_list
        self.assertIn(call(2,0,FILTER,-1800),calls)
        self.assertIn(call(2,16,FILTER,-1800),calls)
        self.assertEqual(s.lib.fluid_synth_pitch_bend.call_count,32)
