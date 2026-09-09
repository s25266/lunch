import datetime
import calendar
import streamlit as st

st.set_page_config(page_title="축구선수 맞춤형 영양 급식 달력", page_icon="⚽", layout="wide")
st.title("⚽ 축구선수 맞춤형 월간 영양 식단표")
st.caption("고강도 훈련과 경기를 위한 선수용 맞춤 영양 식단 및 알레르기 정보를 확인합니다.")

# 알레르기 표기용 맵
ALLERGY_MAP = {
    1: "난류", 2: "우유", 3: "메밀", 4: "땅콩", 5: "대두",
    6: "밀", 7: "고등어", 8: "게", 9: "새우", 10: "돼지고기",
    11: "복숭아", 12: "토마토", 13: "아황산류", 14: "호두", 15: "닭고기",
    16: "쇠고기", 17: "오징어", 18: "조개류(굴/전복/홍합 포함)", 19: "잣",
}

# ⚽ 축구선수 샘플 식단 데이터베이스 (1일 ~ 31일 순환 제공)
ATHLETE_MEALS_DB = [
    {
        "중식": [f"현미잡곡밥 ({ALLERGY_MAP[5]})", "차돌된장찌개 (5.16.)", "안동찜닭 (5.6.15.)", "계란말이 (1.)", "부추겉절이", "포도"],
        "석식": ["쌀밥", "맑은 콩나물국 (5.)", "돈육간장불고기 (5.6.10.)", "두부구이 (5.)", "상추쌈/쌈장 (5.6.)", "바나나"],
        "tip": "💪 근육 회복 & 탄수화물 로딩 Day"
    },
    {
        "중식": ["기장밥", "쇠고기미역국 (16.)", "고등어구이 (7.)", "메추리알장조림 (1.5.6.16.)", "시금치나물", "사과"],
        "석식": ["토마토해물파스타 (1.2.5.6.8.9.12.17.18.)", "닭가슴살 샐러드 (15.)", "마늘빵 (2.5.6.)", "오렌지주스"],
        "tip": "⚡ 오메가-3 염증 완화 & 고탄수화물"
    },
    {
        "중식": ["흑미밥", "닭개장 (15.)", "연어스테이크 (5.)", "단호박찜", "멸치볶음 (5.6.)", "귤"],
        "석식": ["곤드레밥/양념장 (5.6.)", "소불고기 (5.6.16.)", "해물파전 (1.5.6.9.17.)", "겉절이", "수박"],
        "tip": "🥗 항산화 & 고단백 재건"
    },
    {
        "중식": ["오곡밥", "전복갈비탕 (16.18.)", "오징어볶음 (17.)", "계란찜 (1.)", "브로콜리숙회 (5.6.)", "키위"],
        "석식": ["닭죽 (15.)", "훈제오리구이", "무쌈/부추무침", "방울토마토 (12.)"],
        "tip": "🔥 고보양 단백질 & 빠른 소화"
    },
    {
        "중식": ["카레라이스 (2.5.6.10.12.16.)", "닭다리구이 (15.)", "양상추샐러드 (1.2.5.)", "포기김치 (9.)", "블루베리 요거트 (2.)"],
        "석식": ["연어덮밥(사케동) (5.6.)", "미소시루 (5.)", "계란말이 (1.)", "블루베리"],
        "tip": "⚽ 경기 대비 글리코겐 최대 축적"
    }
]

# 사이드바 설정
st.sidebar.header("⚙️ 식단표 환경 설정")
show_allergen = st.sidebar.toggle("알레르기 정보 표시", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("⚽ 축구선수 영양 가이드")
st.sidebar.info("""
- **탄수화물 (60~70%)**: 운동 전후 주요 에너지원(글리코겐) 보충
- **단백질 (20~25%)**: 근육 손실 방지 및 고강도 훈련 후 회복
- **오메가3 & 비타민**: 관절 염증 완화 및 근육 경련(쥐) 예방
""")

# 연도 및 월 선택 UI
today = datetime.date.today()
col_y, col_m, col_filter = st.columns([1, 1, 2])
with col_y:
    year = st.selectbox("연도 선택", options=list(range(today.year - 1, today.year + 2)), index=1)
with col_m:
    month = st.selectbox("월 선택", options=list(range(1, 13)), index=today.month - 1)
with col_filter:
    meal_filter = st.radio("급식 종류 선택", options=["전체 보기", "중식만 보기", "석식만 보기"], index=0, horizontal=True)

st.markdown("---")

# 달력 계산
month_cal = calendar.monthcalendar(year, month)
weekdays_kr = ["월", "화", "수", "목", "금"]

for week in month_cal:
    cols = st.columns(5)
    has_school_day = False

    for i in range(5):  # 월~금요일만 표시
        day = week[i]
        with cols[i]:
            if day == 0:
                st.empty()
            else:
                has_school_day = True
                is_today = (year == today.year and month == today.month and day == today.day)

                # 일자에 따른 식단 순환 매핑
                meal_info = ATHLETE_MEALS_DB[(day - 1) % len(ATHLETE_MEALS_DB)]

                with st.container(border=True):
                    # 날짜 헤더
                    if is_today:
                        st.markdown(f"**{month}월 {day}일 ({weekdays_kr[i]})** :orange-background[**TODAY**]")
                    else:
                        st.markdown(f"**{month}월 {day}일 ({weekdays_kr[i]})**")

                    # 영양 팁 캡션
                    st.caption(f"💡 {meal_info['tip']}")
                    st.divider()

                    # 중식 출력
                    if meal_filter in ["전체 보기", "중식만 보기"]:
                        st.markdown(":blue[**🥣 중식 (에너지 충전)**]")
                        for dish in meal_info["중식"]:
                            dish_text = dish if show_allergen else dish.split(" (")[0]
                            st.markdown(f"<span style='font-size:0.85rem;'>• {dish_text}</span>", unsafe_allow_html=True)

                    # 석식 출력
                    if meal_filter in ["전체 보기", "석식만 보기"]:
                        if meal_filter == "전체 보기":
                            st.write("")
                        st.markdown(":red[**🌙 석식 (근육 회복)**]")
                        for dish in meal_info["석식"]:
                            dish_text = dish if show_allergen else dish.split(" (")[0]
                            st.markdown(f"<span style='font-size:0.85rem;'>• {dish_text}</span>", unsafe_allow_html=True)

    if has_school_day:
        st.write("")
