import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
import re
import os

# ==========================================
# 1. 설정 및 데이터 로드
# ==========================================
# 한글 폰트 설정 (Windows: 맑은 고딕, Mac: AppleGothic)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv(os.path.join('data', 'total_welfare_data.csv'))
df = df.fillna('') # 결측치 제거

print(f"🔄 데이터 로드 완료: 총 {len(df)}건")

# ==========================================
# 2. 텍스트 정제 (AI 학습용 데이터 만들기)
# ==========================================
def clean_text(text):
    # 1. 한글, 숫자, 공백만 남기고 특수문자 제거
    text = re.sub(r'[^가-힣0-9\s]', '', str(text))
    # 2. 다중 공백을 하나로 줄임
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# 'AI_학습용_데이터'라는 새로운 컬럼을 만듭니다. (다음 단계를 위해!)
# 사업명 + 지원대상 + 지원내용을 다 합쳐서 깨끗하게 청소합니다.
df['AI_학습용_데이터'] = (df['사업명'] + " " + df['지원대상'] + " " + df['지원내용']).apply(clean_text)

# 정제된 데이터를 파일로 저장 (Step 3에서 이걸 로드해서 씁니다)
os.makedirs('data', exist_ok=True)
df.to_csv(os.path.join('data', 'cleaned_welfare_data.csv'), index=False, encoding='utf-8-sig')
print("✅ [전처리 완료] 학습용 데이터 'data/cleaned_welfare_data.csv' 저장 끝!")


# ==========================================
# 3. 시각화 1: 데이터 분포 (Pie Chart)
# ==========================================
plt.figure(figsize=(10, 6))
counts = df['출처'].value_counts()
colors = ['#ff9999', '#66b3ff', '#99ff99'] # 예쁜 색상

plt.pie(counts, labels=counts.index, autopct='%1.1f%%', 
        startangle=140, colors=colors, textprops={'fontsize': 14})
plt.title('데이터 출처 분포 (공공 vs 민간)', fontsize=16)
plt.savefig(os.path.join('data', 'welfare_piechart.png'), bbox_inches='tight')
print("✅ [시각화 1] 분포 그래프 저장 완료")


# ==========================================
# 4. 시각화 2: 워드 클라우드 (Word Cloud)
# ==========================================
# 분석용 텍스트 합치기
text_corpus = " ".join(df['지원대상'].astype(str))

# 명사 추정 (2글자 이상 한글)
words = re.findall(r'[가-힣]{2,}', text_corpus)

# 불용어 제거
stop_words = ['지원', '대상', '신청', '가능', '이상', '이하', '경우', '포함', '해당', '기준', '가구', '내용', '참조', '사업', '모집', '선발', '자격', '요건', '사항', '기타', '또는', '있는']
filtered_words = [w for w in words if w not in stop_words]

# 워드 클라우드 생성
wc = WordCloud(
    font_path='C:/Windows/Fonts/malgun.ttf',
    width=1600, height=1000,
    background_color='white',
    colormap='viridis'
).generate_from_frequencies(Counter(filtered_words))

# 이미지 저장
wc.to_file(os.path.join('data', 'welfare_wordcloud.png'))
print("✅ [시각화 2] 워드 클라우드 저장 완료")

print("\n🚀 모든 전처리 과정이 끝났습니다. PPT에 이미지를 넣으세요!")