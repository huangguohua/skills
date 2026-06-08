/**
 * prototype-generate / router.js
 * 单文件多页面路由核心逻辑
 * 
 * 使用方式：
 * 1. 将此文件内容复制到 HTML 的 <script> 块开头
 * 2. 所有页面 section 使用 id="page-{name}" class="page"
 * 3. 跳转调用 navigate('page-name')
 * 4. 后退调用 goBack()
 */

// ============================================================
// 路由状态
// ============================================================
const Router = {
  current: null,
  history: [],       // 页面历史栈（移动端返回用）
  defaultPage: null, // 初始页面 id（在 init 时设置）
  params: {},        // 当前页面参数

  // 页面元数据配置（按需填充）
  // key: page id (不含 #)
  // value: { title, parent, module }
  pages: {},
};

// ============================================================
// 核心导航函数
// ============================================================

/**
 * 跳转到指定页面
 * @param {string} pageId  - 目标页面 id（不含 #）
 * @param {object} params  - 传递给目标页面的参数
 * @param {boolean} replace - 是否替换当前历史记录（不压栈）
 */
function navigate(pageId, params = {}, replace = false) {
  // 隐藏所有页面
  document.querySelectorAll('.page').forEach(p => p.style.display = 'none');

  // 显示目标页面
  const target = document.getElementById(pageId);
  if (!target) {
    console.warn(`[Router] 页面未找到: ${pageId}`);
    return;
  }
  target.style.display = 'block';

  // 更新路由状态
  const prev = Router.current;
  Router.params = params;

  if (!replace && prev && prev !== pageId) {
    Router.history.push(prev);
  }
  Router.current = pageId;

  // 更新 URL hash
  window.history.replaceState({ pageId, params }, '', `#${pageId}`);

  // 更新导航状态（菜单高亮 / NavBar）
  updateNav(pageId);

  // 触发页面初始化钩子
  const initFn = window[`init_${pageId.replace(/-/g, '_')}`];
  if (typeof initFn === 'function') initFn(params);

  // 滚动到顶部
  target.scrollTop = 0;
  window.scrollTo(0, 0);
}

/**
 * 返回上一页
 */
function goBack() {
  if (Router.history.length > 0) {
    const prev = Router.history.pop();
    navigate(prev, {}, true);
  } else if (Router.defaultPage) {
    navigate(Router.defaultPage, {}, true);
  }
}

// ============================================================
// 导航状态更新
// ============================================================

function updateNav(pageId) {
  // === 后台端：左侧菜单高亮 ===
  const menuItems = document.querySelectorAll('.menu-item[data-page], .menu-sub-item[data-page]');
  menuItems.forEach(item => {
    item.classList.toggle('active', item.dataset.page === pageId);
  });

  // 展开包含当前页的父菜单
  const activeMenu = document.querySelector(`.menu-sub-item[data-page="${pageId}"]`);
  if (activeMenu) {
    const parentGroup = activeMenu.closest('.menu-group');
    if (parentGroup) parentGroup.classList.add('expanded');
  }

  // === 后台端：面包屑更新 ===
  updateBreadcrumb(pageId);

  // === 移动端：NavBar 标题 + 返回按钮 ===
  const pageMeta = Router.pages[pageId];
  const navTitle = document.getElementById('nav-title');
  const navBack = document.getElementById('nav-back');

  if (navTitle && pageMeta) {
    navTitle.textContent = pageMeta.title || pageId;
  }
  if (navBack) {
    navBack.style.display = Router.history.length > 0 ? 'flex' : 'none';
  }

  // === 移动端：TabBar 高亮 ===
  const tabItems = document.querySelectorAll('.tab-item[data-page]');
  tabItems.forEach(item => {
    item.classList.toggle('active', item.dataset.page === pageId);
  });
}

// ============================================================
// 面包屑（后台端）
// ============================================================

function updateBreadcrumb(pageId) {
  const crumbContainer = document.getElementById('breadcrumb');
  if (!crumbContainer) return;

  const pageMeta = Router.pages[pageId];
  if (!pageMeta) {
    crumbContainer.innerHTML = `<span class="crumb-current">${pageId}</span>`;
    return;
  }

  let crumbs = [];
  if (pageMeta.module) crumbs.push({ label: pageMeta.module });
  if (pageMeta.parent) {
    const parentMeta = Router.pages[pageMeta.parent];
    crumbs.push({
      label: parentMeta ? parentMeta.title : pageMeta.parent,
      page: pageMeta.parent
    });
  }
  crumbs.push({ label: pageMeta.title, current: true });

  crumbContainer.innerHTML = crumbs.map((c, i) => {
    if (c.current) return `<span class="crumb-current">${c.label}</span>`;
    if (c.page) return `<a class="crumb-link" onclick="navigate('${c.page}')">${c.label}</a><span class="crumb-sep">›</span>`;
    return `<span class="crumb-item">${c.label}</span><span class="crumb-sep">›</span>`;
  }).join('');
}

// ============================================================
// Modal 控制
// ============================================================

function showModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

function closeModalByOverlay(event, id) {
  if (event.target === event.currentTarget) closeModal(id);
}

// ============================================================
// ActionSheet 控制（移动端）
// ============================================================

function showActionSheet(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}

function closeActionSheet(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

// ============================================================
// Toast（全局）
// ============================================================

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

// ============================================================
// 删除确认弹窗
// ============================================================

function confirmDelete(id, onConfirm) {
  if (!onConfirm) {
    // 默认行为
    if (confirm('确认删除？此操作不可恢复。')) {
      showToast('删除成功');
    }
    return;
  }
  // 可传入自定义确认回调
  const modal = document.getElementById('confirm-delete-modal');
  if (modal) {
    modal.dataset.targetId = id;
    modal.dataset.callback = onConfirm.name || '';
    showModal('confirm-delete-modal');
  }
}

// ============================================================
// Hash 路由监听（刷新/前进/后退）
// ============================================================

window.addEventListener('hashchange', () => {
  const pageId = window.location.hash.replace('#', '');
  if (pageId && pageId !== Router.current) {
    navigate(pageId, {}, true);
  }
});

// ============================================================
// 初始化
// ============================================================

function initRouter(defaultPage, pagesMeta = {}) {
  Router.defaultPage = defaultPage;
  Router.pages = pagesMeta;

  const hash = window.location.hash.replace('#', '');
  navigate(hash || defaultPage, {}, true);
}
