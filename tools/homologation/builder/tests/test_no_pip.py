"""Test derivation preserves reviewed sources and fails on output reuse."""

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_test_image import write_hardened_dockerfile


class NoPipTests(unittest.TestCase):
    def test_source_preserved_and_only_derived_test_target_added(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "original.Dockerfile"
            original = b"FROM pinned AS test\nRUN echo original\nFROM test AS runtime\n"
            source.write_bytes(original)
            result = write_hardened_dockerfile(source, root)
            self.assertEqual(
                hashlib.sha256(source.read_bytes()).digest(),
                hashlib.sha256(original).digest(),
            )
            derived = result.read_bytes()
            self.assertTrue(derived.startswith(original))
            self.assertIn(b"FROM test AS test-without-pip", derived)
            self.assertIn(b"-m pip uninstall --yes pip", derived)
            self.assertIn(b"ensurepip/_bundled", derived)
            self.assertIn(b"assert importlib.util.find_spec('pip') is None", derived)
            with self.assertRaises(ValueError):
                write_hardened_dockerfile(source, root)


if __name__ == "__main__":
    unittest.main()
