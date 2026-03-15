/**
 * SRnD Helper Functions
 * Run via javascript_tool on srnd.snu.ac.kr
 */

// Get the FrameSet (content area)
function getFrameSet() {
  return nexacro.Application.mainframe.VFrameSet.HFrameSet.VFrameSet.FrameSet;
}

// Get the work form for a given menu ID
function getWorkDiv(menuId) {
  return getFrameSet()[menuId].form.div_workForm;
}

// Read all rows from a dataset as an array of objects
function readDataset(ds) {
  const cols = [];
  for (let c = 0; c < ds.getColCount(); c++) cols.push(ds.getColID(c));
  const rows = [];
  for (let r = 0; r < ds.getRowCount(); r++) {
    const row = {};
    for (const col of cols) row[col] = ds.getColumn(r, col);
    rows.push(row);
  }
  return rows;
}

// List all open page frames
function listOpenPages() {
  const fs = getFrameSet();
  const pages = [];
  for (let k in fs) {
    if (fs[k]?.form?.div_workForm && /^\d+$/.test(k)) {
      pages.push({ menuId: k, url: fs[k].form.div_workForm.url });
    }
  }
  return pages;
}

// Discover datasets and functions on any work form
function discoverForm(menuId) {
  const wd = getWorkDiv(menuId);
  const datasets = [], fns = [], tabs = [];
  for (let i = 0; i < wd.all.length; i++) {
    const c = wd.all[i];
    if (c.name?.startsWith('ds_')) {
      try { datasets.push({ name: c.name, rows: c.getRowCount() }); } catch(e) {}
    }
  }
  for (let k in wd) {
    if (k.startsWith('fn_') && typeof wd[k] === 'function') fns.push(k);
  }
  try {
    const tab = wd.div_right.Tab00;
    tab.tabpages.forEach((p, i) => tabs.push({ index: i, text: p.text }));
  } catch(e) {}
  return { datasets, fns, tabs };
}

// Search menus by Korean keyword
function searchMenu(keyword) {
  const ds = nexacro.Application.mainframe.VFrameSet.TopFrame.form.ds_menuAllList;
  const results = [];
  for (let r = 0; r < ds.getRowCount(); r++) {
    const nm = ds.getColumn(r, 'MENU_NM');
    if (nm && nm.includes(keyword)) {
      results.push({
        menuId: ds.getColumn(r, 'MENU_ID'),
        menuNm: nm,
        pgmId: ds.getColumn(r, 'PGM_ID')
      });
    }
  }
  return results;
}