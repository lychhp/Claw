import asyncio
from playwright.async_api import async_playwright

async def scrape_bilibili(keyword):
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        # 伪装成真实的 Windows Chrome 浏览器
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080} # 假装我们有一个全高清大屏幕
        )
        page = await context.new_page()

        print(f"🚀 正在 B 站搜索关键词：【{keyword}】...")
        
        # 1. 访问 B 站搜索页面
        search_url = f"https://search.bilibili.com/all?keyword={keyword}"
        await page.goto(search_url)
        
        # 2. 智能等待：不盲目死等时间，而是等待“视频卡片”元素出现在网页上
        try:
            print("⏳ 正在等待视频列表加载...")
            # B站搜索页的视频卡片通常带有 bili-video-card 这个类名
            await page.wait_for_selector(".bili-video-card", timeout=15000) 
        except Exception as e:
            print("❌ 加载超时，可能遇到了反爬滑动验证码！正在截图保存证据...")
            await page.screenshot(path="social_scraper/error_bilibili.png")
            await browser.close()
            return

        print("✅ 页面加载成功，开始提取爆款数据...\n")
        print("="*40)
        
        # 3. 定位所有的视频卡片
        video_cards = await page.locator(".bili-video-card").all()
        
        # 4. 循环提取前 5 个视频的信息
        for i, card in enumerate(video_cards[:5]):
            # 提取标题 (B站标题一般在 h3 标签里)
            title_elem = card.locator("h3")
            title = await title_elem.inner_text() if await title_elem.count() > 0 else "未知标题"
            
            # 提取链接
            link_elem = card.locator("a").first
            link = await link_elem.get_attribute("href") if await link_elem.count() > 0 else ""
            
            # B站的链接经常省略 https:，我们帮它补全
            if link and link.startswith("//"):
                link = "https:" + link
                
            print(f"🔥 TOP {i+1}: {title}")
            print(f"🔗 链接: {link}")
            print("-" * 40)

        # 抓取完毕，关门大吉
        await browser.close()

if __name__ == "__main__":
    # 你可以在这里把 "AI大模型" 换成任何你想搜的词
    asyncio.run(scrape_bilibili("AI大模型"))