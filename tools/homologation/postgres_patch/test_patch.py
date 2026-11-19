"""Offline regression checks for the narrowly scoped PostgreSQL rebuild."""

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location(
    "postgres_patch_builder", HERE / "build_and_test.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PatchSafetyTests(unittest.TestCase):
    def test_patch_accepts_only_the_two_library_upgrades(self):
        before = ["postgresql-common-1-r0", "libcrypto3-3.5.9-r0", "libssl3-3.5.9-r0"]
        after = ["postgresql-common-1-r0", "libcrypto3-3.5.9-r1", "libssl3-3.5.9-r1"]
        self.assertEqual(len(module.validate_package_changes(before, after)[0]), 2)
        with self.assertRaises(ValueError):
            module.validate_package_changes(before, after + ["unexpected-1-r0"])
        with self.assertRaises(ValueError):
            module.validate_package_changes(before, after[:-1])

    def test_zip_rejects_traversal_absolute_and_windows_paths(self):
        for name in [
            "../escape",
            "/etc/shadow",
            "sealed-package/../../x",
            "C:x",
            r"a\b",
        ]:
            self.assertFalse(module.safe_name(name), name)
        self.assertTrue(module.safe_name("sealed-package/source/pyproject.toml"))

    def test_builder_refuses_local_execution_before_any_mutation(self):
        with patch.dict(module.os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "GitHub-hosted"):
                module.Build()

    def test_builder_requires_explicit_authorization(self):
        with patch.dict(module.os.environ, {"GITHUB_ACTIONS": "true"}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "authorization"):
                module.Build()

    def test_builder_refuses_unreviewed_sha(self):
        with patch.dict(
            module.os.environ,
            {
                "GITHUB_ACTIONS": "true",
                "HML_BUILD_AUTHORIZATION": "TS-PLAN-HML-002:patch-postgres",
                "HML_REVIEWED_COMMIT": "a" * 40,
                "GITHUB_SHA": "b" * 40,
            },
            clear=True,
        ):
            with self.assertRaisesRegex(RuntimeError, "SHA mismatch"):
                module.Build()


if __name__ == "__main__":
    unittest.main()
