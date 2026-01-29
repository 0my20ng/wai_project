import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
import xml.etree.ElementTree as ET

# ==========================================
# 1. 환경 설정 (Configuration)
# ==========================================
# 다운로드 받은 CSV 파일명
CSV_FILE_PATH = r'C:\Users\11\Desktop\wai_project\한국사회보장정보원_민간복지서비스정보_20251105.csv'

# 공공데이터포털에서 발급받은 청년정책 API 키 (여기에 입력하세요)
API_KEY = "30665de9-6085-43b3-980a-f9e94d4fe2f0" 

# ==========================================
# 2. 정형 데이터 수집: CSV 파일 로드
# ==========================================
def load_csv_data(file_path):
    print(f"🔄 [CSV] '{file_path}' 로딩 중...")
    try:
        # 한글 인코딩 처리 (cp949 또는 utf-8-sig)
        df = pd.read_csv(file_path, encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='utf-8')
    except FileNotFoundError:
        print("❌ 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        return pd.DataFrame()

    # 필요한 핵심 컬럼만 선택
    # 실제 컬럼명: '사업명', '지원대상', '지원내용', '신청방법', '사업종료일'
    selected_cols = ['사업명', '지원대상', '지원내용', '신청방법', '사업종료일']
    df = df[selected_cols]
    
    # 종료된 사업 필터링 (예: 2025년 이전 종료 사업 제외)
    # 날짜 형식이 제각각일 수 있어 문자열 비교로 간단히 처리하거나 생략 가능
    df['출처'] = '민간복지(CSV)'
    
    print(f"✅ [CSV] 로드 완료: {len(df)}건")
    return df

# ==========================================
# 3. 실시간 데이터 수집: Open API 호출
# ==========================================
def fetch_api_data(api_key):
    print("🔄 [API] 실제 청년정책 데이터 요청 중...")
    
    # 1. 실제 API URL (청년정책 조회)
    url = "https://www.youthcenter.go.kr/go/ythip/getPlcy"
    
    # 2. 요청 파라미터 설정
    params = {
        'openApiVlak': api_key,  # 발급받은 키 (Decoding Key 추천)
        'display': 100,          # 가져올 개수 (최대 100개)
        'pageIndex': 1,          # 페이지 번호
        'srchPolyBizSecd': '003002001' # (선택) 주거 분야 코드 등 (필요 없으면 삭제 가능)
    }

    try:
        # 3. 실제 요청 보내기
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            # 🚨 중요: 이 API는 기본적으로 XML을 반환합니다.
            # JSON을 원하면 url 뒤에 '&type=json' 같은게 필요한데, 
            # 보통 공공데이터는 XML이 기본이므로 XML 파싱으로 처리하는 게 안전합니다.
            
            try:
                # (1) XML 파싱 시도
                root = ET.fromstring(response.content)
                policies = []
                
                # XML 구조: <youthPolicyList> -> <youthPolicy> -> 각 항목들
                for item in root.findall('youthPolicy'):
                    policy = {
                        '사업명': item.find('polyBizSjnm').text,
                        '지원대상': item.find('ageInfo').text, # 또는 sportScvl(지원규모) 등 확인 필요
                        '지원내용': item.find('polyItcnCn').text,
                        '신청방법': item.find('rqutProcCn').text,
                        '상세링크': item.find('rqutUrla').text
                    }
                    policies.append(policy)
                
                df_api = pd.DataFrame(policies)
                df_api['출처'] = '청년정책(API)'
                print(f"✅ [API] 실제 데이터 수집 완료: {len(df_api)}건")
                return df_api
                
            except Exception as e:
                print(f"❌ 데이터 파싱 오류 (XML 구조 확인 필요): {e}")
                print("응답 내용 앞부분:", response.text[:200]) # 디버깅용
                return pd.DataFrame()
        else:
            print(f"❌ API 요청 실패: {response.status_code}")
            return pd.DataFrame()

    except Exception as e:
        print(f"❌ 연결 오류 발생: {e}")
        return pd.DataFrame()

    # ========================================================
    # 👇 Mock Data는 이제 주석 처리 (실제 키가 없을 때만 사용)
    # ========================================================
    # mock_data = [
    #     {
    #         '사업명': '[테스트] 청년월세지원',
    #         '지원대상': '만 19세~34세',
    #         '지원내용': '월 20만원',
    #         '신청방법': '복지로',
    #         '사업종료일': '2026-12-31'
    #     }
    # ]
    # return pd.DataFrame(mock_data)

# ==========================================
# 4. 상세 정보 수집: 웹 크롤링 (Web Crawling)
# ==========================================
def crawl_detail_content(url):
    """
    공고 상세 페이지 URL을 받아서 본문 텍스트를 긁어오는 함수
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 실제 사이트 구조에 맞춰 태그 수정 필요 (예: div.view_cont)
            # 여기서는 예시로 body 텍스트 전체를 가져옴
            text = soup.body.get_text(strip=True)
            return text[:500] + "..." # 너무 기니까 앞부분만 자름
        return ""
    except:
        return "크롤링 실패"

# ==========================================
# 5. 메인 실행 (Main Execution)
# ==========================================
if __name__ == "__main__":
    # 1. CSV 데이터 가져오기
    df_csv = load_csv_data(CSV_FILE_PATH)
    
    # 2. API 데이터 가져오기
    df_api = fetch_api_data(API_KEY)
    
    # 3. 데이터 통합 (Merge)
    final_df = pd.concat([df_csv, df_api], ignore_index=True)
    
    # 4. 결측치 간단 처리
    final_df = final_df.fillna("내용 없음")
    
    # 5. 결과 확인
    print("\n" + "="*40)
    print("🚀 [Step 1] 통합 데이터 구축 완료")
    print("="*40)
    print(f"총 데이터 개수: {len(final_df)}개")
    print(final_df.head())
    
    # 6. 파일로 저장 (다음 단계를 위해)
    final_df.to_csv("total_welfare_data.csv", index=False, encoding='utf-8-sig')
    print("\n💾 'total_welfare_data.csv' 파일로 저장되었습니다.")