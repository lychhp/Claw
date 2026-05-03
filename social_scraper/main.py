import asyncio
from playwright.async_api import async_playwright
import os
import requests
import json
import yagmail

async def scrape_and_analyze(keyword):
    async with async_playwright() as p:
        # --- 1. 抓取阶段 (增强版) ---
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"🚀 [第一阶段] 正在全方位扫射 B 站【{keyword}】的爆款数据...")
        await page.goto(f"https://search.bilibili.com/all?keyword={keyword}")
        
        try:
            # 增加等待时间，确保统计数据加载出来
            await page.wait_for_selector(".bili-video-card", timeout=15000)
            await asyncio.sleep(2) # 额外缓冲，等待数字跳动完成
        except Exception:
            print("❌ 数据加载超时。")
            await browser.close()
            return

        video_cards = await page.locator(".bili-video-card").all()
        
        scraped_data = ""
        for i, card in enumerate(video_cards[:5]):
            # 1. 提取标题
            title_elem = card.locator("h3")
            title = await title_elem.inner_text() if await title_elem.count() > 0 else "未知标题"
            
            # 2. 提取链接
            link_elem = card.locator("a").first
            link = await link_elem.get_attribute("href") if await link_elem.count() > 0 else ""
            if link and link.startswith("//"): link = "https:" + link
            
            # 3. 提取数据指标 (播放量、弹幕、日期)
            # B站搜索页通常直接显示：播放量、弹幕量、上传日期
            stats_items = await card.locator(".bili-video-card__stats--item").all()
            views = await stats_items[0].inner_text() if len(stats_items) > 0 else "未知播放"
            danmaku = await stats_items[1].inner_text() if len(stats_items) > 1 else "未知弹幕"
            
            date_elem = card.locator(".bili-video-card__info--date")
            upload_date = await date_elem.inner_text() if await date_elem.count() > 0 else "未知日期"
            
            # 拼接到汇总字符串中，喂给 DeepSeek
            scraped_data += f"[{i+1}] 标题：{title}\n"
            scraped_data += f"    🔥 热度：{views}播放 / {danmaku}弹幕 / 发布于{upload_date}\n"
            scraped_data += f"    🔗 链接：{link}\n\n"

        await browser.close()
        print("✅ 深度抓取完成！数据已入库。")

        # --- 2. 大脑分析阶段 (DeepSeek 提示词升级) ---
        print("🧠 [第二阶段] DeepSeek 正在进行多维度数据拆解...")
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key: return

        api_url = "https://api.deepseek.com/v1/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        
        # 升级 Prompt：让 AI 结合“播放量”和“日期”来分析
        prompt = f"""
        你是一个资深的视频内容产品经理。我从 B 站抓取了关于“{keyword}”的 5 条最新爆款数据。
        
        原始抓取数据如下：
        {scraped_data}

        请根据这些数据完成以下分析：
        1. 【流量含金量】：结合播放量和发布日期，判断哪个视频是真正的“黑马”（比如发布时间短但播放量飙升）。
        2. 【内容风向标】：分析目前该领域最吸睛的关键词和封面策略是什么？
        3. 【痛点洞察】：基于这些爆款，分析用户现在的焦虑点或兴趣点在哪里？
        4. 附上这 5 个视频的精简清单（含播放量数据）。
        """

        payload = {
            "model": "deepseek-v4-pro",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }

        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            summary = response.json()['choices'][0]['message']['content']
            
            # --- 3. 自动发信阶段 ---
            email_user = os.environ.get('EMAIL_USER')
            email_pass = os.environ.get('EMAIL_PASS')
            email_to = os.environ.get('EMAIL_TO')
            
            if email_user and email_pass and email_to:
                # 依然使用 Gmail 配置，端口 465
                yag = yagmail.SMTP(user=email_user, password=email_pass, host='smtp.gmail.com', port=465)
                yag.send(
                    to=email_to,
                    subject=f"📊 深度洞察：B站【{keyword}】流量价值简报",
                    contents=[summary]
                )
                print("✅ 报告已送达您的邮箱！")

        except Exception as e:
            print(f"❌ 运行失败: {e}")

if __name__ == "__main__":
    asyncio.run(scrape_and_analyze("大疆眼镜和穿越遥杆"))