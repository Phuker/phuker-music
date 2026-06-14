import os
import sys
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phuker_music.player import (
    get_duration_str,
    get_hash,
    get_music_groups,
    generate,
)
from phuker_music.utils import os_path


TEST_FILES_DIR = os_path.join(os_path.dirname(__file__), 'files')


class TestGetDurationStr(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(get_duration_str(0), '0:00')

    def test_seconds_only(self):
        self.assertEqual(get_duration_str(1), '0:01')
        self.assertEqual(get_duration_str(59), '0:59')

    def test_minutes(self):
        self.assertEqual(get_duration_str(60), '1:00')
        self.assertEqual(get_duration_str(61), '1:01')
        self.assertEqual(get_duration_str(227), '3:47')
        self.assertEqual(get_duration_str(3547), '59:07')
        self.assertEqual(get_duration_str(3599), '59:59')

    def test_hours(self):
        self.assertEqual(get_duration_str(3600), '1:00:00')
        self.assertEqual(get_duration_str(3601), '1:00:01')
        self.assertEqual(get_duration_str(3660), '1:01:00')
        self.assertEqual(get_duration_str(3661), '1:01:01')
        self.assertEqual(get_duration_str(3723), '1:02:03')
        self.assertEqual(get_duration_str(7200), '2:00:00')
        self.assertEqual(get_duration_str(47045), '13:04:05')


class TestGetHash(unittest.TestCase):
    def test_consistency(self):
        self.assertEqual(get_hash('hello'), get_hash('hello'))

    def test_different_inputs(self):
        self.assertNotEqual(get_hash('hello'), get_hash('world'))

    def test_length(self):
        self.assertEqual(len(get_hash('test')), 16)


class TestGetMusicGroups(unittest.TestCase):
    def test_empty_dir(self):
        path = os_path.join(TEST_FILES_DIR, 'test 0 files')

        groups = get_music_groups(path)
        self.assertEqual(groups, [])

    def test_one_file(self):
        path = os_path.join(TEST_FILES_DIR, 'test 1 file')

        groups = get_music_groups(path)
        self.assertEqual(len(groups), 1)

        group = groups[0]
        self.assertEqual(group['name'], '')
        self.assertEqual(len(group['music_info_sub_list']), 1)

        music = group['music_info_sub_list'][0]
        self.assertEqual(music['index'], 0)
        self.assertEqual(music['path'], 'sin 880Hz 10s.m4a')
        self.assertEqual(music['name'], 'sin 880Hz 10s')
        self.assertIn('file_size_str', music)
        self.assertIn('duration_str', music)

    def test_mtime_desc_sort(self):
        path = os_path.join(TEST_FILES_DIR, 'test n files with cover sort_type mtime_desc')

        groups = get_music_groups(path, sort_type='mtime_desc')
        self.assertEqual(len(groups), 1)

        sub_list = groups[0]['music_info_sub_list']
        self.assertEqual(len(sub_list), 3)

        paths = [m['path'] for m in sub_list]
        self.assertIn('sin 440Hz 5s.wav', paths)
        self.assertIn('sin 494Hz 6s.flac', paths)
        self.assertIn('sin 554Hz 7s.mp3', paths)
        mtimes = [os_path.getmtime(os_path.join(path, p)) for p in paths]
        self.assertEqual(mtimes, sorted(mtimes, reverse=True))

    def test_default_sort_is_filename(self):
        path = os_path.join(TEST_FILES_DIR, 'test n files with cover sort_type mtime_desc')

        groups = get_music_groups(path)  # default sort_type='filename'
        self.assertEqual(len(groups), 1)

        sub_list = groups[0]['music_info_sub_list']
        paths = [m['path'] for m in sub_list]
        self.assertEqual(paths, sorted(paths))

    def test_recursive(self):
        path = os_path.join(TEST_FILES_DIR, 'test n files with cover recursively')

        groups = get_music_groups(path, recursively=True)
        self.assertEqual(len(groups), 4)

        group_names = [g['name'] for g in groups]
        self.assertIn('', group_names)
        self.assertIn('Disk 1/Disk 1.1', group_names)
        self.assertIn('Disk 1/Disk 1.2', group_names)
        self.assertIn('Disk 2', group_names)

        total_files = sum(len(g['music_info_sub_list']) for g in groups)
        self.assertEqual(total_files, 6)

    def test_non_recursive_only_top_level(self):
        path = os_path.join(TEST_FILES_DIR, 'test n files with cover recursively')

        groups = get_music_groups(path, recursively=False)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]['name'], '')
        self.assertEqual(len(groups[0]['music_info_sub_list']), 2)

    def test_invalid_sort_type(self):
        path = os_path.join(TEST_FILES_DIR, 'test 1 file')

        with self.assertRaises(ValueError):
            get_music_groups(path, sort_type='invalid')


class TestGenerate(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        src = os_path.join(TEST_FILES_DIR, 'test 1 file')
        self.album_dir_path = os_path.join(self.tmpdir, 'album_' + os.urandom(8).hex())
        shutil.copytree(src, self.album_dir_path)

        player_html = os_path.join(self.album_dir_path, 'player.html')
        if os_path.exists(player_html):
            os.remove(player_html)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_generate_success(self):
        title = 'title_' + os.urandom(8).hex()

        generate({'album_dir_path': self.album_dir_path, 'title': title})

        output = os_path.join(self.album_dir_path, 'player.html')
        self.assertTrue(os_path.exists(output))

        with open(output, 'r', encoding='UTF-8') as f:
            content = f.read()

        self.assertIn(title, content)
        self.assertIn('<html', content.lower())

    def test_file_exists_no_force(self):
        title = 'title_' + os.urandom(8).hex()

        generate({'album_dir_path': self.album_dir_path, 'title': title})

        with self.assertRaises(FileExistsError):
            generate({'album_dir_path': self.album_dir_path, 'title': 'Second'}, overwrite=False)

    def test_file_exists_with_force(self):
        title1 = 'title_' + os.urandom(8).hex()
        title2 = 'title_' + os.urandom(8).hex()

        generate({'album_dir_path': self.album_dir_path, 'title': title1})
        generate({'album_dir_path': self.album_dir_path, 'title': title2}, overwrite=True)

        with open(os_path.join(self.album_dir_path, 'player.html'), 'r', encoding='UTF-8') as f:
            content = f.read()

        self.assertNotIn(title1, content)
        self.assertIn(title2, content)

    def test_generate_title_defaults_to_dirname(self):
        generate({'album_dir_path': self.album_dir_path})

        output = os_path.join(self.album_dir_path, 'player.html')
        self.assertTrue(os_path.exists(output))

        with open(output, 'r', encoding='UTF-8') as f:
            content = f.read()

        self.assertIn(os_path.basename(self.album_dir_path), content)
        self.assertIn('<html', content.lower())

    def test_generate_title_empty_string_fallback(self):
        generate({'album_dir_path': self.album_dir_path, 'title': ''})

        output = os_path.join(self.album_dir_path, 'player.html')
        self.assertTrue(os_path.exists(output))

        with open(output, 'r', encoding='UTF-8') as f:
            content = f.read()

        self.assertIn(os_path.basename(self.album_dir_path), content)

    def test_missing_cover_file(self):
        with self.assertRaisesRegex(AssertionError, 'cover_file does not exist'):
            generate({'album_dir_path': self.album_dir_path, 'title': 'Test', 'cover_file': 'nonexistent.jpg'})


if __name__ == '__main__':
    unittest.main()
