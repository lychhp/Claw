import asyncio
from playwright.async_api import async_playwright
import os
import requests
import json
import yagmail

async def scrape_and_analyze(keyword):
    async with async_playwright() as p:
        # --- 1. 抓取阶段 (YouTube 版) ---
        browser = await p.chromium.launch(headless=True)
        # 将语言设置为中文(或英文)，以便 YouTube 返回对应语言的界面和时间格式
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="zh-CN" 
        )
        page = await context.new_page()

        print(f"🚀 [第一阶段] 正在潜入 YouTube 抓取【{keyword}】的全球爆款...")
        # 1. 网址改为 YouTube 的搜索链接
        await page.goto(f"https://www.youtube.com/results?search_query={keyword}")
        
        try:
            # 2. 定位器改为 YouTube 的视频卡片标签：ytd-video-renderer
            await page.wait_for_selector("ytd-video-renderer", timeout=15000)
            await asyncio.sleep(2) # 额外缓冲，确保数据加载完成
        except Exception:
            print("❌ 数据加载超时，可能需要处理 YouTube 弹窗。")
            await browser.close()
            return

        video_cards = await page.locator("ytd-video-renderer").all()
        
        scraped_data = ""
        for i, card in enumerate(video_cards[:5]):
            # 3. 提取 YouTube 标题和链接 (#video-title)
            title_elem = card.locator("#video-title")
            title = await title_elem.inner_text() if await title_elem.count() > 0 else "未知标题"
            
            link = await title_elem.get_attribute("href") if await title_elem.count() > 0 else ""
            # YouTube 提取的链接通常是 /watch?v=... ，需要补全前缀
            if link and link.startswith("/"): link = "https://www.youtube.com" + link
            
            # 4. 提取 YouTube 播放量和时间 (#metadata-line 里的 span)
            metadata_spans = await card.locator("#metadata-line span").all()
            views = await metadata_spans[0].inner_text() if len(metadata_spans) > 0 else "未知播放"
            upload_date = await metadata_spans[1].inner_text() if len(metadata_spans) > 1 else "未知日期"
            
            scraped_data += f"[{i+1}] 标题：{title}\n"
            scraped_data += f"    🔥 热度：{views} / 发布于：{upload_date}\n"
            scraped_data += f"    🔗 链接：{link}\n\n"

        await browser.close()
        print("✅ YouTube 深度抓取完成！数据已入库。")

        # --- 2. 大脑分析阶段 (DeepSeek) ---
        print("🧠 [第二阶段] DeepSeek 正在进行跨文化数据拆解...")
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key: return

        api_url = "https://api.deepseek.com/v1/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        
        # 5. 提示词全面修改为 YouTube 语境
        prompt = f"""
        你是一个拥有国际视野的视频内容分析师。我刚刚从 YouTube 抓取了关于“{keyword}”的 5 条最新全球爆款视频。
        
        原始抓取数据如下：
        {scraped_data}

        请根据这些数据完成以下分析：
        1. 【全球流量风向】：结合播放量和发布日期，判断该话题在国际上的热度趋势。
        2. 【内容切入点】：分析这些高播放视频是通过什么角度切入的（如硬核评测、教程、娱乐化表达等）？
        3. 附上这 5 个视频的完整清单（⚠️要求：必须原封不动地输出每个视频的完整网页链接和播放量，方便我直接点击观看！）。
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
                yag = yagmail.SMTP(user=email_user, password=email_pass, host='smtp.gmail.com', port=465)
                # 6. 邮件标题修改
                yag.send(
                    to=email_to,
                    subject=f"🌐 国际视野：YouTube【{keyword}】热度洞察简报",
                    contents=[summary]
                )
                print("✅ 报告已送达您的邮箱！")

        except Exception as e:
            print(f"❌ 运行失败: {e}")

if __name__ == "__main__":
    # 可以在这里换成英文关键词测试效果更好，比如 "AI Agent" 或 "DJI drone"
    asyncio.run(scrape_and_analyze("大疆无人机"))