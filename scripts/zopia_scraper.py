#!/usr/bin/env python3
"""zopia.ai API 接口抓取脚本"""

from playwright.sync_api import sync_playwright
import json, time
from datetime import datetime
from urllib.parse import urlparse

def capture():
    all_apis = []
    seen = set()

    skip_ext = ['.js','.css','.png','.jpg','.jpeg','.gif','.svg','.woff','.woff2','.ttf','.ico','.webp','.mp4','.m3u8','.map']

    def on_req(req):
        url = req.url
        if any(url.lower().endswith(e) for e in skip_ext): return
        if url.startswith(('data:','blob:')): return
        if url not in seen:
            seen.add(url)
            parsed = urlparse(url)
            info = {
                'url': url, 'method': req.method,
                'domain': parsed.netloc, 'path': parsed.path,
                'query': parsed.query,
                'timestamp': datetime.now().isoformat(),
                'headers': dict(req.headers),
                'post_data': None
            }
            if req.method in ('POST','PUT','PATCH'):
                try: info['post_data'] = req.post_data[:5000]
                except: pass
            all_apis.append(info)

    def on_resp(resp):
        for api in all_apis:
            if api['url'] == resp.url:
                api['status'] = resp.status
                api['content_type'] = resp.headers.get('content-type','')
                api['resp_headers'] = dict(resp.headers)
                break

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox','--disable-blink-features=AutomationControlled'])
        ctx = browser.new_context(
            viewport={'width':1920,'height':1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN'
        )
        page = ctx.new_page()
        page.on('request', on_req)
        page.on('response', on_resp)

        # 先访问首页看看有哪些链接
        pages = [
            ('https://zopia.ai/', '首页'),
            ('https://zopia.ai/about', '关于'),
            ('https://zopia.ai/pricing', '价格'),
            ('https://zopia.ai/login', '登录'),
            ('https://zopia.ai/signup', '注册'),
            ('https://zopia.ai/contact', '联系'),
            ('https://zopia.ai/blog', '博客'),
            ('https://zopia.ai/docs', '文档'),
            ('https://zopia.ai/api', 'API'),
            ('https://zopia.ai/features', '功能'),
        ]

        for url, name in pages:
            print(f"\n{'='*50}")
            print(f"访问: {name} ({url})")
            try:
                page.goto(url, wait_until='domcontentloaded', timeout=20000)
                time.sleep(3)
                for _ in range(3):
                    page.evaluate('window.scrollBy(0, 800)')
                    time.sleep(1)
                page.screenshot(path=f'/root/zopia_{name}.png')
                print(f"  截图保存: zopia_{name}.png")
                # 抓取页面中的所有链接
                links = page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('a[href]')).map(a => a.href)
                        .filter(h => h.includes('zopia.ai'))
                        .filter((v,i,a) => a.indexOf(v) === i);
                }''')
                print(f"  发现链接: {len(links)} 个")
                for link in links[:10]:
                    print(f"    {link}")
            except Exception as e:
                print(f"  失败: {e}")

        # 尝试点击页面上的按钮和交互元素
        print(f"\n{'='*50}")
        print("尝试页面交互")
        try:
            page.goto('https://zopia.ai/', wait_until='domcontentloaded', timeout=20000)
            time.sleep(2)
            # 点击所有按钮
            buttons = page.locator('button, [role="button"], .btn, [class*="button"]').all()
            print(f"  发现 {len(buttons)} 个按钮")
            for i, btn in enumerate(buttons[:5]):
                try:
                    if btn.is_visible():
                        print(f"  点击按钮 {i}: {btn.text_content()[:50]}")
                        btn.click(timeout=3000)
                        time.sleep(2)
                except: pass
        except Exception as e:
            print(f"  交互失败: {e}")

        # 发现的额外链接再访问
        extra_links = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a[href]')).map(a => a.href)
                .filter(h => h.includes('zopia.ai') && !h.includes('#'))
                .filter((v,i,a) => a.indexOf(v) === i);
        }''')
        
        visited = set(u for u,_ in pages)
        for link in extra_links:
            if link not in visited and len(visited) < 20:
                visited.add(link)
                print(f"\n访问额外链接: {link}")
                try:
                    page.goto(link, wait_until='domcontentloaded', timeout=15000)
                    time.sleep(2)
                    page.screenshot(path=f'/root/zopia_extra_{len(visited)}.png')
                except: pass

        browser.close()

    return all_apis

if __name__ == '__main__':
    print(f"开始抓取 zopia.ai ... {datetime.now()}")
    apis = capture()
    
    with open('/root/zopia_raw_apis.json', 'w', encoding='utf-8') as f:
        json.dump(apis, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n抓取完成! 共 {len(apis)} 个请求")
    
    # 按域名统计
    by_domain = {}
    for a in apis:
        d = a['domain']
        by_domain[d] = by_domain.get(d, 0) + 1
    for d, c in sorted(by_domain.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")
