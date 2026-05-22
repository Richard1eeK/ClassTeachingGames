# AI 修改记录 - CHANGELOG_AI

> 这里记录 AI 实际改了哪些文件、为什么改、如何验证。
> 一行一行的 diff 见 git，本文档关注"做了什么 / 跑过什么 / 留了什么坑"。

---

## 2026-05-22

### v2.1 — 双语帮助说明

**目标**：在设置页增加简单易懂的说明书入口，帮助老师理解如何设置游戏、导入题目和游玩；支持中英文切换。

**新建文件**：
- `docs/superpowers/specs/2026-05-22-v21-bilingual-help-guide-design.md` — v2.1 双语帮助说明设计记录

**改造文件**：
- `game/settings.py` — 新增 `Need Help? ->` + `i` 入口、帮助弹窗、`EN` / `中文` 切换、`Esc` / `X` 关闭
- `game/ui_components.py` — `get_font` 检测中文时优先选择系统中文字体，避免说明弹窗显示方块字
- `game/icons.py` — 新增几何绘制 `draw_info` 图标
- `docs/PROJECT_STATE.md` / `docs/DECISIONS.md` / `docs/CHANGELOG_AI.md` — 记录 v2.1 状态、决策和验证

**验证**：
- `python3 -m compileall main.py game` 通过
- `SDL_VIDEODRIVER=dummy /tmp/pgvenv/bin/python <help preview script>` 通过
- 已导出 Settings 入口、英文帮助弹窗、中文帮助弹窗预览图并检查无明显重叠
- Windows 端仍需用户 `git pull` + `build.bat` 实测中文字体、点击交互和 exe 真实窗口

---

### v2.0 — Shell Cup Game 游戏图标

**目标**：按用户要求采用可爱方向，为 Shell Cup Game 生成并接入正式游戏图标。

**新建文件**：
- `assets/images/shell_cup_game_icon.png` — 可爱暖色游戏图标 PNG，用于 Pygame 窗口图标
- `assets/images/shell_cup_game.ico` — Windows exe 图标，包含 16/32/48/64/128/256 多尺寸

**改造文件**：
- `main.py` — 启动时通过 `resource_path` 加载 PNG 并设置窗口图标
- `build.bat` — PyInstaller 增加 `--icon "assets\images\shell_cup_game.ico"`
- `docs/PROJECT_STATE.md` / `docs/DECISIONS.md` / `docs/CHANGELOG_AI.md` — 记录 v2.0 状态、决策和验证

**验证**：
- PNG / ICO 文件格式检查通过
- `python3 -m compileall main.py game` 通过
- Windows 端仍需用户 `git pull` + `build.bat` 实测 exe 图标和窗口图标

---

### 文档收尾 — 更新项目长期记忆和当前状态

**目标**：按用户要求总结今天主要改动、技术决策、当前项目状态、未完成问题和开发偏好；只更新文档，不继续开发新功能。

**改造文件**：
- `CLAUDE.md` — 更新项目定位、目录结构、PyInstaller 资源说明、当前玩法规则、TODO 和用户协作偏好
- `docs/PROJECT_STATE.md` — 更新当前状态，补充 `AGENTS.md` 未跟踪且待确认
- `docs/DECISIONS.md` — 新增 D-016，记录未确认用途的新文件不随功能提交
- `docs/CHANGELOG_AI.md` — 记录本次文档收尾

**未改动**：
- 未开发新功能
- 未提交 `AGENTS.md`，其内容和用途待确认

---

### v1.9.1 — 多答案设置页改为 Answers/Cups 双滑杆

**目标**：修正 v1.9 三卡设置入口显示不完整且不符合用户期望的问题。用户明确要求上方滑杆调 Answers（1-5），下方滑杆调 Cups；Answers 变化时 Cups 自动至少为 Answers + 2，但 Cups 可以手动调更多。

**改造文件**：
- `game/settings.py` — 用 `Answers` / `Cups` 两条滑杆替代三卡 Correct Answers；Answers 变化时 Cups 自动同步到合法最小值
- `game/shell_game.py` — 使用设置页传入的 `num_cups`，不再强制 `num_cups = answer_count + 2`
- `docs/superpowers/specs/2026-05-22-v19-multi-answer-normal-mode-design.md` — 更新设计说明
- `docs/PROJECT_STATE.md` / `docs/DECISIONS.md` / `docs/CHANGELOG_AI.md` — 更新 v1.9.1 状态和决策

**验证**：
- Settings preview 已导出，确认四条滑杆完整显示
- Answers/Cups 联动 smoke 通过：Cups 不低于 Answers + 2，且可保持更高值
- Gameplay smoke 通过：1/3/5 Answers + 自定义 Cups 路径可正常创建目标和判分
- `python3 -m compileall main.py game` 通过

---

### v1.9 — 多答案 Normal 模式

**目标**：新增 1/2/3 个正确答案的玩法；杯子数量初版按答案数量 + 2 派生；先做 Normal 规则，即有 N 个答案就有 N 次点击机会，选满后统一判定。

**新建文件**：
- `docs/superpowers/specs/2026-05-22-v19-multi-answer-normal-mode-design.md` — v1.9 多答案 Normal 模式设计说明

**改造文件**：
- `game/settings.py` — 将 Cups 滑块替换为初版 `Correct Answers` 三选一卡片：`1 Ans / 3 Cups`、`2 Ans / 4 Cups`、`3 Ans / 5 Cups`（后续 v1.9.1 已改为双滑杆）
- `game/shell_game.py` — 每回合选择 N 个 target items 和 N 个 target cups；支持 N 次点击后统一判分；更新多答案提示文案和选中高亮
- `game/animations.py` — 新增 `MultiIntroBall`，并排展示多个目标；多目标展示淡出后再盖杯/洗牌，避免答案泄露
- `docs/PROJECT_STATE.md` / `docs/DECISIONS.md` / `docs/CHANGELOG_AI.md` — 记录 v1.9 状态、决策和验证

**验证**：
- 导入兼容检查通过：v1.7 TXT 和 v1.8 图片文件夹扫描仍可用
- Settings smoke 通过：1/2/3 Answers 分别返回 3/4/5 Cups
- Gameplay smoke 通过：1/2/3 Answers 全对路径 + 2 Answers 选错路径
- 多目标 intro 卡片泄露检查通过：展示淡出后才进入盖杯/洗牌
- `python3 -m compileall main.py game` 通过
- 已导出 Settings / multi-target intro / guessing 预览图检查视觉
- Windows 端仍需用户 `git pull` + `build.bat` 实测 exe 真实交互

---

## 2026-05-21

### v1.8 — 图片文件夹导入

**目标**：用户希望把图片都放进一个文件夹，然后点击导入到游戏内自动识别。明确不做拖入，先做点击按钮选择文件夹。

**改造文件**：
- `game/question_bank.py` — 新增 `scan_image_folder`，识别 `.png` / `.jpg` / `.jpeg` / `.bmp` / `.gif` 并生成 image items
- `game/settings.py` — 将原单张 `Image` 入口改为 `Folder`，使用 tkinter `askdirectory()` 选择文件夹并追加图片 items
- `docs/PROJECT_STATE.md` / `docs/DECISIONS.md` / `docs/CHANGELOG_AI.md` — 记录 v1.8 状态、决策和验证

**验证**：
- image folder scan sample 通过：忽略非图片文件，按文件名排序，保留原始绝对路径
- `python3 -m compileall main.py game` 通过
- `SDL_VIDEODRIVER=dummy /tmp/pgvenv/bin/python <settings smoke>` 通过：图片 items 导入后 SettingsScreen 仍保持打开，不自动开始游戏
- 已导出 Settings 预览图检查 `Folder` 按钮和图片列表布局
- Windows 端仍需用户 `git pull` + `build.bat` 实测 exe 文件夹选择器和图片导入

---

### v1.7.1 — 修复长单词目标牌显示溢出

**目标**：manufacturer 等长词在目标展示牌/杯内答案牌中无法完整显示。

**改造文件**：
- `game/animations.py` — 目标展示牌和杯内答案牌改为白底黑字；新增自适应字号逻辑；杯内答案牌加宽

**验证**：
- `python3 -m compileall main.py game` 通过
- `SDL_VIDEODRIVER=dummy /tmp/pgvenv/bin/python <long-word smoke>` 通过
- 已导出 manufacturer intro 和杯内答案预览图确认完整可读

---

### v1.7 — 文字题库 TXT 导入

**目标**：先恢复一个最小可用的题库导入版本：老师选择普通 `.txt` 编号列表，程序自动追加到 SettingsScreen 的 `Your Items`，但不自动开始游戏。图片题库先放一边。

**新建文件**：
- `game/question_bank.py` — 纯文本题库解析：支持编号、短横线、星号和普通行，输出 text items
- `docs/superpowers/specs/2026-05-21-v17-text-bank-import-design.md` — v1.7 文字题库导入设计说明

**改造文件**：
- `game/settings.py` — `Your Items` 顶部新增 `Import` 按钮；使用 tkinter 选择 `.txt`，解析后追加到 `manual_items`，设置页保持打开
- `docs/PROJECT_STATE.md` / `docs/DECISIONS.md` / `docs/CHANGELOG_AI.md` — 记录 v1.7 状态、决策和验证

**验证**：
- parser sample check 通过：`1. apple` / `2 banana` / `3) cat` / `4、dog` / `- elephant` / `* frog` / 普通行 / 纯数字题目
- `python3 -m compileall main.py game` 通过
- `SDL_VIDEODRIVER=dummy /tmp/pgvenv/bin/python <settings smoke>` 通过：导入 items 后 SettingsScreen 仍保持打开，不自动开始游戏
- 已导出 Settings 预览图检查 `Import` 按钮布局
- Windows 端仍需用户 `git pull` + `build.bat` 实测 exe 文件选择器和 TXT 导入

---

### v1.6 — Champagne Farm 轻奢香槟配色

**目标**：用户反馈 v1.4 颜色太深、显旧，希望先只改配色，做成更轻奢、明亮、干净的视觉气质。

**新建文件**：
- `docs/superpowers/specs/2026-05-21-v16-champagne-farm-palette-design.md` — v1.6 配色设计说明

**改造文件**：
- `game/theme.py` — 主题 token 改为浅香槟木色、奶油羊皮纸、香槟金、鼠尾草绿、雾蓝；新增柔和阴影和 intro overlay 色值
- `assets/pixel/*.png` — 同名同尺寸重生成像素素材，降低木色饱和和明度压暗感
- `game/decorations.py` / `game/ui_components.py` / `game/animations.py` / `game/shell_game.py` — 替换残留硬编码深棕阴影和 intro 深色遮罩
- `docs/PROJECT_STATE.md` / `docs/DECISIONS.md` / `docs/CHANGELOG_AI.md` — 记录 v1.6 状态、决策和验证

**验证**：
- `python3 -m compileall main.py game` 通过
- `SDL_VIDEODRIVER=dummy /tmp/pgvenv/bin/python <smoke>` 通过：Settings / ShellGame / Scoreboard 三屏渲染正常
- 已导出三屏预览图人工检查，整体比 v1.4 更浅、更接近轻奢香槟配色
- Windows 端仍需用户 `git pull` + `build.bat` 实测 exe 视觉

---

### v1.4-pixel-ui — 像素素材皮肤 + 紧致星露谷风 UI

**目标**：用户反馈当前 UI 只是"简陋模仿"，要求更紧致，并且真正靠近星露谷 / cozy farming pixel game 的视觉语言。

**新建文件**：
- `game/assets.py` — 统一处理 PyInstaller `_MEIPASS` 资源路径、PNG 加载缓存、tile 绘制、9-slice 拉伸
- `assets/pixel/*.png` — 本地生成的像素素材：木纹 tile、羊皮纸 tile、9-slice 面板、木牌、按钮、输入框、杯子 sprite、叶子装饰

**改造文件**：
- `game/theme.py` — 色板改为更低色阶的像素木质 / 羊皮纸 palette；spacing 和字体阶梯整体收紧；radius 降到硬边为主
- `game/decorations.py` — 背景改 tile 木纹；面板、木牌、对话框改 9-slice 像素边框；阴影从柔光改块状偏移
- `game/ui_components.py` — Button / Slider / TextInput 改为像素按钮、硬边滑轨、像素输入框
- `game/animations.py` — Cup 绘制优先使用 `assets/pixel/cup.png` sprite；目标球改成方形像素牌风格
- `game/settings.py` — 设置页双面板压缩，输入栏、图片按钮、列表行和速度图标区更紧凑
- `game/shell_game.py` — HUD、Exit、提示框、杯子尺寸和底座收紧
- `game/scoreboard.py` — 结算卡片、按钮、分数和进度条收紧，进度条改硬边像素风
- `build.bat` — 增加 `--add-data "assets;assets"`，Windows exe 打包包含字体和像素素材
- `docs/PROJECT_STATE.md` / `docs/DECISIONS.md` / `docs/CHANGELOG_AI.md` — 记录 v1.4 状态、决策和验证

**验证**：
- `python3 -m compileall main.py game` 通过
- `SDL_VIDEODRIVER=dummy /tmp/pgvenv/bin/python <smoke>` 通过：素材加载、9-slice、Settings/ShellGame/Scoreboard 三屏绘制正常
- Windows 端仍需用户 `git pull` + `build.bat` 实测 exe 视觉和资源加载

---

## 2026-05-20

今天连续完成 4 个版本（v1.0-stardew → v1.1 → v1.2 → v1.3），加 1 个 statusLine 配置 + 多次 CLAUDE.md 更新。本次会话进入收尾，整理项目记忆。

### 总览

| Tag | Commit | 主题 |
|-----|--------|------|
| v1.0-stardew | `b9c0873` | 重做 UI 为星露谷木质风格 + 删除 Load Bank |
| (无 tag)     | `6c2caf0` | 更新 CLAUDE.md 加 v1.0 后的代码风格与禁止事项 |
| v1.1         | `e0e2070` | 修复设置界面 X 退出后会启动一轮的 bug |
| v1.2         | `6c80d89` | Exit 按钮 + 目标球放大展示飞入动画 |
| v1.3         | `38117e8` | 题库保留 + 中途调难度 |

总变更：11 个文件，+2099 / -363 行。

---

### v1.0-stardew (`b9c0873`) — 星露谷重做

**新建文件**：
- `game/theme.py` — 设计 token：颜色（CREAM_BG / WOOD_DARK / GOLD / SV_BLUE 等）、间距 SPACE_*、圆角 RADIUS_*、字号 FONT_*；保留旧 CANDY_* 名称作为 alias
- `game/decorations.py` — 木板背景（缓存到模块级 dict 避免每帧重画）、羊皮纸卡片（双层描边 + 四角铆钉）、对话气泡、漂浮装饰物（橡子 / 四叶草 / 麦穗）
- `game/effects.py` — 粒子系统（圆形 / 星 / 心三种）、浮字、屏幕震动、屏幕闪光；并行更新

**改造文件**：
- `game/icons.py` — 新增蜗牛 / 兔子 / 闪电 / 火焰 / 旋风 / 心 / 替换箭头 / 门 / 垃圾桶 / 图片标志 / 文字标志 / 加号 共 11 个图标
- `game/ui_components.py` — Button 改成木牌按下回弹；Slider 改金币 knob + 木质轨道；TextInput 羊皮纸；新增 `Card` / `WoodSign` / `render_text_outlined`
- `game/animations.py` — `Cup.draw` 重绘（地面阴影 + 金光 + 摇晃偏移）；新增 `add_shake` / `add_glow`；新增 `ease_out_back` / `ease_out_elastic` 缓动
- `game/settings.py` — 整体重构成左右两张羊皮纸卡片；删除 Bank 模式；速度滑块下方加动态图标；items 列表带删除按钮和滚动
- `game/shell_game.py` — 顶部木板 HUD（圆点进度 + 星星分数）+ 浮动对话气泡 + 答对粒子爆炸 / 答错杯子摇晃 + 屏幕震动反馈
- `game/scoreboard.py` — 分数 spring 弹入；星星错峰 elastic 弹出 + 金色爆炸；进度条流动光泽；按钮带图标

**未动**：`main.py` / `requirements.txt` / `build.bat` / 字体文件——零新依赖、零新资源。

**验证**：
- 创建临时 venv `/tmp/pgvenv` 装 `pygame-ce`（pygame 2.6.1 不支持 Python 3.14 的 font 模块，pygame-ce 兼容 API 可用）
- `SDL_VIDEODRIVER=dummy` headless smoke test：3 屏渲染、点击流、0/2/3 颗星边界全过
- **真实窗口未跑过**——本机 Python 3.14 + pygame 2.6.1 没 font 支持
- 视觉效果交给用户在 Windows 端 `build.bat` 验证

---

### CLAUDE.md 更新 (`6c2caf0`)

补全：技术栈、目录结构、AnimationManager 串行 vs EffectsManager 并行的关键区分、文字描边规范、字体 fallback、PyInstaller 路径处理、10 条禁止事项、已知 TODO。

未在代码层面做任何改动，纯文档。

---

### v1.1 (`e0e2070`) — 修复 X 退出 bug

**Bug 现象**：用户点设置界面右上角 X 退出，程序不会关闭，反而进入一轮游戏。

**根因**：`SettingsScreen.run()` 末尾无脑 `return self._get_settings()`，没区分"用户点 Start"和"用户点 X"。`main.py` 看到 dict 不为 None 就进入 ShellGame。

**修复文件**：
- `game/settings.py` — 加 `self.quit_requested` 标志位，QUIT 事件设为 True，`run()` 末尾根据它决定返回 `None` 还是 settings

**验证**：
- 手动注入 `pygame.event.QUIT` 事件 → `run()` 返回 `None`
- 模拟点 Start 按钮 → `run()` 返回 settings dict（含 num_cups / num_rounds / items 等）

---

### v1.2 (`6c80d89`) — Exit 按钮 + 目标球放大展示

**改动文件**：
- `game/animations.py` — 新增 `IntroBall` 类（独立的、可缩放的目标球展示对象），新增 `add_intro_show`（淡入 + 停留）和 `add_intro_fly`（弧线轨迹 + 缩放）两种动画类型
- `game/shell_game.py` —
  - 加 `intro_ball` 实例和 `intro_active` 状态
  - 加 `exit_btn`（HUD 右端红色小木牌）
  - `_prepare_round` 重排：杯子抬起 → 中央放大球 2000ms → 弧线飞入 → 杯子盖下 → 洗牌
  - `_handle_click` 任意非 finished state 都检测 Exit 按钮
  - `_draw` 加半透明遮罩聚焦 intro 阶段
  - state 加 `intro` 一档，`_update` 推进 `intro → showing`
  - `_handle_click` 在 `result_shown` 时点 Exit 自动 `current_round += 1`，避免 Scoreboard 显示 `1/0` 这种诡异比例

**验证**：
- 5 档速度（1-5）都能 `intro → showing → guessing` 推进
- 第二回合自动重新进入 intro
- 三种 state（intro / showing / result_shown）下 Exit 都正常退出
- 文字 / 图片 / 超长文字 IntroBall 渲染都不崩
- 图片 fallback：图片路径无效时退到文字模式不崩

**已知边界**：首回合 intro 期间立即 Exit 会显示 `0/0`，依赖 `Scoreboard` 内部 `max(1, total)` 保护。视觉是 0 颗星灰色显示，**未优化**。

---

### v1.3 (`38117e8`) — 题库保留 + 中途调难度

**改动文件**：
- `game/icons.py` — 新增 `draw_gear` 齿轮图标（用于 Adjust 按钮）
- `game/scoreboard.py` —
  - 三按钮重布局：`Same Again`（蓝）/ `Adjust`（绿）/ `Quit`（红）
  - `run()` 检测 adjust_btn 返回字符串 `"adjust"`
  - `_draw` 三按钮全画
- `game/settings.py` — `__init__` 加 `initial_settings=None` 参数，预填 cup_slider / round_slider / speed_slider / manual_items
- `main.py` —
  - 维护 `last_settings` 跨场景复用
  - 用 `skip_settings` 标志位控制 `Same Again` 跳过 SettingsScreen
  - 根据 Scoreboard 返回的 `"replay"` / `"adjust"` / `"quit"` 决定走向

**验证**：
- SettingsScreen 预填：滑块值和 items 列表准确还原
- 默认无 initial_settings：滑块回退到 3/5/2 默认值，items 为空
- Scoreboard 三按钮位置（1024 屏幕）：147 / 397 / 647，互不重叠，全部在屏内
- Scoreboard 三按钮分别返回 `"replay"` / `"adjust"` / `"quit"`
- end-to-end：settings dict 经 ShellGame → Scoreboard → 重新喂给 SettingsScreen 能完整 round-trip

---

### 配置类改动（不在 game/* 里）

- 全局 statusLine：新建 `~/.claude/statusline.py`，在 `~/.claude/settings.json` 加 `statusLine` 字段（这部分是用户全局环境，不在本仓库）
- `~/.claude/CLAUDE.md` 加了一段 statusLine 说明（全局，不影响本仓库）

---

## 验证方法学（备忘）

**为什么本机不能跑真实窗口**：
用户 Mac 是 Python 3.14.5，但 `pygame 2.6.1` 的 font 模块在 3.14 上没编译进去——`import pygame.font` 会报 `ModuleNotFoundError: No module named 'pygame.font'`。

**绕过方案**（本会话用的）：
```bash
python3 -m venv /tmp/pgvenv
/tmp/pgvenv/bin/pip install pygame-ce          # API 兼容，3.14 上 font 可用
SDL_VIDEODRIVER=dummy /tmp/pgvenv/bin/python <test-script>
```

这个 venv 只用于 AI 跑 smoke test，**不影响项目正常依赖**（`requirements.txt` 还是 `pygame==2.6.1`）。Windows 端的 PyInstaller 打包用的是项目原依赖。

如果未来 Mac 端需要真实窗口验证，**用户需要降级到 Python 3.11 或 3.12**，或等 pygame 发布 3.14 wheel。

---

## 文档结构（今天新建）

```
docs/
├── PROJECT_STATE.md   — 当前项目状态、已完成/未完成、下一步
├── DECISIONS.md       — 技术决策与原因
└── CHANGELOG_AI.md    — 本文件，AI 修改记录与验证情况
```

CLAUDE.md 仍保留为项目根目录的"长期规则与协作偏好"主文件。
