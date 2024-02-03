import unittest
import src.utils.responses as responses

import src.logger as logger

TAG = "TestResponses"


class TestResponses(unittest.TestCase):
    def test_ohayaho(self):
        provided = "ohayaho"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, responses._ohayoho_responses)

        provided = "Ohayaho"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, responses._ohayoho_responses)

        provided = "OHAYAHO!"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, responses._ohayoho_responses)

        provided = "I've got a whole back of ohayaho in there."
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, responses._ohayoho_responses)

    def test_sixty_nine(self):
        provided = "69"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, responses._sixty_nine_responses)


        provided = "I love 69ing!"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, responses._sixty_nine_responses)


        provided = "nice."
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, responses._sixty_nine_responses)


        provided = "not nice."
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIsNone(response)


        provided = "asdf69adsf"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIn(response, responses._sixty_nine_responses)


        provided = "1234695678"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        self.assertIsNone(response)

    def test_i_love(self):
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
        # TODO: figure out how to test this for more than one response
        self.assertEqual(response, "Syo loves you, too!")

        provided = "I love Masato"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        # TODO: figure out how to test this for more than one response
        self.assertEqual(response, "Masato loves you, too!")

        provided = "I know he's weird, but I love Otoya so much!"
        response = responses.get_response(provided)
        logger.d(TAG, f"provided: {provided}, response: {response}")
        # TODO: figure out how to test this for more than one response
        self.assertEqual(response, "Otoya loves you, too!")


if __name__ == '__main__':
    unittest.main()
