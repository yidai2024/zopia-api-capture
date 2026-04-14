#!/usr/bin/env python3
"""zopia.ai API 抓取 v3 - 简化版"""

from playwright.sync_api import sync_playwright
import json, time
from datetime import datetime
from urllib.parse import urlparse

def capture():
    all_apis = []
    seen = set()
    skip_ext = ['.js','.css','.png','.jpg','.jpeg','.gif','.svg','.woff','.woff2','.ttf','.ico','.webp','.mp4','.m3u8','.map','.xml','.txt']

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
            if req.method in ('POST','PUT','PATCH','DELETE'):
                try: info['post_data'] = req.post_data[:5000]
                except: pass
            all_apis.append(info)

    def on_resp(resp):
        for api in all_apis:
            if api['url'] == resp.url:
                api['status'] = resp.status
                api['content_type'] = resp.headers.get('content-type','')
                try:
                    if 'json' in api.get('content_type',''):
                        api['resp_body_preview'] = resp.text()[:2000]
                except: pass
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

        # 首页
        print("=== 访问首页 ===")
        page.goto('https://zopia.ai/', wait_until='domcontentloaded', timeout=30000)
        time.sleep(8)  # 等JS加载
        page.screenshot(path='/root/zopia_home.png', full_page=False)
        print(f"首页请求数: {len(all_apis)}")

        # 滚动
        for i in range(5):
            page.evaluate('window.scrollBy(0, 800)')
            time.sleep(1.5)
        page.screenshot(path='/root/zopia_scrolled.png', full_page=True)
        
        # 提取链接和按钮
        print("\n=== 页面元素 ===")
        elements = page.evaluate('''() => {
            const result = {links: [], buttons: [], inputs: [], allText: ''};
            document.querySelectorAll('a[href]').forEach(a => {
                result.links.push({href: a.href, text: a.textContent.trim().substring(0,80)});
            });
            document.querySelectorAll('button, [role="button"]').forEach(b => {
                result.buttons.push({text: b.textContent.trim().substring(0,80), classes: b.className.substring(0,50)});
            });
            document.querySelectorAll('input, textarea').forEach(i => {
                result.inputs.push({type: i.type, name: i.name, placeholder: i.placeholder});
            });
            result.allText = document.body.innerText.substring(0, 3000);
            return result;
        }''')
        
        print(f"链接: {len(elements['links'])} 个")
        for l in elements['links']:
            print(f"  {l['href'][:80]}  |  {l['text'][:40]}")
        
        print(f"\n按钮: {len(elements['buttons'])} 个")
        for b in elements['buttons']:
            print(f"  {b['text'][:50]}")
        
        print(f"\n输入框: {len(elements['inputs'])} 个")
        for i in elements['inputs']:
            print(f"  type={i['type']} name={i['name']} placeholder={i['placeholder']}")

        # 点击所有可见按钮
        print("\n=== 点击按钮 ===")
        for b in elements['buttons'][:15]:
            text = b['text'][:30]
            if text:
                try:
                    page.click(f'text="{text}"', timeout=3000)
                    time.sleep(2)
                    page.screenshot(path=f'/root/zopia_click_{text[:10]}.png')
                    print(f"  点击: {text}")
                except Exception as e:
                    print(f"  跳过: {text}")

        # 点击所有链接
        print("\n=== 点击链接 ===")
        for l in elements['links'][:15]:
            href = l['href']
            if 'zopia.ai' in href and '#' not in href.split('/')[-1]:
                try:
                    page.goto(href, wait_until='domcontentloaded', timeout=15000)
                    time.sleep(3)
                    page.screenshot(path=f'/root/zopia_link_{len(all_apis)}.png')
                    print(f"  访问: {href}")
                except Exception as e:
                    print(f"  跳过: {href} - {str(e)[:40]}")

        # 从JS中找API端点
        print("\n=== JS中的API端点 ===")
        js_apis = page.evaluate('''() => {
            const found = [];
            // 检查全局变量
            if (window.__NEXT_DATA__) found.push('__NEXT_DATA__: ' + JSON.stringify(Object.keys(window.__NEXT_DATA__)));
            if (window.__NUXT__) found.push('__NUXT__: found');
            if (window.__APP_DATA__) found.push('__APP_DATA__: found');
            
            // 内联script中找API路径
            document.querySelectorAll('script:not([src])').forEach(s => {
                const t = s.textContent;
                // fetch/axios
                const f1 = t.match(/fetch\s*\(\s*["']([^"']+)["']/g) || [];
                f1.forEach(m => found.push('fetch: ' + m));
                const f2 = t.match(/\.get\s*\(\s*["']([^"']+)["']/g) || [];
                f2.forEach(m => found.push('get: ' + m));
                const f3 = t.match(/\.post\s*\(\s*["']([^"']+)["']/g) || [];
                f3.forEach(m => found.push('post: ' + m));
                // API路径
                const f4 = t.match(/["'](\/api\/[^"']{2,80})["']/g) || [];
                f4.forEach(m => found.push('api_path: ' + m));
                // Base URL
                const f5 = t.match(/["'](https?:\/\/[^"']*(?:api|service|backend|gateway)[^"']*)["']/gi) || [];
                f5.forEach(m => found.push('base_url: ' + m));
            });
            
            // script src
            document.querySelectorAll('script[src]').forEach(s => {
                if (s.src.includes('_next') || s.src.includes('chunk') || s.src.includes('nuxt') || s.src.includes('app')) {
                    found.push('script: ' + s.src);
                }
            });
            
            return found;
        }''')
        for j in js_apis:
            print(f"  {j}")

        # 保存页面HTML
        html = page.content()
        with open('/root/zopia_home.html', 'w') as f:
            f.write(html)
        print(f"\nHTML已保存: {len(html)} 字节")

        browser.close()

    return all_apis

if __name__ == '__main__':
    print(f"开始抓取 zopia.ai v3 ... {datetime.now()}")
    apis = capture()
    
    with open('/root/zopia_raw_apis.json', 'w', encoding='utf-8') as f:
        json.dump(apis, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n抓取完成! 共 {len(apis)} 个请求")
    by_domain = {}
    for a in apis:
        d = a['domain']
        by_domain[d] = by_domain.get(d, 0) + 1
    for d, c in sorted(by_domain.items(), key=lambda x: -x[1]):
        print(f"  {d}: {c}")
