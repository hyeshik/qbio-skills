# Nexacro Dataset API 레퍼런스

## 데이터 읽기

| 메서드 | 설명 |
|---|---|
| `ds.getRowCount()` | 행 수 |
| `ds.getColCount()` | 열 수 |
| `ds.getColID(colIndex)` | 인덱스로 열 이름 조회 |
| `ds.getColumn(rowIndex, 'COL')` | 셀 값 조회 |
| `ds.rowposition` | 현재 선택된 행 |
| `ds.findRow('COL', 'value')` | 첫 번째 일치 행 인덱스 |
| `ds.findRowExpr(expr)` | 표현식으로 검색 |
| `ds.getSum('COL')` | 숫자 열 합계 |
| `ds.getMax('COL')` / `ds.getMin('COL')` | 최대/최소 |
| `ds.getAvg('COL')` | 평균 |

> **팁**: 전체 행을 객체 배열로 읽으려면 `scripts/srnd-helpers.js`의
> `readDataset(ds)` 함수를 사용한다.

## 데이터 쓰기

| 메서드 | 설명 |
|---|---|
| `ds.setColumn(rowIndex, 'COL', value)` | 셀 값 설정 |
| `ds.set_rowposition(rowIndex)` | 행 선택 (`onrowposchanged` 발생) |
| `ds.addRow()` | 빈 행 추가 |
| `ds.insertRow(rowIndex)` | 지정 위치에 행 삽입 |
| `ds.deleteRow(rowIndex)` | 행 삭제 |
| `ds.clearData()` | 모든 행 제거 |
| `ds.filter('COL == "val"')` | 행 필터링 |
| `ds.filter('')` | 필터 해제 |

## Combo (드롭다운) 상호작용

```js
const cmb = workDiv.cmb_fieldName;
cmb.value          // 선택된 코드
cmb.text           // 표시 텍스트
cmb.innerdataset   // 옵션을 담고 있는 Dataset 이름
cmb.codecolumn     // 코드 열 이름
cmb.datacolumn     // 표시 텍스트 열 이름
cmb.set_value('RM04900004');  // 코드로 설정
```

## Grid 상호작용

Grid는 Dataset에 바인딩되어 있다. Grid가 아닌 Dataset을 조작한다:

```js
const grd = workDiv.grd_main;
grd.binddataset              // 바인딩된 Dataset 이름
grd.getCellText(row, col)    // 렌더링된 텍스트
grd.setCellPos(row, col)     // 커서 이동
```

## Transaction (API 호출)

```js
workDiv.transaction(
  svcId,       // 예: 'selectList'
  url,         // 예: 'svc::RMSRPMF150E/selectRprjList.do'
  inDs,        // 예: 'dsSearch=ds_search'
  outDs,       // 예: 'ds_main=dsResult'
  args,        // 예: 'arg_pgmId=RMSRPMF530Z'
  callback,    // 예: 'fn_callBack'
  true,        // async
  'POST'       // HTTP method
);
```

## 공통 라이브러리 함수 (gfn_*)

모든 폼에서 사용 가능한 98개 유틸리티 함수 중 주요 항목:

| 함수 | 용도 |
|---|---|
| `gfn_initForm()` | 표준 폼 초기화 |
| `gfn_transactionCallback` | 기본 트랜잭션 핸들러 |
| `gfn_openPopup(id, url, params, w, h)` | 팝업 창 열기 |
| `gfn_getPopupRtn()` | 팝업 반환값 가져오기 |
| `gfn_popupClose()` | 팝업 닫기 |
| `gfn_msg(type, title, msg)` | 메시지 다이얼로그 표시 |
| `gfn_setGrid(grid)` | 그리드 초기화 |
| `gfn_initGridHeadClickSort()` | 헤더 클릭 정렬 활성화 |
| `gfn_setGridCheckAll()` | 전체 행 체크/해제 |
| `gfn_downloadFile()` | 파일 다운로드 |
| `gfn_fileUploadPopup()` | 파일 업로드 다이얼로그 |
| `gfn_getCommCode(codeId)` | 공통 코드 로드 |
| `gfn_btnControl()` | 권한별 버튼 표시/숨김 |
| `gfn_getRoleDept()` | 사용자 소속 부서 가져오기 |
| `gfn_EcmAttach()` | ECM 문서 첨부 |
