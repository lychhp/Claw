import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # 启动 Chromium 浏览器
        browser = await p.chromium.launch(headless=True) # headless=True 表示在后台运行
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("正在尝试访问 B 站...")
        await page.goto("https://www.bilibili.com")
        
        # 等待页面加载一会儿
        await page.wait_for_timeout(3000)
        
        # 截图保存，看看我们看到的画面是否正常
        await page.screenshot(path="bilibili_check.png")
        print("✅ 访问成功！截图已保存为 bilibili_check.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())