# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Ahmii Labs. See LICENSE.
import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout

from _load import ROOT


def _load_root_script():
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_pack", os.path.join(ROOT, "check_pack.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class CheckPack(unittest.TestCase):
    def setUp(self):
        self.cp = _load_root_script()
        self.tmp = tempfile.mkdtemp()
        self.copy = os.path.join(self.tmp, "pack")
        shutil.copytree(ROOT, self.copy, ignore=shutil.ignore_patterns("__pycache__", ".git"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_the_real_pack_is_clean(self):
        results = self.cp.run(ROOT)
        self.assertEqual({k: v for k, v in results.items() if v}, {})

    def test_cli_exit_code_and_json(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = self.cp.main([ROOT, "--json"])
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(buf.getvalue())["ok"])

    def test_missing_license_fails(self):
        os.remove(os.path.join(self.copy, "LICENSE"))
        self.assertIn("LICENSE is missing", self.cp.check_license(self.copy))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(self.cp.main([self.copy]), 1)

    def test_license_must_keep_the_earlier_notice(self):
        path = os.path.join(self.copy, "LICENSE")
        with open(path, encoding="utf-8") as fh:
            lines = [l for l in fh.read().split("\n") if l.count("Copyright (c)") == 0
                     or "Ahmii Labs" in l]
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        self.assertTrue(any("earlier copyright" in p for p in self.cp.check_license(self.copy)))

    def test_missing_header_is_reported(self):
        path = os.path.join(self.copy, "replica-brand", "sweep.py")
        with open(path, encoding="utf-8") as fh:
            text = fh.read().replace("SPDX-License-Identifier: MIT", "")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        self.assertTrue(any("sweep.py" in p for p in self.cp.check_headers(self.copy)))

    def test_broken_link_and_em_dash_are_reported(self):
        path = os.path.join(self.copy, "README.md")
        with open(path, "a", encoding="utf-8") as fh:
            fh.write("\n[gone](nope/missing.md) a%sb\n" % chr(0x2014))
        self.assertTrue(any("nope/missing.md" in p for p in self.cp.check_links(self.copy)))
        self.assertTrue(any("README.md" in p for p in self.cp.check_dashes(self.copy)))

    def test_version_mismatch_is_reported(self):
        path = os.path.join(self.copy, ".claude-plugin", "marketplace.json")
        with open(path) as fh:
            d = json.load(fh)
        d["plugins"][0]["version"] = "9.9.9"
        with open(path, "w") as fh:
            json.dump(d, fh)
        self.assertTrue(any("versions differ" in p for p in self.cp.check_manifests(self.copy)))


if __name__ == "__main__":
    unittest.main()
