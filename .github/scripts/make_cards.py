"""Generate the terminal-style README panes (assets/*.svg), project cards and contact lines (assets/cards/).

Run from the repo root: python3 .github/scripts/make_cards.py
"""
import re
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
            f'<rect width="{w}" height="{h}" fill="{BG}"/>\n{body}\n</svg>\n')


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


PROMPT = [('ari', MINT, True), ('@github', LIME, False), (':~$ ', MUTED, False)]
W, LH, X, OUT = 840, 22, 12, 32  # README panes share the hero's width; prompts sit at X, output at OUT


def line(x, y, parts):
    """One text line from (text, colour, bold) spans, pinned to its monospace width."""
    spans = ''.join(f'<tspan fill="{c}"{" font-weight=\"700\"" if b else ""}>{esc(s)}</tspan>' for s, c, b in parts)
    return f'<text x="{x}" y="{y}" xml:space="preserve"{fit("".join(t for t, _, _ in parts))}>{spans}</text>'


def pane(cmd, rows, extra=''):
    """Full-width terminal pane: a prompt running `cmd`, then its output rows."""
    lines = ([PROMPT + [(cmd, FG, False)]] if cmd else []) + rows
    xs = [X if ln[:len(PROMPT)] == PROMPT else OUT for ln in lines]
    for x, ln in zip(xs, lines):
        assert x + sum(len(t) for t, _, _ in ln) * CW <= W - X, f'too wide: {ln}'
    h = 18 + len(lines) * LH + 12
    body = '\n'.join(line(x, 32 + i * LH, ln) for i, (x, ln) in enumerate(zip(xs, lines)))
    plain = '\n'.join(''.join(t for t, _, _ in ln) for ln in lines)
    return svg(W, h, f'$ {cmd}' if cmd else 'ari@github:~$', plain, body + extra)


def pipes(s, color=FG):
    """Values separated by ' | ', with muted pipes."""
    out = []
    for i, v in enumerate(s.split(' | ')):
        out += ([(' | ', MUTED, False)] if i else []) + [(v, color, False)]
    return out


def tree_row(ln):
    pre, rest = re.match(r'([│├└─ ]*)(.*)', ln).groups()
    key, gap, val = (re.split(r'(\s{2,})', rest, maxsplit=1) + ['', ''])[:3]
    depth = len(pre) // 4
    if not pre or depth == 1:
        k = [(key, BLUE, True)]          # root and categories look like directories
    elif val:
        k = [(key, MINT, False)]
    else:
        k = pipes(key)                    # plain leaf or wrapped continuation
    return [(pre, MUTED, False)] + k + ([(gap, FG, False)] + pipes(val) if val else [])


SKILLS = """~/skills
├── infra
│   ├── linux           debian | ubuntu (server, xubuntu, lubuntu) | fedora
│   │                   raspberry pi os | wsl2
│   ├── windows         windows server | active directory (basics)
│   ├── virtualization  hyper-v | proxmox (basics)
│   ├── containers      docker | compose v2
│   ├── network         caddy | tailscale (acls) | adguard home dns
│   │                   cloudflare tunnel | iot segmentation
│   ├── storage         lvm thin provisioning | mdadm raid1 | rclone backups
│   ├── identity        authentik sso | vaultwarden
│   ├── monitoring      uptime kuma | beszel | diun
│   └── game servers    cubecoders amp | fivem
├── security
│   ├── zero-trust access, no port forwarding
│   ├── secrets management | default-deny firewalling (iptables)
│   ├── http security headers | code audits
│   └── prompt-injection testing for ai agents
├── dev
│   ├── scripting       bash | powershell | python
│   ├── web             next.js | svelte 5 | typescript | node.js | tailwind
│   ├── game            lua (fivem)
│   └── ai              self-taught: local llms (ollama)
│                       quantization trade-offs (gguf, vram)
│                       claude code plugins | agent tooling
├── docs
│   └── runbooks | troubleshooting guides | markdown doc sites
└── web3
    └── on-chain analysis | blockscout api | dune | solana rpc"""

WIP = [('homelab-duo-setup/', 'docs for a two-server homelab, public when it\'s done'),
       ('dash-mgr/', 'Docker container manager in Bash, public when it\'s done')]

CURSOR = (f'<style>.c {{ animation: blink 1.1s steps(1) infinite; }} @keyframes blink {{ 50% {{ opacity: 0; }} }} '
          f'@media (prefers-reduced-motion: reduce) {{ .c {{ animation: none; }} }}</style>'
          f'<rect class="c" x="{X + len('ari@github:~$ ') * CW:.0f}" y="19" width="9" height="17" fill="{MINT}"/>')

PANES = {  # file: (command, output rows, extra svg)
    'projects': ('ls ~/projects', [], ''),
    'wip': ('ls ~/projects/.wip', [[(d, BLUE, True), (' ' * (21 - len(d)), FG, False), (t, MUTED, False)] for d, t in WIP], ''),
    'skills': ('tree ~/skills', [tree_row(ln) for ln in SKILLS.splitlines()], ''),
    'end': ('', [PROMPT], CURSOR),
}


def contact(cmd, arg, comment):
    parts = PROMPT + [(cmd + ' ', FG, False), (arg, BLUE, False)] + ([('  ' + comment, MUTED, False)] if comment else [])
    label = f'{cmd} {arg} {comment}'.strip()
    return svg(W, 36, label, label, line(X, 23, parts))  # full width so it lines up with the panes


if __name__ == '__main__':
    for f, *a in PROJECTS:
        open(f'assets/cards/{f}.svg', 'w').write(card(*a))
    for f, *a in CONTACT:
        open(f'assets/cards/{f}.svg', 'w').write(contact(*a))
    for f, (cmd, rows, extra) in PANES.items():
        open(f'assets/{f}.svg', 'w').write(pane(cmd, rows, extra=extra))
    print(f'{len(PROJECTS)} cards, {len(CONTACT)} contact lines, {len(PANES)} panes')
