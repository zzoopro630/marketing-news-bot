import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

def get_marketing_news():
    """마케팅 뉴스 수집"""
    news_list = []
    
    # RSS 피드 소스들
    rss_feeds = [
        'https://feeds.feedburner.com/MarketingLand',
        'https://feeds.feedburner.com/socialmediaexaminer',
        'https://blog.hubspot.com/marketing/rss.xml',
    ]
    
    # 간단한 RSS 파싱 (실제로는 더 복잡한 파싱 필요)
    # 여기서는 예시로 고정된 뉴스를 보여드립니다
    sample_news = [
        {"title": "2024 마케팅 트렌드 TOP 10", "url": "https://example.com/1"},
        {"title": "SNS 마케팅 최신 전략", "url": "https://example.com/2"},
        {"title": "구글 광고 정책 변경사항", "url": "https://example.com/3"},
        # ... 실제로는 RSS에서 가져온 데이터
    ]
    
    return sample_news[:20]  # 20개까지만

def send_email(news_list):
    """이메일 발송"""
    # 환경변수에서 이메일 정보 가져오기
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')
    receiver_email = os.environ.get('RECEIVER_EMAIL')
    
    if not all([sender_email, sender_password, receiver_email]):
        print("이메일 환경변수가 설정되지 않았습니다.")
        return
    
    # 이메일 내용 구성
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"🚀 오늘의 마케팅 뉴스 ({datetime.now().strftime('%Y-%m-%d')})"
    
    # HTML 형식으로 뉴스 목록 만들기
    html_content = """
    <html>
    <body>
        <h2>🚀 오늘의 마케팅 뉴스</h2>
        <p>안녕하세요! 오늘의 마케팅 뉴스를 전달드립니다.</p>
        <ul>
    """
    
    for i, news in enumerate(news_list, 1):
        html_content += f'<li><strong>{i}.</strong> <a href="{news["url"]}">{news["title"]}</a></li>'
    
    html_content += """
        </ul>
        <p>좋은 하루 되세요! 📈</p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_content, 'html'))
    
    # Gmail SMTP 서버로 이메일 발송
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("이메일 발송 완료!")
    except Exception as e:
        print(f"이메일 발송 실패: {e}")

if __name__ == "__main__":
    print("마케팅 뉴스 수집 시작...")
    news = get_marketing_news()
    send_email(news)
    print("완료!")
