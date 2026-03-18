# Nexacro 컴포넌트 경로 참조

각 IRIS 페이지의 Nexacro 컴포넌트 경로를 기록한다. 새 페이지를 방문할 때마다 여기에 추가한다.

## 공통 베이스 경로

```javascript
var iframe = document.querySelectorAll('iframe')[1];
var win = iframe.contentWindow;
var app = win.nexacro.getApplication();
var baseForm = app.mainframe.frame.form;
var pageForm = baseForm.divWork.form.divCenter.form.divWork.form;
```

## 연구비 지급현황 (과제수행 > 연구비 > 연구비 지급현황)

- 페이지 폼: `pageForm` → form name = `RECHCT0001_000`
- 검색 영역: `pageForm.divSearch.form`
- 공통 검색 영역: `pageForm.divSearch.form.divSearchComm.form.divSearch.form`

### 검색 조건 컴포넌트

| 컴포넌트 | 경로 (공통검색 기준) | 타입 | 설명 |
|---------|-------------------|------|------|
| cboSSorgn | divSearch.form.cboSSorgn | Combo | 전문기관 |
| cboSBsnsYy | divSearch.form.cboSBsnsYy | Combo | 사업년도 |
| edtSBsns | divSearch.form.edtSBsns | Edit | 사업명 |

| 컴포넌트 | 경로 (divSearch.form 기준) | 타입 | 설명 |
|---------|------------------------|------|------|
| edtRndSbjtNoForSearch | 직접 자식 | Edit | 연구개발과제번호 |
| edtSbjtNmForSearch | 직접 자식 | Edit | 연구개발과제명 |
| edtRscrNmForSearch | 직접 자식 | Edit | 연구책임자 |
| cboRsctPayTpSeForSearch | 직접 자식 | Combo | 지급유형 |
| edtRschOrgnForSearch | 직접 자식 | Edit | 연구개발기관 |
| btnSearch | 직접 자식 | Button | 검색 |
| btnReset | 직접 자식 | Button | 초기화 |

### 주요 전문기관 코드 (cboSSorgn)

| 코드 | 전문기관명 |
|------|----------|
| 10001 | 한국연구재단 |
| 10003 | 정보통신기획평가원 |
| 10005 | 한국산업기술기획평가원 |
| 10008 | 한국보건산업진흥원 |
| 10007 | 한국에너지기술평가원 |

### 결과 그리드
- `pageForm.grdRechctPaySbjtInfoList` (Grid) — 지급과제정보 목록
- `pageForm.btnDtl` (Button) — 상세보기
- `pageForm.btnExcelExportGrdRechctPaySbjtInfoList` (Button) — Excel 내보내기

---

## 보고서제출 (과제평가 > 보고서 > 보고서제출(연차/단계/최종))

- 페이지 폼: `pageForm` → form name = `EVALRPTP0001_T01`
- 검색 영역: `pageForm.divSearch.form`
- 공통 검색 영역: `pageForm.divSearch.form.divSearchCmm.form.divSearch.form`

### 검색 조건 컴포넌트

공통 검색 (divSearchCmm > divSearch):

| 컴포넌트 | 타입 | 설명 |
|---------|------|------|
| cboSSorgn | Combo | 전문기관 |
| cboSBsnsYy | Combo | 사업년도 |

메인 검색 (divSearch.form):

| 컴포넌트 | 타입 | 설명 |
|---------|------|------|
| edtRndSbjtNo | Edit | 연구개발과제번호 |
| edtSbjtNm | Edit | 연구개발과제명 |
| edtRschMbrNm | Edit | 연구책임자 |
| chkYear | CheckBox | 연차보고서 (set_value('1') 체크) |
| chkStep | CheckBox | 단계보고서 |
| chkFinal | CheckBox | 최종보고서 |
| chkOpn | CheckBox | 수정/공개용 |
| chkSbmt | CheckBox | 제출완료 |
| chkRcve | CheckBox | 접수완료 |
| btnSearch | Button | 검색 |

---

(새 페이지 방문 시 여기에 추가)
