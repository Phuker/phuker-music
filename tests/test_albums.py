import os
import sys
import shutil
import json
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phuker_music.albums import get_config, main
from phuker_music.utils import os_path


TEST_FILES_DIR = os_path.join(os_path.dirname(__file__), 'files')


class TestGetConfigFromDocs(unittest.TestCase):
    def test_valid_config(self):
        albums_config_file_path = os_path.join(TEST_FILES_DIR, 'albums.test.json')

        albums_config = get_config(albums_config_file_path)

        self.assertIn('albums_index_file_path', albums_config)
        self.assertIn('albums', albums_config)
        self.assertEqual(len(albums_config['albums']), 4)
        self.assertTrue(os_path.isabs(albums_config['albums_index_file_path']))
        self.assertTrue(albums_config['albums_index_file_path'].endswith('albums.html'))

    def test_album_fields(self):
        albums_config_file_path = os_path.join(TEST_FILES_DIR, 'albums.test.json')

        albums_config = get_config(albums_config_file_path)

        for album in albums_config['albums']:
            self.assertIn('album_dir_path', album)
            self.assertIsInstance(album['album_dir_path'], str)
            self.assertTrue(os_path.isabs(album['album_dir_path']))

            self.assertIn('title', album)
            self.assertIsInstance(album['title'], str)

            self.assertIn('cover_file', album)

            self.assertIn('recursively', album)
            self.assertIsInstance(album['recursively'], bool)

            self.assertIn('sort_type', album)
            self.assertIsInstance(album['sort_type'], str)

            self.assertIn('output_filename', album)
            self.assertEqual(album['output_filename'], 'player.html')

    def test_default_fields(self):
        albums_config_file_path = os_path.join(TEST_FILES_DIR, 'albums.test.json')

        albums_config = get_config(albums_config_file_path)

        self.assertEqual(albums_config['albums'][0]['recursively'], False)
        self.assertEqual(albums_config['albums'][0]['sort_type'], 'filename')
        self.assertIsNone(albums_config['albums'][0]['cover_file'])

    def test_specific_album_config(self):
        albums_config_file_path = os_path.join(TEST_FILES_DIR, 'albums.test.json')

        albums_config = get_config(albums_config_file_path)

        album3 = albums_config['albums'][2]
        self.assertEqual(album3['sort_type'], 'mtime_desc')
        self.assertEqual(album3['recursively'], False)
        self.assertIsNotNone(album3['cover_file'])

        album4 = albums_config['albums'][3]
        self.assertEqual(album4['recursively'], True)
        self.assertIsNotNone(album4['cover_file'])


class TestGetConfigFromTemp(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.albums_config_file_path = os_path.join(self.tmpdir, 'config.json')

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _write_config(self, albums_config):
        with open(self.albums_config_file_path, 'w', encoding='UTF-8') as f:
            json.dump(albums_config, f)
            f.write('\n')

    def test_nonexistent_album_dir_path(self):
        self._write_config({
            'albums_index_file_path': './index.html',
            'albums': [
                {
                    'album_dir_path': 'nonexistent_subdir',
                    'title': 'Test',
                },
            ],
        })

        with self.assertRaisesRegex(AssertionError, 'album_dir_path does not exist'):
            get_config(self.albums_config_file_path)

    def test_invalid_type_recursively(self):
        test_dir = os_path.join(self.tmpdir, 'testdir')
        os.makedirs(test_dir)
        self._write_config({
            'albums_index_file_path': os_path.join(self.tmpdir, 'index.html'),
            'albums': [
                {
                    'album_dir_path': test_dir,
                    'title': 'Test',
                    'recursively': 'not-a-bool',
                },
            ],
        })

        with self.assertRaisesRegex(AssertionError, 'invalid album_config:'):
            get_config(self.albums_config_file_path)

    def test_missing_title(self):
        test_dir = os_path.join(self.tmpdir, 'dirname_' + os.urandom(8).hex())
        os.makedirs(test_dir)
        self._write_config({
            'albums_index_file_path': os_path.join(self.tmpdir, 'index.html'),
            'albums': [
                {
                    'album_dir_path': test_dir,
                },
            ],
        })

        albums_config = get_config(self.albums_config_file_path)
        self.assertEqual(albums_config['albums'][0]['title'], os_path.basename(test_dir))

    def test_empty_title(self):
        test_dir = os_path.join(self.tmpdir, 'dirname_' + os.urandom(8).hex())
        os.makedirs(test_dir)
        self._write_config({
            'albums_index_file_path': os_path.join(self.tmpdir, 'index.html'),
            'albums': [
                {
                    'album_dir_path': test_dir,
                    'title': '',
                },
            ],
        })

        albums_config = get_config(self.albums_config_file_path)
        self.assertEqual(albums_config['albums'][0]['title'], os_path.basename(test_dir))


class TestMain(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_main_generates_player_and_index(self):
        src = os_path.join(TEST_FILES_DIR, 'test 1 file')
        album_dir = os_path.join(self.tmpdir, 'album')
        shutil.copytree(src, album_dir)

        player_html = os_path.join(album_dir, 'player.html')
        if os_path.exists(player_html):
            os.remove(player_html)

        title = 'title_' + os.urandom(8).hex()
        albums_config = {
            'albums_index_file_path': os_path.join(self.tmpdir, 'index.html'),
            'albums': [
                {
                    'album_dir_path': album_dir,
                    'title': title,
                },
            ],
        }

        albums_config_file_path = os_path.join(self.tmpdir, 'config.json')
        with open(albums_config_file_path, 'w', encoding='UTF-8') as f:
            json.dump(albums_config, f)
            f.write('\n')

        main(albums_config_file_path, overwrite=True)

        self.assertTrue(os_path.exists(player_html))
        with open(player_html, 'r', encoding='UTF-8') as f:
            self.assertIn(title, f.read())

        index_html = albums_config['albums_index_file_path']
        self.assertTrue(os_path.exists(index_html))

        with open(index_html, 'r', encoding='UTF-8') as f:
            content = f.read()

        self.assertIn(title, content)
        self.assertIn('<html', content.lower())

    def test_main_file_exists_no_force(self):
        src = os_path.join(TEST_FILES_DIR, 'test 1 file')
        album_dir = os_path.join(self.tmpdir, 'album')
        shutil.copytree(src, album_dir)

        player_html = os_path.join(album_dir, 'player.html')
        if os_path.exists(player_html):
            os.remove(player_html)

        title = 'title_' + os.urandom(8).hex()
        albums_config = {
            'albums_index_file_path': os_path.join(self.tmpdir, 'index.html'),
            'albums': [
                {
                    'album_dir_path': album_dir,
                    'title': title,
                },
            ],
        }

        albums_config_file_path = os_path.join(self.tmpdir, 'config.json')
        with open(albums_config_file_path, 'w', encoding='UTF-8') as f:
            json.dump(albums_config, f)
            f.write('\n')

        main(albums_config_file_path, overwrite=True)  # first run succeeds

        with self.assertRaises(FileExistsError):
            main(albums_config_file_path, overwrite=False)

    def test_main_title_xss_encoding(self):
        src = os_path.join(TEST_FILES_DIR, 'test 1 file')
        album_dir = os_path.join(self.tmpdir, 'album')
        shutil.copytree(src, album_dir)

        title = '<script>alert(1);</script>'
        albums_config = {
            'albums_index_file_path': os_path.join(self.tmpdir, 'index.html'),
            'albums': [
                {
                    'album_dir_path': album_dir,
                    'title': title,
                },
            ],
        }

        albums_config_file_path = os_path.join(self.tmpdir, 'config.json')
        with open(albums_config_file_path, 'w', encoding='UTF-8') as f:
            json.dump(albums_config, f)
            f.write('\n')

        main(albums_config_file_path, overwrite=True)

        index_html = albums_config['albums_index_file_path']
        with open(index_html, 'r', encoding='UTF-8') as f:
            index_content = f.read()

        player_html = os_path.join(album_dir, 'player.html')
        with open(player_html, 'r', encoding='UTF-8') as f:
            player_content = f.read()

        self.assertNotIn('<script>alert(1);</script>', index_content)
        self.assertNotIn('<script>alert(1);</script>', player_content)
        self.assertIn('&lt;script&gt;alert(1);&lt;/script&gt;', index_content)
        self.assertIn('&lt;script&gt;alert(1);&lt;/script&gt;', player_content)


if __name__ == '__main__':
    unittest.main()
