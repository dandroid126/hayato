import unittest
import src.utils.responses as responses

import src.logger as logger

TAG = "TestResponses"


class TestResponses(unittest.TestCase):
    def test_ohayaho(self):
        expected = ["OHAYAHO!!!!!"]
        
        provided = "ohayaho"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, expected)

        provided = "Ohayaho"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, expected)

        provided = "OHAYAHO!"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, expected)

        provided = "I've got a whole back of ohayaho in there."
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, expected)

    def test_sixty_nine(self):
        expected = ["nice."]
        
        provided = "69"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, expected)


        provided = "I love 69ing!"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, expected)

        provided = "nice."
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, expected)

        provided = "not nice."
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIsNone(response)

        provided = "asdf69adsf"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, expected)

        provided = "1234695678"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIsNone(response)

    def test_i_love(self):
        expected = ["Syo loves you, too!", "Masato loves you, too!", "Otoya loves you, too!"]

        provided = "i love these pancakes"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIsNone(response)

        provided = "i love you"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIsNone(response)

        provided = "i love syo"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertEqual(response, expected[0])

        provided = "I love Masato"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertEqual(response, expected[1])

        provided = "I know he's weird, but I love Otoya so much!"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertEqual(response, expected[2])

    def test_i_love_hayato(self):
        expected = ["I LOVE YOU, TOO!", "AWWW, THANKS! HAYATO LOVES YOU, TOO!", "<:hayato:1206817126959161394>"]
        
        provided = "i love hayato"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, expected)

        provided = "I LOVE HAYATO"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, expected)

        provided = "I love Hayato"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, expected)

        provided = "I love Hayato!"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, expected)

    def test_starish_forever(self):
        expected = "WE ARE AND YOU ARE ST☆RISH!"
        provided = "starish forever"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertEqual(response, expected)


if __name__ == '__main__':
    unittest.main()
