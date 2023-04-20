import unittest
import configparser

from core import translate


class TranslateTest(unittest.TestCase):

    def setUp(self):
        self.cfg = configparser.ConfigParser()
        self.cfg['general'] = {
            'confirm': 'bestätigen',
            'close': 'schließen',
            'cancel': 'abbrechen'
        }
        self.cfg['editor'] = {
            'save_as': 'Speichern unter',
            'open': 'Datei öffnen',
            'file_list': 'Dateiliste'
        }

    def test__match__getattr__(self):
        m = translate.Match(self.cfg)

        self.assertEqual(m.general.confirm, 'bestätigen')
        self.assertEqual(m.general.cancel, 'abbrechen')
        self.assertEqual(m.general.close, 'schließen')

        self.assertEqual(m.editor.save_as, 'Speichern unter')
        self.assertEqual(m.editor.open, 'Datei öffnen')
        self.assertEqual(m.editor.file_list, 'Dateiliste')

        self.assertEqual(m.editor.bar, 'editor.BAR')
        self.assertEqual(m.foo.bar, 'FOO.BAR')
