import os
import sys
import unittest
import unittest.mock
from pathlib import Path
from logger import Logger
from .logger import Config


BASE_DIR = Path(__file__).parent


class TestLogger(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = Logger(1)

    def tearDown(self) -> None:
        self.logger = Logger(1)

    def test_invalid_instance(self) -> None:
        with self.assertRaises(ValueError, msg='An instance with level=0 is created'):
            Logger(0)

        with self.assertRaises(ValueError, msg='An instance with level=6 is created'):
            Logger(6)

        logger = Logger(2)
        with self.assertRaises(ValueError, msg='A settings instance changed level above limit after creation'):  # noqa
            logger.settings.level = 6

        logger = Logger(2)
        with self.assertRaises(ValueError, msg='A settings instance changed level above limit after creation'):  # noqa
            logger.settings.level = 0

    def test_instance_counter(self) -> None:
        Config._INSTANCE = 0
        l1 = Logger()
        self.assertEqual(l1.settings._INSTANCE, 1, msg="First instance counter is wrong")
        l2 = Logger()
        self.assertEqual(l2.settings._INSTANCE, 2, msg="Second instance counter is wrong")

        self.assertEqual(l1.settings._INSTANCE, 1, msg="Repeated instance counter is wrong")

    def test_update_settings(self) -> None:
        self.logger.settings.update(success=4)
        self.assertEqual(self.logger.settings['success'], 4)

        with self.assertRaises(TypeError, msg="self.logger object is directly assignable"):
            self.logger.settings['success'] = 4  # type: ignore

        with self.assertRaises(ValueError, msg="not existing key passed into self.settings"):
            self.logger.settings.update(not_exists=4)

        with self.assertRaises(TypeError, msg="String passed as value in self.settings"):
            self.logger.settings.update(success='4')  # type: ignore

        with self.assertRaises(ValueError, msg='0 Passed as valid key in self.settings'):
            self.logger.settings.update(success=0)

        with self.assertRaises(ValueError, msg="Above the allowed limit passed as valid key in self.settings"):  # noqa
            self.logger.settings.update(success=6)

        with self.assertRaises(AttributeError, msg="self.settings is overwritable (`=`)"):
            self.logger.settings.settings = 'fsaf'  # type: ignore

        self.logger.settings.update(success=2, info=1)
        self.assertEqual(self.logger.settings['success'], 2, msg='Error in updating 2 values at once at `success`')  # noqa
        self.assertEqual(self.logger.settings['info'], 1, msg='Error in updating 2 values at once at `info`')  # noqa

    def test_get_settings(self) -> None:
        with self.assertRaises(AttributeError, msg="self.settings is overwritable (`=`) instead of read-only"):  # noqa
            self.logger.settings = 'fsaf'  # type: ignore

    def test_get_setting(self) -> None:
        self.assertEqual(self.logger.settings.get('info'), 3, msg="settings.get() returns value from wrong key or the value has changed")  # noqa
        with self.assertRaises(KeyError):
            self.logger.settings.get('not_existing')

    def test_iter_next(self) -> None:
        for i2 in self.logger.settings:
            ...

        for i1 in self.logger.settings:
            ...

        self.assertEqual(i1, i2, msg="There is something wrong with Config.__iter__ and Config.__next__. Maybe the index (self._iter) is not refreshing correctly")  # noqa

    def test_log_to_file(self) -> None:
        msg = 'This should be written in the file'
        file = Path(f"{BASE_DIR}tests.txt")
        logger = Logger(1, str(file))

        # Redirect the annoying log to '/dev/null'
        # (or according file for other platforms) and bring it back
        std_out = sys.stdout
        f = open(os.devnull, mode='w')
        sys.stdout = f
        logger.info(msg)
        f.close()
        sys.stdout = std_out

        self.assertTrue(os.path.exists(file))
        with open(file, mode='r') as f:
            self.assertEqual(f"[INFO]: {msg}", f.read()[:-1])  # Slice to remove '\n' from the file
        os.remove(file)
