import datetime
import calendar
import re
import requests
import streamlit as st

st.set_page_config(page_title="우리학교 급식 기반 축구선수 영양 달력", page_icon="⚽", layout="wide")
st.title("⚽ 우리학교 급식 기반 축구선수 맞춤 영양 달력")
st.caption("나이스 API를 통해 우리 학교의 실제 급식 메뉴를 불러온 후, 축구선수를 위한 영양 분석 정보를 제공합니다.")

# 알레르기 번호 맵
ALLERGY_MAP = {
    1: "난류", 2: "우유", 3: "메밀", 4: "땅콩", 5: "대두",
    6: "밀", 7: "고등어", 8: "게", 9: "새우", 10: "돼지고기",
    11: "복숭아", 12: "토마토", 13: "아황산류", 14: "호두", 15: "닭고기",
    16: "쇠고기", 17: "오징어", 18: "조개류(굴/전복/홍합 포함)", 19: "잣",
}

def replace_allergy_codes(dish_text, convert_to_text=True):
    """메뉴명 뒤의 알레르기 번호를 한글 식재료명으로 치환합니다."""
    if not convert_to_text or not dish_text:
        return dish_text

    def convert_match(match):
        raw = match.group(0)
        nums = re.findall(r"\d+", raw)
        allergens = [ALLERGY_MAP[int(n)] for n in nums if int(n) in ALLERGY_MAP]
        if allergens:
            return f" :orange[[{', '.join(allergens)}]]"
        return raw

    pattern = r"\(?(\d+\.)+\)?"
    return re.sub(pattern, convert_match, dish_text)

def analyze_athlete_nutrition(dishes):
    """급식 메뉴 구성을 분석하여 축구선수를 위한 영양 평가 및 조언을 생성합니다."""
    text = " ".join(dishes)
    
    # 영양 키워드 탐지
    has_protein = any(k in text for k in ["고기", "닭", "오리", "돼지", "소", "불고기", "갈비", "생선", "고등어", "삼치", "오징어", "새우", "두부", "계란", "달걀", "돈육"])
    has_carb = any(k in text for k in ["밥", "국수", "라멘", "파스타", "우동", "떡", "감자", "고구마", "빵"])
    has_recovery = any(k in text for k in ["샐러드", "과일", "귤", "사과", "포도", "바나나", "요거트", "채소"])

    tips = []
    if has_protein:
        tips.append("💪 단백질 풍부 (근 손실 예방 및 회복)")
    else:
        tips.append("⚠️ 단백질 부족 가능성 (달걀/두부류 추가 권장)")

    if has_carb:
        tips.append("⚡ 글리코겐 충전 적합")

    if has_recovery:
        tips.append("🥗 비타민/항산화 보충 (피로 회복)")

    return " / ".join(tips) if tips else "⚽ 균형 잡힌 식단 섭취 필요"

# 사이드바: 학교 정보 설정
st.sidebar.header("⚙️ 학교 정보 설정")
office_code = st.sidebar.text_input("시도교육청코드", value="T10", help="기본값: 제주특별자치도교육청(T10)")
school_code = st.sidebar.text_input("표준학교코드", value="9290088", help="기본값: 제주중앙고등학교(9290088)")

st.sidebar.markdown("---")
st.sidebar.subheader("🍽️ 알레르기 및 옵션 설정")
show_allergen_names = st.sidebar.toggle(
    "알레르기 식품명으로 변환", value=True,
    help="체크 시 숫자(예: 1. 5.) 대신 [난류, 대두] 형태로 변환하여 표시합니다."
)

st.sidebar.markdown("---")
st.sidebar.subheader("⚽ 축구선수 영양 팁")
st.sidebar.info("""
- **고강도 훈련 전**: 빠르게 흡수되는 탄수화물(밥, 면, 과일)로 에너지 로딩
- **훈련/경기 직후**: 30분 이내 단백질 및 수분 보충으로 근육 재건
- **부상 예방**: 오메가-3(생선류) 및 항산화 채소로 관절 및 근육 염증 완화
""")

# 날짜 및 필터 선택
today = datetime.date.today()
col_y, col_m, col_filter = st.columns([1, 1, 2])
with col_y:
    year = st.selectbox("연도 선택", options=list(range(today.year - 1, today.year + 2)), index=1)
with col_m:
    month = st.selectbox("월 선택", options=list(range(1, 13)), index=today.month - 1)
with col_filter:
    meal_filter = st.radio(
        "급식 종류 선택", options=["전체 보기", "중식만 보기", "석식만 보기"], index=0, horizontal=True
    )

def fetch_monthly_meals(key, ofcdc_code, schul_code, yr, mo):
    """선택한 월의 급식 데이터를 가져옵니다."""
    _, last_day = calendar.monthrange(yr, mo)
    from_ymd = f"{yr}{mo:02d}01"
    to_ymd = f"{yr}{mo:02d}{last_day:02d}"

    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        "KEY": key, "Type": "json", "pIndex": 1, "pSize": 100,
        "ATPT_OFCDC_SC_CODE": ofcdc_code, "SD_SCHUL_CODE": schul_code,
        "MLSV_FROM_YMD": from_ymd, "MLSV_TO_YMD": to_ymd,
    }
    response = requests.get(url, params=params, timeout=7)
    return response.json()

if "NEIS_KEY" not in st.secrets:
    st.error("⚠️ Streamlit Secrets에 `NEIS_KEY`가 설정되어 있지 않습니다.")
    st.stop()

neis_key = st.secrets["NEIS_KEY"]

try:
    with st.spinner(f"{year}년 {month}월 급식 정보를 불러오는 중..."):
        res_data = fetch_monthly_meals(neis_key, office_code, school_code, year, month)

    meal_dict = {}
    if "mealServiceDietInfo" in res_data:
        rows = res_data["mealServiceDietInfo"][1]["row"]
        for row in rows:
            ymd = row.get("MLSV_YMD")
            meal_type = row.get("MMEAL_SC_NM", "급식")
            dish = row.get("DDISH_NM", "")

            formatted_dish = replace_allergy_codes(dish, convert_to_text=show_allergen_names)
            dish_lines = [d.strip() for d in formatted_dish.replace("<br/>", "\n").split("\n") if d.strip()]

            meal_dict.setdefault(ymd, {})[meal_type] = dish_lines

    month_cal = calendar.monthcalendar(year, month)
    weekdays_kr = ["월", "화", "수", "목", "금"]

    st.markdown("---")

    for week in month_cal:
        cols = st.columns(5)
        has_school_day = False

        for i in range(5):  # 월~금요일
            day = week[i]
            with cols[i]:
                if day == 0:
                    st.empty()
                else:
                    has_school_day = True
                    ymd_str = f"{year}{month:02d}{day:02d}"
                    day_meals = meal_dict.get(ymd_str, {})
                    is_today = (year == today.year and month == today.month and day == today.day)

                    with st.container(border=True):
                        if is_today:
                            st.markdown(f"**{month}월 {day}일 ({weekdays_kr[i]})** :orange-background[**TODAY**]")
                        else:
                            st.markdown(f"**{month}월 {day}일 ({weekdays_kr[i]})**")

                        st.divider()

                        if not day_meals:
                            st.caption("급식 없음 (휴업/방학)")
                        else:
                            displayed_count = 0

                            # 중식 출력 및 축구 영양 평가
                            if meal_filter in ["전체 보기", "중식만 보기"] and "중식" in day_meals:
                                displayed_count += 1
                                st.markdown(":blue[**🥣 중식**]")
                                
                                # 선수용 영양 팁 가이드
                                nutrition_tip = analyze_athlete_nutrition(day_meals["중식"])
                                st.caption(f"💡 {nutrition_tip}")

                                for dish in day_meals["중식"]:
                                    st.markdown(f"<span style='font-size:0.85rem;'>• {dish}</span>", unsafe_allow_html=True)

                            # 석식 출력 및 축구 영양 평가
                            if meal_filter in ["전체 보기", "석식만 보기"] and "석식" in day_meals:
                                displayed_count += 1
                                if meal_filter == "전체 보기" and "중식" in day_meals:
                                    st.write("")
                                st.markdown(":red[**🌙 석식**]")

                                nutrition_tip = analyze_athlete_nutrition(day_meals["석식"])
                                st.caption(f"💡 {nutrition_tip}")

                                for dish in day_meals["석식"]:
                                    st.markdown(f"<span style='font-size:0.85rem;'>• {dish}</span>", unsafe_allow_html=True)

                            if displayed_count == 0:
                                st.caption("해당 식단 없음")

        if has_school_day:
            st.write("")

except requests.exceptions.RequestException as e:
    st.error(f"⚠️ 나이스 API 통신 오류: 네트워크 상태를 확인해 주세요. ({e})")
except Exception as e:
    st.error(f"⚠️ 화면 구성 중 오류가 발생했습니다: {e}")
