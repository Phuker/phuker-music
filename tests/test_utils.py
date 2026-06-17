import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phuker_music.utils import (
    assert_,
    OsPathProxy,
    match_ext_list,
    is_sub_path,
    get_rel_path,
    get_abs_joined_path,
)


class TestAssert(unittest.TestCase):
    def test_truthy_no_raise(self):
        assert_(True)
        assert_(1)
        assert_('hello')
        assert_([1])
        assert_(object())

    def test_false_raises(self):
        with self.assertRaises(AssertionError):
            assert_(False)

    def test_falsy_zero_raises(self):
        with self.assertRaises(AssertionError):
            assert_(0)

    def test_falsy_none_raises(self):
        with self.assertRaises(AssertionError):
            assert_(None)

    def test_falsy_empty_list_raises(self):
        with self.assertRaises(AssertionError):
            assert_([])

    def test_custom_message_raises(self):
        with self.assertRaisesRegex(AssertionError, 'custom msg'):
            assert_(False, 'custom msg')

    def test_empty_message_raises(self):
        with self.assertRaises(AssertionError) as ctx:
            assert_(False)

        self.assertEqual(str(ctx.exception), '')


class TestOsPathProxy(unittest.TestCase):
    def setUp(self):
        self.os_path = OsPathProxy()

    def test_abspath_returns_string(self):
        result = self.os_path.abspath('foo')
        self.assertIsInstance(result, str)
        self.assertNotIn('\\', result)

    def test_commonpath_returns_string(self):
        result = self.os_path.commonpath(['/a/b', '/a/c'])
        self.assertIsInstance(result, str)
        self.assertNotIn('\\', result)

    def test_dirname_normalizes(self):
        result = self.os_path.dirname('a/b/c')
        self.assertEqual(result, 'a/b')

    def test_expanduser_normalizes(self):
        result = self.os_path.expanduser('~')
        self.assertIsInstance(result, str)
        self.assertNotIn('\\', result)

    def test_join_normalizes_separators(self):
        result = self.os_path.join('a', 'b')
        self.assertIsInstance(result, str)
        self.assertEqual(result, 'a/b')

    def test_normpath_normalizes(self):
        result = self.os_path.normpath('a//b')
        self.assertIsInstance(result, str)
        self.assertNotIn('\\', result)

    def test_realpath_normalizes(self):
        result = self.os_path.realpath('foo')
        self.assertIsInstance(result, str)
        self.assertNotIn('\\', result)

    def test_relpath_normalizes(self):
        result = self.os_path.relpath('/a/b/c/d', '/a/b')
        self.assertIsInstance(result, str)
        self.assertNotIn('\\', result)

    def test_splitext_returns_tuple_untouched(self):
        result = self.os_path.splitext('foo.txt')
        self.assertIsInstance(result, tuple)
        self.assertEqual(result, ('foo', '.txt'))

    def test_exists_returns_bool(self):
        result = self.os_path.exists('/')
        self.assertIsInstance(result, bool)

    def test_basename_not_wrapped(self):
        result = self.os_path.basename('a/b')
        self.assertEqual(result, 'b')

    def test_isfile_returns_bool(self):
        result = self.os_path.isfile('/')
        self.assertIsInstance(result, bool)


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


class TestIsSubPath(unittest.TestCase):
    def test_child_in_parent(self):
        self.assertTrue(is_sub_path('/tmp/a/b', '/tmp/a'))

    def test_same_path(self):
        self.assertTrue(is_sub_path('/tmp/a', '/tmp/a'))

    def test_path_outside_parent(self):
        self.assertFalse(is_sub_path('/tmp/', '/tmp/a/'))
        self.assertFalse(is_sub_path('/tmp/b', '/tmp/a'))


class TestGetRelPath(unittest.TestCase):
    def test_same_path(self):
        self.assertEqual(get_rel_path('/tmp/a', '/tmp/a'), '.')

    def test_child_path(self):
        self.assertEqual(get_rel_path('/tmp/a/b', '/tmp/a'), './b')

    def test_deeper_child_path(self):
        self.assertEqual(get_rel_path('/tmp/a/b/c', '/tmp/a'), './b/c')

    def test_parent_of_start(self):
        self.assertEqual(get_rel_path('/tmp/a', '/tmp/a/b'), './..')


class TestGetAbsJoinedPath(unittest.TestCase):
    def test_single_path(self):
        result = get_abs_joined_path('/tmp')
        self.assertTrue(os.path.isabs(result))
        self.assertNotIn('\\', result)

    def test_multiple_paths(self):
        # Avoid asserting full abspath on Windows: depends on current drive, '/' == 'C:\\' 'D:\\' ...

        result = get_abs_joined_path('/tmp', 'sub', 'file.txt')
        self.assertTrue(os.path.isabs(result))
        self.assertNotIn('\\', result)
        self.assertEqual(result, get_abs_joined_path('/tmp/sub/file.txt'))

        result = get_abs_joined_path('sub1', '/tmp', './sub2/sub3/', '../file.txt')
        self.assertTrue(os.path.isabs(result))
        self.assertNotIn('\\', result)
        self.assertEqual(result, get_abs_joined_path('/tmp/sub2/file.txt'))

    def test_expanduser(self):
        result = get_abs_joined_path('~')
        self.assertTrue(os.path.isabs(result))
        self.assertNotIn('~', result)

    def test_empty_args_raises(self):
        with self.assertRaises(AssertionError):
            get_abs_joined_path()

    def test_empty_string_raises(self):
        with self.assertRaises(AssertionError):
            get_abs_joined_path('')

    def test_none_raises(self):
        with self.assertRaises(AssertionError):
            get_abs_joined_path(None)

    def test_non_string_raises(self):
        with self.assertRaises(AssertionError):
            get_abs_joined_path(123)


if __name__ == '__main__':
    unittest.main()
