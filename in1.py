import requests
from bs4 import BeautifulSoup             # 크롤링
import time                               # sleep
from konlpy.tag import Okt                # 워드클라우드 
from collections import Counter           # 워드클라우드
from wordcloud import WordCloud           # 워드클라우드
import matplotlib.pyplot as plt           # 시각화

# 네이버 지식인 : 데이터 분석가 취업 검색 
base_url="https://kin.naver.com/search/list.nhn?sort=none&query=%EB%8D%B0%EC%9D%B4%ED%84%B0%EB%B6%84%EC%84%9D%EA%B0%80%20%EC%B7%A8%EC%97%85&period=2025.01.01.%7C2025.02.22.&section=kin&page={}"

headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}

# 링크 저장용 리스트 생성
all_links=[]

# 댓글 저장용 리스트 생성
all_comments=[]

# 1~20 페이지 크롤링
for page in range(1,21):
    url=base_url.format(page)
    response=requests.get(url, headers=headers)
    
    # 오류 걸러내기
    if response.status_code!=200:
        print(f"페이지 요청 실패 : {url}")
        continue

    soup=BeautifulSoup(response.text,"html.parser")
    print(f"{page} 페이지 크롤링 시작")

    # 게시글 URL 가져오기
    ul_data=soup.find('ul', {'class': 'basic1'})
    
    if ul_data:
        links=ul_data.find_all('a', {'class': '_nclicks:kin.txt _searchListTitleAnchor'})
        for link in links:
            href=link.get('href')
            full_link=href
            all_links.append(full_link)
            print(f"추출된 링크: {full_link}")
    else:
        print("게시글 목록을 찾지 못했습니다.")

    print(f"{page} 페이지 크롤링 완료")
    time.sleep(1) # 1초마다 실행

# 각 링크에서 답변 텍스트 추출
for link in all_links:
    response=requests.get(link, headers=headers)
    
    # 오류 걸러내기
    if response.status_code!=200:
        print(f"페이지 요청 실패: {link}")
        continue

    soup=BeautifulSoup(response.text, "html.parser")

    # 답변 텍스트 추출
    answers=soup.find_all('div', {'class': 'se-module se-module-text'})
    for answer in answers:
        all_comments.append(answer.get_text(strip=True))


# 댓글 텍스트 합치기
all_text = " ".join(all_comments)

# 형태소 분석 및 명사 추출
okt = Okt()
nouns = okt.nouns(all_text)

# 단어 빈도수 계산
word_counts = Counter(nouns)

# 워드 클라우드 생성
wordcloud = WordCloud(font_path='malgun.ttf', background_color='white', width=800, height=600).generate_from_frequencies(word_counts)

# 워드 클라우드 출력
plt.figure(figsize=(10, 8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.show()
