"""Render assets/repos.svg: the most recently pushed public repos as terminal output."""
import json
import os
import textwrap
import urllib.request

from make_cards import BLUE, FG, MUTED, pane

USER = 'AriVenatus'
HIDDEN = {USER, 'hash-broker-miner', 'Musik-Streaming-Plattform'}  # never listed
headers = {'Accept': 'application/vnd.github+json'}
if os.environ.get('GH_TOKEN'):
    headers['Authorization'] = f"Bearer {os.environ['GH_TOKEN']}"
url = f'https://api.github.com/users/{USER}/repos?sort=pushed&per_page=30&type=owner'
repos = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=headers)))
repos = [r for r in repos if r['name'] not in HIDDEN and not r['private']][:5]

rows = []
for r in repos:
    desc = textwrap.wrap(r['description'] or '', 52) or ['']  # 52 = what fits right of the name column
    rows.append([(r['pushed_at'][:10] + '  ', MUTED, False), (f"{r['name']:<26}  ", BLUE, True), (desc[0], FG, False)])
    rows += [[(' ' * 40, FG, False), (d, FG, False)] for d in desc[1:]]
rows.append([('# updated daily by a GitHub Action', MUTED, False)])
open('assets/repos.svg', 'w', encoding='utf-8').write(pane('ls -lt ~/repos | head -5', rows))
