import unittest
from datetime import datetime

from db.announcements.announcements_record import AnnouncementsRecord


class TestAnnouncementsRecord(unittest.TestCase):

    def test_str(self):
        expected = "ID: 1, time: 2022-01-01 00:00:00, channel: 1, message: message, attachment: None"
        provided = AnnouncementsRecord(1, datetime(2022, 1, 1, 0, 0, 0), 1, "message")
        self.assertEqual(provided.__str__(), expected)

    def test_str_with_attachment(self):
        expected = "ID: 1, time: 2022-01-01 00:00:00, channel: 1, message: message, attachment: url"
        provided = AnnouncementsRecord(1, datetime(2022, 1, 1, 0, 0, 0), 1, "message", {"url": "url"})
        self.assertEqual(provided.__str__(), expected)


if __name__ == '__main__':
    unittest.main()
