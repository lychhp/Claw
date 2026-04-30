#!/bin/bash
# 本地测试 AI 大模型资讯爬虫

set -e

echo "📦 Installing dependencies..."
pip install -r scripts/requirements.txt

echo ""
echo "🚀 Running news collector..."
python scripts/fetch_ai_models_news.py

echo ""
echo "✅ Report generated successfully!"
echo ""
echo "📂 Generated reports:"
ls -lah reports/ 2>/dev/null || echo "   (No reports directory yet)"
