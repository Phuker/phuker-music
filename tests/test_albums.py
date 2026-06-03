import os
import sys
import shutil
import json
import tempfile
import re
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phuker_music.albums import get_config, main

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), 'files')


class TestGetConfigFromDocs(unittest.TestCase):
    def test_valid_config(self):
        config_file = os.path.join(TEST_FILES_DIR, 'albums.test.json')

        config = get_config(config_file)

        self.assertIn('albums_index_file_path', config)
        self.assertIn('albums', config)
        self.assertEqual(len(config['albums']), 4)
        self.assertTrue(os.path.isabs(config['albums_index_file_path']))
        self.assertTrue(config['albums_index_file_path'].endswith('albums.html'))

    def test_album_fields(self):
        config_file = os.path.join(TEST_FILES_DIR, 'albums.test.json')

        config = get_config(config_file)

        for album in config['albums']:
            self.assertIn('dir_path', album)
            self.assertIsInstance(album['dir_path'], str)
            self.assertTrue(os.path.isabs(album['dir_path']))

            self.assertIn('title', album)
            self.assertIsInstance(album['title'], str)

            self.assertIn('cover_file', album)

            self.assertIn('recursively', album)
            self.assertIsInstance(album['recursively'], bool)

            self.assertIn('sort_type', album)
            self.assertIsInstance(album['sort_type'], str)

            self.assertIn('overwrite', album)
            self.assertIsInstance(album['overwrite'], bool)

            self.assertIn('output_filename', album)
            self.assertEqual(album['output_filename'], 'player.html')

    def test_default_fields(self):
        config_file = os.path.join(TEST_FILES_DIR, 'albums.test.json')

        config = get_config(config_file)

        self.assertEqual(config['albums'][0]['recursively'], False)
        self.assertEqual(config['albums'][0]['sort_type'], 'filename')
        self.assertEqual(config['albums'][0]['overwrite'], True)
        self.assertIsNone(config['albums'][0]['cover_file'])

    def test_specific_album_config(self):
        config_file = os.path.join(TEST_FILES_DIR, 'albums.test.json')

        config = get_config(config_file)

        album3 = config['albums'][2]
        self.assertEqual(album3['sort_type'], 'mtime_desc')
        self.assertEqual(album3['recursively'], False)
        self.assertIsNotNone(album3['cover_file'])

        album4 = config['albums'][3]
        self.assertEqual(album4['recursively'], True)
        self.assertIsNotNone(album4['cover_file'])


class TestGetConfigFromTemp(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmpdir, 'config.json')

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_config(self, config_data):
        with open(self.config_path, 'w', encoding='UTF-8') as f:
            json.dump(config_data, f)

    def test_nonexistent_dir_path(self):
        self._write_config({
            'albums_index_file_path': './index.html',
            'albums': [
                {
                    'dir_path': '/nonexistent/path/12345',
                    'title': 'Test',
                },
            ],
        })

        with self.assertRaisesRegex(AssertionError, 'Album dir path not exist'):
            get_config(self.config_path)

    def test_invalid_type_recursively(self):
        test_dir = os.path.join(self.tmpdir, 'testdir')
        os.makedirs(test_dir)
        self._write_config({
            'albums_index_file_path': os.path.join(self.tmpdir, 'index.html'),
            'albums': [
                {
                    'dir_path': test_dir,
                    'title': 'Test',
                    'recursively': 'not-a-bool',
                },
            ],
        })

        with self.assertRaisesRegex(AssertionError, re.escape("invalid config['albums'][0]['recursively']")):
            get_config(self.config_path)

    def test_missing_title(self):
        test_dir = os.path.join(self.tmpdir, 'dirname_' + os.urandom(8).hex())
        os.makedirs(test_dir)
        self._write_config({
            'albums_index_file_path': os.path.join(self.tmpdir, 'index.html'),
            'albums': [
                {
                    'dir_path': test_dir,
                },
            ],
        })

        config = get_config(self.config_path)
        self.assertEqual(config['albums'][0]['title'], os.path.basename(test_dir))

    def test_empty_title(self):
        test_dir = os.path.join(self.tmpdir, 'dirname_' + os.urandom(8).hex())
        os.makedirs(test_dir)
        self._write_config({
            'albums_index_file_path': os.path.join(self.tmpdir, 'index.html'),
            'albums': [
                {
                    'dir_path': test_dir,
                    'title': '',
                },
            ],
        })

        config = get_config(self.config_path)
        self.assertEqual(config['albums'][0]['title'], os.path.basename(test_dir))


class TestMain(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_main_generates_player_and_index(self):
        src = os.path.join(TEST_FILES_DIR, 'test 1 file')
        album_dir = os.path.join(self.tmpdir, 'album')
        shutil.copytree(src, album_dir)

        player_html = os.path.join(album_dir, 'player.html')
        if os.path.exists(player_html):
            os.remove(player_html)

        title = 'title_' + os.urandom(8).hex()
        config_data = {
            'albums_index_file_path': os.path.join(self.tmpdir, 'index.html'),
            'albums': [
                {
                    'dir_path': album_dir,
                    'title': title,
                },
            ],
        }

        config_path = os.path.join(self.tmpdir, 'config.json')
        with open(config_path, 'w', encoding='UTF-8') as f:
            json.dump(config_data, f)

        main(config_path, force=True)

        self.assertTrue(os.path.exists(player_html))
        with open(player_html, 'r', encoding='UTF-8') as f:
            self.assertIn(title, f.read())

        index_html = config_data['albums_index_file_path']
        self.assertTrue(os.path.exists(index_html))

        with open(index_html, 'r', encoding='UTF-8') as f:
            content = f.read()

        self.assertIn(title, content)
        self.assertIn('<html', content.lower())

    def test_main_file_exists_no_force(self):
        src = os.path.join(TEST_FILES_DIR, 'test 1 file')
        album_dir = os.path.join(self.tmpdir, 'album')
        shutil.copytree(src, album_dir)

        player_html = os.path.join(album_dir, 'player.html')
        if os.path.exists(player_html):
            os.remove(player_html)

        title = 'title_' + os.urandom(8).hex()
        config_data = {
            'albums_index_file_path': os.path.join(self.tmpdir, 'index.html'),
            'albums': [
                {
                    'dir_path': album_dir,
                    'title': title,
                },
            ],
        }

        config_path = os.path.join(self.tmpdir, 'config.json')
        with open(config_path, 'w', encoding='UTF-8') as f:
            json.dump(config_data, f)

        main(config_path, force=True)  # first run succeeds

        with self.assertRaises(FileExistsError):
            main(config_path, force=False)


if __name__ == '__main__':
    unittest.main()
