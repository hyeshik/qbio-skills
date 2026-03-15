# 사용자 요청 → 데이터 경로 매핑

한국어 사용자 요청을 SRnD 네비게이션·데이터 접근 경로로 매핑한다.
새로운 패턴이 발견되면 이 파일에 추가한다.

## 과제 (Projects)

| 사용자 요청 | 메뉴 ID | 데이터 경로 |
|---|---|---|
| 과제 목록 / 내 과제 | `1300020000` | `workDiv.ds_main` |
| 진행 중인 과제 | `1300020000` | `ds_search.PROG_ST_FG='RM04900004'` → `fn_search()` |
| 종료된 과제 | `1300020000` | `ds_search.PROG_ST_FG='RM04900005'` → `fn_search()` |
| 과제 상세 정보 | `1300020000` | 행 선택 → `ds_rprjMain` 자동 로드 |
| 참여연구원 목록 | `1300020000` | 행 선택 → `Tab00.set_tabindex(2)` → 대기 → `tabpage9.div_rech.ds_paticpRecher` |
| 실행예산 | `1300020000` | `Tab00.set_tabindex(1)` → 대기 → 탭 내 중첩 Div |
| 입금내역 | `1300020000` | `Tab00.set_tabindex(3)` |
| 수입지출내역 | `1300020000` | `Tab00.set_tabindex(4)` |
| 카드사용내역 | `1300020000` | `Tab00.set_tabindex(6)` |

## 지출 (Expenditure)

| 사용자 요청 | 메뉴 ID | 데이터 경로 |
|---|---|---|
| 지출신청 | `1300030000` | `workDiv.ds_main` |
| 카드간편청구 | `1300040000` | `workDiv.ds_main` |

## 출장 (Business Travel)

| 사용자 요청 | 메뉴 ID | 데이터 경로 |
|---|---|---|
| 출장신청 | `1300020100` | `workDiv.ds_main` |
| 회의비사전신청 | `1300020110` | `workDiv.ds_main` |

## 연구업적 (Research Achievements)

| 사용자 요청 | 메뉴 ID | 데이터 경로 |
|---|---|---|
| 연구업적 등록 | `1300220000` | `workDiv.ds_main` |
| 연구업적 현황 | `1300210000` | `workDiv.ds_main` |

## 구매 (Procurement)

| 사용자 요청 | 메뉴 ID | 데이터 경로 |
|---|---|---|
| 구매대시보드 | `1300410000` | `workDiv.ds_main` |
| 재물조사 | `1300420000` | `workDiv.ds_main` |

## 지식재산권 (Intellectual Property)

| 사용자 요청 | 메뉴 ID | 데이터 경로 |
|---|---|---|
| 특허신고 | `1300510000` | `workDiv.ds_main` |
| 권리승계확인서 | `1300520000` | `workDiv.ds_main` |

## 카드 (Corporate Card)

| 사용자 요청 | 메뉴 ID | 데이터 경로 |
|---|---|---|
| 법인카드 발급 | `1300070000` | `workDiv.ds_main` |
| 원카드 발급 | `1300080000` | `workDiv.ds_main` |

## 복합 작업 패턴

### "전체 과제의 참여연구원 전부 가져와"

1. `1300020000` 페이지로 이동 → 3초 대기
2. 검색 파라미터 설정 (상태, 기간) → `fn_search()` → 3초 대기
3. `ds_main.getRowCount()`로 과제 수 확인
4. 각 과제 행에 대해 반복:
   - `ds_main.set_rowposition(i)` → 2초 대기
   - `Tab00.set_tabindex(2)` → 3초 대기
   - `tabpage9.div_rech.ds_paticpRecher` 읽기 (`readDataset()` 사용)
5. 결과 취합 및 제시
