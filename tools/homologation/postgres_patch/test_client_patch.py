"""Offline scope and security regressions for the client OpenSSL patch."""

import copy
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location(
    "client_patch_builder", HERE / "client_build_and_test.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ClientPatchTests(unittest.TestCase):
    def fixtures(self, kind):
        names = module.POLICY["allowed_package_updates"][kind]
        before = {
            "apks": {name: "3.5.9-r0" for name in names} | {"musl": "unchanged"},
            "source_hashes": {"/workspace/src/example.py": "source"},
            "python_packages": [["psycopg", "3.3.8"]],
            "psycopg": "3.3.8",
            "libpq": 180007,
            "implementation": "c",
            "pip_absent": True,
            "native_hashes": {
                "/usr/lib/" + name: "old"
                for name in module.POLICY["expected_library_hashes"]
            }
            | {"/opt/runtime/lib/libpq.so.5.18": "unchanged"},
        }
        after = copy.deepcopy(before)
        after["apks"].update({name: "3.5.9-r1" for name in names})
        after["native_hashes"].update(
            {
                "/usr/lib/" + name: h
                for name, h in module.POLICY["expected_library_hashes"].items()
            }
        )
        return before, after

    def test_exact_two_runtime_and_three_test_updates_are_accepted(self):
        for kind in ("runtime", "test"):
            module.validate_client_delta(kind, *self.fixtures(kind))

    def test_test_headers_must_also_be_corrected(self):
        before, after = self.fixtures("test")
        after["apks"]["openssl-dev"] = "3.5.9-r0"
        with self.assertRaises(ValueError):
            module.validate_client_delta("test", before, after)

    def test_unrelated_package_or_native_binary_change_is_rejected(self):
        for field in ("apks", "native_hashes"):
            before, after = self.fixtures("runtime")
            after[field][
                "musl" if field == "apks" else "/opt/runtime/lib/libpq.so.5.18"
            ] = "changed"
            with self.assertRaises(ValueError):
                module.validate_client_delta("runtime", before, after)

    def test_source_or_python_dependency_change_is_rejected(self):
        for field in ("source_hashes", "python_packages", "psycopg", "libpq"):
            before, after = self.fixtures("test")
            after[field] = "changed"
            with self.assertRaises(ValueError):
                module.validate_client_delta("test", before, after)

    def test_pip_reintroduction_is_rejected(self):
        before, after = self.fixtures("test")
        after["pip_absent"] = False
        with self.assertRaises(ValueError):
            module.validate_client_delta("test", before, after)

    def test_missing_loaded_openssl_proof_is_rejected(self):
        before, after = self.fixtures("runtime")
        for obj in (before, after):
            obj["native_hashes"].pop("/usr/lib/libssl.so.3")
        with self.assertRaises(ValueError):
            module.validate_client_delta("runtime", before, after)

    def test_new_findings_never_inherit_prior_exceptions(self):
        known = {
            "VulnerabilityID": "GHSA-xmj3-9gf7-h52w",
            "PkgName": "setuptools",
            "InstalledVersion": "83.0.0",
            "Severity": "LOW",
        }
        self.assertTrue(module.accepted_finding(known, "test"))
        self.assertFalse(module.accepted_finding(known, "runtime"))
        for key in known:
            self.assertFalse(module.accepted_finding(known | {key: "changed"}, "test"))

    def test_local_or_unauthorized_builder_is_rejected(self):
        for env, message in [
            ({}, "Disposable"),
            ({"GITHUB_ACTIONS": "true"}, "authorization"),
        ]:
            with patch.dict(module.os.environ, env, clear=True):
                with self.assertRaisesRegex(RuntimeError, message):
                    module.ClientBuild()

    def test_unreviewed_commit_is_rejected(self):
        with patch.dict(
            module.os.environ,
            {
                "GITHUB_ACTIONS": "true",
                "HML_BUILD_AUTHORIZATION": module.POLICY["authorization"],
                "HML_REVIEWED_COMMIT": "a" * 40,
                "GITHUB_SHA": "b" * 40,
            },
            clear=True,
        ):
            with self.assertRaisesRegex(RuntimeError, "SHA mismatch"):
                module.ClientBuild()

    def test_probes_require_no_pip_and_the_reviewed_test_source_manifest(self):
        script = module.probe_script("test")
        compile(script, "probe", "exec")
        compile(module.probe_script("runtime"), "probe", "exec")
        self.assertIn("find_spec('pip') is None", script)
        self.assertIn("/review/source-manifest.json", script)
        self.assertIn("pq.__build_version__==180007", script)


if __name__ == "__main__":
    unittest.main()
