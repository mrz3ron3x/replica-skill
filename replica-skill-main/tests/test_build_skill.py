# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Ahmii Labs. See LICENSE.
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
import zipfile

from _load import ROOT


def _load_builder():
    spec = importlib.util.spec_from_file_location("build_skill", os.path.join(ROOT, "build_skill.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class BuildSkill(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.b = _load_builder()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.folder = cls.b.build_folder(cls.tmp.name)
        cls.zip = cls.b.build_zip(cls.folder, cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def skill_md(self):
        with open(os.path.join(self.folder, "SKILL.md"), encoding="utf-8") as fh:
            return fh.read()

    def test_zip_has_one_top_folder_with_skill_md(self):
        with zipfile.ZipFile(self.zip) as zf:
            names = zf.namelist()
        self.assertIn("replica/SKILL.md", names)
        self.assertEqual({n.split("/")[0] for n in names}, {"replica"})
        self.assertIn("replica/LICENSE", names)

    def test_frontmatter_respects_the_skill_limits(self):
        m = re.match(r"^---\n(.*?)\n---\n", self.skill_md(), re.S)
        self.assertTrue(m)
        fm = m.group(1)
        self.assertIn("name: replica\n", fm + "\n")
        desc = re.search(r"description: >-\n((?:  .*\n)+)", fm + "\n").group(1)
        flat = " ".join(desc.split())
        self.assertLessEqual(len(flat), 1024)
        self.assertGreater(len(flat), 300)
        self.assertLess(len(self.skill_md().splitlines()), 500)
        self.assertNotIn("{{version}}", self.skill_md())

    def test_every_stage_has_a_reference_and_is_routed(self):
        for stage in self.b.STAGES:
            self.assertTrue(os.path.isfile(os.path.join(self.folder, "references", stage + ".md")), stage)
            self.assertIn("`references/%s.md`" % stage, self.skill_md())

    def test_every_path_the_router_names_exists(self):
        paths = set(re.findall(r"`((?:references|scripts|assets)/[A-Za-z0-9_.\-]+)`", self.skill_md()))
        self.assertGreater(len(paths), 20)
        for p in paths:
            self.assertTrue(os.path.exists(os.path.join(self.folder, p)), p)

    def test_no_stale_paths_or_slash_commands_in_references(self):
        for stage in self.b.STAGES:
            with open(os.path.join(self.folder, "references", stage + ".md"), encoding="utf-8") as fh:
                text = fh.read()
            for bad in ("../replica-", "~/.claude", "this folder", "/replica-", "---\nname:"):
                self.assertNotIn(bad, text, "%s: %s" % (stage, bad))

    def test_tool_commands_point_at_scripts(self):
        for stage in self.b.STAGES:
            with open(os.path.join(self.folder, "references", stage + ".md"), encoding="utf-8") as fh:
                text = fh.read()
            for call in re.findall(r"python3 (\S+\.py)", text):
                self.assertTrue(call.startswith("scripts/"), "%s: %s" % (stage, call))
                self.assertTrue(os.path.isfile(os.path.join(self.folder, call)), call)

    def test_tools_run_from_inside_the_build(self):
        scripts = os.path.join(self.folder, "scripts")
        for fn in sorted(os.listdir(scripts)):
            if fn.endswith(".py"):
                r = subprocess.run([sys.executable, os.path.join(scripts, fn), "--help"],
                                   capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, fn)
        r = subprocess.run([sys.executable, os.path.join(scripts, "parity.py"),
                            os.path.join(self.folder, "assets", "features.csv")],
                           capture_output=True, text=True)
        self.assertIn("Parity", r.stdout)
        self.assertTrue(os.path.isfile(os.path.join(scripts, "themes.json")))

    def test_no_em_dashes_in_the_build(self):
        for dirpath, _, files in os.walk(self.folder):
            for fn in files:
                with open(os.path.join(dirpath, fn), encoding="utf-8") as fh:
                    self.assertNotIn(chr(0x2014), fh.read(), fn)

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as other:
            f2 = self.b.build_folder(other)
            z2 = self.b.build_zip(f2, other)
            with open(self.zip, "rb") as a, open(z2, "rb") as b:
                self.assertEqual(a.read(), b.read())

    def test_prebuilt_release_matches_the_source(self):
        release = os.path.join(ROOT, "releases", "replica.zip")
        self.assertTrue(os.path.isfile(release), "run: python3 build_skill.py && cp dist/replica.zip releases/")
        with open(release, "rb") as a, open(self.zip, "rb") as b:
            self.assertEqual(a.read(), b.read(), "releases/replica.zip is stale, rebuild it")


if __name__ == "__main__":
    unittest.main()
