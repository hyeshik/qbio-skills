---
name: snu-srnd
description: >
  서울대학교 SRnD(연구행정통합관리시스템, srnd.snu.ac.kr) 브라우저 자동화 스킬.
  Nexacro Platform 14 기반 UI를 javascript_tool로 제어하여 과제조회, 지출신청,
  참여연구원 관리, 카드청구, 연구업적, 구매, 출장신청 등 연구행정 작업을 수행한다.
  TRIGGER: 사용자가 srnd.snu.ac.kr에 있거나, SRnD/연구행정을 언급하거나,
  과제조회·지출신청·참여연구원·연구비·카드청구·연구업적·구매·출장신청 등
  서울대 연구행정 업무를 요청할 때. DO NOT TRIGGER: 다른 대학 시스템이나
  일반 웹앱을 다룰 때.
---

# SRnD 브라우저 자동화 스킬

SRnD는 서울대학교 연구행정통합관리시스템으로 **Nexacro Platform 14**(TOBESOFT)
위에서 동작한다. Nexacro는 자체 JavaScript 가상 DOM으로 UI 전체를 렌더링하기 때문에
표준 DOM 검사 도구(`read_page`, `find`)는 무의미한 `generic` 요소만 반환한다.

> **핵심 원칙**: 항상 `javascript_tool`로 Nexacro 객체 모델에 직접 접근하고,
> `screenshot`으로 시각적 확인을 병행한다.

## 환경 요구사항

- Claude Cowork (Claude in Chrome 확장)
- 주 상호작용 도구: `javascript_tool` (표준 `read_page`는 사용 불가)

## 시작 절차

스킬이 트리거되면 가장 먼저 SRnD 세션 상태를 확인한다.

**1단계: 로그인 상태 확인**

`javascript_tool`로 아래 코드를 실행하여 Nexacro 앱이 로딩되어 있는지 확인한다:

```js
try {
  const app = nexacro.Application.mainframe.VFrameSet.TopFrame.form;
  const menuCount = app.ds_menuAllList.getRowCount();
  'LOGGED_IN:' + menuCount + ' menus';
} catch (e) {
  'NOT_LOGGED_IN';
}
```

**2단계: 결과에 따른 분기**

- `LOGGED_IN` 반환 → 정상. 바로 사용자의 요청을 처리한다.
- `NOT_LOGGED_IN` 반환 또는 오류 → 아래 절차를 수행한다:
  1. `navigate` 도구로 `https://srnd.snu.ac.kr/`에 접속한다.
  2. 사용자에게 로그인을 요청한다:
     "SRnD에 로그인이 필요합니다. 브라우저에서 로그인해 주세요. 완료되면 알려주세요."
  3. 사용자가 로그인 완료를 알리면 1단계를 다시 실행하여 `LOGGED_IN`을 확인한다.
  4. 여전히 실패하면 페이지 로딩이 덜 된 것일 수 있으므로 3초 대기 후 재시도한다.

## 기본 규칙

1. **`read_page` 사용 금지** — Nexacro 콘텐츠에는 무효하다. `javascript_tool`만 사용.
2. **비동기 대기 필수** — `fn_search()`나 탭 전환 후 **2–3초 대기** 후 데이터셋 읽기.
3. **날짜 형식은 `YYYYMMDD`** — 예: `'20250401'` (2025-04-01).
4. **백엔드 API 직접 호출 금지** — Nexacro의 `fn_search()`, `fn_save()`,
   `transaction()`을 통해서만 호출. 세션 토큰·직렬화·에러 처리를 자동으로 해준다.
5. **Audit Trail 필수** — 아래 "Audit Trail" 섹션의 규칙을 따른다.
6. **자가 학습** — 기존 참조 파일에 없는 경로를 탐색해서 작업에 성공하면,
   알아낸 내용을 참조 파일에 반영한다. 아래 "자가 학습" 섹션 참조.

## Audit Trail

SRnD에서 수행하는 의미 있는 작업은 모두 HTML 파일에 기록한다. 사용자가 나중에
무엇이 수행되었는지 확인할 수 있도록 하기 위함이다.

### 기록 대상

기록하는 작업 (서버 요청을 수반하거나 side effect가 있는 것):

- 페이지 이동 (`fn_OpenMainForm`)
- 조회 실행 (`fn_search`) — 검색 파라미터 포함
- 데이터 저장 (`fn_save`) — 변경 내용 요약 포함
- 행 추가/삭제 (`addRow`, `deleteRow`)
- 셀 값 변경 (`setColumn`) — 변경 전·후 값
- 팝업 호출 및 결과
- Excel 내보내기 (`fn_exportExcel`)
- 기타 `transaction()` 호출

기록하지 않는 작업 (읽기 전용, side effect 없음):

- 프로퍼티 단순 읽기 (`getColumn`, `getRowCount`, `value` 조회 등)
- 폼 구조 탐색 (`discoverForm`, `searchMenu`, `listOpenPages`)
- 탭 목록 조회, 컴포넌트 이름 확인 등

### 운영 절차

1. **세션 시작 시** `scripts/audit-trail.py init`을 실행하여 HTML 파일을 생성한다.
   파일 경로를 세션 내내 기억한다.
2. **기록 대상 작업을 수행할 때마다** 즉시 `scripts/audit-trail.py log`를 호출하여
   기록을 추가한다. 작업 후가 아니라 작업과 동시에 기록하는 것이 원칙이다.
3. **작업 완료 또는 중단 시** `scripts/audit-trail.py finalize`를 호출하고,
   HTML 파일 링크를 사용자에게 제공한다.

사용법:

```bash
# 1. 초기화 — HTML 파일 생성, 경로 출력
python3 <skill-path>/scripts/audit-trail.py init \
  --output /sessions/eager-inspiring-bardeen/mnt/srnd/audit-trail-YYYYMMDD-HHMMSS.html

# 2. 항목 추가 — 작업을 수행할 때마다 호출
python3 <skill-path>/scripts/audit-trail.py log \
  --file <audit-html-path> \
  --action "fn_search" \
  --category "조회" \
  --page "과제조회(연구자용) [1300020000]" \
  --detail "PROG_ST_FG=RM04900004, FR_DT=20240101, TO_DT=20261231" \
  --result "성공: 15건 조회"

# 3. 종료 — 완료 표시 추가, 최종 경로 출력
python3 <skill-path>/scripts/audit-trail.py finalize \
  --file <audit-html-path>
```

### 기록 항목별 가이드

| 작업 | category | detail에 포함할 내용 |
|---|---|---|
| 페이지 이동 | `네비게이션` | 메뉴명, 메뉴 ID |
| 조회 | `조회` | 검색 파라미터 (키=값 나열) |
| 저장 | `저장` | 변경된 필드와 값 요약 |
| 행 추가 | `데이터변경` | 추가된 행의 주요 필드 |
| 행 삭제 | `데이터변경` | 삭제된 행 식별 정보 |
| 셀 수정 | `데이터변경` | 필드명, 변경 전→후 값 |
| Excel 내보내기 | `내보내기` | 그리드명, 행 수 |
| 팝업 | `팝업` | 팝업 ID, 파라미터, 반환값 |

## 프레임 계층 구조

SRnD 전체가 `nexacro.Application` 안에 있다:

```
nexacro.Application.mainframe.VFrameSet
├── TopFrame.form                          ← 상단 바, 전역 데이터
│   ├── ds_menuAllList                     ← 전체 264개 메뉴
│   ├── ds_topMenu                         ← 10개 최상위 카테고리
│   ├── fn_AddTabPage(menuId, params)      ← 새 탭으로 페이지 열기
│   └── fn_SetTab(menuId)                  ← 기존 탭으로 전환
├── HFrameSet
│   ├── LeftFrame.form                     ← 좌측 메뉴 패널
│   │   └── fn_OpenMainForm(menuId)        ← 페이지 네비게이션
│   └── VFrameSet
│       ├── TabFrame.form.tab_openMenu     ← 탭 바
│       └── FrameSet                       ← ★ 콘텐츠 영역 ★
│           └── [MENU_ID]                  ← 열린 페이지 (메뉴 ID가 키)
│               └── .form.div_workForm     ← 실제 작업 폼
```

콘텐츠 영역 접근 패턴:

```js
const fs = nexacro.Application.mainframe.VFrameSet.HFrameSet.VFrameSet.FrameSet;
const workDiv = fs['{MENU_ID}'].form.div_workForm;
```

`scripts/srnd-helpers.js`의 `getFrameSet()`과 `getWorkDiv(menuId)`를 사용하면
더 간결하게 접근할 수 있다.

## 폼 공통 구조

264개 페이지 모두 `div_workForm` 안에서 동일한 패턴을 따른다:

| 컴포넌트 | 용도 |
|---|---|
| `ds_search` | 검색 파라미터 (1행, 검색 전 설정) |
| `ds_main` | 메인 결과 데이터 (검색 후 채워짐) |
| `grd_main` | 그리드 (`ds_main`에 바인딩) |
| `fn_search()` | 검색 실행 (`ds_search` → API → `ds_main`) |
| `fn_save()` | 저장 실행 |
| `fn_callBack(svc, errCd, errMsg)` | 트랜잭션 결과 핸들러 |
| `fn_exportExcel()` | 현재 그리드를 Excel로 내보내기 |

## 상세 패널 (우측 탭)

대부분의 폼에는 우측 상세 패널이 있다:

```
workDiv
└── div_right (또는 div_detail)
    └── Tab00
        ├── tabpage1  "협약정보"
        ├── tabpage2  "실행예산"
        ├── tabpage9  "참여연구원"
        │   └── div_rech              ← 중첩 Div, 자체 서브폼 로드
        │       └── ds_paticpRecher   ← 실제 연구원 데이터 (70 컬럼)
        ├── tabpage5  "입금내역"
        └── ...
```

**탭 데이터는 지연 로딩된다.** `tab.set_tabindex(N)` 호출 후 반드시 대기해야 한다:

```js
const tab = workDiv.div_right.Tab00;
// 탭 목록 확인:
tab.tabpages.forEach((pg, i) => console.log(i, pg.text));
// 탭 전환:
tab.set_tabindex(2);
// 2–3초 대기 후 탭 내부 데이터 접근:
const subDiv = tab.tabpages[2].all[N]; // .url 속성을 가진 Div
```

## 컴포넌트 네이밍 규칙

| 접두사 | 타입 | 비고 |
|---|---|---|
| `ds_` | Dataset | 데이터 컨테이너 (비표시) |
| `grd_` | Grid | `.binddataset`으로 Dataset에 바인딩 |
| `div_` | Div | 컨테이너; `.url`로 서브폼 로드 가능 |
| `btn_` | Button | `.onclick` 핸들러 |
| `edt_` | Edit | 단일 행 텍스트 입력 |
| `cmb_` | Combo | 드롭다운. `.value`=코드, `.text`=표시값 |
| `cal_` | Calendar | 날짜 선택기 |
| `tab_` | Tab | `.tabpages[]`로 탭 페이지 접근 |
| `stc_` / `Static` | Static | 라벨·장식 요소 |

## 레시피

### 페이지 이동

```js
const leftForm = nexacro.Application.mainframe.VFrameSet.HFrameSet.LeftFrame.form;
leftForm.fn_OpenMainForm('1300020000'); // 과제조회(연구자용)
// 2–3초 대기
```

### 검색 실행

```js
const workDiv = getWorkDiv('1300020000'); // srnd-helpers.js
workDiv.ds_search.setColumn(0, 'PROG_ST_FG', 'RM04900004'); // 진행
workDiv.ds_search.setColumn(0, 'FR_DT', '20240101');
workDiv.ds_search.setColumn(0, 'TO_DT', '20261231');
workDiv.fn_search();
// 2–3초 대기 후 ds_main 읽기
```

### 데이터셋 전체 읽기

`scripts/srnd-helpers.js`의 `readDataset(ds)` 함수를 사용:

```js
const rows = readDataset(workDiv.ds_main);
```

### 그리드 행 선택 (상세 로딩)

```js
workDiv.ds_main.set_rowposition(rowIndex);
// onrowposchanged 트리거 → 상세 패널 갱신. 2초 대기.
```

### 알 수 없는 폼 탐색

`scripts/srnd-helpers.js`의 `discoverForm(menuId)` 함수를 사용:

```js
const info = discoverForm(menuId);
// info.datasets: [{name, rows}, ...]
// info.fns: ['fn_search', 'fn_save', ...]
// info.tabs: [{index, text}, ...]
```

### 메뉴 검색

`scripts/srnd-helpers.js`의 `searchMenu(keyword)` 함수를 사용:

```js
const results = searchMenu('과제');
// [{menuId, menuNm, pgmId}, ...]
```

## 자가 학습

MENU-TREE.md와 INTENT-MAP.md는 자주 쓰이는 경로만 담고 있어서,
사용자의 요청이 기존에 매핑되지 않은 메뉴나 작업을 필요로 할 수 있다.
이때 탐색을 통해 방법을 알아냈다면, 그 지식을 참조 파일에 기록하여
다음번에는 탐색 없이 바로 수행할 수 있도록 한다.

### 트리거 조건

다음 중 하나라도 해당하면 자가 학습을 수행한다:

- `searchMenu()`로 메뉴를 찾았는데 MENU-TREE.md에 해당 항목이 없을 때
- `discoverForm()`으로 폼 구조를 탐색하여 작업을 완료했을 때
- INTENT-MAP.md에 매핑이 없는 사용자 요청을 시행착오를 거쳐 성공했을 때
- 기존 매핑의 데이터 경로가 실제와 다른 것을 발견했을 때

### 업데이트 절차

1. **작업을 먼저 완료한다.** 참조 파일 업데이트는 사용자의 요청을 처리한 뒤에 한다.
2. **알아낸 내용을 정리한다.** 최소한 다음을 확인한다:
   - 메뉴 ID, 메뉴명, PGM_ID
   - 해당 폼의 주요 Dataset 이름과 용도
   - 검색 파라미터 (`ds_search`의 컬럼명과 유효 값)
   - 탭 구조가 있으면 탭 인덱스와 이름
   - 작업을 완료하기 위해 호출한 함수 순서
3. **참조 파일을 업데이트한다:**
   - **MENU-TREE.md** — 새 메뉴 항목을 해당 모듈 섹션에 추가한다.
     형식: `- [MENU_ID] 메뉴명 (PGM_ID)`
   - **INTENT-MAP.md** — 사용자 요청 → 메뉴 ID → 데이터 경로 매핑을 추가한다.
     기존 카테고리에 맞으면 해당 테이블에 행을 추가하고,
     새 카테고리가 필요하면 섹션을 만든다.
     복합 작업이었으면 "복합 작업 패턴" 섹션에 단계별 절차를 추가한다.
4. **Audit Trail에 기록한다.** category `자가학습`, action `update-references`,
   detail에 어떤 파일에 무엇을 추가했는지 기술한다.

### 주의사항

- 한 번 성공한 것만 기록한다. 시행착오 중 실패한 경로는 기록하지 않는다.
- 기존 매핑과 충돌하면 실제 동작을 기준으로 기존 내용을 수정한다.
- 업데이트 후 사용자에게 "새로 알아낸 경로를 스킬에 반영했습니다"라고 알린다.

## 자주 발생하는 문제

- **`div_workForm.form`이 `undefined`**: Nexacro 14에서는 정상이다. `div_workForm`에서
  직접 자식 컴포넌트에 접근한다 (예: `workDiv.ds_main`).
- **탭 전환 후 데이터셋이 비어있음**: 대기 시간이 부족하다. `set_tabindex()` 후 3초 대기.
- **프레임이 사라짐**: 사용자가 탭을 닫은 경우. `fn_OpenMainForm(menuId)`로 재이동.
- **Combo 값 설정**: `cmb.set_value('CODE')`. 옵션 목록은 `workDiv[cmb.innerdataset]`.
- **팝업**: Nexacro 팝업은 브라우저 창이 아닌 오버레이 div이다. `screenshot`으로 확인.
  반환값은 `fn_popupAfter()`를 통해 전달된다.

## 참조 파일

- [references/MENU-TREE.md](references/MENU-TREE.md) — 264개 전체 메뉴 계층 (메뉴 ID, 프로그램 ID 포함)
- [references/DATASET-API.md](references/DATASET-API.md) — Dataset 읽기/쓰기 API, Grid 상호작용
- [references/INTENT-MAP.md](references/INTENT-MAP.md) — 한국어 사용자 요청 → 네비게이션 경로·데이터셋 위치 매핑
- [scripts/srnd-helpers.js](scripts/srnd-helpers.js) — 공통 헬퍼 함수 (`getWorkDiv`, `readDataset`, `discoverForm`, `searchMenu`)
- [scripts/audit-trail.py](scripts/audit-trail.py) — Audit Trail HTML 생성·기록·종료 스크립트
