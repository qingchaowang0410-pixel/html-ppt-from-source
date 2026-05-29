---
name: html-ppt-from-source
description: 把 PDF / Markdown / 纯文本源文档转成"双击即看"的单 HTML 版 PPT。两套主题二选一——中国风/报纸金句风（米黄底 + 朱砂红 + 宋体 + 印章）或 Editorial 知识工作者风（深/浅双模、衬线巨字、出版物质感）。自带可点击案例卡片 + 中心弹窗、scroll-snap 翻页、键盘导航。零外链、纯系统字体。当用户说"把这些 PDF 做成 HTML PPT""做一份 HTML 课件""生成 HTML 演示文稿"时触发。
---

# html-ppt-from-source

## 启动流程（生成前必问，最多两次）

收到 PDF/Markdown 源文档后，**先弹框确认主题方向，再开始生成**。用 AskUserQuestion 工具，不要用纯文字提问。

### 第一次弹框 · 主题方向（必问）

```
question: 这份 PPT 想用哪种风格？
header: 主题风格
options:
  - 中国风 · 报纸金句风
    description: 米黄纸 + 朱砂红 + 宋体 + 印章。适合课程讲义、文化/教育/出版类内容。
  - Editorial · 知识工作者风
    description: 衬线巨字 + 极简留白 + 西文斜体强调。适合发布会、技术深稿、白皮书、个人简历。
```

### 第二次弹框 · 配色模式（仅当选 Editorial 时再问）

```
question: Editorial 用深色还是浅色？
header: 配色模式
options:
  - 深色模式
    description: 近黑底 #0E0E10 + 白字。适合发布会、深度长稿、夜间阅读。
  - 浅色模式
    description: 米黄暖灰底 #E8E4DC + 黑字。适合白皮书、深度博客、纸刊感。
```

**主题方向选定后，按以下规则一次性生成 HTML，不再问启动问题**：

- **章节结构**：一份源文件 = 一个一级章节，顺序按用户给的顺序
- **案例卡片**：自动识别"案例 / 学员分享 / 故事 / 含人物对话 / 项目经历 / 工作经历"段落做成可点击卡片
- **成品文件名**：默认 `index.html`，除非用户指定别名
- **DESIGN.md**：跳过，不再写中间产物

**只有这一种情况才再问用户**：源文档没有任何叙事案例——确认是否要做"纯要点页"。

## 执行流程（4 步）

### 1. 读源文档

用 Read 工具读全部 PDF/MD。读完立刻在脑中分两类：
- **要点段落** → 直接写进 slide 正文
- **叙事案例段落**（含"有一次""某学员""他说"等标记，或带人物对话）→ 抽出来做成案例卡片

**案例 ID 命名约定**：纯英文小写 + 连字符（例：`huawei-libya`、`tire-old-man`）。

### 2. 直接 Write 单 HTML 文件

**按主题选择对应的 CSS BLOCK**：
- 中国风 → 用本文件「CSS BLOCK · 中国风」段（默认主题，最完整）
- Editorial 深色 → 用「CSS BLOCK · Editorial」段，并给 `<html>` 加 `data-mode="dark"`
- Editorial 浅色 → 用「CSS BLOCK · Editorial」段，并给 `<html>` 加 `data-mode="light"`

JS BLOCK 与 HTML 骨架两个主题完全共用，**整段复制，不要重写**。

只需要思考的部分：
1. `<title>` 和 `.topnav__brand` 文字
2. 各个 `<section class="slide">` 里的具体内容
3. `const CASES = {...}` 里的案例数据
4. `NAV_LABELS_DISPLAY` 和 `CHAPTERS`（按章节数填）
5. Editorial 主题专属：章节首页可用 `<div class="act-marker">ACT I · THE EVOLUTION</div>` 代替朱砂印章

### 3. 自检（一行命令）

```bash
FILE="path/to/index.html"
echo "外链: $(grep -cE '@import|<link[^>]+href=|<script[^>]+src=|src=\"https?' "$FILE")（应为0）"
echo "section: 开$(grep -c '<section ' "$FILE") 闭$(grep -c '</section>' "$FILE")（应相等）"
awk '/<script>/{f=1;next}/<\/script>/{f=0}f' "$FILE" > /tmp/_chk.js && node --check /tmp/_chk.js
```

### 4. 中文繁简兜底（仅当源文档含繁体或模型可能输出繁体时）

```bash
python3 ~/.claude/skills/html-ppt-from-source/scripts/t2s_safe.py path/to/index.html
```

---

## HTML 骨架（用户指定文件名后整页一次性写出）

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>[[文档标题]]</title>
<style>[[整段粘贴 CSS BLOCK，见下]]</style>
</head>
<body>
<nav class="topnav">
  <div class="topnav__brand">[[品牌短标题]]</div>
  <div class="topnav__chapters" id="navChapters"></div>
  <button class="topnav__mobile-toggle" id="mobileToggle">目录</button>
  <div class="topnav__progress" id="progress"></div>
</nav>
<div class="page-hint"><kbd>↑</kbd><kbd>↓</kbd> 翻页 · <kbd>ESC</kbd> 关闭案例</div>
<div class="page-counter" id="pageCounter">01 / 00</div>
<div class="case-modal-backdrop" id="modalBackdrop" data-open="false"></div>
<div class="case-modal" id="caseModal" data-open="false" role="dialog" aria-modal="true">
  <button class="case-modal__close" id="modalClose">✕</button>
  <div class="case-modal__eyebrow">案例详读</div>
  <h2 class="case-modal__title" id="modalTitle"></h2>
  <div class="case-modal__chapter" id="modalChapter"></div>
  <div class="case-modal__body" id="modalBody"></div>
  <div class="case-modal__seal"><span class="stamp stamp--small"><span class="stamp__inner"><span>娄印</span></span></span></div>
</div>
<main id="main">
[[全部 <section class="slide" data-chapter="N"> ... </section>]]
</main>
<script>
const CASES = { [[案例字典]] };
const NAV_LABELS_DISPLAY = ["首", "壹", "贰", "叁"];  // 按章节数填
const CHAPTERS = [{ id: 0, label: "首", title: "封面" }];
[[整段粘贴 JS BLOCK，见下]]
</script>
</body>
</html>
```

## Slide 结构示例（复用即可）

```html
<!-- 封面 -->
<section class="slide slide--cover" data-chapter="0">
  <div class="slide__inner">
    <div class="masthead"><span class="masthead__title">主标题</span><span class="masthead__meta">副标题</span></div>
    <div class="eyebrow reveal">小标识</div>
    <h1 class="hero-h1 reveal">主标题</h1>
    <p class="subtitle reveal">副题</p>
  </div>
</section>

<!-- 章节首页 -->
<section class="slide" data-chapter="1">
  <div class="chapter-numeral">壹</div>
  <div class="slide__inner">
    <div class="eyebrow reveal">第一章</div>
    <h2 class="h2 reveal">章节标题</h2>
    <p class="subtitle reveal">副题</p>
    <p class="lead reveal">导读</p>
  </div>
  <span class="stamp chapter-stamp"><span class="stamp__inner"><span>壹章</span></span></span>
</section>

<!-- 金句屏 -->
<section class="slide slide--quote" data-chapter="1">
  <div class="slide__inner" style="text-align:center;">
    <p class="quote-main reveal">这是金句。</p>
    <p class="quote-source reveal">—— 出处</p>
  </div>
</section>

<!-- 内容屏（带案例卡片） -->
<section class="slide" data-chapter="1">
  <div class="slide__inner">
    <p class="eyebrow reveal">小节标识</p>
    <h3 class="h3 reveal">小节标题</h3>
    <p class="lead reveal">引导文字</p>
    <div class="case-grid reveal-stagger">
      <button class="case-card" data-case-id="example-id">
        <div class="case-card__title">案例标题</div>
        <p class="case-card__excerpt">案例摘要（3 行内）</p>
      </button>
    </div>
  </div>
</section>
```

## CASES 字典格式

```js
"example-id": {
  title: "案例完整标题",
  chapter: "第一章 · 小节",
  body: `
    <p>正文段落。</p>
    <p class="dialogue">「人物对话用 dialogue 类。」</p>
    <p class="takeaway">小结/启示用 takeaway 类。</p>
  `
}
```

## 大写章序号映射

| 章 | 印章文字 | 巨型序号 | 导航字符 |
|---|---|---|---|
| 1 | 壹章 | 壹 | 壹 |
| 2 | 贰章 | 贰 | 贰 |
| 3 | 叁章 | 叁 | 叁 |
| 4 | 肆章 | 肆 | 肆 |
| 5 | 伍章 | 伍 | 伍 |
| 6 | 陆章 | 陆 | 陆 |
| 7 | 柒章 | 柒 | 柒 |

---

## CSS BLOCK · 中国风（默认主题，整段复制，不要改）

```css
:root{--paper:#F3E9D2;--paper-deep:#EBDFC2;--paper-edge:#DFD2B0;--paper-stain:#C9B789;--vermilion:#9B2A1F;--vermilion-deep:#7A1F17;--vermilion-light:#C84E3F;--vermilion-wash:#D9B5A8;--vermilion-rgb:155,42,31;--ink:#1C1612;--ink-soft:#3A2F26;--ink-fade:#6B5E50;--ink-rgb:28,22,18;--gold:#A8843D;--modal-mask:rgba(28,22,18,0.72);--card-shadow:0 2px 0 var(--paper-edge),0 8px 20px rgba(28,22,18,.08);--card-shadow-hover:0 4px 0 var(--vermilion-deep),0 14px 32px rgba(155,42,31,.18);--font-display:"Songti SC","STSong","SimSun","Source Han Serif SC","Noto Serif CJK SC","FangSong",serif;--font-body:"Songti SC","STSong","Source Han Serif SC","Noto Serif CJK SC","SimSun",serif;--font-quote:"Kaiti SC","STKaiti","KaiTi","BiauKai","Songti SC",serif;--font-numeral:"Georgia","Times New Roman","Songti SC",serif}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;scroll-snap-type:y mandatory;overflow-y:scroll;background:var(--paper)}
body{font-family:var(--font-body);color:var(--ink-soft);background:var(--paper);font-size:16px;line-height:1.85;-webkit-font-smoothing:antialiased}
.topnav{position:fixed;top:0;left:0;right:0;height:56px;background:rgba(243,233,210,.92);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border-bottom:1px solid var(--paper-edge);z-index:100;display:flex;align-items:center;padding:0 32px;font-family:var(--font-display);font-size:13px;letter-spacing:.3em}
.topnav__brand{font-weight:700;color:var(--ink);margin-right:auto;cursor:pointer}
.topnav__chapters{display:flex;gap:4px;align-items:center}
.topnav__chapter{background:transparent;border:1px solid transparent;padding:6px 12px;font:inherit;color:var(--ink-fade);cursor:pointer;letter-spacing:0;transition:all 180ms ease;font-family:var(--font-numeral);font-style:italic;font-size:16px}
.topnav__chapter:hover{color:var(--vermilion)}
.topnav__chapter[data-active="true"]{color:var(--paper);background:var(--vermilion);border-color:var(--vermilion)}
.topnav__progress{position:absolute;left:0;bottom:-1px;height:2px;background:var(--vermilion);width:0%;transition:width 240ms ease}
.topnav__mobile-toggle{display:none;background:none;border:none;font-family:var(--font-display);font-size:16px;color:var(--ink);cursor:pointer;padding:6px 10px}
.slide{min-height:100vh;padding:96px;display:flex;flex-direction:column;justify-content:center;position:relative;background:var(--paper);scroll-snap-align:start;scroll-snap-stop:always;background-image:radial-gradient(circle at 20% 30%,rgba(155,42,31,.015) 0,transparent 50%),radial-gradient(circle at 80% 70%,rgba(168,132,61,.02) 0,transparent 40%);overflow:hidden}
.slide__inner{max-width:960px;width:100%;margin:0 auto;position:relative;z-index:1}
.slide--cover{text-align:center;background:var(--paper-deep)}
.slide--quote::before{content:"「";position:absolute;top:40px;left:60px;font-family:var(--font-display);font-size:clamp(180px,22vw,320px);color:var(--vermilion-wash);line-height:1;z-index:0;user-select:none;pointer-events:none}
.slide--quote::after{content:"」";position:absolute;bottom:40px;right:60px;font-family:var(--font-display);font-size:clamp(180px,22vw,320px);color:var(--vermilion-wash);line-height:1;z-index:0}
.chapter-numeral{position:absolute;top:50%;right:6%;transform:translateY(-50%);font-family:var(--font-display);font-size:clamp(180px,26vw,360px);color:var(--paper-stain);opacity:.45;line-height:1;z-index:0;font-weight:400;letter-spacing:-.04em;user-select:none}
.masthead{display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-top:4px double var(--ink);border-bottom:1px solid var(--ink);font-family:var(--font-display);font-size:13px;letter-spacing:.4em;color:var(--ink);margin-bottom:56px}
.masthead__title{font-weight:700}
.masthead__meta{color:var(--ink-fade);letter-spacing:.2em;font-size:12px}
.stamp{--size:96px;width:var(--size);height:var(--size);display:inline-flex;align-items:center;justify-content:center;background:var(--vermilion);color:var(--paper);font-family:var(--font-display);font-weight:800;font-size:calc(var(--size)*.3);letter-spacing:.04em;line-height:1.1;border-radius:3px;transform:rotate(-6deg);box-shadow:inset 0 0 0 2px var(--paper),inset 0 0 0 4px var(--vermilion);text-align:center;flex-shrink:0}
.stamp__inner{display:flex;flex-direction:column;align-items:center;gap:2px}
.stamp--small{--size:64px}
.chapter-stamp{position:absolute;bottom:12%;right:12%;z-index:2}
.eyebrow{font-family:var(--font-display);font-size:13px;font-weight:700;letter-spacing:.5em;color:var(--vermilion);margin-bottom:24px}
.hero-h1{font-family:var(--font-display);font-size:clamp(56px,8vw,120px);font-weight:800;color:var(--ink);line-height:1.08;letter-spacing:.05em;margin-bottom:32px;-webkit-text-stroke:.4px var(--vermilion-deep);text-shadow:0 2px 6px rgba(28,22,18,.08)}
.h2{font-family:var(--font-display);font-size:clamp(40px,5vw,64px);font-weight:700;color:var(--ink);line-height:1.15;letter-spacing:.04em;margin-bottom:24px}
.h3{font-family:var(--font-display);font-size:clamp(26px,3vw,36px);font-weight:700;color:var(--ink);line-height:1.25;letter-spacing:.03em;margin-bottom:20px}
.h4{font-family:var(--font-display);font-size:22px;font-weight:700;color:var(--vermilion);margin:28px 0 14px;letter-spacing:.05em}
.subtitle{font-family:var(--font-quote);font-size:clamp(20px,2vw,28px);color:var(--ink-fade);letter-spacing:.06em;line-height:1.6;margin-bottom:32px}
.lead{font-family:var(--font-body);font-size:18px;line-height:1.9;color:var(--ink-soft);margin-bottom:24px}
.body-text{font-family:var(--font-body);font-size:16px;line-height:1.9;color:var(--ink-soft);margin-bottom:16px}
.body-text strong{color:var(--vermilion);font-weight:700}
.quote-main{font-family:var(--font-quote);font-size:clamp(36px,5vw,64px);font-weight:400;color:var(--vermilion);letter-spacing:.08em;line-height:1.5;text-align:center;margin:0 auto;max-width:800px;position:relative;z-index:1}
.quote-source{font-family:var(--font-display);font-size:14px;color:var(--ink-fade);letter-spacing:.3em;text-align:center;margin-top:32px;position:relative;z-index:1}
.point-list{list-style:none;padding:0}
.point-list li{font-family:var(--font-body);font-size:16px;line-height:1.9;color:var(--ink-soft);padding:12px 0 12px 36px;position:relative;border-bottom:1px dashed var(--paper-edge)}
.point-list li:last-child{border-bottom:none}
.point-list li::before{content:"·";position:absolute;left:12px;top:8px;color:var(--vermilion);font-size:28px;font-weight:700;line-height:1.4}
.point-list--numbered{counter-reset:pli}
.point-list--numbered li::before{counter-increment:pli;content:counter(pli,cjk-decimal) "、";font-family:var(--font-display);font-size:16px;font-weight:700;color:var(--vermilion);left:0;top:12px}
.point-list--numbered li{padding-left:44px}
.pullquote{font-family:var(--font-quote);font-size:clamp(20px,1.8vw,26px);color:var(--ink);line-height:1.7;padding:16px 0 16px 28px;border-left:3px solid var(--vermilion);margin:24px 0;letter-spacing:.04em}
.cols-2{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start}
.cols-3{display:grid;grid-template-columns:repeat(3,1fr);gap:32px}
.numbered-box{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin:28px 0}
.numbered-box__item{background:var(--paper-deep);border:1px solid var(--paper-edge);border-left:3px solid var(--vermilion);padding:20px 22px}
.numbered-box__num{font-family:var(--font-numeral);font-style:italic;font-size:28px;color:var(--vermilion);display:block;margin-bottom:6px}
.numbered-box__title{font-family:var(--font-display);font-size:17px;font-weight:700;color:var(--ink);margin-bottom:6px}
.numbered-box__desc{font-family:var(--font-body);font-size:14px;color:var(--ink-fade);line-height:1.7}
.case-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:24px;margin-top:32px}
.case-card{position:relative;background:var(--paper-deep);border:1px solid var(--paper-edge);border-left:4px solid var(--vermilion);padding:32px 28px 44px 32px;cursor:pointer;transition:transform 320ms cubic-bezier(.22,1,.36,1),box-shadow 320ms cubic-bezier(.22,1,.36,1);box-shadow:var(--card-shadow);user-select:none;outline:none;text-align:left;font-family:inherit}
.case-card::before{content:"案例";position:absolute;top:-10px;left:20px;background:var(--vermilion);color:var(--paper);font-family:var(--font-display);font-size:12px;font-weight:700;letter-spacing:.3em;padding:3px 12px 3px 16px;line-height:1.4}
.case-card::after{content:"点开细读 →";position:absolute;bottom:14px;right:22px;font-family:var(--font-body);font-size:12px;color:var(--ink-fade);letter-spacing:.2em;opacity:.7;transition:opacity 200ms ease,transform 200ms ease}
.case-card__title{font-family:var(--font-display);font-size:21px;font-weight:700;color:var(--ink);margin-bottom:12px;line-height:1.35}
.case-card__excerpt{font-family:var(--font-body);font-size:14.5px;color:var(--ink-soft);line-height:1.75;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;margin-bottom:8px}
.case-card:hover,.case-card:focus-visible{transform:translateY(-4px);box-shadow:var(--card-shadow-hover);border-left-color:var(--vermilion-deep)}
.case-card:hover::after{opacity:1;transform:translateX(4px)}
.case-card:focus-visible{outline:2px solid var(--vermilion);outline-offset:4px}
.case-card[data-read="true"]{opacity:.78}
.case-card[data-read="true"]::before{content:"已读";background:var(--ink-fade)}
.case-card[data-read="true"] .case-card__title::after{content:"阅";display:inline-block;margin-left:12px;width:26px;height:26px;background:var(--vermilion);color:var(--paper);font-size:13px;font-weight:700;text-align:center;line-height:26px;transform:rotate(-8deg) translateY(-3px);vertical-align:middle;border-radius:1px;box-shadow:inset 0 0 0 1.5px var(--paper)}
.case-modal-backdrop{position:fixed;inset:0;background:var(--modal-mask);z-index:9000;opacity:0;pointer-events:none;transition:opacity 280ms ease}
.case-modal-backdrop[data-open="true"]{opacity:1;pointer-events:auto}
.case-modal{position:fixed;top:50%;left:50%;width:min(720px,calc(100vw - 48px));max-height:calc(100vh - 80px);background:var(--paper);box-shadow:0 0 0 8px var(--paper),0 0 0 9px var(--vermilion),0 30px 60px rgba(28,22,18,.4);z-index:9100;padding:56px 56px 48px;overflow-y:auto;opacity:0;transform:translate(-50%,-50%) scale(.92);pointer-events:none;transition:opacity 320ms cubic-bezier(.22,1,.36,1),transform 380ms cubic-bezier(.22,1,.36,1)}
.case-modal[data-open="true"]{opacity:1;transform:translate(-50%,-50%) scale(1);pointer-events:auto}
.case-modal__eyebrow{font-family:var(--font-display);font-size:13px;font-weight:700;letter-spacing:.5em;color:var(--vermilion);margin-bottom:18px;padding-bottom:14px;border-bottom:2px solid var(--ink);position:relative}
.case-modal__eyebrow::after{content:"";position:absolute;left:0;right:0;bottom:-6px;border-bottom:1px solid var(--ink)}
.case-modal__title{font-family:var(--font-display);font-size:clamp(26px,3vw,34px);font-weight:800;color:var(--ink);line-height:1.25;margin-bottom:12px}
.case-modal__chapter{font-family:var(--font-body);font-size:13px;color:var(--ink-fade);margin-bottom:32px;letter-spacing:.2em}
.case-modal__body{font-family:var(--font-body);font-size:16px;line-height:1.95;color:var(--ink-soft)}
.case-modal__body p{margin-bottom:1em}
.case-modal__body p.dialogue{font-family:var(--font-quote);color:var(--ink);padding:8px 0 8px 20px;border-left:3px solid var(--vermilion-light);margin:1.2em 0;font-size:17px}
.case-modal__body p.takeaway{background:var(--paper-deep);border-left:3px solid var(--vermilion);padding:14px 18px;margin:1.4em 0;color:var(--vermilion-deep);font-weight:700}
.case-modal__close{position:absolute;top:18px;right:18px;width:36px;height:36px;background:transparent;border:1.5px solid var(--ink);color:var(--ink);font-family:var(--font-display);font-size:20px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all 200ms ease;border-radius:1px;line-height:1}
.case-modal__close:hover{background:var(--vermilion);border-color:var(--vermilion);color:var(--paper);transform:rotate(90deg)}
.case-modal__seal{display:flex;justify-content:flex-end;margin-top:32px;padding-top:24px;border-top:1px dashed var(--paper-edge)}
.page-hint{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);font-family:var(--font-display);font-size:11px;color:var(--ink-fade);letter-spacing:.4em;display:flex;align-items:center;gap:12px;z-index:90;opacity:.7}
.page-hint kbd{display:inline-block;font-family:var(--font-numeral);font-size:12px;border:1px solid var(--ink-fade);padding:2px 6px;border-radius:2px;background:var(--paper-deep)}
.page-counter{position:fixed;bottom:24px;right:24px;font-family:var(--font-numeral);font-size:13px;color:var(--ink-fade);font-style:italic;letter-spacing:.1em;z-index:90}
.reveal{opacity:0;transform:translateY(24px);transition:opacity 700ms cubic-bezier(.22,1,.36,1),transform 700ms cubic-bezier(.22,1,.36,1)}
.reveal[data-visible="true"]{opacity:1;transform:translateY(0)}
.reveal-stagger > *{opacity:0;transform:translateY(20px);transition:all 500ms cubic-bezier(.22,1,.36,1)}
.reveal-stagger[data-visible="true"] > *{opacity:1;transform:translateY(0)}
.reveal-stagger[data-visible="true"] > *:nth-child(1){transition-delay:0ms}
.reveal-stagger[data-visible="true"] > *:nth-child(2){transition-delay:80ms}
.reveal-stagger[data-visible="true"] > *:nth-child(3){transition-delay:160ms}
.reveal-stagger[data-visible="true"] > *:nth-child(4){transition-delay:240ms}
.reveal-stagger[data-visible="true"] > *:nth-child(5){transition-delay:320ms}
.reveal-stagger[data-visible="true"] > *:nth-child(6){transition-delay:400ms}
@media (max-width:1024px){.slide{padding:80px 48px}.cols-2,.cols-3{grid-template-columns:1fr;gap:28px}.case-grid{grid-template-columns:repeat(2,1fr)}.chapter-numeral{font-size:220px}.topnav__chapter{padding:4px 8px;font-size:14px}}
@media (max-width:768px){html{scroll-snap-type:none}.slide{padding:64px 24px 56px;min-height:auto;padding-top:80px}.case-grid{grid-template-columns:1fr}.chapter-numeral{font-size:140px;opacity:.3}.case-modal{width:calc(100vw - 24px);max-height:92vh;padding:40px 24px 24px}.topnav{padding:0 16px}.topnav__chapters{display:none}.topnav__mobile-toggle{display:block}.page-hint{display:none}.slide--quote::before,.slide--quote::after{font-size:100px;opacity:.5}.hero-h1{font-size:48px}.quote-main{font-size:30px}}
@media (max-width:480px){.slide{padding:64px 16px 48px}.case-modal{padding:32px 18px 24px}.stamp{--size:64px}}
@media (hover:none){.case-card:hover{transform:none;box-shadow:var(--card-shadow)}.case-card:active{transform:scale(.98)}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}html{scroll-behavior:auto;scroll-snap-type:none}.reveal,.reveal-stagger > *{opacity:1;transform:none}.case-modal{transform:translate(-50%,-50%) scale(1)}}
```

## JS BLOCK（整段复制，不要改）

```js
document.addEventListener('DOMContentLoaded',()=>{
  const slides=[...document.querySelectorAll('.slide')];
  const navWrap=document.getElementById('navChapters');
  const progress=document.getElementById('progress');
  const pageCounter=document.getElementById('pageCounter');
  const total=slides.length;
  let cur=0,modalOpen=false,lastFocused=null;
  NAV_LABELS_DISPLAY.forEach((label,idx)=>{
    const btn=document.createElement('button');
    btn.className='topnav__chapter';btn.textContent=label;
    if(CHAPTERS[idx])btn.title=CHAPTERS[idx].title;
    btn.addEventListener('click',()=>{const t=slides.find(s=>parseInt(s.dataset.chapter)===idx);if(t)t.scrollIntoView({behavior:'smooth',block:'start'});});
    navWrap.appendChild(btn);
  });
  document.querySelector('.topnav__brand').addEventListener('click',()=>slides[0].scrollIntoView({behavior:'smooth'}));
  const upd=()=>{
    progress.style.width=((cur+1)/total*100)+'%';
    pageCounter.textContent=String(cur+1).padStart(2,'0')+' / '+String(total).padStart(2,'0');
    const ch=parseInt(slides[cur].dataset.chapter||'0');
    [...navWrap.children].forEach((b,i)=>b.dataset.active=(i===ch)?'true':'false');
  };
  const slideIO=new IntersectionObserver((es)=>{es.forEach(e=>{if(e.intersectionRatio>0.5){const i=slides.indexOf(e.target);if(i!==-1&&i!==cur){cur=i;upd();}}});},{threshold:[0.5]});
  slides.forEach(s=>slideIO.observe(s));
  const revealIO=new IntersectionObserver((es)=>{es.forEach(e=>{if(e.isIntersecting){e.target.setAttribute('data-visible','true');revealIO.unobserve(e.target);}});},{threshold:0.15});
  document.querySelectorAll('.reveal, .reveal-stagger').forEach(el=>revealIO.observe(el));
  const goTo=(i)=>{i=Math.max(0,Math.min(slides.length-1,i));slides[i].scrollIntoView({behavior:'smooth',block:'start'});};
  document.addEventListener('keydown',(e)=>{
    if(modalOpen){if(e.key==='Escape')closeCase();return;}
    if(['ArrowDown','ArrowRight','PageDown'].includes(e.key)){e.preventDefault();goTo(cur+1);}
    else if(e.key===' '&&document.activeElement===document.body){e.preventDefault();goTo(cur+1);}
    else if(['ArrowUp','ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();goTo(cur-1);}
    else if(e.key==='Home'){e.preventDefault();goTo(0);}
    else if(e.key==='End'){e.preventDefault();goTo(slides.length-1);}
  });
  document.getElementById('mobileToggle').addEventListener('click',()=>{
    const c=document.getElementById('navChapters');
    const on=c.style.display==='flex';
    Object.assign(c.style,on?{display:''}:{display:'flex',position:'absolute',top:'56px',right:'16px',flexDirection:'column',background:'var(--paper)',border:'1px solid var(--paper-edge)',padding:'8px',boxShadow:'0 8px 24px rgba(28,22,18,0.15)'});
  });
  const backdrop=document.getElementById('modalBackdrop');
  const modal=document.getElementById('caseModal');
  const mTitle=document.getElementById('modalTitle');
  const mCh=document.getElementById('modalChapter');
  const mBody=document.getElementById('modalBody');
  const mClose=document.getElementById('modalClose');
  const openCase=(id,el)=>{
    const d=CASES[id];if(!d)return;
    mTitle.textContent=d.title;mCh.textContent=d.chapter||'';mBody.innerHTML=d.body;modal.scrollTop=0;
    lastFocused=el;
    backdrop.dataset.open=modal.dataset.open='true';
    modalOpen=true;document.body.style.overflow='hidden';
    if(el){el.dataset.read='true';saveRead(id);}
    setTimeout(()=>mClose.focus(),320);
  };
  const closeCase=()=>{
    backdrop.dataset.open=modal.dataset.open='false';
    modalOpen=false;document.body.style.overflow='';
    if(lastFocused){lastFocused.focus();lastFocused=null;}
  };
  backdrop.addEventListener('click',closeCase);
  mClose.addEventListener('click',closeCase);
  modal.addEventListener('click',e=>e.stopPropagation());
  document.querySelectorAll('.case-card').forEach(card=>{
    card.setAttribute('tabindex','0');
    card.addEventListener('click',()=>openCase(card.dataset.caseId,card));
    card.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();openCase(card.dataset.caseId,card);}});
  });
  const KEY='html_ppt_read_'+(document.title||'default');
  const saveRead=(id)=>{try{const r=JSON.parse(localStorage.getItem(KEY)||'[]');if(!r.includes(id)){r.push(id);localStorage.setItem(KEY,JSON.stringify(r));}}catch(e){}};
  try{JSON.parse(localStorage.getItem(KEY)||'[]').forEach(id=>{const c=document.querySelector(`[data-case-id="${id}"]`);if(c)c.dataset.read='true';});}catch(e){}
  upd();
});
```

---

## CSS BLOCK · Editorial（深/浅双模，整段复制，不要改）

**使用方法**：把 `<html lang="zh-CN">` 改成 `<html lang="zh-CN" data-mode="dark">` 或 `data-mode="light"`，CSS 自动切换配色。其余结构与中国风完全一致。

```css
:root[data-mode="dark"]{--bg:#0E0E10;--bg-soft:#15151A;--bg-card:#1A1A1F;--bg-edge:#26262E;--ink:#F4F1EA;--ink-soft:#C8C3B8;--ink-fade:#7A766D;--accent:#D14B3A;--accent-soft:#A33828;--accent-wash:rgba(209,75,58,.14);--quote:#E8E2D2;--rule:rgba(244,241,234,.12);--rule-strong:rgba(244,241,234,.28);--modal-mask:rgba(0,0,0,.78);--card-shadow:0 1px 0 rgba(244,241,234,.05),0 12px 32px rgba(0,0,0,.35);--card-shadow-hover:0 1px 0 var(--accent),0 18px 40px rgba(209,75,58,.25)}
:root[data-mode="light"]{--bg:#E8E4DC;--bg-soft:#EFEBE2;--bg-card:#F2EFE6;--bg-edge:#D8D3C6;--ink:#15140F;--ink-soft:#3A372E;--ink-fade:#7D7868;--accent:#9B2A1F;--accent-soft:#7A1F17;--accent-wash:rgba(155,42,31,.08);--quote:#1C1A14;--rule:rgba(21,20,15,.16);--rule-strong:rgba(21,20,15,.36);--modal-mask:rgba(21,20,15,.55);--card-shadow:0 1px 0 var(--bg-edge),0 8px 20px rgba(21,20,15,.08);--card-shadow-hover:0 2px 0 var(--accent),0 14px 32px rgba(155,42,31,.18)}
:root{--font-display:"Source Han Serif SC","Noto Serif CJK SC","Songti SC","STSong","SimSun",serif;--font-body:"Source Han Serif SC","Noto Serif CJK SC","Songti SC","STSong",serif;--font-quote:"Source Han Serif SC","Songti SC","STSong",serif;--font-en:"GT Sectra","Tiempos Headline","Charter","Georgia","Times New Roman",serif;--font-en-italic:"GT Sectra","Tiempos Headline","Charter","Georgia",serif;--font-mono:"JetBrains Mono","SF Mono","Menlo","Consolas",monospace}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;scroll-snap-type:y mandatory;overflow-y:scroll;background:var(--bg)}
body{font-family:var(--font-body);color:var(--ink-soft);background:var(--bg);font-size:16px;line-height:1.8;-webkit-font-smoothing:antialiased;font-feature-settings:"kern" 1,"liga" 1}
.topnav{position:fixed;top:0;left:0;right:0;height:48px;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--rule);z-index:100;display:flex;align-items:center;padding:0 40px;font-family:var(--font-en);font-size:11px;letter-spacing:.32em;text-transform:uppercase}
.topnav__brand{font-weight:500;color:var(--ink);margin-right:auto;cursor:pointer;font-style:italic;letter-spacing:.18em;text-transform:none}
.topnav__chapters{display:flex;gap:2px;align-items:center}
.topnav__chapter{background:transparent;border:1px solid transparent;padding:5px 11px;font:inherit;color:var(--ink-fade);cursor:pointer;letter-spacing:.3em;transition:all 200ms ease;font-family:var(--font-en);font-style:italic;font-size:13px;text-transform:none}
.topnav__chapter:hover{color:var(--ink)}
.topnav__chapter[data-active="true"]{color:var(--accent);border-bottom:1px solid var(--accent)}
.topnav__progress{position:absolute;left:0;bottom:-1px;height:1px;background:var(--accent);width:0%;transition:width 240ms ease}
.topnav__mobile-toggle{display:none;background:none;border:none;font-family:var(--font-en);font-size:13px;color:var(--ink);cursor:pointer;padding:6px 10px;letter-spacing:.2em}
.slide{min-height:100vh;padding:88px 96px;display:flex;flex-direction:column;justify-content:center;position:relative;background:var(--bg);scroll-snap-align:start;scroll-snap-stop:always;overflow:hidden}
.slide__inner{max-width:1120px;width:100%;margin:0 auto;position:relative;z-index:1}
.slide--cover{justify-content:center}
.slide--quote{justify-content:center;text-align:left}
.act-marker{position:absolute;top:64px;left:96px;font-family:var(--font-en);font-size:11px;letter-spacing:.42em;color:var(--ink-fade);text-transform:uppercase;z-index:2}
.act-marker em{font-style:normal;color:var(--accent);margin-right:10px}
.act-numeral{position:absolute;bottom:-4%;right:-2%;font-family:var(--font-en-italic);font-style:italic;font-size:clamp(220px,32vw,460px);color:var(--ink);opacity:.06;line-height:.85;z-index:0;user-select:none;letter-spacing:-.04em}
.masthead{display:flex;align-items:baseline;justify-content:space-between;padding:14px 0;border-top:1px solid var(--rule-strong);border-bottom:1px solid var(--rule);font-family:var(--font-en);font-size:11px;letter-spacing:.42em;color:var(--ink-fade);margin-bottom:80px;text-transform:uppercase}
.masthead__title{font-weight:500;color:var(--ink);letter-spacing:.32em}
.masthead__meta{letter-spacing:.28em}
.eyebrow{font-family:var(--font-en);font-size:11px;font-weight:500;letter-spacing:.42em;color:var(--accent);margin-bottom:32px;text-transform:uppercase}
.eyebrow em{font-style:italic;color:var(--ink-fade);margin-right:8px}
.hero-h1{font-family:var(--font-display);font-size:clamp(64px,9vw,140px);font-weight:600;color:var(--ink);line-height:1;letter-spacing:-.02em;margin-bottom:40px}
.hero-h1 em{font-family:var(--font-en-italic);font-style:italic;font-weight:500;color:var(--ink);letter-spacing:-.01em}
.h2{font-family:var(--font-display);font-size:clamp(48px,6.5vw,96px);font-weight:600;color:var(--ink);line-height:1.04;letter-spacing:-.02em;margin-bottom:28px}
.h2 em{font-family:var(--font-en-italic);font-style:italic;font-weight:500;color:var(--ink)}
.h3{font-family:var(--font-display);font-size:clamp(30px,3.6vw,46px);font-weight:600;color:var(--ink);line-height:1.18;letter-spacing:-.015em;margin-bottom:24px}
.h4{font-family:var(--font-display);font-size:22px;font-weight:600;color:var(--ink);margin:32px 0 14px;letter-spacing:-.01em}
.subtitle{font-family:var(--font-body);font-size:clamp(18px,1.7vw,22px);color:var(--ink-soft);letter-spacing:.01em;line-height:1.55;margin-bottom:40px;max-width:780px;font-weight:400}
.lead{font-family:var(--font-body);font-size:17px;line-height:1.85;color:var(--ink-soft);margin-bottom:24px;max-width:760px}
.body-text{font-family:var(--font-body);font-size:16px;line-height:1.85;color:var(--ink-soft);margin-bottom:16px;max-width:760px}
.body-text strong{color:var(--ink);font-weight:600}
.quote-main{font-family:var(--font-display);font-size:clamp(34px,4.4vw,60px);font-weight:500;color:var(--quote);letter-spacing:-.015em;line-height:1.3;margin:0;max-width:900px;position:relative;z-index:1}
.quote-main em{font-family:var(--font-en-italic);font-style:italic;font-weight:500}
.quote-main::before{content:"\201C";font-family:var(--font-en);color:var(--ink-fade);margin-right:.1em;opacity:.6}
.quote-main::after{content:"\201D";font-family:var(--font-en);color:var(--ink-fade);margin-left:.1em;opacity:.6}
.quote-source{font-family:var(--font-en);font-size:11px;color:var(--ink-fade);letter-spacing:.4em;margin-top:36px;position:relative;z-index:1;text-transform:uppercase}
.quote-source em{font-style:italic;color:var(--accent);margin-right:10px}
.bottom-quote{margin-top:64px;padding:20px 24px;border-left:2px solid var(--accent);background:var(--accent-wash);font-family:var(--font-quote);font-size:17px;color:var(--ink);line-height:1.7;max-width:820px}
.bottom-quote::before{content:"\201C ";color:var(--accent);font-weight:600}
.bottom-quote::after{content:" \201D";color:var(--accent);font-weight:600}
.point-list{list-style:none;padding:0;max-width:760px}
.point-list li{font-family:var(--font-body);font-size:16px;line-height:1.85;color:var(--ink-soft);padding:14px 0 14px 32px;position:relative;border-bottom:1px solid var(--rule)}
.point-list li:last-child{border-bottom:none}
.point-list li::before{content:"";position:absolute;left:0;top:24px;width:14px;height:1px;background:var(--accent)}
.point-list--numbered{counter-reset:pli;padding-left:0}
.point-list--numbered li{padding-left:54px}
.point-list--numbered li::before{counter-increment:pli;content:counter(pli,decimal-leading-zero);font-family:var(--font-en);font-style:italic;font-size:14px;font-weight:500;color:var(--accent);left:0;top:14px;width:auto;height:auto;background:none;letter-spacing:.05em}
.pullquote{font-family:var(--font-display);font-size:clamp(22px,2vw,28px);color:var(--ink);line-height:1.55;padding:8px 0 8px 28px;border-left:2px solid var(--accent);margin:32px 0;max-width:820px;font-weight:500}
.pullquote em{font-family:var(--font-en-italic);font-style:italic}
.cols-2{display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:start;margin-top:8px}
.cols-3{display:grid;grid-template-columns:repeat(3,1fr);gap:48px;margin-top:40px}
.col-block .col-block__label{font-family:var(--font-en);font-size:11px;letter-spacing:.42em;color:var(--ink-fade);margin-bottom:18px;text-transform:uppercase}
.col-block .col-block__label em{font-style:italic;color:var(--accent);margin-right:8px}
.col-block .col-block__num{font-family:var(--font-en-italic);font-style:italic;font-size:11px;color:var(--accent);letter-spacing:.2em;margin-bottom:12px;display:block}
.col-block .col-block__title{font-family:var(--font-display);font-size:22px;font-weight:600;color:var(--ink);line-height:1.3;margin-bottom:12px;letter-spacing:-.01em}
.col-block .col-block__desc{font-family:var(--font-body);font-size:14.5px;line-height:1.7;color:var(--ink-soft)}
.bignum-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:48px;margin:40px 0}
.bignum{position:relative}
.bignum__label{font-family:var(--font-en);font-size:11px;letter-spacing:.42em;color:var(--ink-fade);margin-bottom:18px;text-transform:uppercase}
.bignum__value{font-family:var(--font-display);font-size:clamp(56px,6.5vw,88px);font-weight:600;color:var(--ink);line-height:.95;letter-spacing:-.03em;margin-bottom:14px}
.bignum__value em{font-family:var(--font-en-italic);font-style:italic}
.bignum__desc{font-family:var(--font-body);font-size:14px;line-height:1.7;color:var(--ink-soft);max-width:280px}
.case-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:24px;margin-top:40px}
.case-card{position:relative;background:var(--bg-card);border:1px solid var(--bg-edge);border-left:2px solid var(--accent);padding:28px 28px 44px 30px;cursor:pointer;transition:transform 280ms cubic-bezier(.22,1,.36,1),box-shadow 280ms cubic-bezier(.22,1,.36,1),border-color 280ms ease;box-shadow:var(--card-shadow);user-select:none;outline:none;text-align:left;font-family:inherit}
.case-card::before{content:"CASE";position:absolute;top:14px;right:20px;font-family:var(--font-en);font-size:10px;font-weight:500;letter-spacing:.4em;color:var(--ink-fade);text-transform:uppercase}
.case-card::after{content:"Read →";position:absolute;bottom:14px;right:24px;font-family:var(--font-en-italic);font-style:italic;font-size:12px;color:var(--ink-fade);letter-spacing:.05em;opacity:.7;transition:opacity 200ms ease,transform 200ms ease,color 200ms ease}
.case-card__title{font-family:var(--font-display);font-size:21px;font-weight:600;color:var(--ink);margin-bottom:14px;line-height:1.3;letter-spacing:-.01em;padding-right:60px}
.case-card__excerpt{font-family:var(--font-body);font-size:14.5px;color:var(--ink-soft);line-height:1.7;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;margin-bottom:8px}
.case-card:hover,.case-card:focus-visible{transform:translateY(-2px);box-shadow:var(--card-shadow-hover);border-left-color:var(--accent);border-color:var(--rule-strong)}
.case-card:hover::after{opacity:1;transform:translateX(4px);color:var(--accent)}
.case-card:focus-visible{outline:1px solid var(--accent);outline-offset:4px}
.case-card[data-read="true"]{opacity:.6}
.case-card[data-read="true"]::before{content:"READ"}
.case-modal-backdrop{position:fixed;inset:0;background:var(--modal-mask);z-index:9000;opacity:0;pointer-events:none;transition:opacity 280ms ease;backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px)}
.case-modal-backdrop[data-open="true"]{opacity:1;pointer-events:auto}
.case-modal{position:fixed;top:50%;left:50%;width:min(760px,calc(100vw - 48px));max-height:calc(100vh - 80px);background:var(--bg-soft);border:1px solid var(--rule-strong);box-shadow:0 30px 80px rgba(0,0,0,.55);z-index:9100;padding:56px 60px 48px;overflow-y:auto;opacity:0;transform:translate(-50%,-50%) scale(.96);pointer-events:none;transition:opacity 320ms cubic-bezier(.22,1,.36,1),transform 380ms cubic-bezier(.22,1,.36,1)}
.case-modal[data-open="true"]{opacity:1;transform:translate(-50%,-50%) scale(1);pointer-events:auto}
.case-modal__eyebrow{font-family:var(--font-en);font-size:11px;font-weight:500;letter-spacing:.42em;color:var(--accent);margin-bottom:18px;padding-bottom:14px;border-bottom:1px solid var(--rule-strong);text-transform:uppercase}
.case-modal__title{font-family:var(--font-display);font-size:clamp(28px,3vw,38px);font-weight:600;color:var(--ink);line-height:1.18;margin-bottom:12px;letter-spacing:-.015em}
.case-modal__chapter{font-family:var(--font-en-italic);font-style:italic;font-size:13px;color:var(--ink-fade);margin-bottom:32px;letter-spacing:.08em}
.case-modal__body{font-family:var(--font-body);font-size:16px;line-height:1.9;color:var(--ink-soft)}
.case-modal__body p{margin-bottom:1em}
.case-modal__body p.dialogue{font-family:var(--font-quote);color:var(--ink);padding:8px 0 8px 20px;border-left:2px solid var(--accent);margin:1.2em 0;font-size:17px;font-weight:500}
.case-modal__body p.takeaway{background:var(--accent-wash);border-left:2px solid var(--accent);padding:16px 20px;margin:1.4em 0;color:var(--ink);font-weight:500}
.case-modal__close{position:absolute;top:18px;right:18px;width:34px;height:34px;background:transparent;border:1px solid var(--rule-strong);color:var(--ink-soft);font-family:var(--font-en);font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all 200ms ease;line-height:1}
.case-modal__close:hover{background:var(--accent);border-color:var(--accent);color:#fff;transform:rotate(90deg)}
.case-modal__seal{display:none}
.page-hint{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);font-family:var(--font-en);font-size:10px;color:var(--ink-fade);letter-spacing:.42em;display:flex;align-items:center;gap:12px;z-index:90;opacity:.65;text-transform:uppercase}
.page-hint kbd{display:inline-block;font-family:var(--font-en);font-size:11px;border:1px solid var(--rule-strong);padding:2px 6px;background:var(--bg-card);color:var(--ink-soft);letter-spacing:0}
.page-counter{position:fixed;bottom:20px;right:32px;font-family:var(--font-en-italic);font-style:italic;font-size:12px;color:var(--ink-fade);letter-spacing:.08em;z-index:90}
.page-counter em{font-style:normal;color:var(--accent);margin:0 6px}
.reveal{opacity:0;transform:translateY(20px);transition:opacity 800ms cubic-bezier(.22,1,.36,1),transform 800ms cubic-bezier(.22,1,.36,1)}
.reveal[data-visible="true"]{opacity:1;transform:translateY(0)}
.reveal-stagger > *{opacity:0;transform:translateY(18px);transition:all 540ms cubic-bezier(.22,1,.36,1)}
.reveal-stagger[data-visible="true"] > *{opacity:1;transform:translateY(0)}
.reveal-stagger[data-visible="true"] > *:nth-child(1){transition-delay:0ms}
.reveal-stagger[data-visible="true"] > *:nth-child(2){transition-delay:90ms}
.reveal-stagger[data-visible="true"] > *:nth-child(3){transition-delay:180ms}
.reveal-stagger[data-visible="true"] > *:nth-child(4){transition-delay:270ms}
.reveal-stagger[data-visible="true"] > *:nth-child(5){transition-delay:360ms}
.reveal-stagger[data-visible="true"] > *:nth-child(6){transition-delay:450ms}
@media (max-width:1024px){.slide{padding:80px 56px}.cols-2,.cols-3{grid-template-columns:1fr;gap:36px}.case-grid{grid-template-columns:repeat(2,1fr)}.act-marker{left:56px;top:60px}.act-numeral{font-size:220px}.topnav__chapter{padding:4px 8px;font-size:12px}}
@media (max-width:768px){html{scroll-snap-type:none}.slide{padding:72px 24px 56px;min-height:auto;padding-top:84px}.case-grid{grid-template-columns:1fr}.bignum-grid{grid-template-columns:1fr;gap:32px}.act-numeral{font-size:140px;opacity:.04}.case-modal{width:calc(100vw - 24px);max-height:92vh;padding:40px 24px 24px}.topnav{padding:0 16px}.topnav__chapters{display:none}.topnav__mobile-toggle{display:block}.page-hint{display:none}.hero-h1{font-size:54px}.h2{font-size:42px}.quote-main{font-size:30px}.act-marker{left:24px;top:60px;font-size:10px}}
@media (max-width:480px){.slide{padding:72px 18px 48px}.case-modal{padding:32px 20px 24px}}
@media (hover:none){.case-card:hover{transform:none;box-shadow:var(--card-shadow)}.case-card:active{transform:scale(.98)}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}html{scroll-behavior:auto;scroll-snap-type:none}.reveal,.reveal-stagger > *{opacity:1;transform:none}.case-modal{transform:translate(-50%,-50%) scale(1)}}
```

## Editorial 主题专属 Slide 示例（复用即可）

```html
<!-- Editorial 封面 -->
<section class="slide slide--cover" data-chapter="0">
  <div class="slide__inner">
    <div class="masthead"><span class="masthead__title">DOCUMENT TITLE</span><span class="masthead__meta">2026 · A NOTE</span></div>
    <p class="eyebrow reveal"><em>·</em>A Personal Note</p>
    <h1 class="hero-h1 reveal">主标题<br/><em>can be italic</em></h1>
    <p class="subtitle reveal">副标题用克制的灰字，留白比花哨更高级。</p>
  </div>
</section>

<!-- Editorial 章节首页 -->
<section class="slide" data-chapter="1">
  <div class="act-marker"><em>ACT I</em>· THE EVOLUTION</div>
  <div class="act-numeral">I</div>
  <div class="slide__inner">
    <p class="eyebrow reveal"><em>01</em>开场</p>
    <h2 class="h2 reveal">三年里脚手架没有消失——<br/>它只是<em>换了名字</em>。</h2>
    <p class="subtitle reveal">从 RAG Chains 到 LangGraph，再到今天的 Claude Code / Codex / Deep Agents。</p>
  </div>
</section>

<!-- Editorial 金句屏 -->
<section class="slide slide--quote" data-chapter="1">
  <div class="act-marker"><em>ACT I</em>· HARNESSES AREN'T GOING AWAY</div>
  <div class="slide__inner">
    <p class="eyebrow reveal"><em>·</em>核心论点</p>
    <p class="quote-main reveal">即使是做出全球最强模型的公司，也在疯狂投资 harness。Harness 不会消失，它只会变换形态。</p>
    <p class="quote-source reveal"><em>—</em>Harrison Chase</p>
  </div>
</section>

<!-- Editorial 大数字栏 -->
<section class="slide" data-chapter="1">
  <div class="slide__inner">
    <p class="eyebrow reveal"><em>02</em>数据切片</p>
    <h3 class="h3 reveal">当 <em>Claude Code</em> 源码泄露，<br/>人们数了一下行数。</h3>
    <div class="bignum-grid reveal-stagger">
      <div class="bignum">
        <div class="bignum__label">Leaked Codebase</div>
        <div class="bignum__value">512,000<em>行</em></div>
        <div class="bignum__desc">Claude Code 被泄露的代码量，几乎全是 harness 本身，而不是"模型"。</div>
      </div>
      <div class="bignum">
        <div class="bignum__label">Investment From</div>
        <div class="bignum__value">3<em>家</em></div>
        <div class="bignum__desc">全球最强模型提供商——OpenAI / Anthropic / Google——都在重仓押注 harness。</div>
      </div>
      <div class="bignum">
        <div class="bignum__label">Part of "the model"</div>
        <div class="bignum__value">0<em>%</em></div>
        <div class="bignum__desc">Web search、工具调用、agent 编排，都不是模型，而是 harness 在协调。</div>
      </div>
    </div>
    <p class="bottom-quote">即使是做出全球最强模型的公司，也在疯狂投资 harness。</p>
  </div>
</section>

<!-- Editorial 双栏对比 -->
<section class="slide" data-chapter="2">
  <div class="act-marker"><em>ACT II</em>· LATENT VS DETERMINISTIC</div>
  <div class="slide__inner">
    <p class="eyebrow reveal"><em>·</em>我的两个工作面</p>
    <h2 class="h2 reveal"><em>Latent</em> 留给我 · <em>Deterministic</em> 交给 AI。</h2>
    <div class="cols-2 reveal-stagger" style="margin-top:48px">
      <div class="col-block">
        <div class="col-block__label"><em>Latent</em>· 判断态</div>
        <h3 class="col-block__title">留给我自己</h3>
        <ul class="point-list">
          <li><strong>判断</strong>——什么值得写</li>
          <li><strong>定调</strong>——观点与情绪</li>
          <li><strong>质检</strong>——最后一道把关</li>
        </ul>
        <p class="col-block__desc" style="margin-top:18px">同样的输入 → 不同的结果。需要品味、上下文、校衡。</p>
      </div>
      <div class="col-block">
        <div class="col-block__label"><em>Deterministic</em>· 执行态</div>
        <h3 class="col-block__title">交给 AI / 自动化</h3>
        <ul class="point-list">
          <li>写初稿 · 格式变形</li>
          <li>信息图生成 · 数据抓取</li>
          <li>多平台分发 · 同步发布</li>
        </ul>
        <p class="col-block__desc" style="margin-top:18px">同样的输入 → 结果必须一致。规则化、可重复、可验证。</p>
      </div>
    </div>
    <p class="bottom-quote">AI 最常见的翻车，是把精确执行题交给了会做梦的模型。</p>
  </div>
</section>
```

**Editorial 主题与中国风的关键差别**：
- 章序号水印用 `.act-numeral`（巨型 I/II/III 斜体半透明 6% 不透明度），**不要朱砂印章**
- 章节标识用 `.act-marker`（左上角 `ACT I · THE EVOLUTION` 小字），**不要章节戳印**
- 西文用斜体衬线（`<em>` 标签）做强调，是这套主题的灵魂
- 案例卡片右上角是 `CASE` 小字，**不是朱砂"案例"角标**

## 章节标识对照表

| 章 | 中国风（印章+大字） | Editorial（ACT 小字+巨型水印） |
|---|---|---|
| 1 | 壹章 / 壹 | ACT I · 章节英文名 / I |
| 2 | 贰章 / 贰 | ACT II · 章节英文名 / II |
| 3 | 叁章 / 叁 | ACT III · 章节英文名 / III |
| 4 | 肆章 / 肆 | ACT IV · 章节英文名 / IV |
| 5 | 伍章 / 伍 | ACT V · 章节英文名 / V |

---

## 提速规则（给执行此 skill 的 Claude）

- ✅ **第一步必做**：用 AskUserQuestion 弹"主题方向"框；如选 Editorial，再弹一次"配色模式"框
- ❌ **不要**反复读 PDF、不要写 DESIGN.md、不要在弹框前问其他问题
- ✅ **直接 Write 整个 index.html**：选定主题对应的 CSS BLOCK + JS BLOCK 整段复制，不要重新生成、不要逐行思考
- ✅ Editorial 主题别忘了 `<html lang="zh-CN" data-mode="dark">` 或 `data-mode="light"`
- ✅ 思考时间只花在内容（slide 文本 + CASES 字典），不要花在样式
- ✅ 每次任务的合理时间：8-15 分钟（PDF 4-9 页规模）。超过 20 分钟说明出问题，停下来报告
