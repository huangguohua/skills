# 标准组件 HTML 模板库

使用时将组件 HTML 复制到对应页面，样式已通过 CSS 变量统一。

---

## 目录
- [后台端组件](#后台端组件)
  - [数据表格](#数据表格)
  - [搜索筛选栏](#搜索筛选栏)
  - [Modal 弹窗](#modal-弹窗)
  - [表单](#表单)
  - [状态标签 Badge](#状态标签-badge)
  - [统计卡片](#统计卡片)
  - [面包屑](#面包屑)
- [移动端组件](#移动端组件)
  - [列表项 Cell](#列表项-cell)
  - [底部弹出层 ActionSheet](#底部弹出层-actionsheet)
  - [Toast 提示](#toast-提示)
  - [空状态](#空状态)
  - [搜索框](#搜索框)

---

## 后台端组件

### 数据表格

```html
<div class="table-container">
  <table class="data-table">
    <thead>
      <tr>
        <th><input type="checkbox" class="checkbox"></th>
        <th>列名1</th>
        <th>列名2</th>
        <th>状态</th>
        <th>操作</th>
      </tr>
    </thead>
    <tbody id="table-body">
      <tr>
        <td><input type="checkbox" class="checkbox"></td>
        <td>数据内容</td>
        <td>数据内容</td>
        <td><span class="badge badge-success">正常</span></td>
        <td>
          <button class="btn-link" onclick="navigate('edit-page')">编辑</button>
          <button class="btn-link btn-danger" onclick="confirmDelete(1)">删除</button>
        </td>
      </tr>
    </tbody>
  </table>
  <!-- 分页 -->
  <div class="pagination">
    <span class="pagination-info">共 100 条</span>
    <div class="pagination-pages">
      <button class="page-btn" disabled>‹</button>
      <button class="page-btn active">1</button>
      <button class="page-btn">2</button>
      <button class="page-btn">3</button>
      <button class="page-btn">›</button>
    </div>
    <select class="page-size-select">
      <option>10条/页</option>
      <option>20条/页</option>
      <option>50条/页</option>
    </select>
  </div>
</div>
```

```css
.table-container { background: var(--color-bg-container); border-radius: var(--border-radius-lg); overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { padding: 12px 16px; background: var(--color-bg-base); color: var(--color-text-secondary); font-weight: 500; font-size: var(--font-size-sm); text-align: left; border-bottom: 1px solid var(--color-border); }
.data-table td { padding: 12px 16px; border-bottom: 1px solid var(--color-border-secondary); color: var(--color-text-primary); font-size: var(--font-size-base); }
.data-table tbody tr:hover { background: var(--color-bg-base); }
.data-table tbody tr:last-child td { border-bottom: none; }
.pagination { display: flex; align-items: center; gap: 8px; padding: 12px 16px; justify-content: flex-end; }
.pagination-info { color: var(--color-text-secondary); font-size: var(--font-size-sm); margin-right: auto; }
.page-btn { min-width: 32px; height: 32px; padding: 0 8px; border: 1px solid var(--color-border); border-radius: var(--border-radius-sm); background: white; cursor: pointer; }
.page-btn.active { background: var(--color-primary); color: white; border-color: var(--color-primary); }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-size-select { height: 32px; border: 1px solid var(--color-border); border-radius: var(--border-radius-sm); padding: 0 8px; }
.btn-link { background: none; border: none; color: var(--color-primary); cursor: pointer; font-size: var(--font-size-sm); padding: 0 4px; }
.btn-link.btn-danger { color: var(--color-error); }
.btn-link:hover { opacity: 0.8; }
```

---

### 搜索筛选栏

```html
<div class="filter-bar">
  <div class="filter-item">
    <label>关键词</label>
    <input type="text" class="filter-input" placeholder="请输入关键词">
  </div>
  <div class="filter-item">
    <label>状态</label>
    <select class="filter-select">
      <option value="">全部</option>
      <option value="1">启用</option>
      <option value="0">禁用</option>
    </select>
  </div>
  <div class="filter-item">
    <label>日期范围</label>
    <input type="date" class="filter-input"> 至 <input type="date" class="filter-input">
  </div>
  <div class="filter-actions">
    <button class="btn btn-primary" onclick="handleSearch()">查询</button>
    <button class="btn btn-default" onclick="handleReset()">重置</button>
  </div>
</div>
```

```css
.filter-bar { background: var(--color-bg-container); padding: 16px 24px; border-radius: var(--border-radius-lg); display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-end; margin-bottom: 16px; }
.filter-item { display: flex; flex-direction: column; gap: 4px; }
.filter-item label { font-size: var(--font-size-sm); color: var(--color-text-secondary); }
.filter-input, .filter-select { height: 32px; padding: 0 11px; border: 1px solid var(--color-border); border-radius: var(--border-radius-sm); font-size: var(--font-size-base); outline: none; }
.filter-input:focus, .filter-select:focus { border-color: var(--color-primary); box-shadow: 0 0 0 2px var(--color-primary-light); }
.filter-actions { display: flex; gap: 8px; }
```

---

### Modal 弹窗

```html
<!-- 触发：showModal('modal-example') -->
<div class="modal-overlay" id="modal-example" onclick="closeModalByOverlay(event, 'modal-example')">
  <div class="modal">
    <div class="modal-header">
      <span class="modal-title">弹窗标题</span>
      <button class="modal-close" onclick="closeModal('modal-example')">✕</button>
    </div>
    <div class="modal-body">
      <!-- 内容 -->
      <p>弹窗内容区域</p>
    </div>
    <div class="modal-footer">
      <button class="btn btn-default" onclick="closeModal('modal-example')">取消</button>
      <button class="btn btn-primary" onclick="handleModalConfirm()">确认</button>
    </div>
  </div>
</div>
```

```css
.modal-overlay { display: none; position: fixed; inset: 0; background: var(--color-bg-mask); z-index: 1000; align-items: center; justify-content: center; }
.modal-overlay.open { display: flex; }
.modal { background: white; border-radius: var(--border-radius-lg); box-shadow: var(--shadow-modal); min-width: 480px; max-width: 600px; max-height: 80vh; display: flex; flex-direction: column; }
.modal-header { padding: 16px 24px; border-bottom: 1px solid var(--color-border); display: flex; align-items: center; justify-content: space-between; }
.modal-title { font-size: 16px; font-weight: 600; color: var(--color-text-primary); }
.modal-close { background: none; border: none; cursor: pointer; color: var(--color-text-tertiary); font-size: 16px; line-height: 1; padding: 4px; }
.modal-body { padding: 24px; overflow-y: auto; }
.modal-footer { padding: 12px 24px; border-top: 1px solid var(--color-border); display: flex; gap: 8px; justify-content: flex-end; }
```

---

### 表单

```html
<form class="form" onsubmit="handleFormSubmit(event)">
  <div class="form-item">
    <label class="form-label required">字段名称</label>
    <input type="text" class="form-input" placeholder="请输入" required>
    <span class="form-error">请填写此字段</span>
  </div>
  <div class="form-item">
    <label class="form-label">描述</label>
    <textarea class="form-textarea" rows="4" placeholder="请输入描述"></textarea>
  </div>
  <div class="form-item">
    <label class="form-label">状态</label>
    <div class="form-radio-group">
      <label class="radio-label"><input type="radio" name="status" value="1" checked> 启用</label>
      <label class="radio-label"><input type="radio" name="status" value="0"> 禁用</label>
    </div>
  </div>
</form>
```

```css
.form { max-width: 600px; }
.form-item { display: flex; flex-direction: column; gap: 6px; margin-bottom: 20px; }
.form-label { font-size: var(--font-size-base); color: var(--color-text-primary); font-weight: 500; }
.form-label.required::before { content: '*'; color: var(--color-error); margin-right: 4px; }
.form-input, .form-textarea, .form-select { width: 100%; padding: 8px 12px; border: 1px solid var(--color-border); border-radius: var(--border-radius-sm); font-size: var(--font-size-base); outline: none; font-family: inherit; }
.form-input:focus, .form-textarea:focus { border-color: var(--color-primary); box-shadow: 0 0 0 2px var(--color-primary-light); }
.form-error { display: none; color: var(--color-error); font-size: var(--font-size-sm); }
.radio-label { display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: var(--font-size-base); }
.form-radio-group { display: flex; gap: 24px; }
```

---

### 状态标签 Badge

```html
<span class="badge badge-success">成功</span>
<span class="badge badge-warning">待处理</span>
<span class="badge badge-error">失败</span>
<span class="badge badge-default">默认</span>
<span class="badge badge-info">进行中</span>
```

```css
.badge { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: var(--border-radius-full); font-size: var(--font-size-sm); font-weight: 500; }
.badge-success { background: var(--color-success-bg); color: var(--color-success); }
.badge-warning { background: var(--color-warning-bg); color: var(--color-warning); }
.badge-error { background: var(--color-error-bg); color: var(--color-error); }
.badge-default { background: var(--color-bg-base); color: var(--color-text-secondary); }
.badge-info { background: var(--color-primary-light); color: var(--color-primary); }
```

---

### 统计卡片

```html
<div class="stats-grid">
  <div class="stat-card">
    <div class="stat-label">今日订单</div>
    <div class="stat-value">1,234</div>
    <div class="stat-trend trend-up">↑ 12.5% 较昨日</div>
  </div>
  <!-- 重复 stat-card -->
</div>
```

```css
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
.stat-card { background: var(--color-bg-container); border-radius: var(--border-radius-lg); padding: 20px 24px; box-shadow: var(--shadow-card); }
.stat-label { font-size: var(--font-size-sm); color: var(--color-text-secondary); margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 700; color: var(--color-text-primary); margin-bottom: 8px; }
.stat-trend { font-size: var(--font-size-sm); }
.trend-up { color: var(--color-success); }
.trend-down { color: var(--color-error); }
```

---

## 移动端组件

### 列表项 Cell

```html
<div class="cell-group">
  <div class="cell" onclick="navigate('detail-page')">
    <div class="cell-icon">🏠</div>
    <div class="cell-content">
      <div class="cell-title">标题内容</div>
      <div class="cell-desc">描述文字</div>
    </div>
    <div class="cell-extra">
      <span class="cell-value">详情值</span>
      <span class="cell-arrow">›</span>
    </div>
  </div>
</div>
```

```css
.cell-group { background: var(--color-bg-1); border-radius: var(--border-radius); overflow: hidden; margin-bottom: 12px; }
.cell { display: flex; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--color-border-1); cursor: pointer; transition: var(--transition-base); gap: 12px; }
.cell:last-child { border-bottom: none; }
.cell:active { background: var(--color-bg-2); }
.cell-icon { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: var(--border-radius-sm); background: var(--color-bg-2); font-size: 18px; flex-shrink: 0; }
.cell-content { flex: 1; min-width: 0; }
.cell-title { font-size: var(--font-size-base); color: var(--color-text-1); font-weight: 500; }
.cell-desc { font-size: var(--font-size-sm); color: var(--color-text-3); margin-top: 2px; }
.cell-extra { display: flex; align-items: center; gap: 4px; }
.cell-value { font-size: var(--font-size-sm); color: var(--color-text-3); }
.cell-arrow { color: var(--color-text-4); font-size: 18px; }
```

---

### 底部弹出层 ActionSheet

```html
<!-- 触发：showActionSheet('sheet-example') -->
<div class="sheet-overlay" id="sheet-example" onclick="closeActionSheet('sheet-example')">
  <div class="sheet" onclick="event.stopPropagation()">
    <div class="sheet-handle"></div>
    <div class="sheet-title">操作标题</div>
    <div class="sheet-actions">
      <button class="sheet-action" onclick="handleAction1()">操作一</button>
      <button class="sheet-action" onclick="handleAction2()">操作二</button>
      <button class="sheet-action sheet-action-danger" onclick="handleDelete()">删除</button>
    </div>
    <div class="sheet-divider"></div>
    <button class="sheet-cancel" onclick="closeActionSheet('sheet-example')">取消</button>
  </div>
</div>
```

```css
.sheet-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 1000; align-items: flex-end; justify-content: center; }
.sheet-overlay.open { display: flex; }
.sheet { background: var(--color-bg-1); border-radius: var(--border-radius-xl) var(--border-radius-xl) 0 0; width: 100%; max-width: var(--phone-width); padding-bottom: var(--safe-area-bottom); }
.sheet-handle { width: 36px; height: 4px; background: var(--color-bg-3); border-radius: 2px; margin: 8px auto; }
.sheet-title { text-align: center; font-size: var(--font-size-sm); color: var(--color-text-3); padding: 8px 16px 12px; }
.sheet-actions { border-top: 1px solid var(--color-border-1); }
.sheet-action { width: 100%; padding: 14px 16px; background: none; border: none; border-bottom: 1px solid var(--color-border-1); font-size: var(--font-size-lg); color: var(--color-text-1); cursor: pointer; text-align: center; }
.sheet-action:active { background: var(--color-bg-2); }
.sheet-action-danger { color: var(--color-error); }
.sheet-divider { height: 8px; background: var(--color-bg-2); }
.sheet-cancel { width: 100%; padding: 14px 16px; background: none; border: none; font-size: var(--font-size-lg); color: var(--color-text-1); cursor: pointer; font-weight: 500; }
.sheet-cancel:active { background: var(--color-bg-2); }
```

---

### Toast 提示

```javascript
// 全局 Toast 函数（放入 <script> 块）
function showToast(message, type = 'success', duration = 2000) {
  const existing = document.getElementById('global-toast');
  if (existing) existing.remove();
  const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
  const toast = document.createElement('div');
  toast.id = 'global-toast';
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span class="toast-icon">${icons[type]}</span><span>${message}</span>`;
  document.body.appendChild(toast);
  setTimeout(() => toast.classList.add('toast-show'), 10);
  setTimeout(() => {
    toast.classList.remove('toast-show');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}
```

```css
.toast { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%) scale(0.9); background: rgba(0,0,0,0.75); color: white; padding: 10px 20px; border-radius: var(--border-radius-lg); display: flex; align-items: center; gap: 8px; font-size: var(--font-size-base); z-index: 9999; opacity: 0; transition: all 0.25s ease; pointer-events: none; white-space: nowrap; }
.toast.toast-show { opacity: 1; transform: translate(-50%, -50%) scale(1); }
.toast-icon { font-size: 16px; }
```

---

### 空状态

```html
<div class="empty-state">
  <div class="empty-icon">📭</div>
  <div class="empty-title">暂无数据</div>
  <div class="empty-desc">当前没有相关内容</div>
  <button class="btn btn-primary" onclick="handleAdd()">立即添加</button>
</div>
```

```css
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 24px; gap: 8px; }
.empty-icon { font-size: 48px; margin-bottom: 8px; }
.empty-title { font-size: var(--font-size-lg); color: var(--color-text-1); font-weight: 500; }
.empty-desc { font-size: var(--font-size-sm); color: var(--color-text-3); }
```

---

### 搜索框

```html
<div class="search-bar">
  <div class="search-input-wrap">
    <span class="search-icon">🔍</span>
    <input type="search" class="search-input" placeholder="搜索..." oninput="handleSearch(this.value)">
  </div>
</div>
```

```css
.search-bar { padding: 8px 16px; background: var(--color-bg-page); }
.search-input-wrap { background: var(--color-bg-1); border-radius: var(--border-radius-full); display: flex; align-items: center; padding: 0 12px; gap: 8px; }
.search-icon { font-size: 14px; color: var(--color-text-3); }
.search-input { flex: 1; border: none; outline: none; padding: 8px 0; font-size: var(--font-size-base); background: transparent; color: var(--color-text-1); }
```
