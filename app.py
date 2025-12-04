import streamlit as st
import pandas as pd
import gobang  # gobang.py 파일(엔진)을 불러옵니다.

# =========================================================
# [1] 세션 상태 초기화
# =========================================================
if 'diagnosis_results' not in st.session_state:
    st.session_state['diagnosis_results'] = None
if 'selected_symptoms' not in st.session_state:
    st.session_state['selected_symptoms'] = []

# =========================================================
# [2] 처방 DB (키워드 정밀화 및 희안/복만 증상 보강 완료)
# =========================================================
FORMULA_DB = [
    # [1] 시호제
    {"name": "소시호탕", "symptoms": ["흉협고만", "구고", "인건", "목현", "왕래한열", "식욕부진", "구역", "편두통", "이명", "림프절종", "생리통", "피로", "불면", "아토피", "소변불리", "짜증", "신경질", "맥현"], "info": "간담의 열. 흉협고만과 식욕부진이 핵심. 흉부희안/복만과는 연관성이 낮습니다. [표준진료부]"},
    {"name": "대시호탕", "symptoms": ["흉협고만(강)", "심하급", "변비", "복통", "구토", "울울미번", "복부탄력(강)", "비만", "성격급함", "고혈압", "조열"], "info": "소시호탕증에 실증(변비, 복통)이 겸한 경우. [표준진료부]"},
    {"name": "시호가용골모려탕", "symptoms": ["흉만", "경(놀람)", "불면", "다몽", "섬어", "신중", "소변불리", "뇌전증", "틱", "불안초조", "심계", "제상동계"], "info": "기가 위로 뜨고 잘 놀라며, 몸이 무겁고 소변불리. [표준진료부]"},
    
    # [2] 백호/양명 계열
    {"name": "백호가인삼탕", "symptoms": ["대갈", "인음(물벌컥)", "구건", "설상건조", "수족냉(겨울)", "수족열(여름)", "소변불리", "구취", "식욕부진(여름)", "무한", "맥홍대", "피부건조", "피부거침", "아토피", "당뇨"], "info": "진액 고갈. 극심한 갈증, 피부건조/거침, 소변불리. [표준진료부]"},
    {"name": "백호탕", "symptoms": ["고열", "땀많음", "대갈", "맥홍대", "면구", "더위탐", "전신열"], "info": "4대 증상(고열, 땀, 갈증, 맥홍대) 실열. [표준진료부]"},
    {"name": "조위승기탕", "symptoms": ["변비", "복만", "섬어", "조열", "심번", "복부탄력(강)", "위장열"], "info": "대변 굳고 배 빵빵(복만), 위장 열. [표준진료부]"},
    
    # [3] 마황/계지 계열 (무한 증상 포함)
    {"name": "마황탕", "symptoms": ["무한", "오한", "발열", "두통", "신체통", "관절통", "천식", "맥부긴"], "info": "표실. 땀 없고 뼈마디 쑤심. [표준진료부]"},
    {"name": "갈근탕", "symptoms": ["항강", "무한", "오풍", "설사", "후중", "두통", "발열", "피부염", "눈다래끼"], "info": "뒷목 뻣뻣함. 무한. 설사 동반 감기/몸살. [표준진료부]"},
    {"name": "대청룡탕", "symptoms": ["고열", "무한", "번조", "갈증", "신중", "맥부긴", "아토피", "식욕좋음"], "info": "표는 차고 속은 열. 무한. [표준진료부]"},
    
    # [4] 수기/담음 (소변불리 포함)
    {"name": "오령산", "symptoms": ["소변불리", "갈증", "물설사", "두통", "부종", "구토", "과민성대장"], "info": "목 마른데 소변 안 나옴(소변불리). 물설사. [표준진료부]"},
    {"name": "영계출감탕", "symptoms": ["어지러움", "기립성현훈", "심계", "기상충", "흉협희안", "소변불리", "담음"], "info": "위장에 물이 차서 어지러움. 흉협희안. 소변불리. [표준진료부]"},
    {"name": "진무탕", "symptoms": ["어지러움", "신중", "설사", "복통", "소변불리", "떨림", "수족냉", "부종"], "info": "양기 부족, 몸이 무겁고 떨림. 소변불리. [표준진료부]"},
    
    # [5] 허한/음증 (흉부희안, 복만 핵심)
    {"name": "이중탕", "symptoms": ["복냉", "설사", "구토", "식욕부진", "흉협희안", "복통", "복만"], "info": "비위 허한. 누르면 편안함(흉협희안). 배 아프고 설사. 복만. [표준진료부]"},
    {"name": "당귀사역가오수유생강탕", "symptoms": ["수족궐한", "동창", "아랫배통증", "요통", "흉협희안", "오래된냉증"], "info": "혈허+한사. 흉협희안. 손발 시림 극심. [표준진료부]"},
    {"name": "오수유탕", "symptoms": ["두통(정수리)", "구역질", "수족냉", "번조", "토연말", "위장냉", "흉협희안"], "info": "위장 차가움, 흉협희안. 심한 구토와 두통. [표준진료부]"},
    {"name": "계지복령환", "symptoms": ["제하경결", "하복통", "생리통", "어혈", "다크서클", "족냉", "피부거침"], "info": "아랫배 어혈(계령괴). 피부가 거침. [표준진료부]"},
    {"name": "자감초탕", "symptoms": ["맥결대", "심계", "입마름", "변비", "불면", "피부건조"], "info": "진액 부족, 피부건조, 부정맥. [표준진료부]"},
    
    # [0] 기타
    {"name": "소함흉탕", "symptoms": ["정재심하", "심하통", "흉통", "가래", "기침", "거안", "비염", "소화불량"], "info": "명치 밑이 딱 걸려 아픔(정재심하). 누르면 통증. [표준진료부]"},
    {"name": "황련아교탕", "symptoms": ["불면(심함)", "심중번", "흉부거안", "가슴답답", "혀붉음", "코피", "수족열", "심계", "다리무력"], "info": "심열이 강해 잠을 못 잠. 음허화왕. [표준진료부]"},
]

# =========================================================
# [3] 진단 엔진 (매칭 로직 엄격하게 강화)
# =========================================================
def calculate_score(selected_symptoms):
    results = []
    for formula in FORMULA_DB:
        score = 0
        matched = []
        for db_symptom in formula['symptoms']:
            for user_symptom in selected_symptoms:
                # [핵심 수정] 완벽하게 일치할 때만 점수 획득 (신뢰도 극대화)
                if user_symptom == db_symptom: 
                    score += 1
                    matched.append(db_symptom)
                     
        if score > 0:
            matched = list(set(matched))
            results.append({
                "name": formula['name'],
                "score": score,
                "matched": matched,
                "info": formula['info']
            })
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

# =========================================================
# [4] UI 메인 함수
# =========================================================
def main():
    st.set_page_config(page_title="상한론 표준진료부", layout="wide")
    st.title("🩺 상한론 표준진료부 정밀 진단기")
    
    with st.expander("📝 표준진료부 체크리스트 열기/닫기", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        current_inputs = []

        with c1:
            st.markdown("**흉부/명치**")
            if st.checkbox("흉부거안 (답답/아픔)"): current_inputs.append("흉부거안")
            if st.checkbox("흉부희안 (누르면 시원)"): current_inputs.append("흉부희안")
            if st.checkbox("흉협고만 (옆구리 그득)"): current_inputs.append("흉협고만")
            if st.checkbox("심하비 (명치 답답)"): current_inputs.append("심하비")
            if st.checkbox("정재심하 (명치통)"): current_inputs.append("정재심하")
        with c2:
            st.markdown("**복부 상태**")
            if st.checkbox("복직근 긴장"): current_inputs.append("복직근")
            if st.checkbox("제하경결 (배꼽 옆)"): current_inputs.append("제하경결")
            if st.checkbox("소복현급 (아랫배 당김)"): current_inputs.append("소복현급")
            if st.checkbox("복만 (배가 빵빵)"): current_inputs.append("복만")
            if st.checkbox("복냉 (배가 참)"): current_inputs.append("복냉")
        with c3:
            st.markdown("**복부 탄력/압통**")
            if st.checkbox("복부탄력 강 (실함)"): current_inputs.append("복부탄력(강)")
            if st.checkbox("거안 (누르면 아픔)"): current_inputs.append("거안")
            if st.checkbox("희안 (누르면 좋음)"): current_inputs.append("희안")
            if st.checkbox("심하유수기 (꿀렁)"): current_inputs.append("심하유수기")
            if st.checkbox("장명 (물소리)"): current_inputs.append("장명")
        with c4:
            st.markdown("**기타 복진**")
            if st.checkbox("소복불인 (감각둔함)"): current_inputs.append("소복불인")
            if st.checkbox("소복경결"): current_inputs.append("소복경결")
            if st.checkbox("제상동계 (배꼽 뜀)"): current_inputs.append("제상동계")

        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("**설진**")
            if st.checkbox("설태 (백태/황태)"): current_inputs.append("설태")
            if st.checkbox("설홍 (혀가 붉음)"): current_inputs.append("혀붉음")
            if st.checkbox("설상건조 (마름)"): current_inputs.append("설상건조")
            if st.checkbox("치흔 (이빨자국)"): current_inputs.append("치흔")
        with c2:
            st.markdown("**맥진**")
            if st.checkbox("맥부 (뜸)"): current_inputs.append("맥부")
            if st.checkbox("맥침 (가라앉음)"): current_inputs.append("맥침")
            if st.checkbox("맥현 (활줄)"): current_inputs.append("맥현")
            if st.checkbox("맥긴 (팽팽)"): current_inputs.append("맥긴")
            if st.checkbox("맥약/미세"): current_inputs.append("맥약")
            if st.checkbox("맥홍대 (크고 넓음)"): current_inputs.append("맥홍대")
            if st.checkbox("맥결대 (부정맥)"): current_inputs.append("맥결대")
        with c3:
            st.markdown("**안면/피부**")
            if st.checkbox("안면홍조 (붉음)"): current_inputs.append("안면홍조")
            if st.checkbox("하안검 창백"): current_inputs.append("하안검")
            if st.checkbox("피부 건조 (Dry)"): current_inputs.append("피부건조")
            if st.checkbox("피부 거침 (Rough)"): current_inputs.append("피부거침")
            if st.checkbox("아토피/피부병"): current_inputs.append("아토피")
            if st.checkbox("부종 (붓기)"): current_inputs.append("부종")
        with c4:
            st.markdown("**한열/땀**")
            if st.checkbox("오한 (추위)"): current_inputs.append("오한")
            if st.checkbox("발열 (열)"): current_inputs.append("발열")
            if st.checkbox("상열하냉"): current_inputs.append("상열하냉")
            if st.checkbox("무한 (땀안남)"): current_inputs.append("무한")
            if st.checkbox("자한 (식은땀)"): current_inputs.append("자한")
            if st.checkbox("도한 (잘때 땀)"): current_inputs.append("도한")
            if st.checkbox("두한 (머리 땀)"): current_inputs.append("두한")

        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("**소화기**")
            if st.checkbox("식욕부진 (못 먹음)"): current_inputs.append("식욕부진")
            if st.checkbox("식욕왕성 (잘 먹음)"): current_inputs.append("식욕좋음")
            if st.checkbox("구토/구역"): current_inputs.append("구역")
            if st.checkbox("소화불량"): current_inputs.append("소화불량")
            if st.checkbox("입덧"): current_inputs.append("입덧")
            if st.checkbox("신물/속쓰림"): current_inputs.append("신물")
        with c2:
            st.markdown("**대소변**")
            if st.checkbox("설사 (하리)"): current_inputs.append("설사")
            if st.checkbox("변비"): current_inputs.append("변비")
            if st.checkbox("후중 (뒤무직)"): current_inputs.append("후중")
            if st.checkbox("소변불리 (안나옴)"): current_inputs.append("소변불리")
            if st.checkbox("소변빈삭 (자주 봄)"): current_inputs.append("소변빈삭")
            if st.checkbox("야뇨"): current_inputs.append("야뇨")
        with c3:
            st.markdown("**통증/신경**")
            if st.checkbox("두통"): current_inputs.append("두통")
            if st.checkbox("편두통"): current_inputs.append("편두통")
            if st.checkbox("항강 (뒷목뻣뻣)"): current_inputs.append("항강")
            if st.checkbox("신체통 (몸살)"): current_inputs.append("신체통")
            if st.checkbox("관절통"): current_inputs.append("관절통")
            if st.checkbox("생리통"): current_inputs.append("생리통")
        with c4:
            st.markdown("**정신/기타**")
            if st.checkbox("불면"): current_inputs.append("불면")
            if st.checkbox("가슴두근 (심계)"): current_inputs.append("심계")
            if st.checkbox("불안/초조"): current_inputs.append("불안")
            if st.checkbox("짜증/신경질"): current_inputs.append("짜증")
            if st.checkbox("어지러움 (현훈)"): current_inputs.append("어지러움")
            if st.checkbox("매핵기 (목이물감)"): current_inputs.append("매핵기")
            if st.checkbox("구갈/구건 (입마름)"): current_inputs.append("구건")
            if st.checkbox("수족냉 (손발참)"): current_inputs.append("수족냉")

    # 분석 버튼
    if st.button("🚀 처방 분석 및 리스트 갱신", type="primary", use_container_width=True):
        st.session_state['selected_symptoms'] = current_inputs
        if current_inputs:
            results = calculate_score(current_inputs)
            st.session_state['diagnosis_results'] = results
        else:
            st.session_state['diagnosis_results'] = None
            st.error("증상을 하나 이상 선택해주세요.")

    # =========================================================
    # [결과 화면 및 자동 합방 로직]
    # =========================================================
    if st.session_state['diagnosis_results']:
        st.divider()
        st.subheader("📋 추천 처방 리스트 (체크하여 자동 합방)")
        st.info(f"선택된 증상: {', '.join(st.session_state['selected_symptoms'])}")
        
        df_gobang = gobang.load_data()
        formulas_to_combine = []
        
        for i, res in enumerate(st.session_state['diagnosis_results'][:15]):
            
            row = df_gobang[df_gobang['처방명'] == res['name']]
            herb_info = "약재 정보 없음"
            if not row.empty:
                herb_info = row.iloc[0]['구성약재']
            
            c_chk, c_name, c_herb = st.columns([1.5, 3, 4])
            
            with c_chk:
                default_chk = True if i == 0 else False
                is_checked = st.checkbox(f"선택 {i+1}", value=default_chk, key=f"chk_{i}")
                ratio = st.number_input("배율", min_value=0.1, value=1.0, step=0.1, key=f"ratio_{i}", label_visibility="collapsed")
            
            with c_name:
                # [수정] 매칭된 증상 목록을 강조하여 보여줍니다.
                matched_str = ', '.join(res['matched'])
                st.markdown(f"**{res['name']}** ({res['score']}개 일치)")
                st.caption(f"**일치 증상:** {matched_str}")
                st.caption(f"{res['info']}")
                
            with c_herb:
                st.text(f"구성: {herb_info}")
            
            st.markdown("---")
            
            if is_checked:
                formulas_to_combine.append((res['name'], ratio))

        if formulas_to_combine:
            st.success(f"🥣 자동 합방 결과 ({len(formulas_to_combine)}개 처방)")
            
            final_herbs = {}
            for fname, multiplier in formulas_to_combine:
                row = df_gobang[df_gobang['처방명'] == fname]
                if not row.empty:
                    herbs_dict = gobang.parse_herbs(row.iloc[0]['구성약재'])
                    for herb, qty in herbs_dict.items():
                        scaled_qty = qty * multiplier
                        if herb in final_herbs:
                            final_herbs[herb] = max(final_herbs[herb], scaled_qty)
                        else:
                            final_herbs[herb] = scaled_qty
            
            if final_herbs:
                result_df = pd.DataFrame(list(final_herbs.items()), columns=['약재명', '용량(g)'])
                result_df = result_df.sort_values(by='용량(g)', ascending=False)
                result_df['용량(g)'] = result_df['용량(g)'].apply(lambda x: round(x, 1) if x % 1 != 0 else int(x))
                
                st.table(result_df)
                
                summary_text = " + ".join([f"{name}(x{r})" for name, r in formulas_to_combine])
                st.caption(f"합방된 처방: {summary_text}")

if __name__ == "__main__":
    main()
