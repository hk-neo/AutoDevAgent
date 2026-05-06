# Intended Use Document 티켓 처리

command_args를 기반으로 Intended Use 티켓(이슈 타입: "Intended Use")을 1개 생성합니다.
command_args는 제품명이나 기능 설명입니다 (예: "로컬 CBCT 웹 뷰어").

## 초안 작성 규칙

- 제품명/기능 설명을 기반으로 모든 필드의 초안을 자동 작성
- 치과(Dental) 분야 의료기기에 맞게 내용 작성
- MDR 규정에 맞게 작성

## Intended Use 필드 목록

| 필드명 | 키 | 타입 | 설명 |
|--------|-----|------|------|
| Summary | summary | text | 제목 (예: "로컬 CBCT 웹 뷰어") |
| Phase | customfield_10382 | select | "PA" 고정 |
| Intended Purpose | customfield_10103 | textarea | 의도된 사용 목적 |
| Indication | customfield_10104 | textarea | 적응증 |
| Intended Patient Population | customfield_10105 | textarea | 대상 환자군 |
| Intended User | customfield_10106 | textarea | 예상 사용자 |
| Clinical Benefit | customfield_10107 | textarea | 임상적 이점 |
| User Constraint | customfield_10111 | textarea | 사용 제한사항 |
| Part of Body | customfield_10301 | text | 적용 부위 |
| Use Environment | customfield_10302 | text | 사용 환경 |
| Principle of Operation | customfield_10303 | text | 작동 원리 |
| Key Performance Spec | customfield_10304 | text | 주요 성능 사양 |
| Warnings and Precautions | customfield_10305 | textarea | 경고 및 주의사항 |

## 생성 예시 (command_args: "로컬 CBCT 웹 뷰어")

```json
{
  "fields": {
    "project": {"key": "PLAYG"},
    "summary": "로컬 CBCT 웹 뷰어",
    "issuetype": {"name": "Intended Use"},
    "customfield_10382": {"value": "PA"},
    "customfield_10103": "치과용 CBCT 영상을 로컬 환경에서 웹 브라우저를 통해 조회하고 진단 보조를 제공하는 소프트웨어",
    "customfield_10104": "치과 진단을 위한 CBCT 영상의 조회 및 분석",
    "customfield_10105": "치과 진료가 필요한 모든 환자",
    "customfield_10106": "치과의사, 구강악안면외과 전문의",
    "customfield_10107": "CBCT 영상의 정확한 조회를 통해 치과 진단의 정확도 향상",
    "customfield_10111": "본 소프트웨어는 진단 보조 목적이며, 최종 진단은 반드시 전문의가 수행해야 함",
    "customfield_10301": "구강 및 악안면 부위",
    "customfield_10302": "치과 병/의원 진료실",
    "customfield_10303": "DICOM 형식의 CBCT 영상을 로드하여 웹 브라우저에서 MPR 3단면 렌더링",
    "customfield_10304": "DICOM 파일 로드, MPR 3단면 표시, Window Level 조절",
    "customfield_10305": "네트워크 연결이 필요하지 않은 로컬 전용 소프트웨어입니다"
  }
}
```

## 링크

- "Relates" 링크로 Intended Use Document와 연결
