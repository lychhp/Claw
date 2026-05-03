import asyncio
from playwright.async_api import async_playwright
import os
import requests
import json
import yagmail  # 新增：用于发邮件的武器库

async def scrape_and_analyze(keyword):
    async with async_playwright() as p:
        # --- 1. 抓取阶段 ---
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print(f"🚀 [第一阶段] 正在 B 站抓取【{keyword}】的最新爆款...")
        await page.goto(f"https://search.bilibili.com/all?keyword={keyword}")
        
        try:
            await page.wait_for_selector(".bili-video-card", timeout=15000)
        except Exception:
            print("❌ 加载超时，可能遇到风控。")
            await browser.close()
            return

        video_cards = await page.locator(".bili-video-card").all()
        
        scraped_data = ""
        for i, card in enumerate(video_cards[:5]):
            title_elem = card.locator("h3")
            title = await title_elem.inner_text() if await title_elem.count() > 0 else "未知"
            
            link_elem = card.locator("a").first
            link = await link_elem.get_attribute("href") if await link_elem.count() > 0 else ""
            if link and link.startswith("//"): link = "https:" + link
            
            scraped_data += f"{i+1}. 标题：{title}\n   链接：{link}\n\n"

        await browser.close()
        print("✅ 抓取完成！收集到鲜活数据，准备提交给大脑...\n")

        # --- 2. 大脑分析阶段 (DeepSeek) ---
        print("🧠 [第二阶段] 正在呼叫 DeepSeek-v4-pro 进行深度洞察...")
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        
        if not api_key:
            print("⚠️ 警告：当前终端找不到你的 DEEPSEEK_API_KEY！")
            return

        api_url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json", 
            "Authorization": f"Bearer {api_key}"
        }
        
        prompt = f"""
        你是一个资深的 AI 行业观察员。我刚刚从 B 站抓取了关于“{keyword}”的最热排名前 5 的爆款视频。
        请根据这些视频的标题，帮我写一份《B站 AI 趋势洞察简报》。
        
        要求：
        1. 语气专业、犀利，直接切中要害。
        2. 总结目前大众最关注的核心痛点是什么？
        3. 排版美观，并在最后附上这 5 个视频的完整清单及链接。
        
        原始抓取数据如下：
        {scraped_data}
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
            print("📧 [第三阶段] 正在打包报告发送至您的邮箱...")
            email_user = os.environ.get('EMAIL_USER')
            email_pass = os.environ.get('EMAIL_PASS')
            email_to = os.environ.get('EMAIL_TO')
            
            if email_user and email_pass and email_to:
                # 💡 注意：如果你用的是163邮箱，把 smtp.qq.com 换成 smtp.163.com
                yag = yagmail.SMTP(user=email_user, password=email_pass, host='smtp.gmail.com', port=465)
                yag.send(
                    to=email_to,
                    subject=f"🔥 专属定制：B站【{keyword}】趋势洞察简报",
                    contents=[summary]
                )
                print("✅ 邮件发送成功！目标已达成！")
            else:
                print("⚠️ 缺少邮箱秘钥（云端会自动读取，本地测试若没配则跳过）。")

        except Exception as e:
            print(f"❌ DeepSeek 调用或发信失败，错误信息: {e}")

if __name__ == "__main__":
    asyncio.run(scrape_and_analyze("AI大模型"))