#!/usr/bin/env python3
"""Localize NXShare web UI to Chinese. Uses navigator.language for auto-detection."""

import re

with open("data/web/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# === 1. Insert language detection script at top of <head> ===
detect_script = '''<script>
// Auto-detect language for NXShare web UI
const isZH = navigator.language.startsWith('zh');
const _ = (en, zh) => isZH ? zh : en;
</script>
'''
html = html.replace('<meta charset="UTF-8">',
                     '<meta charset="UTF-8">\n' + detect_script)

# === 2. Fix HTML lang attribute ===
html = html.replace('<html lang="en">', '<html lang="zh-CN">')

# === 3. Replace Google Fonts with system font stack (CJK-compatible) ===
html = html.replace(
    '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">',
    '<!-- System font stack with CJK support; Google Fonts removed for offline/Chinese localization -->')

# Replace DM Sans references with system font stack
html = html.replace(
    "font-family: 'DM Sans', sans-serif;",
    "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', 'Hiragino Sans GB', sans-serif;")

html = html.replace(
    "font-family: 'DM Mono', monospace;",
    "font-family: 'SF Mono', 'Cascadia Code', 'Consolas', 'PingFang SC', monospace;")

# Also replace any remaining DM Sans/Mono references in CSS
html = html.replace("font-family: 'DM Sans', sans-serif", "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif")
html = html.replace("font-family: 'DM Mono', monospace", "font-family: 'SF Mono', 'Cascadia Code', 'Consolas', monospace")

# === 4. Filter buttons (static HTML) ===
html = html.replace(
    '<button class="filter-btn active" data-filter="">All</button>',
    '<button class="filter-btn active" data-filter="" id="filter-all">All</button>')
html = html.replace(
    '<button class="filter-btn" data-filter="screenshots">Screenshots</button>',
    '<button class="filter-btn" data-filter="screenshots" id="filter-screenshots">Screenshots</button>')
html = html.replace(
    '<button class="filter-btn" data-filter="videos">Videos</button>',
    '<button class="filter-btn" data-filter="videos" id="filter-videos">Videos</button>')

# === 5. Select all / Close buttons ===
html = html.replace(
    '<button class="select-all-btn" id="select-all-btn">Select all</button>',
    '<button class="select-all-btn" id="select-all-btn">Select all</button>')
html = html.replace(
    '<button class="lb-btn lb-close" id="lb-close">✕ Close</button>',
    '<button class="lb-btn lb-close" id="lb-close">✕ Close</button>')

# === 6. Download buttons ===
html = html.replace(
    '<button class="dl-btn" id="dl-selected">Download</button>',
    '<button class="dl-btn" id="dl-selected">Download</button>')
html = html.replace(
    '<button class="lb-btn lb-dl" id="lb-dl">Download</button>',
    '<button class="lb-btn lb-dl" id="lb-dl">Download</button>')

# === 7. Footer ===
html = html.replace(
    '<span class="footer-text"><b>NXShare</b> v1.7.4 &nbsp;—&nbsp; made by musebrot ♥</span>',
    '<span class="footer-text"><b>NXShare</b> v1.7.4 &nbsp;—&nbsp; <span id="footer-author">made by musebrot ♥</span></span>')

# === 8. JS: months array ===
html = html.replace(
    "const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];",
    "const months = isZH ? ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']\n"
    "              : ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];")

# === 9. JS: toggleGameFilters button text ("Games ▾" / "游戏 ▾") ===
html = html.replace(
    "btn.textContent = visible ? 'Games ▾' : 'Games ▴';",
    "btn.textContent = visible ? _( 'Games ▾', '游戏 ▾') : _( 'Games ▴', '游戏 ▴');")

# === 10. JS: buildGameFilters "All Games" button ===
html = html.replace(
    "allBtn.textContent = 'All Games';",
    "allBtn.textContent = _('All Games', '全部游戏');")

# === 11. JS: Connection error ===
html = html.replace(
    "document.getElementById('content').innerHTML = `<div class=\"status-msg\">⚠️ Connection error<br><small>${e.message}</small></div>`;",
    "document.getElementById('content').innerHTML = `<div class=\"status-msg\">` + _('⚠️ Connection error', '⚠️ 连接错误') + `<br><small>${e.message}</small></div>`;")

# === 12. JS: No media found ===
html = html.replace(
    "content.innerHTML = '<div class=\"status-msg\">No media found 🎮</div>';",
    "content.innerHTML = '<div class=\"status-msg\">' + _('No media found 🎮', '未找到媒体文件 🎮') + '</div>';")

# === 13. JS: Type badges ("Video" / "PNG" / "Photo") ===
html = html.replace(
    '${isVideo ? \'Video\' : file.filename.toLowerCase().endsWith(\'.png\') ? \'PNG\' : \'Photo\'}',
    "${isVideo ? _('Video','视频') : file.filename.toLowerCase().endsWith('.png') ? 'PNG' : _('Photo','照片')}")

# === 14. JS: Load more button ===
html = html.replace(
    "wrap.innerHTML = `<button class=\"load-more-btn\">Load more &nbsp;(${total - offset} remaining)</button>`;",
    "wrap.innerHTML = `<button class=\"load-more-btn\">` + _('Load more', '加载更多') + ` &nbsp;(${total - offset} ` + _('remaining', '剩余') + `)</button>`;")

# === 15. JS: Download button text ===
html = html.replace(
    "btn.textContent = '⬇ Download';",
    "btn.textContent = '⬇ ' + _('Download', '下载');")

# === 16. JS: Refreshing message ===
html = html.replace(
    "document.getElementById('content').innerHTML = '<div class=\"status-msg\"><div class=\"spinner\"></div><br>Refreshing...</div>';",
    "document.getElementById('content').innerHTML = '<div class=\"status-msg\"><div class=\"spinner\"></div><br>' + _('Refreshing...', '刷新中...') + '</div>';")

# === 17. Add i18n initialization at end of script (before </script>) ===
init_i18n = '''
// --- i18n: update static UI elements on load ---
(function applyI18n() {
  // Filter buttons
  const allBtn = document.getElementById('filter-all');
  if (allBtn) allBtn.textContent = _('All', '全部');
  const ssBtn = document.getElementById('filter-screenshots');
  if (ssBtn) ssBtn.textContent = _('Screenshots', '截图');
  const vidBtn = document.getElementById('filter-videos');
  if (vidBtn) vidBtn.textContent = _('Videos', '视频');

  // Select all
  const selBtn = document.getElementById('select-all-btn');
  if (selBtn) selBtn.textContent = _('Select all', '全选');

  // Download bar button
  const dlBtn = document.getElementById('dl-selected');
  if (dlBtn) dlBtn.textContent = _('Download', '下载');

  // Lightbox buttons
  const lbDl = document.getElementById('lb-dl');
  if (lbDl) lbDl.textContent = _('Download', '下载');
  const lbClose = document.getElementById('lb-close');
  if (lbClose) lbClose.textContent = '✕ ' + _('Close', '关闭');

  // Footer
  const footerAuth = document.getElementById('footer-author');
  if (footerAuth) footerAuth.textContent = _('made by musebrot ♥', '作者 musebrot ♥  忘忧汉化');
})();
'''
html = html.replace('</script>\n</body>', init_i18n + '\n</script>\n</body>')

# === 18. Also set document.title ===
html = html.replace('<title>NXShare</title>', '<title>NXShare</title>')

# Write output
with open("data/web/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Web UI localized successfully.")
print(f"File size: {len(html)} bytes")
