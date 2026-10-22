import unittest
from unittest.mock import Mock, patch
from ivorybox.app import configure_headphone_volume

class MixerTests(unittest.TestCase):
    @patch('ivorybox.app.subprocess.run')
    def test_default_does_not_change_mixer(self,run):
        configure_headphone_volume(None,'default')
        run.assert_not_called()

    @patch('ivorybox.app.subprocess.run')
    def test_mixer_command_is_fixed_and_unprivileged(self,run):
        run.return_value=Mock(stdout='PCM 88%')
        configure_headphone_volume(88,'plughw:CARD=Headphones,DEV=0')
        run.assert_called_once_with(['amixer','-c','Headphones','sset','PCM','88%'],check=True,capture_output=True,text=True,timeout=5)

    @patch('ivorybox.app.subprocess.run')
    def test_invalid_or_other_device_is_rejected_without_running_command(self,run):
        for percent,device in [(-1,'plughw:CARD=Headphones'),(101,'plughw:CARD=Headphones'),(88,'default')]:
            with self.assertRaises(ValueError):configure_headphone_volume(percent,device)
        run.assert_not_called()
