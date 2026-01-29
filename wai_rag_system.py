import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
import time

class WelfareNavigator:
    def __init__(self, csv_path='total_welfare_data.csv', model_name='snunlp/KR-SBERT-V40K-klueNLI-augSTS'):
        """
        초기화 함수: 데이터 로드 및 모델 로드
        """
        print("⏳ [System] 데이터 및 모델 로딩 중... (시간이 조금 걸릴 수 있습니다)")
        self.df = self._load_data(csv_path)
        self.model = SentenceTransformer(model_name)
        self.embeddings = self._create_embeddings()
        print("✅ [System] 시스템 준비 완료!")

    def _load_data(self, path):
        """
        CSV 파일을 로드하고 필요한 전처리를 수행합니다.
        """
        try:
            df = pd.read_csv(path)
            # 결측치 처리
            df.fillna('', inplace=True)
            
            # 검색 및 임베딩을 위한 통합 텍스트 컬럼 생성
            # 사업명 + 지원대상 + 지원내용을 합쳐서 문맥을 풍부하게 함
            df['combined_text'] = (
                "사업명: " + df['사업명'] + " | " + 
                "지원대상: " + df['지원대상'] + " | " + 
                "지원내용: " + df['지원내용']
            )
            return df
        except FileNotFoundError:
            raise Exception(f"❌ '{path}' 파일을 찾을 수 없습니다. STEP 1을 먼저 실행해주세요.")

    def _create_embeddings(self):
        """
        텍스트 데이터를 벡터화(Embedding)합니다.
        """
        print("🔄 [Embedding] 정책 데이터 벡터화 진행 중...")
        # encode 함수는 텍스트 리스트를 입력받아 벡터 행렬을 반환
        return self.model.encode(self.df['combined_text'].tolist(), show_progress_bar=True)

    def search(self, user_query, top_k=3):
        """
        사용자 질문과 가장 유사한 복지 정책을 검색합니다.
        """
        # 1. 사용자 질문 벡터화
        query_embedding = self.model.encode([user_query])
        
        # 2. 코사인 유사도 계산
        # query_embedding(1, 768) vs embeddings(N, 768)
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # 3. 상위 k개 인덱스 추출
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'rank': len(results) + 1,
                'similarity': float(similarities[idx]),
                '사업명': self.df.iloc[idx]['사업명'],
                '지원대상': self.df.iloc[idx]['지원대상'],
                '지원내용': self.df.iloc[idx]['지원내용'],
                '신청방법': self.df.iloc[idx]['신청방법'],
                '상세링크': self.df.iloc[idx]['상세링크']
            })
            
        return results

    def generate_answer(self, query, retrieval_results):
        """
        (선택사항) LLM을 사용하여 친절한 답변을 생성합니다.
        실제 API 키가 필요하므로 여기서는 시뮬레이션 로직을 구현합니다.
        """
        context = ""
        for res in retrieval_results:
            context += f"- {res['사업명']} (적합도: {res['similarity']:.2f}): {res['지원내용'][:50]}...\n"

        prompt = f"""
        [역할] 당신은 원주시 복지 상담사입니다.
        [질문] {query}
        [참고 정보]
        {context}
        
        [지시] 위 참고 정보를 바탕으로 사용자에게 도움이 될만한 정책을 추천해주고, 신청 방법을 안내해주세요.
        """
        
        # 실제 LLM 연결 시:
        # response = openai.ChatCompletion.create(...)
        # return response.choices[0].message.content
        
        return f"[LLM 답변 시뮬레이션]\n안녕하세요! 질문하신 내용에 맞춰 추천드리는 정책은 다음과 같습니다.\n\n{context}\n위 정보를 참고하여 신청해주시면 큰 도움이 될 것 같습니다!"

# 실행 테스트
if __name__ == "__main__":
    navigator = WelfareNavigator()
    
    question = "나 원주 사는 대학생인데 생활비가 부족해. 장학금 같은 거 없을까?"
    print(f"\n🗣️ 질문: {question}")
    
    results = navigator.search(question)
    
    print("\n🔍 검색 결과:")
    for res in results:
        print(f"[{res['rank']}위] {res['사업명']} (유사도: {res['similarity']:.4f})")
    
    print("\n🤖 AI 답변:")
    print(navigator.generate_answer(question, results))
