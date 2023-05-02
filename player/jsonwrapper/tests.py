import os
import random
import unittest
from handler import Handler, HandlerError  # type: ignore
from pathlib import Path

BASE_DIR = f'{os.sep}'.join(__file__.split(os.sep)[:-1])


class TestHandler(unittest.TestCase):
    def setUp(self) -> None:
        path = str(Path(f"{BASE_DIR}/testconfig.json"))
        self.data = {'c0': 'v0', 'c1': 'v1'}
        self.file = Handler(path, self.data)
        self.file.init()

    def tearDown(self) -> None:
        self.file.init()
        self.file.restore_default()

    def test_set_attr(self) -> None:
        self.assertEqual(self.file.c0, 'v0')
        self.assertEqual(self.file.c1, 'v1')

    def test_len(self) -> None:
        self.assertEqual(len(self.file), len(self.file.read()))

    def test_read(self) -> None:
        data = self.file.read()
        self.assertEqual(self.data, data)
        self.assertEqual(self.file.read(), self.file._config)

    def test_get(self) -> None:
        # Functional
        c0 = self.file.get('c0')
        v0 = self.file._config['c0']
        self.assertEqual(c0, v0)
        self.assertEqual(self.file.read(), self.file._config)

        # Subscript
        c0 = self.file['c0']
        v0 = self.data['c0']
        self.assertEqual(c0, v0)

        default = 5
        val = self.file.get('Not existing key')
        self.assertIsNone(val)

        val = self.file.get('Not existing key', default)
        self.assertEqual(val, default)

        with self.assertRaises(KeyError):
            self.file['Not existing key']

    def test_edit(self) -> None:
        self.file.edit('c0', 'o0')
        o0 = self.file.get('c0')
        self.assertEqual(o0, 'o0')

        with self.assertRaises(HandlerError):
            self.file['c0'] = 'asfas'

    def test_remove_key(self) -> None:
        delete = 'c0'
        self.file.remove_key(delete)
        with self.assertRaises(KeyError):
            self.file[delete]

    def test_restore_default(self) -> None:
        data = self.file.read()
        for i in data:
            data[i] = 'other'
        self.file.write(data)
        self.file.restore_default()
        default = self.file.read()
        self.assertEqual(self.data, default)

    def test_add(self) -> None:
        with self.assertRaises(HandlerError):
            existing_key = list(self.file.read().keys())[0]
            self.file.add(existing_key, 'test')

        new_key = 'test'
        self.file.add(new_key, '...')
        self.assertIn(new_key, self.file.read())

    def test_purge(self) -> None:
        self.file.purge()
        self.assertNotIn(self.file.file, os.listdir())

    def test_update(self) -> None:
        data = {'new_key': '...'}
        self.file.update(data)
        expected = self.data | self.file.read()
        self.assertEqual(self.file.read(), expected)

        with self.assertRaises(HandlerError):
            self.file.update([1, 2, 3])

    def test_clear(self) -> None:
        self.file.clear()
        self.assertEqual(self.file.read(), {})

        self.assertFalse(bool(self.file))

    def test_remove_entries(self) -> None:
        key = random.choice(list(self.file.keys()))
        del self.file._config[key]

        self.file.sync()
        self.assertNotIn(key, self.file.read())

    def test_add_entries(self) -> None:
        key = 'new_key'
        self.file._config[key] = 'new_val'
        self.file.sync()
        self.assertIn(key, self.file.keys())

    def test_eq(self) -> None:
        data = self.data.copy()
        new_file = 'delete_me.json'
        new = Handler(new_file, data)
        new.init()

        self.assertEqual(self.file, new)
        self.assertEqual(self.file, data)
        self.assertNotEqual(self.file, 'test')

        new.purge()

    def test_or(self) -> None:
        data = {'newkey': 'newval'}
        new_file = 'delete_me.json'
        new = Handler(new_file, data)
        new.init()

        piped = self.file | new
        expected = {**new.read(), **self.file.read()}
        self.assertEqual(piped, expected)
        self.assertEqual(self.file.read(), piped)

        self.file.restore_default()
        piped = self.file | data
        self.assertEqual(self.file.read(), piped)

        new.purge()

        with self.assertRaises(TypeError):
            self.file | 'this is not allowed'
