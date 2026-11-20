"""Generate the terminal-style project cards and contact lines in assets/cards/.

Run from the repo root: python3 .github/scripts/make_cards.py
"""
import textwrap

BG, FG, MUTED = '#070a06', '#e3ecdc', '#8a938a'
MINT, LIME, AMBER, BLUE, PINK = '#4cd4a4', '#a3f26a', '#f9bc4b', '#6cb4e8', '#ff6fae'
FONT = ("font-family: 'Fira Mono', 'Fira Code', 'FiraCode Nerd Font', 'DejaVu Sans Mono', "
        "ui-monospace, Menlo, Consolas, monospace; font-size: 14px; white-space: pre;")

PROJECTS = [  # file, title, description, tags, link label
    ('timeless-city', 'Timeless City',
     'Long-running (2+ years) FiveM roleplay server: administration, scripting in Lua, project lead.',
     ['fivem', 'lua', 'discord'], 'discord.gg/timelesscity'),
    ('timeless-services', 'Timeless Services',
     'My next project, coming soon. Follow along on Discord.',
     ['upcoming'], 'discord.gg/dSx7Sfu6Pz'),
    ('gatekeeper', 'GatekeeperV4',
     'Discord bot for CubeCoders AMP game servers. My fork adds role-to-whitelist sync, '
     'self-service account linking, EN/DE i18n and hardened secrets and permissions.',
     ['python', 'discord.py', 'amp-api'], 'github.com/AriVenatus/GatekeeperV4'),
    ('claude-usage-limits', 'claude-usage-limits',
     'Claude Code plugin: a Usage pane with context, cost, 5h and weekly limits, '
     'pace hints and a cache keep-alive.',
     ['typescript', 'claude-code'], 'github.com/AriVenatus/claude-usage-limits'),
    ('token-radar', 'token-radar',
     'Multi-chain Telegram token listener with a terminal UI.',
     ['python', 'telegram', 'web3'], 'github.com/AriVenatus/token-radar'),
    ('zyphex', 'Zyphex',
     "Website for an external client's crypto trading web app (Gate.io CrossEx).",
     ['next.js', 'react', 'tailwind', 'typescript'], 'zyphex.xyz'),
]
CONTACT = [  # file, command, argument, comment
    ('mail', 'mail', 'arivenatus@gmail.com', ''),
    ('discord-services', 'open', 'discord.gg/dSx7Sfu6Pz', '# Timeless Services'),
    ('discord-city', 'open', 'discord.gg/timelesscity', '# Timeless City'),
]
CW = 8.4  # monospace advance at 14px; every line is pinned to len * CW so any fallback font fits


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;')


def fit(s):
    return f' textLength="{len(s) * CW:.1f}" lengthAdjust="spacingAndGlyphs"'


def svg(w, h, title, desc, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-labelledby="t d">\n<title id="t">{esc(title)}</title>\n'
            f'<desc id="d">{esc(desc)}</desc>\n<style>text {{ {FONT} }}</style>\n'
            f'<rect width="{w}" height="{h}" rx="6" fill="{BG}"/>\n{body}\n</svg>\n')


def card(title, text, tags, link):
    w, h = 420, 188
    lines = textwrap.wrap(text, 44)
    assert len(lines) <= 4, f'{title}: description wraps to {len(lines)} lines, max 4'
    out = [f'<rect x="12.5" y="18.5" width="{w - 25}" height="{h - 31}" fill="none" '
           f'stroke="{MUTED}" stroke-opacity=".55"/>',
           f'<rect x="22" y="10" width="{len(title) * CW + 10:.0f}" height="16" fill="{BG}"/>',
           f'<text x="27" y="23" fill="{MINT}" font-weight="700"{fit(title)}>{esc(title)}</text>']
    for i, ln in enumerate(lines):
        out.append(f'<text x="28" y="{50 + i * 20}" fill="{FG}"{fit(ln)}>{esc(ln)}</text>')
    tag_text = ' '.join('#' + t for t in tags)
    out.append(f'<text x="28" y="{h - 50}" fill="{LIME}"{fit(tag_text)}>{esc(tag_text)}</text>')
    out.append(f'<text x="28" y="{h - 28}" fill="{BLUE}"{fit(link + " ↗")}>{esc(link)} ↗</text>')
    return svg(w, h, title, f'{text} Tags: {", ".join(tags)}. Link: {link}.', '\n'.join(out))


def contact(cmd, arg, comment):
    h = 36
    parts = [('ari', MINT, True), ('@github', LIME, False), (':~$ ', MUTED, False),
             (cmd + ' ', FG, False), (arg, BLUE, False)] + ([('  ' + comment, MUTED, False)] if comment else [])
    spans = ''.join(f'<tspan fill="{c}"{" font-weight=\"700\"" if b else ""}>{esc(s)}</tspan>' for s, c, b in parts)
    label = f'{cmd} {arg} {comment}'.strip()
    w = round(32 + sum(len(t) for t, _, _ in parts) * CW)  # fit the line; the img keeps its natural size
    return svg(w, h, label, label, f'<text x="16" y="23" xml:space="preserve"{fit("".join(t for t, _, _ in parts))}>{spans}</text>')


for f, *a in PROJECTS:
    open(f'assets/cards/{f}.svg', 'w').write(card(*a))
for f, *a in CONTACT:
    open(f'assets/cards/{f}.svg', 'w').write(contact(*a))
print(f'{len(PROJECTS)} cards, {len(CONTACT)} contact lines')
