# 移动端手势交互实现

## 左滑/右滑页面切换

```javascript
// 在页面切换容器上初始化手势
function initSwipeGesture(containerSelector, onSwipeLeft, onSwipeRight) {
  const container = document.querySelector(containerSelector);
  if (!container) return;

  let startX = 0;
  let startY = 0;
  const threshold = 60; // 触发阈值 px
  const restraint = 50; // 垂直容忍 px

  container.addEventListener('touchstart', e => {
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
  }, { passive: true });

  container.addEventListener('touchend', e => {
    const deltaX = e.changedTouches[0].clientX - startX;
    const deltaY = e.changedTouches[0].clientY - startY;
    if (Math.abs(deltaX) > threshold && Math.abs(deltaY) < restraint) {
      if (deltaX < 0 && typeof onSwipeLeft === 'function') onSwipeLeft();
      if (deltaX > 0 && typeof onSwipeRight === 'function') onSwipeRight();
    }
  }, { passive: true });
}

// 使用示例：右滑返回
initSwipeGesture('.page-content', null, () => goBack());
```

## 下拉刷新（视觉效果）

```javascript
function initPullToRefresh(container, onRefresh) {
  let startY = 0;
  let pulling = false;
  const threshold = 60;

  const indicator = document.createElement('div');
  indicator.className = 'ptr-indicator';
  indicator.textContent = '下拉刷新';
  container.prepend(indicator);

  container.addEventListener('touchstart', e => {
    if (container.scrollTop === 0) {
      startY = e.touches[0].clientY;
      pulling = true;
    }
  }, { passive: true });

  container.addEventListener('touchmove', e => {
    if (!pulling) return;
    const delta = e.touches[0].clientY - startY;
    if (delta > 0 && delta < threshold * 1.5) {
      indicator.style.height = delta + 'px';
      indicator.textContent = delta > threshold ? '释放刷新' : '下拉刷新';
    }
  }, { passive: true });

  container.addEventListener('touchend', async () => {
    if (!pulling) return;
    pulling = false;
    const h = parseInt(indicator.style.height || 0);
    if (h > threshold) {
      indicator.textContent = '刷新中...';
      await onRefresh();
    }
    indicator.style.height = '0';
    setTimeout(() => indicator.textContent = '下拉刷新', 300);
  }, { passive: true });
}
```

```css
.ptr-indicator {
  overflow: hidden;
  height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--color-text-3);
  transition: height 0.2s ease;
  background: var(--color-bg-page);
}
```

## 长按操作

```javascript
function initLongPress(selector, onLongPress, delay = 500) {
  document.querySelectorAll(selector).forEach(el => {
    let timer = null;
    el.addEventListener('touchstart', e => {
      timer = setTimeout(() => {
        onLongPress(el, e);
        navigator.vibrate && navigator.vibrate(50); // 震动反馈
      }, delay);
    }, { passive: true });
    el.addEventListener('touchend', () => clearTimeout(timer), { passive: true });
    el.addEventListener('touchmove', () => clearTimeout(timer), { passive: true });
  });
}
```
