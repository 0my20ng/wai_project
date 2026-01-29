from wai_rag_system import WelfareNavigator
import pandas as pd
import numpy as np

def run_evaluation():
    # 1. RAG 시스템 로드
    print("🧪 [Evaluation] 평가 시스템 초기화 중...")
    navigator = WelfareNavigator()
    
    # 2. 테스트 시나리오 (STEP 4-1)
    # 페르소나와 예상되는 정답 키워드 정의
    test_scenarios = [
        {
            "id": 1,
            "persona": "원주 거주 대학생",
            "query": "원주시에 사는 대학생인데 등록금이랑 생활비 지원받을 수 있을까요?",
            "expected_keywords": ["장학", "학자금", "대학생"]
        },
        {
            "id": 2,
            "persona": "미취업 청년 (취업 준비)",
            "query": "졸업하고 아직 취업을 못했어요. 구직 활동 지원금이나 면접 정장 대여 같은거 있나요?",
            "expected_keywords": ["구직", "취업", "미취업", "면접"]
        },
        {
            "id": 3,
            "persona": "주거비 부담 청년",
            "query": "자취하는데 월세가 너무 비싸요. 전세 자금 대출이나 월세 지원 정책 좀 알려주세요.",
            "expected_keywords": ["주거", "월세", "전세", "주택"]
        },
        {
            "id": 4,
            "persona": "창업 희망자",
            "query": "카페를 창업하고 싶은데 초기 자금이나 사무실 지원 받을 수 있는 곳이 있나요?",
            "expected_keywords": ["창업", "스타트업", "사업화"]
        },
        {
            "id": 5,
            "persona": "문화 생활",
            "query": "주말에 심심한데 청년들이 모여서 활동하거나 문화비 지원해주는거 없나요?",
            "expected_keywords": ["동아리", "네트워크", "문화", "활동"]
        }
    ]
    
    # 3. 평가 실행 및 정량적 수치 계산 (STEP 4-2)
    print(f"\n🚀 총 {len(test_scenarios)}개의 테스트 시나리오에 대해 평가를 시작합니다.\n")
    
    correct_count = 0
    total_similarity_sum = 0
    total_results_count = 0
    
    results_summary = []

    for case in test_scenarios:
        print(f"--- [Scenario #{case['id']}] {case['persona']} ---")
        print(f"❓ 질문: {case['query']}")
        
        # 검색 수행 (Top 3)
        search_results = navigator.search(case['query'], top_k=3)
        
        # 정답 여부 판단 (Keyword Matching)
        is_correct = False
        matched_policy = "없음"
        
        current_similarities = []
        
        print("🔍 추천 결과:")
        for res in search_results:
            current_similarities.append(res['similarity'])
            print(f"  - {res['사업명']} (유사도: {res['similarity']:.4f})")
            
            # 예상 키워드가 사업명이나 내용에 포함되어 있는지 확인
            for keyword in case['expected_keywords']:
                if keyword in res['사업명'] or keyword in res['지원대상'] or keyword in res['지원내용']:
                    is_correct = True
                    matched_policy = res['사업명']
                    break
            if is_correct: break # 하나라도 맞으면 정답 처리
        
        if is_correct:
            correct_count += 1
            print(f"✅ 결과: 정답 (매칭된 정책: {matched_policy})")
        else:
            print(f"❌ 결과: 오답 (적절한 키워드 '{case['expected_keywords']}' 미발견)")
        
        print("")
        
        total_similarity_sum += sum(current_similarities)
        total_results_count += len(current_similarities)
        
        results_summary.append({
            "id": case['id'],
            "is_correct": is_correct,
            "avg_sim": np.mean(current_similarities)
        })

    # 4. 최종 리포트 출력
    accuracy = (correct_count / len(test_scenarios)) * 100
    avg_similarity_total = total_similarity_sum / total_results_count if total_results_count > 0 else 0
    
    print("\n" + "="*50)
    print("📊 [STEP 4] 성능 평가 최종 리포트")
    print("="*50)
    print(f"1. Top-3 정확도 (Accuracy): {accuracy:.1f}%")
    print(f"   - (목표치 90% 달성 여부: {'성공 🎉' if accuracy >= 90 else '미달 (데이터 보완 필요) ⚠️'})")
    print(f"2. 평균 유사도 점수 (Avg Similarity): {avg_similarity_total:.4f}")
    print("="*50)
    
    # 상세 결과 저장
    df_res = pd.DataFrame(results_summary)
    df_res.to_csv("evaluation_result.csv", index=False)
    print("💾 상세 평가 결과가 'evaluation_result.csv'에 저장되었습니다.")

if __name__ == "__main__":
    run_evaluation()
