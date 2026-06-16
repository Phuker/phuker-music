import os
import sys
import json
import time
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phuker_music import constants
from phuker_music.utils import os_path
from phuker_music import albums_webui


TEST_FILES_DIR = os_path.join(os_path.dirname(__file__), 'files')


class TestAlbumsWebUI(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.albums_config_file_path = os_path.join(self.tmpdir, 'config.json')

        albums_webui.albums_config_file_path = self.albums_config_file_path
        albums_webui.albums_dir_path = self.tmpdir

        albums_webui.scan_status['status'] = 'idle'
        albums_webui.scan_status['scanned_dirs'] = 0
        albums_webui.scan_status['available_albums'] = None
        albums_webui.scan_status['message'] = None

        albums_webui.generate_status['status'] = 'idle'
        albums_webui.generate_status['message'] = None

        self.app = albums_webui.app.test_client()

    def tearDown(self):
        albums_webui.albums_config_file_path = ''
        albums_webui.albums_dir_path = ''

        albums_webui.scan_status['status'] = 'idle'
        albums_webui.scan_status['scanned_dirs'] = 0
        albums_webui.scan_status['available_albums'] = None
        albums_webui.scan_status['message'] = None

        albums_webui.generate_status['status'] = 'idle'
        albums_webui.generate_status['message'] = None

        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _copy_test_audio_dir(self, name):
        src = os_path.join(TEST_FILES_DIR, name)
        dest = os_path.join(self.tmpdir, name)
        shutil.copytree(src, dest)

        player_file_path = os_path.join(self.tmpdir, name, constants.DEFAULT_OUTPUT_FILENAME)
        if os_path.exists(player_file_path):
            os.remove(player_file_path)

    def test_index_page(self):
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Albums config editor', resp.text)

    def test_scan_empty_dir(self):
        resp = self.app.post('/api/scan')
        self.assertEqual(resp.json['status'], 'running')

        time.sleep(1)
        resp = self.app.post('/api/scan')
        data = resp.json
        self.assertEqual(data['status'], 'done')
        self.assertEqual(data['data']['available_albums'], {})

    def test_scan_with_audio_files(self):
        self._copy_test_audio_dir('test 1 file')

        resp = self.app.post('/api/scan')
        self.assertEqual(resp.json['status'], 'running')

        for _ in range(50):
            time.sleep(0.2)
            resp = self.app.post('/api/scan')
            data = resp.json
            if data['status'] == 'done':
                break
        else:
            self.fail('/api/scan status not done')

        self.assertIn('albums_config', data['data'])

        self.assertIn('available_albums', data['data'])
        available = data['data']['available_albums']
        self.assertGreater(len(available), 0)
        self.assertIn('./test 1 file', available)

    def test_scan_resets_after_done(self):
        self._copy_test_audio_dir('test 1 file')

        resp = self.app.post('/api/scan')
        self.assertEqual(resp.json['status'], 'running')

        for _ in range(50):
            time.sleep(0.2)
            resp = self.app.post('/api/scan')
            if resp.json['status'] == 'done':
                break
        else:
            self.fail('/api/scan status not done')

        resp2 = self.app.post('/api/scan')
        self.assertEqual(resp2.json['status'], 'running')

    def test_save_config_creates_file(self):
        self.assertFalse(os_path.isfile(self.albums_config_file_path))

        config = {
            'albums_index_file_path': 'index.html',
            'albums': [],
        }

        resp = self.app.post('/api/save-config', json=config)
        self.assertEqual(resp.json['status'], 'done')

        self.assertTrue(os_path.isfile(self.albums_config_file_path))
        with open(self.albums_config_file_path, 'r', encoding='UTF-8') as f:
            saved_config = json.load(f)

        self.assertIn('albums_index_file_path', saved_config)
        self.assertIn('albums', saved_config)

    def test_save_config_with_albums(self):
        self._copy_test_audio_dir('test 1 file')
        album_dir_path = os_path.join(self.tmpdir, 'test 1 file')
        title = 'title_' + os.urandom(8).hex()

        config = {
            'albums_index_file_path': 'index.html',
            'albums': [
                {
                    'album_dir_path': album_dir_path,
                    'title': title,
                },
            ],
        }

        resp = self.app.post('/api/save-config', json=config)
        self.assertEqual(resp.json['status'], 'done')

        with open(self.albums_config_file_path, 'r', encoding='UTF-8') as f:
            saved_config = json.load(f)

        self.assertEqual(len(saved_config['albums']), 1)
        self.assertEqual(saved_config['albums'][0]['title'], title)

    def test_save_config_with_relative_album_dir_path(self):
        self._copy_test_audio_dir('test 1 file')

        config = {
            'albums_index_file_path': './index.html',
            'albums': [
                {
                    'album_dir_path': './test 1 file',
                    'title': 'Relative Path Test',
                },
            ],
        }

        resp = self.app.post('/api/save-config', json=config)
        self.assertEqual(resp.json['status'], 'done')

    def test_save_config_invalid_input(self):
        resp = self.app.post('/api/save-config', json='not-a-dict', content_type='application/json')
        self.assertEqual(resp.status_code, 500)

        resp = self.app.post('/api/save-config', json={})
        self.assertEqual(resp.status_code, 500)

    def test_save_config_updates_existing_file(self):
        title1 = 'title_1_' + os.urandom(8).hex()
        config1 = {
            'albums_index_file_path': 'index.html',
            'albums': [
                {
                    'album_dir_path': self.tmpdir,
                    'title': title1,
                }
            ],
        }

        resp = self.app.post('/api/save-config', json=config1)
        self.assertEqual(resp.json['status'], 'done')

        title2 = 'title_2_' + os.urandom(8).hex()
        config2 = {
            'albums_index_file_path': 'index.html',
            'albums': [
                {
                    'album_dir_path': self.tmpdir,
                    'title': title2,
                },
            ],
        }

        resp = self.app.post('/api/save-config', json=config2)
        self.assertEqual(resp.json['status'], 'done')

        with open(self.albums_config_file_path, 'r', encoding='UTF-8') as f:
            saved_config = json.load(f)

        self.assertEqual(len(saved_config['albums']), 1)
        self.assertEqual(saved_config['albums'][0]['title'], title2)

    def test_generate(self):
        self._copy_test_audio_dir('test 1 file')

        config = {
            'albums_index_file_path': './index.html',
            'albums': [
                {
                    'album_dir_path': './test 1 file',
                    'title': 'Regen',
                },
            ],
        }
        resp = self.app.post('/api/save-config', json=config)
        self.assertEqual(resp.json['status'], 'done')

        resp = self.app.post('/api/generate')
        self.assertEqual(resp.json['status'], 'running')

        for _ in range(50):
            time.sleep(0.2)
            resp = self.app.post('/api/generate')
            if resp.json['status'] == 'done':
                break
        else:
            self.fail('/api/generate status not done')

        index_file_path = os_path.join(self.tmpdir, 'index.html')
        self.assertTrue(os_path.isfile(index_file_path))

        player_file_path = os_path.join(self.tmpdir, 'test 1 file', constants.DEFAULT_OUTPUT_FILENAME)
        self.assertTrue(os_path.isfile(player_file_path))


if __name__ == '__main__':
    unittest.main()
