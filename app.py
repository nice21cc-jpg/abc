import streamlit as st
import pandas as pd
import os

# --------------------------------------------------------------------------
# 1. 페이지 및 스타일 설정
# --------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="2025 진로·진학 가이드", page_icon="🎓")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }
    
    .main-title { font-size: 32px; font-weight: 900; color: #1e3a8a; margin-bottom: 10px; }
    
    .section-header {
        font-size: 22px; font-weight: 800; color: #2d3748;
        margin-top: 50px; margin-bottom: 20px;
        display: flex; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px;
    }
    .section-header::before {
        content: ''; display: inline-block; width: 6px; height: 26px;
        background-color: #3182ce; margin-right: 12px; border-radius: 4px;
    }
    
    .desc-box {
        background-color: #f7fafc; border-left: 5px solid #3182ce; padding: 25px;
        border-radius: 0 12px 12px 0; font-size: 16px; line-height: 1.8; color: #2d3748;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-top: 10px; margin-bottom: 30px;
    }
    
    .subject-card {
        background-color: #ffffff; border: 1px solid #cbd5e0; border-radius: 16px; padding: 24px; height: 100%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); transition: transform 0.2s;
    }
    .subject-card:hover { transform: translateY(-5px); border-color: #3182ce; box-shadow: 0 10px 15px rgba(0,0,0,0.1); }
    
    .subj-badge {
        display: inline-block; padding: 6px 12px; border-radius: 8px; font-weight: 800;
        font-size: 15px; margin-bottom: 15px; width: 100%; text-align: center;
    }
    .badge-blue { background-color: #ebf8ff; color: #2c5282; border: 1px solid #bee3f8; }
    .badge-orange { background-color: #fffaf0; color: #c05621; border: 1px solid #feebc8; }
    .badge-green { background-color: #f0fff4; color: #276749; border: 1px solid #c6f6d5; }
    
    .subj-content { font-size: 16px; color: #1a202c; font-weight: 500; line-height: 1.6; word-break: keep-all; text-align: center; }
    
    .inquiry-box {
        background-color: #ffffff; border: 1px solid #9ae6b4; border-left: 5px solid #48bb78;
        border-radius: 8px; padding: 18px 24px; margin-bottom: 12px; color: #2f855a; font-weight: 600;
        display: flex; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .subject-tag {
        font-size: 0.9em; color: #22543d; border: 1px solid #9ae6b4; padding: 4px 10px;
        border-radius: 20px; margin-right: 12px; background-color: #f0fff4; font-weight: 800;
        min-width: 80px; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# 2. 스마트 매칭 함수
# --------------------------------------------------------------------------
def is_related(target_dept, source_str):
    if pd.isna(source_str) or source_str == '': return False
    target = str(target_dept).replace("학과", "").replace("학부", "").replace("전공", "").strip()
    source = str(source_str).replace("학과", "").replace("학부", "").replace("전공", "").strip()
    return target in source or source in target

# --------------------------------------------------------------------------
# 3. 데이터 로드 (★ 파일 찾기 도우미 추가 ★)
# --------------------------------------------------------------------------
@st.cache_data
def load_data():
    db_file = "학과카드_DB.xlsx"
    inq_file = "탐구주제목록.xlsx"

    # [1] 학과 데이터 (Sheet1)
    if os.path.exists(db_file):
        try:
            # 헤더 자동 찾기 로직
            df_major = pd.read_excel(db_file, sheet_name=0)
            for i in range(10):
                temp_cols = [str(c) for c in df_major.columns]
                if any("학과" in c for c in temp_cols) or any("계열" in c for c in temp_cols):
                    break
                df_major = pd.read_excel(db_file, sheet_name=0, header=i+1)
            
            # 컬럼명 공백 제거
            df_major.columns = df_major.columns.astype(str).str.replace(" ", "").str.strip()
            
            # [2] 도서 데이터 (Sheet2)
            try: 
                df_books = pd.read_excel(db_file, sheet_name=1)
                df_books.fillna('', inplace=True)
            except: df_books = pd.DataFrame()
        except Exception as e:
            st.error(f"파일 읽기 오류: {e}")
            return None, None, None
    else:
        # ★ 여기가 파일 찾기 도우미입니다 ★
        st.error(f"❌ '{db_file}' 파일을 찾을 수 없습니다.")
        st.warning(f"📂 현재 폴더 위치: {os.getcwd()}")
        
        # 현재 폴더의 파일 목록을 보여줍니다.
        files = os.listdir()
        st.write("📂 **현재 폴더에 있는 파일 목록:**")
        st.code("\n".join(files))
        
        st.info("💡 팁: 위 목록에 있는 파일 이름과 코드에 적힌 이름('학과카드_DB.xlsx')이 정확히 같은지 확인해보세요.")
        return None, None, None

    # [3] 탐구 주제 데이터
    df_inq = pd.DataFrame()
    if os.path.exists(inq_file):
        try:
            df_inq = pd.read_excel(inq_file)
            df_inq.fillna('', inplace=True)
        except: pass
    else:
        st.warning(f"⚠️ '{inq_file}' 파일이 없습니다.")

    return df_major, df_books, df_inq

df_major, df_books, df_inq = load_data()

# --------------------------------------------------------------------------
# 4. 화면 출력
# --------------------------------------------------------------------------
st.sidebar.title("🔍 검색 메뉴")
if df_major is not None:
    # 컬럼명 찾기
    dept_col = next((c for c in df_major.columns if "학과" in c), None)
    cat_col = next((c for c in df_major.columns if "계열" in c), "계열")
    
    if not dept_col:
        st.error("🚨 '학과' 관련 제목을 찾지 못했습니다.")
        st.write("현재 인식된 제목들:", df_major.columns.tolist())
        st.stop()
        
    if cat_col not in df_major.columns: df_major[cat_col] = '전체'

    # 필터
    cat_list = ["전체"] + sorted(df_major[cat_col].astype(str).unique().tolist())
    selected_cat = st.sidebar.selectbox("📂 계열 선택", cat_list)
    search_keyword = st.sidebar.text_input("🎓 학과명 검색")

    filtered = df_major.copy()
    if selected_cat != "전체": filtered = filtered[filtered[cat_col] == selected_cat]
    if search_keyword: filtered = filtered[filtered[dept_col].astype(str).str.contains(search_keyword)]

    st.markdown('<div class="main-title">🎓 2025학년도 학과별 진로 가이드</div>', unsafe_allow_html=True)
    st.divider()

    for idx, row in filtered.iterrows():
        dept_name = row[dept_col]
        cat_name = row[cat_col]
        
        st.markdown(f"## 🏫 {dept_name} <span style='font-size:0.6em; color:#4a5568;'>({cat_name})</span>", unsafe_allow_html=True)
        
        # [1] 학과 설명
        desc_col = next((c for c in df_major.columns if "설명" in c or "소개" in c), None)
        desc = row[desc_col] if desc_col else (row.iloc[2] if len(row) > 2 else "-")
        st.markdown(f'<div class="desc-box"><b>💡 학과 소개</b><br>{desc}</div>', unsafe_allow_html=True)
        
        # [2] 선택 과목
        st.markdown('<div class="section-header">📚 권장 선택 과목</div>', unsafe_allow_html=True)
        
        def find_val(r, k):
            for col in df_major.columns:
                if k in col and ("선택" in col or "과목" in col or "교과" in col): return r[col]
            return "-"

        gen = find_val(row, "일반")
        car = find_val(row, "진로")
        fus = find_val(row, "융합")

        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="subject-card"><span class="subj-badge badge-blue">📘 일반 선택</span><div class="subj-content">{gen}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="subject-card"><span class="subj-badge badge-orange">📙 진로 선택</span><div class="subj-content">{car}</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="subject-card"><span class="subj-badge badge-green">📗 융합 선택</span><div class="subj-content">{fus}</div></div>', unsafe_allow_html=True)

        # [3] 추천 도서
        st.markdown('<div class="section-header">📖 전공 추천 도서</div>', unsafe_allow_html=True)
        if not df_books.empty:
            major_col_idx = 1
            for i, c in enumerate(df_books.columns):
                if '전공' in str(c) or '학과' in str(c):
                    major_col_idx = i; break
            
            matches = df_books[df_books.iloc[:, major_col_idx].apply(lambda x: is_related(dept_name, x))]
            if not matches.empty:
                st.dataframe(matches, hide_index=True, use_container_width=True)
            else: st.info("관련 도서 정보가 없습니다.")

        # [4] 탐구 주제
        st.markdown('<div class="section-header">🔬 추천 탐구 주제</div>', unsafe_allow_html=True)
        if not df_inq.empty:
            inq_matches = df_inq[df_inq['학과'].apply(lambda x: is_related(dept_name, x))]
            if not inq_matches.empty:
                for _, q in inq_matches.iterrows():
                    st.markdown(f'<div class="inquiry-box"><span class="subject-tag">{q["관련교과"]}</span> {q["주제명"]}</div>', unsafe_allow_html=True)
            else: st.info("탐구 주제 정보가 없습니다.")
        
        st.markdown("<br><hr><br>", unsafe_allow_html=True)