# html-ppt-from-source

> 一个 [Claude Code](https://claude.com/claude-code) Skill —— 把 PDF / Markdown / 纯文本源文档转成**双击即看**的单 HTML 版 PPT。

零外链、零依赖、纯系统字体。两套主题二选一：

- **中国风 · 报纸金句风** —— 米黄底 + 朱砂红 + 宋体 + 印章。适合课程讲义、文化 / 教育 / 出版类内容。
- **Editorial · 知识工作者风** —— 衬线巨字 + 极简留白 + 西文斜体强调，深 / 浅双模。适合发布会、技术深稿、白皮书、个人简历。

自带可点击案例卡片 + 中心弹窗、scroll-snap 翻页、键盘导航、已读状态持久化。

---

## 它能做什么

把这样的输入：

```
📄 课程讲义.pdf
📄 学员故事.md
📄 案例集.txt
```

一次性变成这样的输出：

```
📦 index.html  ← 单文件，双击即看
```

成品 HTML 自动包含：

- 一份源文件 = 一个一级章节，按你给的顺序排
- "案例 / 学员分享 / 故事 / 含人物对话" 段落自动识别为可点击卡片
- 顶部导航 + 进度条 + 翻页提示 + 页码计数
- 中心弹窗细读、ESC 关闭、已读状态 localStorage 持久化
- 响应式适配 + `prefers-reduced-motion` 友好

---

## 安装

### 前置条件

- 安装了 [Claude Code](https://claude.com/claude-code)
- macOS / Linux / WSL（脚本路径用 `~`，Windows 原生需自行调整）

### 方式一：直接 clone 到 Claude Code skills 目录

```bash
git clone https://github.com/qingchaowang0410-pixel/html-ppt-from-source.git \
  ~/.claude/skills/html-ppt-from-source
```

### 方式二：先 clone 到任意位置再软链

```bash
git clone https://github.com/qingchaowang0410-pixel/html-ppt-from-source.git
ln -s "$(pwd)/html-ppt-from-source/.claude/skills/html-ppt-from-source" \
  ~/.claude/skills/html-ppt-from-source
```

> ⚠️ **路径必须叫 `~/.claude/skills/html-ppt-from-source/`**。
> SKILL.md 内部引用了 `~/.claude/skills/html-ppt-from-source/scripts/t2s_safe.py`，
> 改名后繁→简兜底脚本会找不到。

### 验证安装

打开 Claude Code，新开一个会话，输入：

```
帮我把这份 PDF 做成 HTML PPT
```

如果触发器生效，Claude 会先弹一个主题选择框（"中国风" / "Editorial"），就说明 skill 装好了。

---

## 使用

把源文档（PDF / MD / TXT，多份也行）拖给 Claude Code，说一句：

> "把这些做成 HTML PPT"

接下来：

1. Claude 弹框问你**主题方向**（中国风 / Editorial）
2. 如果选 Editorial，再弹一次**配色模式**（深色 / 浅色）
3. 8 ~ 15 分钟后产出 `index.html`（PDF 4 ~ 9 页规模）

成品在当前目录，双击浏览器打开即可。键盘 ↑ ↓ / Space / PgUp / PgDn / Home / End 翻页，ESC 关闭案例弹窗。

### 触发词

任意一句都行：

- 把这些 PDF 做成 HTML PPT
- 做一份 HTML 课件
- 生成 HTML 演示文稿

---

## 可选依赖

只有当**源文档含繁体**，或希望模型可能输出的繁体被自动归一到简体时，才需要：

```bash
pip3 install --user zhconv
```

或：

```bash
pip3 install --user -r ~/.claude/skills/html-ppt-from-source/scripts/requirements.txt
```

> 脚本 `t2s_safe.py` 在缺失 `zhconv` 时也会尝试自动 `pip install --user`，
> 上面这步只是为了离线环境或权限受限时显式准备。

`t2s_safe.py` 在标准 `zhconv` 基础上额外保护：

- 「」直角引号（中国风主题的视觉签名，zhconv 默认会转成弯引号）
- 壹贰叁肆伍陆柒捌玖 大写数字（章序号 / 印章用，zhconv 默认会转成简体一二三）

---

## 文件结构

```
.
├── README.md
├── LICENSE
├── .gitignore
└── .claude/
    └── skills/
        └── html-ppt-from-source/
            ├── SKILL.md                ← skill 主文件（含两套主题 CSS + JS 整段）
            └── scripts/
                ├── t2s_safe.py         ← 安全繁→简转换（可选）
                └── requirements.txt    ← t2s_safe.py 依赖
```

`SKILL.md` 是单一真相源 —— 主题 CSS、JS 骨架、Slide 模板、CASES 字典格式、章节标识对照表全都在里面。Claude 会按主题选择对应的 CSS BLOCK 整段复制，不重新生成样式。

---

## 设计原则

- **零外链** —— 不引 Google Fonts、不引 CDN、不引 CSS 框架。`file://` 协议下完整可用。
- **纯系统字体** —— 中国风走 Songti SC / Kaiti SC，Editorial 走 Source Han Serif SC / Georgia。
- **两套主题，不要更多** —— 多了反而难选。两套已经覆盖大多数中文长内容场景。
- **样式与内容解耦** —— Claude 只在内容（slide 文本 + CASES 字典）上花思考时间，样式整段复制。
- **可读优先** —— scroll-snap 翻页、案例卡片 + 弹窗细读、已读状态持久化，都为长内容服务。

---

## 贡献

欢迎提 Issue 和 PR。改样式之前请先确认：

- 改完后单 HTML 文件 `grep -cE '@import|<link[^>]+href=|<script[^>]+src='` 仍为 0
- `<section ` 开闭仍相等
- 提取 `<script>` 内联 JS 跑 `node --check` 仍通过

这三个自检在 SKILL.md 的第 3 步里有现成命令。

---

## License

[MIT](./LICENSE) © 2026 qingchaowang0410-pixel
