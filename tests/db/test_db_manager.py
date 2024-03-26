import os
import unittest

from src.db import db_manager
from src.db.db_manager import DbManager
from tests import test_constants


class TestDbClient(unittest.TestCase):

    def setUp(self):
        if os.path.exists(test_constants.TEST_DB_PATH):
            os.remove(test_constants.TEST_DB_PATH)
        else:
            print("test.db doesn't exist. Skipping deleting it.")
        self.db_manager = DbManager(test_constants.TEST_DB_PATH)

    def test_get_db_schema(self):
        self.assertEqual(self.db_manager.get_db_schema_version(), db_manager.DB_SCHEMA_VERSION)

    def test_upgrade_db_schema(self):
        db_manager.DB_SCHEMA_VERSION = db_manager.DB_SCHEMA_VERSION + 1
        self.db_manager.upgrade_db_schema()
        self.assertEqual(self.db_manager.get_db_schema_version(), db_manager.DB_SCHEMA_VERSION)


if __name__ == '__main__':
    unittest.main()
