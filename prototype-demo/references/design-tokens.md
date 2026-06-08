# Design Tokens 完整参考

## 后台管理端 (Admin)

```css
:root {
  /* === 品牌主色 === */
  --color-primary: #1677FF;
  --color-primary-hover: #4096FF;
  --color-primary-active: #0958D9;
  --color-primary-light: #E6F4FF;
  --color-primary-bg: #F0F5FF;

  /* === 功能色 === */
  --color-success: #52C41A;
  --color-success-bg: #F6FFED;
  --color-warning: #FAAD14;
  --color-warning-bg: #FFFBE6;
  --color-error: #FF4D4F;
  --color-error-bg: #FFF2F0;
  --color-info: #1677FF;

  /* === 中性色 === */
  --color-text-primary: #1D2129;
  --color-text-secondary: #4E5969;
  --color-text-tertiary: #86909C;
  --color-text-disabled: #C9CDD4;
  --color-text-white: #FFFFFF;

  /* === 背景色 === */
  --color-bg-base: #F2F3F5;
  --color-bg-container: #FFFFFF;
  --color-bg-elevated: #FFFFFF;
  --color-bg-layout: #F5F7FA;
  --color-bg-mask: rgba(0, 0, 0, 0.45);
  --color-bg-header: #001529;
  --color-bg-sider: #001529;
  --color-bg-sider-light: #FFFFFF;

  /* === 边框 === */
  --color-border: #E8E8E8;
  --color-border-secondary: #F0F0F0;
  --color-border-strong: #D9D9D9;

  /* === 字体 === */
  --font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
  --font-size-xs: 11px;
  --font-size-sm: 12px;
  --font-size-base: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 20px;
  --font-size-2xl: 24px;
  --font-size-3xl: 30px;

  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  --line-height-tight: 1.25;
  --line-height-base: 1.5714;
  --line-height-relaxed: 1.75;

  /* === 间距 === */
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 20px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  --spacing-10: 40px;
  --spacing-12: 48px;

  /* === 圆角 === */
  --border-radius-sm: 4px;
  --border-radius: 6px;
  --border-radius-lg: 8px;
  --border-radius-xl: 12px;
  --border-radius-full: 9999px;

  /* === 阴影 === */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.08);
  --shadow-modal: 0 6px 16px rgba(0, 0, 0, 0.12), 0 3px 6px rgba(0, 0, 0, 0.08);
  --shadow-dropdown: 0 6px 16px rgba(0, 0, 0, 0.08);

  /* === 布局 === */
  --sider-width: 220px;
  --sider-collapsed-width: 60px;
  --header-height: 56px;
  --breadcrumb-height: 40px;
  --content-padding: 24px;

  /* === 过渡 === */
  --transition-base: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  --transition-fast: all 0.1s ease;
  --transition-slow: all 0.3s ease;
}
```

---

## 移动端 (Mobile)

```css
:root {
  /* === 品牌主色 === */
  --color-primary: #1677FF;
  --color-primary-hover: #4096FF;
  --color-primary-light: #E6F4FF;

  /* === 功能色 === */
  --color-success: #00B42A;
  --color-warning: #FF7D00;
  --color-error: #F53F3F;
  --color-link: #165DFF;

  /* === 中性色 === */
  --color-text-1: #1D2129;
  --color-text-2: #4E5969;
  --color-text-3: #86909C;
  --color-text-4: #C9CDD4;

  /* === 背景色 === */
  --color-bg-1: #FFFFFF;
  --color-bg-2: #F2F3F5;
  --color-bg-3: #E5E6EB;
  --color-bg-page: #F7F8FA;

  /* === 边框 === */
  --color-border-1: #E5E6EB;
  --color-border-2: #C9CDD4;

  /* === 字体 === */
  --font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', sans-serif;
  --font-size-xs: 10px;
  --font-size-sm: 12px;
  --font-size-base: 14px;
  --font-size-lg: 16px;
  --font-size-xl: 18px;
  --font-size-2xl: 20px;

  /* === 间距 === */
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 20px;
  --spacing-6: 24px;

  /* === 圆角 === */
  --border-radius-sm: 4px;
  --border-radius: 8px;
  --border-radius-lg: 12px;
  --border-radius-xl: 16px;
  --border-radius-full: 9999px;

  /* === 阴影 === */
  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.06);
  --shadow-popup: 0 -4px 16px rgba(0, 0, 0, 0.08);

  /* === 移动端布局 === */
  --phone-width: 375px;
  --nav-bar-height: 44px;
  --tab-bar-height: 50px;
  --status-bar-height: 44px;
  --safe-area-bottom: env(safe-area-inset-bottom, 0px);
  --content-padding: 16px;

  /* === 过渡 === */
  --transition-base: all 0.25s ease;
  --page-transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
```
