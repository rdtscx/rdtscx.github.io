#!/usr/bin/env python3
"""同步 rdtscx.github.io 根站数据。

流程：
  1. 拉取 rdtscx 账号下全部公开仓库（分页）
  2. 拉取每个仓库的 Releases，只统计「版本数量 + 最新版本号」
     （安装包直链一律放在各仓库的 /downloads.html 二级页，根站不出现下载直链）
  3. 读取 sites.json 清单，合并外部站点条目
  4. 把 APPINFO（版本数量/最新版本号）/ EXTRA 注入 index.html 的标记块

用法：
  python3 scripts/sync.py                 # 生成并写回 index.html（本地/CI 均可）
  GITHUB_TOKEN=xxx python3 scripts/sync.py  # CI 内传令牌，避免限流

仅依赖标准库，便于在 GitHub Actions 的 setup-python 上直接运行。
"""
import json
import os
import re
import sys
import urllib.request
import urllib.error

OWNER = 'rdtscx'
SELF_REPO = OWNER + '.github.io'
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INDEX = os.path.join(ROOT, 'index.html')
MANIFEST = os.path.join(ROOT, 'sites.json')

API = 'https://api.github.com'
TOKEN = os.environ.get('GITHUB_TOKEN', '').strip()

START_MARK = '/* SYNC:START — 由 scripts/sync.py 自动生成，请勿手改 */'
END_MARK = '/* SYNC:END */'

# 视为软件安装包的资产扩展名，按优先级排列
APP_EXT = ('.apk', '.aab', '.exe', '.zip', '.dmg', '.msi', '.xapk')


def _headers():
    h = {'Accept': 'application/vnd.github+json', 'User-Agent': 'rdtscx-root-sync'}
    if TOKEN:
        h['Authorization'] = 'token ' + TOKEN
    return h


def _next_link(link):
    if not link:
        return None
    m = re.search(r'<([^>]+)>\s*;\s*rel="next"', link)
    return m.group(1) if m else None


def get_json(url):
    req = urllib.request.Request(url, headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r), r.headers.get('Link')
    except urllib.error.HTTPError as e:
        print('  ! HTTP %s %s' % (e.code, url), file=sys.stderr)
        return None, None


def list_repos():
    repos, url = [], API + '/users/%s/repos?per_page=100&sort=pushed' % OWNER
    while url:
        data, link = get_json(url)
        if not data:
            break
        repos.extend(data)
        url = _next_link(link)
    return [r for r in repos if r['name'].lower() != SELF_REPO]


def pick_asset(assets):
    """选最合适的下载资产：优先安装包，否则第一个资产；返回 None 表示无可用资产。"""
    if not assets:
        return None
    for ext in APP_EXT:
        for a in assets:
            if a['name'].lower().endswith(ext):
                return a
    return assets[0]


def _verkey(tag):
    """把 tag 拆成可比较的数字元组，如 v1.5.9 → (1,5,9)；无数字时返回空元组。"""
    nums = re.findall(r'\d+', tag or '')
    return tuple(int(n) for n in nums)


def releases_for(repo):
    data, _ = get_json(API + '/repos/%s/%s/releases?per_page=100' % (OWNER, repo))
    if not data:
        return []
    out = []
    for rel in data:
        if rel.get('draft'):
            continue
        asset = pick_asset(rel.get('assets') or [])
        if not asset:
            continue
        out.append({
            'tag': rel.get('tag_name') or rel.get('name') or '',
            'name': rel.get('name') or rel.get('tag_name') or '',
            'date': rel.get('published_at') or rel.get('created_at') or '',
            'assets': [{
                'name': asset['name'],
                'url': asset['browser_download_url'],
                'size': asset.get('size') or 0,
            }],
        })
    out.sort(key=lambda r: _verkey(r['tag']), reverse=True)
    return out


def load_manifest():
    if not os.path.exists(MANIFEST):
        return []
    with open(MANIFEST, encoding='utf-8') as f:
        data = json.load(f)
    sites = data.get('sites') if isinstance(data, dict) else data
    return sites or []


def build():
    print('拉取账号仓库…')
    repos = list_repos()
    print('  共 %d 个公开仓库' % len(repos))

    pages = {}
    for r in repos:
        rs = releases_for(r['name'])
        if rs:
            pages[r['name']] = {'count': len(rs), 'latest': rs[0]['tag']}
            print('  %-28s %d 个版本 → %s/downloads.html' % (r['name'], len(rs), r['name']))

    extra = []
    manifest = load_manifest()
    repo_names = {r['name'] for r in repos}
    for s in manifest:
        name = (s.get('name') or '').strip()
        url = (s.get('url') or '').strip()
        if not name or not url:
            print('  ! 清单条目不完整，跳过：%r' % s, file=sys.stderr)
            continue
        if name in repo_names:
            print('  清单 %s 与账号仓库同名，以账号仓库为准' % name, file=sys.stderr)
            continue
        extra.append({
            'name': name,
            'url': url,
            'description': s.get('description') or '',
            'pushed_at': s.get('pushed_at') or '',
            'language': s.get('language') or '',
        })
    if extra:
        print('  清单收录 %d 个外部站点' % len(extra))

    return pages, extra


def dump_js(obj):
    # ensure_ascii=False 保留中文，separators 压掉多余空格
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))


def inject(pages, extra):
    with open(INDEX, encoding='utf-8') as f:
        html = f.read()

    block = '%s\nconst APPINFO = %s;\nconst EXTRA = %s;\n%s' % (
        START_MARK, dump_js(pages), dump_js(extra), END_MARK)

    if START_MARK in html and END_MARK in html:
        html = re.sub(re.escape(START_MARK) + r'.*?' + re.escape(END_MARK),
                      lambda m: block, html, count=1, flags=re.S)
    else:
        # 首次迁移：把旧的两处常量包裹进标记块
        html, n1 = re.subn(r'^const (?:RELEASES|DOWNLOAD_PAGES|APPINFO) = .*?;\s*$',
                           lambda m: START_MARK, html, count=1, flags=re.M)
        html, n2 = re.subn(r'^(const EXTRA = .*?;\s*)$',
                           lambda m: m.group(1) + '\n' + END_MARK, html, count=1, flags=re.M)
        if not (n1 and n2):
            sys.exit('迁移失败：index.html 中未同时找到 const APPINFO 与 const EXTRA 行')
        html = re.sub(re.escape(START_MARK) + r'.*?' + re.escape(END_MARK),
                      lambda m: block, html, count=1, flags=re.S)

    with open(INDEX, 'w', encoding='utf-8') as f:
        f.write(html)
    print('已写入 index.html（%d 字节）' % len(html.encode('utf-8')))


def main():
    pages, extra = build()
    inject(pages, extra)


if __name__ == '__main__':
    main()
