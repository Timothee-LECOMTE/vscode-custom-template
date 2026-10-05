import json
import random
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THEME_DIR = ROOT / "json_file"
COLOR_SETTINGS_KEY = "workbench.colorCustomizations"
DEFAULT_INDENT = "    "


def skip_trivia(text, index):
    while index < len(text):
        if text[index].isspace():
            index += 1
            continue
        if text.startswith("//", index):
            newline = text.find("\n", index + 2)
            if newline == -1:
                return len(text)
            index = newline + 1
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            if end == -1:
                raise ValueError("Commentaire JSONC non terminé")
            index = end + 2
            continue
        break
    return index


def parse_string(text, index):
    try:
        value, end = json.JSONDecoder().raw_decode(text[index:])
    except json.JSONDecodeError as error:
        raise ValueError("Chaîne JSON invalide dans settings.json") from error
    if not isinstance(value, str):
        raise ValueError("Une clé JSON doit être une chaîne")
    return value, index + end


def parse_jsonc(text):
    without_comments = []
    cursor = 0
    in_string = False
    escaped = False
    while cursor < len(text):
        char = text[cursor]
        if in_string:
            without_comments.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            cursor += 1
            continue
        if char == '"':
            in_string = True
            without_comments.append(char)
            cursor += 1
            continue
        if text.startswith("//", cursor):
            newline = text.find("\n", cursor + 2)
            if newline == -1:
                break
            without_comments.append("\n")
            cursor = newline + 1
            continue
        if text.startswith("/*", cursor):
            end = text.find("*/", cursor + 2)
            if end == -1:
                raise ValueError("Commentaire JSONC non terminé")
            comment = text[cursor : end + 2]
            without_comments.extend("\n" for char in comment if char == "\n")
            cursor = end + 2
            continue
        without_comments.append(char)
        cursor += 1

    comment_free_text = "".join(without_comments)
    without_trailing_commas = []
    cursor = 0
    in_string = False
    escaped = False
    while cursor < len(comment_free_text):
        char = comment_free_text[cursor]
        if in_string:
            without_trailing_commas.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
            without_trailing_commas.append(char)
        elif char == ",":
            lookahead = cursor + 1
            while lookahead < len(comment_free_text) and comment_free_text[lookahead].isspace():
                lookahead += 1
            if lookahead >= len(comment_free_text) or comment_free_text[lookahead] not in "}]":
                without_trailing_commas.append(char)
        else:
            without_trailing_commas.append(char)
        cursor += 1
    return json.loads("".join(without_trailing_commas))


def parse_value_end(text, index):
    if index >= len(text):
        raise ValueError("Valeur JSON manquante dans settings.json")
    if text[index] == '"':
        _, end = parse_string(text, index)
        return end
    if text[index] not in "[{":
        end = index
        while end < len(text) and text[end] not in ",}]":
            if text[end].isspace() or text.startswith("//", end) or text.startswith("/*", end):
                break
            end += 1
        if end == index:
            raise ValueError("Valeur JSON invalide dans settings.json")
        return end

    expected_closers = []
    in_string = False
    escaped = False
    cursor = index
    while cursor < len(text):
        char = text[cursor]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            cursor += 1
            continue
        if text.startswith("//", cursor):
            newline = text.find("\n", cursor + 2)
            if newline == -1:
                raise ValueError("Valeur JSON incomplète dans settings.json")
            cursor = newline + 1
            continue
        if text.startswith("/*", cursor):
            comment_end = text.find("*/", cursor + 2)
            if comment_end == -1:
                raise ValueError("Commentaire JSONC non terminé")
            cursor = comment_end + 2
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            expected_closers.append("}")
        elif char == "[":
            expected_closers.append("]")
        elif char in "}]":
            if not expected_closers or expected_closers.pop() != char:
                raise ValueError("Valeur JSON mal formée dans settings.json")
            if not expected_closers:
                return cursor + 1
        cursor += 1
    raise ValueError("Valeur JSON incomplète dans settings.json")


def property_indentation(text, index):
    line_start = text.rfind("\n", 0, index) + 1
    prefix = text[line_start:index]
    if prefix.isspace():
        return prefix
    return DEFAULT_INDENT


def line_indentation(text, index):
    line_start = text.rfind("\n", 0, index) + 1
    prefix = text[line_start:index]
    if prefix.isspace():
        return prefix
    return ""


def format_value(value, indentation):
    rendered = json.dumps(value, indent=4, ensure_ascii=True)
    return rendered.replace("\n", "\n" + indentation)


def replace_color_settings(text, color_settings):
    root_start = skip_trivia(text, 0)
    if root_start >= len(text) or text[root_start] != "{":
        raise ValueError("Le fichier settings.json doit contenir un objet JSON à la racine")

    cursor = skip_trivia(text, root_start + 1)
    if cursor < len(text) and text[cursor] == "}":
        root_end = cursor
        properties = []
    else:
        properties = []
        while True:
            cursor = skip_trivia(text, cursor)
            if cursor >= len(text) or text[cursor] != '"':
                raise ValueError("Clé JSON invalide à la racine de settings.json")
            key, key_end = parse_string(text, cursor)
            colon = skip_trivia(text, key_end)
            if colon >= len(text) or text[colon] != ":":
                raise ValueError("Séparateur manquant dans settings.json")
            value_start = skip_trivia(text, colon + 1)
            value_end = parse_value_end(text, value_start)
            properties.append((key, value_start, value_end, cursor))
            cursor = skip_trivia(text, value_end)
            if cursor < len(text) and text[cursor] == ",":
                cursor = skip_trivia(text, cursor + 1)
                if cursor < len(text) and text[cursor] == "}":
                    root_end = cursor
                    break
                continue
            if cursor < len(text) and text[cursor] == "}":
                root_end = cursor
                break
            raise ValueError("Séparateur ou fin d’objet manquant dans settings.json")

    for key, value_start, value_end, key_start in properties:
        if key == COLOR_SETTINGS_KEY:
            indentation = property_indentation(text, key_start)
            replacement = format_value(color_settings, indentation)
            return text[:value_start] + replacement + text[value_end:]

    if properties:
        last_value_end = properties[-1][2]
        separator = skip_trivia(text, last_value_end)
        indentation = property_indentation(text, properties[0][3])
        if separator < root_end and text[separator] == ",":
            insertion = separator + 1
            prefix = "\n" + indentation
        else:
            insertion = last_value_end
            prefix = ",\n" + indentation
    else:
        insertion = root_start + 1
        root_indentation = line_indentation(text, root_start)
        indentation = root_indentation + DEFAULT_INDENT
        prefix = "\n" + indentation

    rendered = format_value(color_settings, indentation)
    if properties:
        return text[:insertion] + prefix + json.dumps(COLOR_SETTINGS_KEY) + ": " + rendered + text[insertion:]
    suffix = "\n" + root_indentation
    return text[:insertion] + prefix + json.dumps(COLOR_SETTINGS_KEY) + ": " + rendered + suffix + text[insertion:]


def load_theme_colors():
    settings_files = sorted(THEME_DIR.rglob("settings.json"))
    if not settings_files:
        raise SystemExit(f"Aucun settings.json trouvé dans {THEME_DIR}")

    selected_file = random.choice(settings_files)
    content = selected_file.read_text(encoding="utf-8")
    try:
        _, separator, theme_content = content.partition("\n")
        if not separator:
            theme_content = content
        theme = parse_jsonc(theme_content)
        color_settings = theme["workbench.colorCustomizations"]
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Thème invalide dans {selected_file}") from error
    if not isinstance(color_settings, dict):
        raise ValueError(f"Couleurs invalides dans {selected_file}")
    print(f"Thème choisi : {selected_file.parent.name}", file=sys.stderr)
    return color_settings


def main():
    settings_file = Path.cwd() / ".vscode" / "settings.json"
    color_settings = load_theme_colors()
    settings_file.parent.mkdir(parents=True, exist_ok=True)

    if settings_file.exists():
        current_settings = settings_file.read_text(encoding="utf-8")
        updated_settings = replace_color_settings(current_settings, color_settings)
    else:
        updated_settings = json.dumps(
            {COLOR_SETTINGS_KEY: color_settings},
            indent=4,
            ensure_ascii=True,
        ) + "\n"

    settings_file.write_text(updated_settings, encoding="utf-8")
    print(f"Thème appliqué dans {settings_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
