# AI 修改记录 - CHANGELOG_AI

> 这里记录 AI 实际改了哪些文件、为什么改、如何验证。
> 一行一行的 diff 见 git，本文档关注"做了什么 / 跑过什么 / 留了什么坑"。

---

## 2026-05-21

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
