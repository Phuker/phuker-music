import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phuker_music.utils import match_ext_list


class TestMatchExtList(unittest.TestCase):
    def test_valid_extensions(self):
        ext_list = ('.mp3', '.ogg', '.flac')
        self.assertTrue(match_ext_list('song.mp3', ext_list))
        self.assertTrue(match_ext_list('song.ogg', ext_list))
        self.assertTrue(match_ext_list('song.flac', ext_list))

    def test_case_insensitive(self):
        ext_list = ('.mp3',)
        self.assertTrue(match_ext_list('song.MP3', ext_list))
        self.assertTrue(match_ext_list('song.Mp3', ext_list))
        self.assertTrue(match_ext_list('song.mP3', ext_list))

    def test_invalid_extensions(self):
        ext_list = ('.mp3', '.ogg')
        self.assertFalse(match_ext_list('song.txt', ext_list))
        self.assertFalse(match_ext_list('song.jpg', ext_list))
        self.assertFalse(match_ext_list('song', ext_list))
        self.assertFalse(match_ext_list('song.mp3.bak', ext_list))

    def test_path_with_dirs(self):
        ext_list = ('.flac',)
        self.assertTrue(match_ext_list('/a/b/c/song.flac', ext_list))
        self.assertFalse(match_ext_list('/path/to/song.ogg', ext_list))


if __name__ == '__main__':
    unittest.main()
