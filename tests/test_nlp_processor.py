
import unittest
import sys
import os

# Add the parent directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import NLPProcessor, TaskType

class TestNLPProcessor(unittest.TestCase):

    def setUp(self):
        self.nlp = NLPProcessor()

    def test_extract_intent(self):
        # Test file operation intents
        self.assertEqual(self.nlp.extract_intent("open the file report.txt")[0], TaskType.FILE_OPERATION)
        self.assertEqual(self.nlp.extract_intent("create a new document")[0], TaskType.FILE_OPERATION)
        self.assertEqual(self.nlp.extract_intent("delete the folder images")[0], TaskType.FILE_OPERATION)

        # Test browser action intents
        self.assertEqual(self.nlp.extract_intent("open google.com")[0], TaskType.BROWSER_ACTION)
        self.assertEqual(self.nlp.extract_intent("search for cats")[0], TaskType.BROWSER_ACTION)
        self.assertEqual(self.nlp.extract_intent("click the login button")[0], TaskType.BROWSER_ACTION)

        # Test system command intents
        self.assertEqual(self.nlp.extract_intent("check memory usage")[0], TaskType.SYSTEM_COMMAND)
        self.assertEqual(self.nlp.extract_intent("restart the computer")[0], TaskType.SYSTEM_COMMAND)
        self.assertEqual(self.nlp.extract_intent("install python")[0], TaskType.SYSTEM_COMMAND)

        # Test application task intents
        self.assertEqual(self.nlp.extract_intent("open the browser")[0], TaskType.APPLICATION_TASK)
        self.assertEqual(self.nlp.extract_intent("close the text editor")[0], TaskType.APPLICATION_TASK)
        self.assertEqual(self.nlp.extract_intent("send an email to john.doe@example.com")[0], TaskType.APPLICATION_TASK)

        # Test workflow intents
        self.assertEqual(self.nlp.extract_intent("automate the backup process")[0], TaskType.WORKFLOW)
        self.assertEqual(self.nlp.extract_intent("schedule a reminder for tomorrow")[0], TaskType.WORKFLOW)
        self.assertEqual(self.nlp.extract_intent("combine the two reports")[0], TaskType.WORKFLOW)

    def test_extract_parameters(self):
        # Test file operation parameters
        params = self.nlp.extract_parameters("open the file /home/user/documents/report.txt", TaskType.FILE_OPERATION)
        self.assertEqual(params['filename'], '/home/user/documents/report.txt')

        # Test browser action parameters
        params = self.nlp.extract_parameters("open https://www.google.com", TaskType.BROWSER_ACTION)
        self.assertEqual(params['url'], 'https://www.google.com')

        params = self.nlp.extract_parameters("search for 'cute cats'", TaskType.BROWSER_ACTION)
        self.assertEqual(params['query'], 'cute cats')

        # Test application task parameters
        params = self.nlp.extract_parameters("open the text editor", TaskType.APPLICATION_TASK)
        self.assertEqual(params['application'], 'editor')

if __name__ == '__main__':
    unittest.main()
