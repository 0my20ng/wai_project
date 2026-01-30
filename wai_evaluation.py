from wai_rag_system import WelfareNavigator
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

# 한글 폰트 설정 (Windows: 맑은 고딕)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def run_evaluation():
    # 1. RAG 시스템 로드
    print("🧪 [Evaluation] 평가 시스템 초기화 중...")
    navigator = WelfareNavigator()
    
    # 2. 테스트 시나리오 로드 (STEP 4-1)
    import json
    import random
    scenario_path = os.path.join('data', 'test_scenarios.json')
    try:
        with open(scenario_path, 'r', encoding='utf-8') as f:
            all_scenarios = json.load(f)
        
        # 전체 중 50개를 무작위로 샘플링
        test_scenarios = random.sample(all_scenarios, min(50, len(all_scenarios)))
        print(f"📂 [Evaluation] 전체 {len(all_scenarios)}개 중 {len(test_scenarios)}개의 시나리오를 랜덤하게 로드했습니다.")
    except FileNotFoundError:
        print(f"⚠️ {scenario_path} 파일이 없습니다. 기본 5개 시나리오로 진행합니다.")
        test_scenarios = [
            {
                "id": 1,
                "persona": "원주 거주 대학생",
                "query": "원주시에 사는 대학생인데 등록금이랑 생활비 지원받을 수 있을까요?",
                "expected_keywords": ["장학", "학자금", "대학생"]
            },
            # ... (기타 기본 시나리오들)
        ][:1] # 예시로 하나만 유지하거나 에러 처리
    
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
    # 상세 결과 저장 및 시각화 준비
    df_res = pd.DataFrame(results_summary)
    os.makedirs('data', exist_ok=True)
    save_path = os.path.join('data', "evaluation_result.csv")
    df_res.to_csv(save_path, index=False)
    
    # 5. 시각화 (Visualization)
    print("\n📊 [Visualization] 평가 결과 시각화 중...")
    
    # 그래프 1: 정확도 비교 (Accuracy Chart)
    plt.figure(figsize=(8, 6))
    bars = plt.bar(['현재 정확도', '목표 정확도'], [accuracy, 90], color=['#4CAF50', '#FFA000'])
    plt.ylim(0, 100)
    plt.title('AI 모델 Top-3 정확도 (Accuracy)', fontsize=16)
    plt.ylabel('정확도 (%)')
    
    # 수치 표시
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 2, f'{yval}%', ha='center', va='bottom', fontsize=12)

    plt.savefig(os.path.join('data', 'evaluation_accuracy.png'))
    
    # 그래프 2: 시나리오별 유사도 점수 (Similarity per Scenario)
    plt.figure(figsize=(10, 6))
    colors = ['#2196F3' if x else '#F44336' for x in df_res['is_correct']]
    plt.bar(df_res['id'].astype(str), df_res['avg_sim'], color=colors)
    plt.axhline(y=avg_similarity_total, color='gray', linestyle='--', label='전체 평균 유사도')
    plt.title('시나리오별 평균 유사도 점수 (Blue: 정답, Red: 오답)', fontsize=16)
    plt.xlabel('시나리오 ID')
    plt.ylabel('유사도 점수')
    plt.ylim(0, 1.0)
    plt.legend()
    
    plt.savefig(os.path.join('data', 'evaluation_similarity.png'))
    
    print(f"✅ [시각화 완료] 'data/evaluation_accuracy.png', 'data/evaluation_similarity.png' 저장 완료")
    print(f"💾 상세 평가 결과가 '{save_path}'에 저장되었습니다.")

if __name__ == "__main__":
    run_evaluation()
