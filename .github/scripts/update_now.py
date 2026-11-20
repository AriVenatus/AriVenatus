"""Rewrite the README's "now" block with the most recently pushed public repos."""
import json
import os
import re
import urllib.request

USER = 'AriVenatus'
HIDDEN = {USER, 'hash-broker-miner', 'Musik-Streaming-Plattform'}  # never listed
headers = {'Accept': 'application/vnd.github+json'}
if os.environ.get('GH_TOKEN'):
    headers['Authorization'] = f"Bearer {os.environ['GH_TOKEN']}"
url = f'https://api.github.com/users/{USER}/repos?sort=pushed&per_page=30&type=owner'
repos = json.load(urllib.request.urlopen(urllib.request.Request(url, headers=headers)))
repos = [r for r in repos if r['name'] not in HIDDEN and not r['private']][:5]

def short(s, n=58):
    s = s or ''
    return s if len(s) <= n else s[: n - 1] + '…'

lines = [f"{r['pushed_at'][:10]}  {r['name']:<26}  {short(r['description'])}" for r in repos]
block = '```\n$ ls -lt ~/repos | head -5\n' + '\n'.join(lines) + '\n```'

readme = open('README.md', encoding='utf-8').read()
new, n = re.subn(r'(<!-- now:start -->\n)(?:.*?\n)?(<!-- now:end -->)',
                 lambda m: m[1] + block + '\n' + m[2], readme, flags=re.S)
assert n == 1, 'README must contain exactly one now:start/now:end block'
open('README.md', 'w', encoding='utf-8').write(new)
