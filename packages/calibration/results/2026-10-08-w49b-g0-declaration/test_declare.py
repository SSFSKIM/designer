"""The seal fails closed on changed inputs, post-render hashing, and rewritten parts."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('seal', HERE / 'declare.py')
seal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seal)


class DeclarationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.directory = self.root / 'declaration'
        self.directory.mkdir()
        self.scratch = self.root / 'scratch'
        self.source = self.root / 'source.txt'
        self.source.write_text('measured input\n')
        pins = [dict(path='source.txt', sha256=seal.sha(self.source))]
        self.one = dict(schema='w49b-declaration-1', sources=pins)
        self.write('declaration', self.one)
        self.two = dict(schema='w49b-fit-declaration-1', sources=pins,
            partOneSha256=seal.sha(self.directory / 'declaration.json'), noPostGateAmendment=True,
            onFailure='NEITHER: no seal, no publication, no re-selection')
        self.write('fit-declaration', self.two)

    def write(self, part, doc):
        (self.directory / f'{part}.json').write_text(json.dumps(doc) + '\n')

    def do_seal(self):
        seal.seal(self.directory, self.root, self.scratch)

    def test_valid_and_no_rehash(self):
        self.do_seal()
        seal.verify(self.directory, self.root)
        with self.assertRaisesRegex(ValueError, 'Existing'):
            self.do_seal()

    def test_changed_source_fails(self):
        self.do_seal()
        self.source.write_text('changed\n')
        with self.assertRaisesRegex(ValueError, 'Changed'):
            seal.verify(self.directory, self.root)

    def test_changed_part_is_not_a_new_seal(self):
        self.do_seal()
        path = self.directory / 'fit-declaration.json'
        path.write_text(path.read_text() + ' ')
        with self.assertRaisesRegex(ValueError, 'bytes differ'):
            seal.verify(self.directory, self.root)

    def test_render_prevents_first_hash(self):
        (self.scratch / 'renders' / 'first').mkdir(parents=True)
        with self.assertRaisesRegex(ValueError, 'render exists'):
            self.do_seal()

    def test_part_two_must_name_part_one(self):
        self.two['partOneSha256'] = '0' * 64
        self.write('fit-declaration', self.two)
        with self.assertRaisesRegex(ValueError, 'another part one'):
            self.do_seal()

    def test_no_post_gate_amendment_is_required(self):
        self.two['noPostGateAmendment'] = False
        self.write('fit-declaration', self.two)
        with self.assertRaisesRegex(ValueError, 'DL4 stop'):
            self.do_seal()

    def test_other_wave_refused(self):
        self.one['schema'] = 'w48-declaration-1'
        self.write('declaration', self.one)
        with self.assertRaisesRegex(ValueError, 'schema'):
            self.do_seal()


if __name__ == '__main__':
    unittest.main()
