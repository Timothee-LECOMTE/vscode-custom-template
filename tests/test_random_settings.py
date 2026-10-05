import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import random_settings


COLORS = {
    "activityBar.background": "#201629",
    "activityBar.activeBorder": "#faf7f2",
}


class ReplaceColorSettingsTests(unittest.TestCase):
    def test_replaces_only_the_color_customization_value(self):
        original = (
            '{\n'
            '    "editor.fontSize": 14,\n'
            '    "workbench.colorCustomizations": {"old": "#000000"},\n'
            '    "files.autoSave": "afterDelay"\n'
            '}\n'
        )

        updated = random_settings.replace_color_settings(original, COLORS)
        parsed = json.loads(updated)

        self.assertEqual(parsed["editor.fontSize"], 14)
        self.assertEqual(parsed["files.autoSave"], "afterDelay")
        self.assertEqual(parsed["workbench.colorCustomizations"], COLORS)
        self.assertTrue(updated.startswith(original[: original.index('"workbench.colorCustomizations"')]))
        self.assertTrue(updated.endswith(original[original.index('    "files.autoSave"'):]))

    def test_adds_color_customization_to_existing_jsonc(self):
        original = (
            '{\n'
            '    // Keep this user setting and comment.\n'
            '    "editor.fontSize": 14,\n'
            '}\n'
        )

        updated = random_settings.replace_color_settings(original, COLORS)

        self.assertIn("// Keep this user setting and comment.", updated)
        self.assertIn('"editor.fontSize": 14', updated)
        self.assertIn('"workbench.colorCustomizations":', updated)
        self.assertTrue(updated.endswith("}\n"))
        parsed = random_settings.parse_jsonc(updated)
        self.assertEqual(parsed["editor.fontSize"], 14)
        self.assertEqual(parsed["workbench.colorCustomizations"], COLORS)

    def test_adds_color_customization_to_an_empty_object(self):
        updated = random_settings.replace_color_settings("{}\n", COLORS)

        self.assertEqual(json.loads(updated)["workbench.colorCustomizations"], COLORS)

    def test_rejects_a_non_object_root(self):
        with self.assertRaisesRegex(ValueError, "objet JSON à la racine"):
            random_settings.replace_color_settings("[]", COLORS)

    def test_parses_jsonc_comments_and_trailing_commas(self):
        theme = random_settings.parse_jsonc(
            '{\n'
            '    "workbench.colorCustomizations": {\n'
            '        "editor.background": "#101216", // Preserve # in strings.\n'
            '    },\n'
            '}\n'
        )

        self.assertEqual(
            theme["workbench.colorCustomizations"]["editor.background"],
            "#101216",
        )


class ApplyThemeTests(unittest.TestCase):
    def test_creates_vscode_folder_and_settings_file_in_current_directory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            with (
                patch.object(Path, "cwd", return_value=workspace),
                patch.object(random_settings, "load_theme_colors", return_value=COLORS),
                patch("sys.stderr"),
            ):
                random_settings.main()

            settings_file = workspace / ".vscode" / "settings.json"
            self.assertTrue(settings_file.is_file())
            self.assertEqual(
                json.loads(settings_file.read_text(encoding="utf-8"))[
                    "workbench.colorCustomizations"
                ],
                COLORS,
            )

    def test_loads_a_theme_containing_jsonc_comments(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            theme_file = Path(temporary_directory) / "theme" / "settings.json"
            theme_file.parent.mkdir()
            theme_file.write_text(
                '// Example theme\n'
                '{\n'
                '    "workbench.colorCustomizations": {\n'
                '        "editor.background": "#101216", // Comment\n'
                '    },\n'
                '}\n',
                encoding="utf-8",
            )
            with (
                patch.object(random_settings, "THEME_DIR", theme_file.parent.parent),
                patch.object(random_settings.random, "choice", return_value=theme_file),
                patch("sys.stderr"),
            ):
                colors = random_settings.load_theme_colors()

        self.assertEqual(colors, {"editor.background": "#101216"})

    def test_preserves_existing_settings_when_applying_theme(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            vscode_directory = workspace / ".vscode"
            vscode_directory.mkdir()
            settings_file = vscode_directory / "settings.json"
            settings_file.write_text(
                '{\n'
                '    // Preserve the existing comment.\n'
                '    "editor.fontSize": 14,\n'
                '}\n',
                encoding="utf-8",
            )

            with (
                patch.object(Path, "cwd", return_value=workspace),
                patch.object(random_settings, "load_theme_colors", return_value=COLORS),
                patch("sys.stderr"),
            ):
                random_settings.main()

            updated = settings_file.read_text(encoding="utf-8")
            settings = random_settings.parse_jsonc(updated)
            self.assertIn("// Preserve the existing comment.", updated)
            self.assertEqual(settings["editor.fontSize"], 14)
            self.assertEqual(settings["workbench.colorCustomizations"], COLORS)


if __name__ == "__main__":
    unittest.main()
