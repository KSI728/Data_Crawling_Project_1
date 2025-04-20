import requests
from bs4 import BeautifulSoup             # 크롤링
import time                               # sleep
from konlpy.tag import Okt                # 워드클라우드 
from collections import Counter           # 워드클라우드
from wordcloud import WordCloud           # 워드클라우드
import matplotlib.pyplot as plt           # 시각화 
import numpy as np                        # 배열
from PIL import Image                     # 이미지   
import re                                 # 정규식
import koreanize_matplotlib               # 한글화
import textwrap

# 크롤링 함수 생성
def crawl_saramin(searchword):
    base_url = "https://www.saramin.co.kr/zf_user/search/recruit?search_area=main&search_done=y&search_optional_item=n&searchType=search&searchword={}&show_applied=&except_read=&ai_head_hunting=&recruitPage={}&recruitSort=accuracy&recruitPageCount=40&inner_com_type=&company_cd=0%2C1%2C2%2C3%2C4%2C5%2C6%2C7%2C9%2C10&quick_apply=&mainSearch=n"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}

    # 데이터 저장용 리스트 생성
    all_data = []

    # 1~20 페이지 크롤링
    for page in range(1, 21):
        url = base_url.format(searchword, page)
        response = requests.get(url, headers=headers)

        # 오류 걸러내기
        if response.status_code != 200:
            print(f"페이지 요청 실패 : {url}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        print(f"{page} 페이지 크롤링 시작")

        # 필요한 데이터 추출하기
        job_sectors = soup.find_all("div", class_="job_sector")
        
        for job_sector in job_sectors:
            job_titles = job_sector.find_all("a")
            for job_title in job_titles:
                all_data.append(job_title.text.strip())

    return all_data

# 사용자로부터 검색어 입력 받기
searchword = input("검색어를 입력하세요: ")
all_data = crawl_saramin(searchword)
print(all_data)

# 제외할 단어 목록
stopwords=set(['DBA', 'SE(시스템엔지니어)', 'RFP(제안요청서)', 'IT·통신기기판매', 'SI·시스템통합', 'IT강사', 'PM(프로젝트매니저)', 'AE(광고기획자)', 'PL(프로젝트리더)',
               'HR컨설팅','A·S센터', 'IT컨설팅', 'IT학원','SI영업','IT영업','GM(게임운영)'])

# 영어 단어만 추출하기
english_words = [word for word in all_data if re.match(r'^[a-zA-Z].*$', word)]

# 필요없는 단어 제외
filtered_words = [word for word in english_words if word not in stopwords]
word_counts = Counter(filtered_words)

# 빈도수가 낮은 항목들을 '기타' 항목으로 묶기
threshold = 4  # 임계값 설정 
other_items = []
filtered_counts = {}

for word, count in word_counts.items():
    if count <= threshold:
        other_items.append(word)
    else:
        filtered_counts[word] = count

if other_items:
    filtered_counts['기타'] = sum([word_counts[word] for word in other_items])

# 파이 차트 생성을 위한 준비
labels = list(filtered_counts.keys())
sizes = list(filtered_counts.values())

# 제일 퍼센트가 큰 거 부터 정렬 : 기타 항목은 제일 뒤로
# "기타" 항목을 분리
if '기타' in labels:
    guitar_index = labels.index('기타')
    guitar_size = sizes.pop(guitar_index)
    labels.pop(guitar_index)
else:
    guitar_size = None

# 퍼센트가 큰 순서로 정렬
sorted_data = sorted(zip(sizes, labels), reverse=True)
sizes, labels = zip(*sorted_data)

# "기타" 항목을 제일 뒤에 추가
if guitar_size is not None:
    sizes = list(sizes)
    labels = list(labels)
    sizes.append(guitar_size)
    labels.append('기타')

fig, ax = plt.subplots(1, 2, figsize=(18, 8))

# 파이 차트
colors = ['#FF6347', '#FFB266', '#FFD700', '#FFE766', '#FFFF99', 
        '#CCFF99', '#99FF99', '#99FFCC', '#99FFFF', '#99CCFF', 
        '#9999FF', '#CC99FF', '#FF99FF','#FFB6C1']
ax[0].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
ax[0].axis('equal')  
ax[0].set_title(f'{searchword} 취업 시장에서 필요로 하는 능력', pad=20)

# 기타 항목 목록 표시
if other_items:
    other_text = "\n".join(other_items)
else:
    other_text = "기타 항목 없음"

# 텍스트를 줄 바꿈하여 리스트로 변환
wrapped_text = "\n".join(textwrap.wrap(other_text, width=30))
                                       
# 텍스트 박스 설정
props = dict(boxstyle='round,pad=1', facecolor='wheat', alpha=0.5)
ax[1].text(
    0.5, 0.5, 
    wrapped_text, 
    ha='center', 
    va='center', 
    fontsize=12, 
    wrap=True,
    bbox=props)

# 축 숨김 설정
ax[1].axis('off')

# 제목 설정
ax[1].set_title('기타 항목 목록', pad=20)

plt.tight_layout()
plt.show()




