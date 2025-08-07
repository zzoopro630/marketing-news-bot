import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import re
from html import unescape

def clean_text(text):
    """HTML 태그 제거 및 텍스트 정리"""
    if not text:
        return ""
    
    # HTML 태그 제거
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    
    # HTML 엔티티 디코딩
    text = unescape(text)
    
    # 여러 공백을 하나로
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def fetch_rss_feed(url, source_name):
    """RSS 피드에서 뉴스 가져오기"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        articles = []
        
        # RSS 2.0 형식 파싱
        for item in root.findall('.//item')[:8]:  # 각 소스당 최대 8개
            title_elem = item.find('title')
            link_elem = item.find('link')
            description_elem = item.find('description')
            pub_date_elem = item.find('pubDate')
            
            if title_elem is not None and link_elem is not None:
                title = clean_text(title_elem.text)
                link = link_elem.text.strip() if link_elem.text else ""
                description = clean_text(description_elem.text) if description_elem is not None else ""
                
                # 제목이나 링크가 없으면 스킵
                if not title or not link:
                    continue
                
                # 제목 길이 제한 (너무 길면 자름)
                if len(title) > 100:
                    title = title[:97] + "..."
                
                articles.append({
                    'title': title,
                    'url': link,
                    'description': description[:200] + "..." if len(description) > 200 else description,
                    'source': source_name
                })
        
        print(f"✅ {source_name}: {len(articles)}개 뉴스 수집 완료")
        return articles
        
    except Exception as e:
        print(f"❌ {source_name} RSS 피드 오류: {e}")
        return []

def get_marketing_news():
    """다양한 소스에서 마케팅 뉴스 수집"""
    all_news = []
    
    # RSS 피드 소스들 (실제 작동하는 피드들)
    rss_sources = [
        {
            'url': 'https://marketingland.com/feed',
            'name': 'Marketing Land'
        },
        {
            'url': 'https://www.socialmediaexaminer.com/feed/',
            'name': 'Social Media Examiner'
        },
        {
            'url': 'https://blog.hubspot.com/marketing/rss.xml',
            'name': 'HubSpot Marketing'
        },
        {
            'url': 'https://neilpatel.com/feed/',
            'name': 'Neil Patel Blog'
        },
        {
            'url': 'https://contentmarketinginstitute.com/feed/',
            'name': 'Content Marketing Institute'
        },
        {
            'url': 'https://searchengineland.com/feed',
            'name': 'Search Engine Land'
        }
    ]
    
    print("🔍 마케팅 뉴스 수집 시작...")
    
    for source in rss_sources:
        articles = fetch_rss_feed(source['url'], source['name'])
        all_news.extend(articles)
    
    # 중복 제거 (제목 기준)
    seen_titles = set()
    unique_news = []
    for news in all_news:
        title_lower = news['title'].lower()
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            unique_news.append(news)
    
    print(f"📰 총 {len(unique_news)}개 고유 뉴스 수집 완료")
    
    # 최신 20개만 선택
    return unique_news[:20]

def send_email(news_list):
    """이메일 발송 (개선된 HTML 템플릿)"""
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    receiver_email = os.environ.get('RECEIVER_EMAIL')
    
    if not all([sender_email, sender_password, receiver_email]):
        print("❌ 이메일 환경변수가 설정되지 않았습니다.")
        return False
    
    if not news_list:
        print("❌ 보낼 뉴스가 없습니다.")
        return False
    
    # 이메일 구성
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"🚀 오늘의 마케팅 뉴스 TOP {len(news_list)}개 ({datetime.now().strftime('%Y-%m-%d')})"
    
    # 개선된 HTML 템플릿
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; }}
            .news-item {{ background: #f8f9fa; border-left: 4px solid #667eea; padding: 15px; margin: 15px 0; border-radius: 5px; }}
            .news-title {{ font-weight: bold; font-size: 16px; margin-bottom: 8px; }}
            .news-title a {{ color: #2c3e50; text-decoration: none; }}
            .news-title a:hover {{ color: #667eea; }}
            .news-source {{ color: #6c757d; font-size: 12px; font-weight: bold; }}
            .news-description {{ color: #555; font-size: 14px; margin-top: 8px; }}
            .footer {{ text-align: center; margin-top: 30px; padding: 20px; background: #f1f3f4; border-radius: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 오늘의 마케팅 뉴스</h1>
                <p>{datetime.now().strftime('%Y년 %m월 %d일')} • 총 {len(news_list)}개 뉴스</p>
            </div>
    """
    
    # 뉴스 목록 추가
    for i, news in enumerate(news_list, 1):
        html_content += f"""
            <div class="news-item">
                <div class="news-source">{news.get('source', 'Unknown')} • #{i}</div>
                <div class="news-title">
                    <a href="{news['url']}" target="_blank">{news['title']}</a>
                </div>
        """
        if news.get('description'):
            html_content += f'<div class="news-description">{news["description"]}</div>'
        html_content += '</div>'
    
    html_content += f"""
            <div class="footer">
                <p>📈 성공적인 하루 되세요!</p>
                <p><small>매일 오전 11시에 자동으로 발송됩니다 • Powered by GitHub Actions</small></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    # Gmail로 발송
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        print(f"✅ 이메일 발송 완료! ({len(news_list)}개 뉴스)")
        return True
        
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 마케팅 뉴스 자동 수집 봇 시작")
    print(f"⏰ 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        news = get_marketing_news()
        if news:
            success = send_email(news)
            if success:
                print("🎉 모든 작업 완료!")
            else:
                print("❌ 이메일 발송 실패")
        else:
            print("❌ 수집된 뉴스가 없습니다")
            
    except Exception as e:
        print(f"❌ 프로그램 실행 중 오류: {e}")
    
    print("=" * 50)
