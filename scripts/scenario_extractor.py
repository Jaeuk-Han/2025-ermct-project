import csv
import pandas as pd
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

df = pd.read_csv('data/table_adult.csv')

def clean_age(val):
    if pd.isna(val):
        return "나이 미상"
    return f"{str(val).strip()}세"

def generate_korean_scenario(row):
    no = row['No']
    gender = '남성' if row['Gender'] == 'M' else '여성' if row['Gender'] == 'F' else str(row['Gender'])
    age = clean_age(row['Age'])
    cc = str(row['Chief Complaint']).strip()
    mental = str(row['Mental status']).strip()
    gcs = int(row['GCS']) if pd.notna(row['GCS']) else "미상"
    
    # Vital signs parsing
    vitals_raw = str(row['Vital sign']).strip()
    vitals_parts = [p.strip() for p in vitals_raw.split('-')]
    if len(vitals_parts) >= 4:
        bp, hr, rr, bt = vitals_parts[0], vitals_parts[1], vitals_parts[2], vitals_parts[3]
        vitals_str = f"혈압은 {bp}, 맥박 {hr}, 호흡수 {rr}, 체온 {bt}도입니다."
    else:
        vitals_str = f"바이탈 사인은 {vitals_raw}입니다."
        
    nrs = row['NRS']
    nrs_str = ""
    if pd.notna(nrs) and str(nrs).strip() != '' and str(nrs).lower() != 'nan':
        nrs_str = f" 통증 NRS {str(nrs).strip()}점입니다."
    
    # Check '열1' column for additional clinical context/details
    extra_text = ""
    if '열1' in df.columns:
        val = row['열1']
        if pd.notna(val) and str(val).strip() != '':
            extra_text = " " + str(val).strip()

    # # English medical term to Korean pronunciation mapping as requested
    # cc_map = {
    #     'flank pain': '플랭크 페인(옆구리 통증)',
    #     'diarrhea': '다이어리아(설사)',
    #     'persistence of convulsions': '지속적인 경련',
    #     'head trauma': '헤드 트라우마(두부 외상)',
    #     'abdominal pain': '앱도미날 페인(복통)',
    #     'fever': '피버(발열)',
    #     'dyspnea': '호흡곤란',
    #     'hematemesis': '헤마테메시스(토혈)',
    #     'chest pain': '체스트 페인(흉통)',
    #     'sore throat': '소어 스로트(인후통)',
    #     'altered mental status': '의식 변화',
    #     'dizziness': '어지러움',
    #     'melena': '멜레나(흑색변)',
    #     'vomiting': '보미팅(구토)',
    #     'back pain': '백 페인(요통)',
    #     'foreign body in ear': '귀 내 이물',
    #     'palpitation': '팔피테이션(심계항진)',
    #     'cough': '기침',
    #     'epistaxis': '코피',
    #     'dysuria': '디스유리아(배뇨통)',
    #     'syncope': '실신',
    #     'burn': '번(화상)',
    #     'suicidal attempt': '자살 기도',
    #     'submersion': '익수',
    #     'headache': '헤딕(두통)',
    #     'hemoptysis': '헤모프티시스(객혈)',
    #     'fall': '폴(추락/낙상)',
    #     'shoulder pain': '숄더 페인(어깨 통증)',
    #     'pain in shoulder': '숄더 페인(어깨 통증)',
    #     'hip pain': '힙 페인(고관절 통증)',
    #     'animal bite': '애니멀 바이트(동물 교상)',
    #     'carbon monoxide inhalation': '일산화탄소 흡입',
    #     'seizure': '시저(발작)',
    #     'traffic accident': '트래픽 액시던트(교통사고)',
    #     'constipation': '콘스티페이션(변비)',
    #     'toothache': '투스에이크(치통)',
    #     'cardiac arrest': '카디악 어레스트(심정지)',
    #     'allergic reaction': '알레르기 반응',
    #     'hematuria': '헤마투리아(혈뇨)',
    #     'lethargy': '무기력',
    #     'lower extremity pain': '하지 통증',
    #     'epigastric pain': '에피가스트릭 페인(상복부 통증)',
    #     'eye pain': '아이 페인(안구 통증)',
    #     'foreign body in throat': '목 구멍 내 이물',
    #     'vaginal bleeding': '바지날 블리딩(질 출혈)',
    #     'generalized aches': '전신 통증',
    #     'neck pain': '넥 페인(경부 통증)',
    #     'skin rash': '스킨 래쉬(피부 발진)',
    #     'urinary retention': '유리너리 리텐션(요폐)',
    #     'insect bite': '인섹트 바이트(곤충 교상)',
    #     'chills': '오한',
    #     'hiccup': '힉컵(딸국질)',
    #     'general weakness': '제너럴 위크니스(전신 위약감)',
    #     'dysarthria': '디스아리아(구음장애)'
    # }
    
    mental_map = {
        'alert': '명료',
        'drowsy': '기면',
        'stupor': '혼미',
        'coma': '코마',
        'semi-coma': '세미코마'
    }
    
    # cc_kor = cc_map.get(cc.lower(), cc)
    cc_kor = cc # Use original term for chief complaint without translation
    mental_kor = mental_map.get(mental.lower(), mental)
    
    # Translate terms in extra_text if applicable
    extra_text_clean = '특이사항:'+extra_text.replace('mild dyspnea', '경증 호흡곤란').replace('moderate dyspnea', '중등증 호흡곤란').replace('severe dyspnea', '중증 호흡곤란')

    scenario = f"환자는 {age} {cc_kor} {gender}으로, 의식은 {mental_kor} 상태이며 GCS는 {gcs}점입니다. {vitals_str}{nrs_str} {extra_text_clean}"
    return scenario

output_rows = []
for idx, row in df.iterrows():
    no = int(row['No'])
    scenario_text = generate_korean_scenario(row)
    ktas_gold = int(row['Human rater1 (Gold-standard)'])
    output_rows.append([no, scenario_text, ktas_gold])

print(output_rows)

with open("data/ER_Call_Scenarios_Custom_KTAS.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(['인덱스', '한글 시나리오', 'HUMAN RATER 1의 KTAS'])
    writer.writerows(output_rows)

print(f"Successfully processed {len(output_rows)} entries.")