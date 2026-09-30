import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THEME_DIR = ROOT / "json_file"

# Each profile is (activity bar, accent, status bar, remote accent).
PALETTES = {
    "pirate-red": ("#35161d", "#ffd166", "#632437", "#f07156"),
    "sword-green": ("#142d27", "#91d18b", "#204d3d", "#d8b45c"),
    "sea-blue": ("#14283b", "#77c7e8", "#1d405b", "#f3b35c"),
    "sunny-orange": ("#382016", "#ffc16a", "#60321b", "#68c5cf"),
    "cherry-pink": ("#351d2a", "#ff9db8", "#5a2c42", "#f6c66a"),
    "shadow-violet": ("#241b31", "#c4a2ef", "#3c2852", "#70d5d0"),
    "akatsuki-red": ("#21151c", "#f06b75", "#481e2a", "#d4d2da"),
    "ninja-orange": ("#352017", "#ffad62", "#5e3020", "#83d0e8"),
    "leaf-green": ("#17261e", "#b8d989", "#2b4933", "#e6ad62"),
    "mist-silver": ("#202a32", "#c5d4df", "#34444f", "#77c7e8"),
    "ice-blue": ("#192838", "#a8dcf5", "#263e57", "#e0a9cf"),
    "hollow-red": ("#291921", "#fa8293", "#482333", "#a8d5e8"),
    "reaper-black": ("#17181e", "#e7e1d5", "#292b37", "#a88de0"),
    "dragon-orange": ("#321c16", "#ffbd65", "#5b2e1b", "#f0784c"),
    "prince-blue": ("#172535", "#9bc9f5", "#253b59", "#efc969"),
    "namek-green": ("#18291e", "#a9d875", "#294735", "#d59bdd"),
    "saiyan-gold": ("#312116", "#ffdc70", "#55331d", "#ef785c"),
    "majin-rose": ("#321a29", "#ffa2d2", "#592b4b", "#e9d776"),
    "cosmic-purple": ("#211b32", "#c7b5f5", "#392b59", "#7dd1e3"),
    "phoenix-fire": ("#321917", "#ffaf62", "#612920", "#f06b5d"),
    "pegasus-blue": ("#18243a", "#f1d38a", "#293e65", "#e99a83"),
    "andromeda-rose": ("#2e1c32", "#f2a6cf", "#4d3155", "#8de0ca"),
    "athena-gold": ("#2d2520", "#f3d88c", "#51412c", "#d895a4"),
    "cobra-crimson": ("#25181d", "#f2746c", "#47242b", "#e3c673"),
    "cobra-cyan": ("#142b35", "#79d4df", "#1f4653", "#f0a66f"),
    "bebop-jazz": ("#172634", "#efcc6b", "#273b50", "#ef8068"),
    "eva-neon": ("#21172b", "#b6ef65", "#3a244a", "#ef79b4"),
    "moonlight-pink": ("#25203a", "#f5a9d0", "#3d315c", "#f0d878"),
    "monster-yellow": ("#312717", "#ffe16b", "#53401f", "#ef765f"),
    "cyber-teal": ("#14282d", "#75d6c6", "#21444a", "#e99bc2"),
    "hero-red": ("#32181c", "#ff9c84", "#5b2228", "#f0d16d"),
    "hero-blue": ("#16283c", "#8fc8f2", "#254767", "#f4cb6b"),
    "hero-gold": ("#2e2519", "#ffda78", "#514024", "#f08a66"),
    "hero-green": ("#152a23", "#9cdb8c", "#24483a", "#e1bb6d"),
    "hero-black": ("#191b21", "#d3d7e2", "#2b303b", "#d5a66f"),
    "hero-purple": ("#241a31", "#d2a8ed", "#402852", "#77d5cf"),
    "hero-cyan": ("#14282f", "#83dbe2", "#204653", "#f2b36a"),
    "hero-scarlet": ("#30161f", "#ff8291", "#571e31", "#e8d277"),
    "hero-emerald": ("#15271e", "#a6d77c", "#254332", "#e8b1cb"),
    "hero-sunshine": ("#332316", "#ffcf70", "#5c351d", "#8ad1e2"),
    "punk-orange": ("#321e17", "#ffad66", "#5b3020", "#72d0d1"),
    "punk-green": ("#182820", "#a8dc70", "#2e4930", "#ff8271"),
    "grunge-gold": ("#26241d", "#e6d16d", "#44402a", "#e58b68"),
    "metal-red": ("#21171b", "#f18478", "#41232b", "#d9bf72"),
    "electro-neon": ("#191c31", "#70e3ef", "#2b2851", "#f187d2"),
    "nu-metal": ("#1d2028", "#c5d66c", "#343747", "#ef8b6d"),
    "britpop-blue": ("#19243a", "#a7c5f0", "#2c3b5d", "#f4c86b"),
    "french-rock": ("#291b20", "#ed9e7d", "#4b2931", "#e2cc72"),
    "french-pop": ("#2e2031", "#e8a1cd", "#4d3153", "#e8ce73"),
    "hip-hop-gold": ("#292218", "#f2cf6b", "#4a3820", "#81d0dc"),
    "stadium-blue": ("#17263a", "#95c9f0", "#293f61", "#e99679"),
    "classic-purple": ("#25202e", "#d3b4e7", "#43334f", "#e9cd77"),
    "industrial-red": ("#24191b", "#f28a72", "#462426", "#d5c26e"),
    "glam-pink": ("#301e2b", "#f0a6c9", "#573047", "#f1d575"),
    "ska-yellow": ("#292616", "#f3dd68", "#4c4022", "#74d6c4"),
}


THEMES = """
anime-one-piece-luffy|sunny-orange
anime-one-piece-zoro|sword-green
anime-one-piece-nami|sea-blue
anime-one-piece-sanji|saiyan-gold
anime-one-piece-usopp|punk-orange
anime-one-piece-chopper|cherry-pink
anime-one-piece-robin|shadow-violet
anime-one-piece-franky|cobra-cyan
anime-one-piece-brook|reaper-black
anime-one-piece-jinbe|cyber-teal
anime-one-piece-ace|phoenix-fire
anime-one-piece-shanks|cobra-crimson
anime-one-piece-trafalgar-law|mist-silver
anime-one-piece-sabo|pegasus-blue
anime-one-piece-boa-hancock|moonlight-pink
anime-one-piece-whitebeard|athena-gold
anime-one-piece-doflamingo|hero-purple
anime-one-piece-crocodile|hero-emerald
anime-one-piece-mihawk|reaper-black
anime-one-piece-kaido|cosmic-purple
anime-one-piece-yamato|ice-blue
anime-one-piece-gear-five|moonlight-pink
anime-one-piece-blackbeard|hero-black
anime-one-piece-straw-hat-crew|punk-orange
anime-one-piece-thousand-sunny|saiyan-gold
anime-naruto-uzumaki|ninja-orange
anime-naruto-sasuke|shadow-violet
anime-naruto-sakura|cherry-pink
anime-naruto-kakashi|mist-silver
anime-naruto-itachi|akatsuki-red
anime-naruto-akatsuki|akatsuki-red
anime-naruto-hinata|andromeda-rose
anime-naruto-gaara|cobra-crimson
anime-naruto-jiraiya|hero-red
anime-naruto-tsunade|athena-gold
anime-naruto-minato|saiyan-gold
anime-naruto-shikamaru|hero-green
anime-naruto-rock-lee|leaf-green
anime-naruto-madara|hero-scarlet
anime-naruto-team-seven|hero-blue
anime-bleach-ichigo-kurosaki|hollow-red
anime-bleach-rukia-kuchiki|ice-blue
anime-bleach-byakuya-kuchiki|reaper-black
anime-bleach-renji-abarai|hero-scarlet
anime-bleach-kenpachi-zaraki|metal-red
anime-bleach-kisuke-urahara|punk-green
anime-bleach-sosuke-aizen|cosmic-purple
anime-bleach-toshiro-hitsugaya|ice-blue
anime-bleach-yoruichi-shihoin|hero-purple
anime-bleach-soul-society|hero-black
anime-dragon-ball-goku|dragon-orange
anime-dragon-ball-vegeta|prince-blue
anime-dragon-ball-gohan|shadow-violet
anime-dragon-ball-piccolo|namek-green
anime-dragon-ball-trunks|hero-purple
anime-dragon-ball-frieza|cosmic-purple
anime-dragon-ball-cell|hero-emerald
anime-dragon-ball-majin-buu|majin-rose
anime-dragon-ball-shenron|namek-green
anime-dragon-ball-broly|hero-green
anime-dragon-ball-bulma|sea-blue
anime-dragon-ball-beerus|cosmic-purple
anime-dragon-ball-krillin|saiyan-gold
anime-dragon-ball-android-18|ice-blue
anime-dragon-ball-gotenks|moonlight-pink
anime-dragon-ball-capsule-corp|hero-cyan
anime-dragon-ball-super-saiyan|saiyan-gold
anime-dragon-ball-red-ribbon-army|hero-scarlet
anime-saint-seiya-pegasus-seiya|pegasus-blue
anime-saint-seiya-phoenix-ikki|phoenix-fire
anime-saint-seiya-dragon-shiryu|sword-green
anime-saint-seiya-andromeda-shun|andromeda-rose
anime-saint-seiya-cygnus-hyoga|ice-blue
anime-saint-seiya-athena|athena-gold
anime-saint-seiya-leo-aiolia|hero-gold
anime-saint-seiya-virgo-shaka|cosmic-purple
anime-saint-seiya-scorpio-milo|hero-scarlet
anime-saint-seiya-gemini-saga|shadow-violet
anime-cobra-space-pirate|cobra-crimson
anime-cobra-lady|cobra-cyan
anime-cobra-crystal-boy|ice-blue
anime-cobra-psychogun|hero-red
anime-cowboy-bebop-spike|bebop-jazz
anime-cowboy-bebop-faye|moonlight-pink
anime-cowboy-bebop-jet|hero-green
anime-cowboy-bebop-swordfish-ii|bebop-jazz
anime-neon-genesis-evangelion-unit-01|eva-neon
anime-neon-genesis-evangelion-asuka|hero-scarlet
anime-neon-genesis-evangelion-rei|ice-blue
anime-sailor-moon-usagi|moonlight-pink
anime-yu-gi-oh-yugi|shadow-violet
anime-pokemon-pikachu|monster-yellow
anime-pokemon-team-rocket|akatsuki-red
anime-ghost-in-the-shell-motoko|cyber-teal
anime-city-hunter-ryo|french-rock
anime-lupin-the-third|saiyan-gold
anime-rurouni-kenshin|hero-scarlet
anime-fullmetal-alchemist-edward|metal-red
anime-death-note-light|reaper-black
anime-digimon-agumon|punk-orange
marvel-iron-man|hero-red
marvel-captain-america|hero-blue
marvel-thor|hero-gold
marvel-hulk|hero-green
marvel-spider-man|hero-scarlet
marvel-venom|hero-black
marvel-wolverine|saiyan-gold
marvel-deadpool|hero-scarlet
marvel-cyclops|hero-blue
marvel-storm|hero-cyan
marvel-magneto|hero-purple
marvel-black-panther|reaper-black
marvel-doctor-strange|cosmic-purple
marvel-scarlet-witch|hero-scarlet
marvel-loki|shadow-violet
marvel-daredevil|hero-red
marvel-punisher|hero-black
marvel-thanos|cosmic-purple
marvel-guardians-of-the-galaxy|bebop-jazz
marvel-star-lord|punk-orange
marvel-captain-marvel|saiyan-gold
marvel-hawkeye|shadow-violet
marvel-ant-man|hero-scarlet
marvel-ghost-rider|phoenix-fire
marvel-fantastic-four|hero-cyan
dc-batman|hero-black
dc-joker|hero-purple
dc-robin|hero-scarlet
dc-nightwing|hero-blue
dc-catwoman|reaper-black
dc-superman|hero-blue
dc-wonder-woman|hero-scarlet
dc-the-flash|hero-red
dc-green-lantern|hero-green
dc-aquaman|cyber-teal
dc-harley-quinn|cherry-pink
dc-poison-ivy|leaf-green
dc-riddler|hero-emerald
dc-two-face|mist-silver
dc-bane|metal-red
dc-darkseid|hero-purple
dc-lex-luthor|hero-emerald
dc-justice-league|hero-blue
dc-green-arrow|leaf-green
dc-constantine|bebop-jazz
dc-shazam|saiyan-gold
dc-blue-beetle|hero-cyan
dc-supergirl|saiyan-gold
dc-martian-manhunter|hero-emerald
dc-gotham-city|hero-black
music-the-offspring|punk-orange
music-green-day|punk-green
music-nirvana|grunge-gold
music-ac-dc|metal-red
music-ultravomit|monster-yellow
music-electric-callboy|electro-neon
music-linkin-park|industrial-red
music-red-hot-chili-peppers|hero-scarlet
music-nanowar-of-steel|hero-gold
music-foo-fighters|stadium-blue
music-blink-182|glam-pink
music-sum-41|punk-orange
music-limp-bizkit|nu-metal
music-korn|nu-metal
music-slipknot|hero-black
music-system-of-a-down|punk-green
music-rage-against-the-machine|metal-red
music-metallica|hero-black
music-iron-maiden|hero-scarlet
music-rammstein|industrial-red
music-nightwish|cosmic-purple
music-evanescence|shadow-violet
music-muse|cosmic-purple
music-placebo|shadow-violet
music-radiohead|mist-silver
music-queen|classic-purple
music-david-bowie|glam-pink
music-daft-punk|electro-neon
music-the-prodigy|industrial-red
music-gorillaz|hero-emerald
music-blur|britpop-blue
music-oasis|stadium-blue
music-smashing-pumpkins|moonlight-pink
music-soundgarden|grunge-gold
music-pearl-jam|punk-green
music-alice-in-chains|nu-metal
music-offspring-americana|punk-orange
music-green-day-dookie|punk-green
music-nirvana-in-utero|grunge-gold
music-avril-lavigne|glam-pink
music-britney-spears|moonlight-pink
music-spice-girls|cherry-pink
music-backstreet-boys|hero-blue
music-eminem|hip-hop-gold
music-indochine|french-pop
music-telephone|french-rock
music-trust|metal-red
music-mylene-farmer|french-pop
music-manu-chao|ska-yellow
music-jean-jacques-goldman|stadium-blue
""".strip()

EXPECTED_CATEGORY_COUNTS = {"anime": 100, "marvel": 25, "dc": 25, "music": 50}
REQUIRED_COLORS = {
    "activityBar.background",
    "activityBar.foreground",
    "statusBar.background",
    "sideBar.background",
    "editorCursor.foreground",
    "statusBarItem.remoteHoverBackground",
    "statusBarItem.remoteHoverForeground",
}


def rgb(value):
    return tuple(int(value[index:index + 2], 16) for index in (1, 3, 5))


def luminance(value):
    channels = [component / 255 for component in rgb(value)]
    linear = [component / 12.92 if component <= 0.04045 else ((component + 0.055) / 1.055) ** 2.4 for component in channels]
    return sum(component * weight for component, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(first, second):
    lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def readable(background, preferred):
    if contrast(preferred, background) >= 4.5:
        return preferred
    return "#f4f1e8" if contrast("#f4f1e8", background) >= contrast("#171719", background) else "#171719"


def blend(first, second, amount):
    values = [round(a * (1 - amount) + b * amount) for a, b in zip(rgb(first), rgb(second))]
    return "#" + "".join(f"{value:02x}" for value in values)


def make_settings(slug, profile):
    activity, accent, status, remote = PALETTES[profile]
    surface = blend(activity, "#101216", 0.48)
    sidebar = blend(activity, "#24262d", 0.42)
    title = blend(activity, status, 0.34)
    inactive = blend(activity, "#111318", 0.42)
    light_text = readable(activity, accent)
    status_text = readable(status, accent)
    sidebar_text = readable(sidebar, accent)
    badge_text = readable(accent, activity)
    remote_text = readable(remote, activity)
    colors = {
        "activityBar.background": activity,
        "activityBar.foreground": light_text,
        "activityBar.inactiveForeground": light_text + "99",
        "activityBar.activeBorder": accent,
        "activityBarBadge.background": accent,
        "activityBarBadge.foreground": badge_text,
        "badge.background": accent,
        "badge.foreground": badge_text,
        "editor.background": surface,
        "editor.foreground": "#e6e3dc",
        "editorCursor.foreground": accent,
        "editor.lineHighlightBackground": accent + "1c",
        "editor.selectionBackground": accent + "40",
        "editor.selectionHighlightBackground": accent + "24",
        "editorLineNumber.foreground": "#777b83",
        "editorLineNumber.activeForeground": light_text,
        "focusBorder": accent,
        "panel.background": surface,
        "panel.border": activity,
        "panelTitle.activeBorder": accent,
        "sideBar.background": sidebar,
        "sideBar.foreground": sidebar_text,
        "sideBar.border": activity,
        "sideBarTitle.foreground": light_text,
        "statusBar.background": status,
        "statusBar.foreground": status_text,
        "statusBar.noFolderBackground": status,
        "statusBar.noFolderForeground": status_text,
        "statusBar.debuggingBackground": remote,
        "statusBar.debuggingForeground": readable(remote, accent),
        "statusBarItem.remoteBackground": remote,
        "statusBarItem.remoteForeground": remote_text,
        "statusBarItem.remoteHoverBackground": accent,
        "statusBarItem.remoteHoverForeground": badge_text,
        "statusBarItem.hoverBackground": accent + "33",
        "statusBarItem.hoverForeground": light_text,
        "titleBar.activeBackground": title,
        "titleBar.activeForeground": readable(title, accent),
        "titleBar.inactiveBackground": inactive,
        "titleBar.inactiveForeground": "#b8b6b1",
        "tab.activeBackground": surface,
        "tab.activeForeground": light_text,
        "tab.activeBorderTop": accent,
        "tab.inactiveBackground": sidebar,
        "tab.inactiveForeground": "#a2a3a6",
        "scrollbarSlider.background": accent + "30",
        "scrollbarSlider.hoverBackground": accent + "55",
        "scrollbarSlider.activeBackground": accent + "77",
    }
    body = json.dumps({"workbench.colorCustomizations": colors}, indent=4, ensure_ascii=True)
    label = slug.replace("-", " ").title()
    return f"// {label}\n{body}\n"


def validate_settings(text, slug):
    data = json.loads(text.split("\n", 1)[1])
    colors = data["workbench.colorCustomizations"]
    if not REQUIRED_COLORS <= colors.keys():
        raise ValueError(f"Couleurs requises manquantes dans {slug}")
    if not all(re.fullmatch(r"#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?", value) for value in colors.values()):
        raise ValueError(f"Valeur de couleur invalide dans {slug}")
    contrast_pairs = (
        ("activityBar.foreground", "activityBar.background"),
        ("sideBar.foreground", "sideBar.background"),
        ("statusBar.foreground", "statusBar.background"),
        ("titleBar.activeForeground", "titleBar.activeBackground"),
        ("activityBarBadge.foreground", "activityBarBadge.background"),
        ("statusBarItem.remoteForeground", "statusBarItem.remoteBackground"),
        ("statusBarItem.remoteHoverForeground", "statusBarItem.remoteHoverBackground"),
    )
    if any(contrast(colors[foreground], colors[background]) < 4.5 for foreground, background in contrast_pairs):
        raise ValueError(f"Contraste insuffisant dans {slug}")


def main():
    parser = argparse.ArgumentParser(description="Génère les nouveaux thèmes pop culture dans json_file/.")
    parser.add_argument("--write", action="store_true", help="crée les dossiers et fichiers settings.json")
    args = parser.parse_args()
    entries = [line.split("|", 1) for line in THEMES.splitlines() if line.strip()]
    slugs = [slug for slug, _ in entries]
    if len(entries) != 200 or len(set(slugs)) != len(slugs):
        raise SystemExit(f"Liste incohérente: {len(entries)} thèmes, {len(set(slugs))} noms uniques")
    categories = {prefix: sum(slug.startswith(prefix + "-") for slug in slugs) for prefix in EXPECTED_CATEGORY_COUNTS}
    if categories != EXPECTED_CATEGORY_COUNTS:
        raise SystemExit(f"Répartition inattendue: {categories}")
    if any(profile not in PALETTES for _, profile in entries):
        raise SystemExit("Profil de couleur inconnu dans la liste")
    pending = []
    conflicts = []
    for slug, profile in entries:
        folder = THEME_DIR / slug
        settings_file = folder / "settings.json"
        expected = make_settings(slug, profile)
        if not folder.exists():
            pending.append((slug, expected))
        elif settings_file.is_file() and settings_file.read_text(encoding="utf-8") == expected:
            validate_settings(expected, slug)
        else:
            conflicts.append(slug)
    if conflicts:
        raise SystemExit("Dossiers existants non générés par ce script, aucune modification effectuée: " + ", ".join(conflicts))
    existing_count = len(entries) - len(pending)
    total = len(list(THEME_DIR.glob("*/settings.json"))) + len(pending)
    distribution = ", ".join(f"{key}: {value}" for key, value in categories.items())
    print(f"{len(entries)} thèmes vérifiés ({distribution}); {len(pending)} à créer, {existing_count} déjà conformes; total après génération: {total}.")
    if not args.write:
        return
    for slug, settings in pending:
        folder = THEME_DIR / slug
        folder.mkdir()
        (folder / "settings.json").write_text(settings, encoding="utf-8")
        validate_settings(settings, slug)
    print(f"Génération terminée: {len(pending)} thèmes créés.")


if __name__ == "__main__":
    main()