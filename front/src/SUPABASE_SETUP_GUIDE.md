# Supabase Database Setup Guide

이 가이드는 응급 환자 이송 시스템을 위한 Supabase 데이터베이스 스키마, 보안 정책(RLS), 그리고 초기 데이터를 설정하는 방법을 설명합니다.

## 1. Supabase 프로젝트 설정

1. [Supabase](https://supabase.com)에서 새 프로젝트를 생성합니다.
2. 프로젝트가 생성되면 왼쪽 메뉴의 **SQL Editor**로 이동합니다.
3. 아래의 SQL 코드를 순서대로 복사하여 실행합니다.

---

## 2. 테이블 생성 (SQL Editor에서 실행)

아래 SQL 코드를 복사해서 실행하면 필요한 모든 테이블이 생성됩니다.

```sql
-- 1. 병원 정보 테이블 (Hospitals)
CREATE TABLE IF NOT EXISTS public.hospitals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    phone_number TEXT,
    specialties TEXT[], -- 예: ['ER', 'Trauma', 'Cardio']
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 병원 실시간 상태 테이블 (Hospital Status)
-- 병상 수, 대기 시간 등 자주 변하는 데이터
CREATE TABLE IF NOT EXISTS public.hospital_status (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    hospital_id UUID REFERENCES public.hospitals(id) ON DELETE CASCADE,
    available_beds INTEGER DEFAULT 0,
    total_beds INTEGER DEFAULT 20,
    estimated_wait_time INTEGER DEFAULT 0, -- 분 단위
    is_accepting BOOLEAN DEFAULT true,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. 이송 요청 테이블 (Transfer Requests)
-- 구급대원이 보낸 요청과 환자 정보, KTAS 결과 저장
CREATE TABLE IF NOT EXISTS public.transfer_requests (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- 관계
    hospital_id UUID REFERENCES public.hospitals(id),
    paramedic_id UUID REFERENCES auth.users(id), -- 로그인한 구급대원 ID
    
    -- 환자 정보 (KTAS 및 바이탈)
    patient_age INTEGER,
    patient_gender TEXT,
    symptoms TEXT,
    ktas_level INTEGER, -- 1~5
    
    -- 바이탈 사인
    vitals_bp TEXT,    -- 혈압 (e.g., '120/80')
    vitals_pulse INTEGER,
    vitals_resp INTEGER,
    vitals_temp FLOAT,
    consciousness TEXT, -- AVPU
    
    -- 요청 상태
    -- 'waiting': 대기중, 'approved': 승인, 'rejected': 거절, 
    -- 'transferring': 이송중, 'completed': 완료, 'cancelled': 취소
    status TEXT DEFAULT 'waiting',
    rejection_reason TEXT -- 거절 시 사유
);

-- 4. 사용자 프로필 (선택 사항)
-- 사용자가 구급대원인지 병원 관계자인지 구분
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    role TEXT CHECK (role IN ('paramedic', 'hospital_staff')),
    name TEXT,
    organization TEXT, -- 소속 소방서 또는 병원명
    hospital_id UUID REFERENCES public.hospitals(id) -- 병원 관계자일 경우 소속 병원
);
```

---

## 3. 실시간 기능 활성화 (Realtime)

구급대원과 병원 간의 실시간 알림을 위해 Replication을 활성화해야 합니다.

1. 아래 SQL을 실행합니다.

```sql
-- transfer_requests 테이블의 변경 사항을 실시간으로 구독할 수 있도록 설정
ALTER PUBLICATION supabase_realtime ADD TABLE public.transfer_requests;

-- hospital_status 테이블의 변경 사항도 실시간 구독 (병상 정보 업데이트용)
ALTER PUBLICATION supabase_realtime ADD TABLE public.hospital_status;
```

---

## 4. 초기 데이터(Seed Data) 넣기

앱 테스트를 위해 서울 주요 병원 데이터를 미리 넣어둡니다.

```sql
-- 기존 데이터가 있다면 중복 방지를 위해 확인 후 실행하거나, 아래 쿼리는 새로 넣습니다.

INSERT INTO public.hospitals (name, latitude, longitude, phone_number, specialties, address)
VALUES 
    ('서울대학교병원', 37.5796, 126.9990, '02-2072-2114', ARRAY['권역응급', '외상'], '서울 종로구 대학로 101'),
    ('서울아산병원', 37.5266, 127.1072, '1688-7575', ARRAY['심혈관', '뇌졸중'], '서울 송파구 올림픽로43길 88'),
    ('삼성서울병원', 37.4882, 127.0852, '1599-3114', ARRAY['소아응급', '암센터'], '서울 강남구 일원로 81');

-- 병원 상태 데이터 초기화 (병상 정보 연결)
INSERT INTO public.hospital_status (hospital_id, available_beds, total_beds, estimated_wait_time)
SELECT id, 5, 20, 15 FROM public.hospitals WHERE name = '서울대학교병원';

INSERT INTO public.hospital_status (hospital_id, available_beds, total_beds, estimated_wait_time)
SELECT id, 8, 30, 10 FROM public.hospitals WHERE name = '서울아산병원';

INSERT INTO public.hospital_status (hospital_id, available_beds, total_beds, estimated_wait_time)
SELECT id, 1, 15, 45 FROM public.hospitals WHERE name = '삼성서울병원';
```

---

## 5. 보안 정책 (RLS - Row Level Security) 설정

데이터 보안을 위해 접근 권한을 설정합니다. (개발 편의를 위해 일단 퍼블릭하게 열어두는 정책입니다. 실제 운영 시에는 더 엄격하게 제한해야 합니다.)

```sql
-- RLS 활성화
ALTER TABLE public.hospitals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hospital_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.transfer_requests ENABLE ROW LEVEL SECURITY;

-- 1. 병원 정보는 누구나 읽을 수 있음 (로그인한 사용자)
CREATE POLICY "Enable read access for authenticated users" ON public.hospitals
FOR SELECT TO authenticated USING (true);

-- 2. 병원 상태 정보도 누구나 읽기 가능
CREATE POLICY "Enable read access for authenticated users" ON public.hospital_status
FOR SELECT TO authenticated USING (true);

-- 3. 이송 요청: 누구나 생성(INSERT) 가능
CREATE POLICY "Enable insert for authenticated users" ON public.transfer_requests
FOR INSERT TO authenticated WITH CHECK (true);

-- 4. 이송 요청: 누구나 읽기(SELECT) 가능 (본인 요청만 보게 하려면 auth.uid() 사용)
CREATE POLICY "Enable read for authenticated users" ON public.transfer_requests
FOR SELECT TO authenticated USING (true);

-- 5. 이송 요청: 누구나 업데이트(UPDATE) 가능 (병원에서 승인/거절 처리용)
CREATE POLICY "Enable update for authenticated users" ON public.transfer_requests
FOR UPDATE TO authenticated USING (true);
```

---

## 6. 스토리지 버킷 생성 (옵션)

이미지 업로드가 필요한 경우 (예: 환부 사진)
1. Storage 메뉴로 이동
2. `medical-images` 라는 이름으로 새 버킷 생성
3. Public Access 설정

---

## 7. 프론트엔드 연동 준비

이제 `utils/supabase/client.ts` 파일을 통해 이 데이터베이스와 연결할 수 있습니다.
`transfer_requests` 테이블을 통해 구급대원(INSERT)과 병원(UPDATE status)이 실시간으로 소통하게 됩니다.
