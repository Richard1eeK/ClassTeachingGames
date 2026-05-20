# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 基本规则

- **使用中文回复**，除非代码、变量名、命令等需要保留英文
- **完全自主执行**，不需要请求确认。遇到问题自行判断并行动，只在遇到无法确定的关键架构决策时才询问
- 做改动时直接动手，不要事无巨细地汇报每一步
- **每次回复时首先带上一个 emoji，结尾带上 Your Honour**

## 项目定位

面向**小学生课堂教学**的小游戏集合（文件夹名 ClassTeachingGames），目前只有一个游戏：**Shell Cup Game（猜杯子）**——老师配置内容（字母/单词/图片），杯子洗牌后让学生猜目标在哪个杯子下。

视觉风格：**星露谷木质 + 羊皮纸 + 暖色调**，UI 文字保持英文（face-to-face 课堂适用，方便英语教学）。

## 技术栈

- **Python 3.9+**（开发机 macOS 用 3.9.6，但代码兼容更高版本）
- **Pygame 2.6.1**（游戏引擎，纯几何绘制 UI，不引入新依赖）
- **PyInstaller 6.11.1**（打包 Windows exe，`--onefile --windowed`）
- **tkinter**（仅用于"添加图片"时的文件选择对话框，Python 自带）

## 跨平台开发流程（重要）

**macOS 写代码 → push 到 GitHub → Windows 端 pull + `build.bat` 打包测试 exe**。

仓库：`https://github.com/Richard1eeK/ClassTeachingGames.git`

含义：
- **打包/exe 测试不在 macOS 进行**——本地不要纠结 PyInstaller 在 Mac 能不能跑通
- **路径必须用 `os.path.join`**，绝不硬编码 `/`
- **`build.bat` 里 `--add-data "data;data"` 用分号是 Windows 写法，不要改**
- macOS 端核心验证只是 `python main.py` 能跑通；字体、文件对话框、图像加载等差异交给 Windows 端确认
- 改动完成后默认假设需要 `git push`

## 常用命令

```bash
pip install -r requirements.txt   # 安装依赖
python main.py                    # macOS 本地开发运行
build.bat                         # Windows 端一键打包成 exe
```

无测试框架。不要主动新增。

## 目录结构

```
ClassTeachingGames/
├── main.py                # 入口，三段式状态循环
├── build.bat              # Windows 打包脚本（PyInstaller --onefile --windowed）
├── requirements.txt       # pygame + pyinstaller
├── CLAUDE.md              # 本文件
├── assets/
│   ├── fonts/font.ttf     # 内置 Nunito 圆体字（必须含目标语言字形）
│   ├── images/            # 暂未使用
│   └── sounds/            # 暂未使用（音效系统待加）
├── data/
│   └── custom/            # 题库 JSON 存放位置（当前未启用题库加载）
└── game/
    ├── __init__.py
    ├── theme.py           # 设计 tokens：颜色/间距/圆角/字号
    ├── decorations.py     # 木板背景、羊皮纸卡片、漂浮装饰物（带 surface 缓存）
    ├── icons.py           # 纯几何绘制图标（star/snail/rabbit/lightning/flame/...）
    ├── effects.py         # 粒子系统、浮字、屏幕震动/闪光
    ├── animations.py      # Cup 类 + AnimationManager（串行动画队列）
    ├── ui_components.py   # Button / Slider / TextInput / Card / WoodSign / get_font
    ├── settings.py        # SettingsScreen——开始游戏前的配置界面
    ├── shell_game.py      # ShellGame——主游戏界面 + 状态机
    └── scoreboard.py      # Scoreboard——结算界面
```

## 架构概览

### 1. 三段式主循环（`main.py`）

`SettingsScreen → ShellGame → Scoreboard → 回到 SettingsScreen`，每段是独立的类，自己持有 `pygame.Clock` 和事件循环，通过 `run()` 返回值传递状态：
- `SettingsScreen.run()` → `settings dict` 或 `None`（退出）
- `ShellGame.run()` → `{score, total, quit}`
- `Scoreboard.run()` → `"replay"` 或 `"quit"`

**加新场景照这个模式做**：自己的 `run()`、自己的事件循环、自己的 `pygame.display.flip()`。**禁止**在场景之间共享可变状态，所有数据通过返回的 dict 传。

### 2. ShellGame 状态机

```
init → showing → guessing → revealing → result_shown → (next round) showing ...
                                                     → (last round) finished
```

切换由两个东西触发：
1. `AnimationManager.done`——动画队列空了就推进（`showing → guessing`，`revealing → result_shown`）
2. 鼠标点击——`guessing` 阶段点杯子触发 `revealing`，`result_shown` 阶段点 Next 按钮触发下一回合

**加新交互前必须检查当前 `state`**，否则会出现"动画还没播完用户就能点"的 bug。

### 3. AnimationManager 是串行 FIFO 队列

`game/animations.py` 的 `AnimationManager` **不是并行动画系统**，是先进先出的队列：每次 `update(dt)` 只推进 `animations[0]`，做完才弹出下一个。
- 已有动画类型：`add_swap` / `add_scramble` / `add_lift` / `add_lower` / `add_pause` / `add_shake` / `add_glow`
- `Cup.x` 直接被动画 mutate（不是事件驱动），杯子的"逻辑位置"和"屏幕位置"是同一个值
- `Cup.shake_offset` / `Cup.glow` / `Cup.lift_offset` 同理
- `done` 属性 = 队列空 = 当前阶段动画结束
- 缓动函数：`ease_in_out` / `ease_out_back`（spring）/ `ease_out_elastic`

`speed_level`（1-5）在 `ShellGame._prepare_round` 直接影响动画编排：
- 1-3 Normal：`lift → pause → lower → swap × N`
- 4 Ultra Fast：更快展示 + 更多 swap
- 5 Insane：用 `scramble`（所有杯子同时打乱位置）代替两两 swap

### 4. EffectsManager 是并行特效层

`game/effects.py` 的 `EffectsManager` 与 `AnimationManager` 不同——**它是并行的**：粒子、浮字、屏幕震动、闪光独立 update。
- `burst_correct(x, y)` —— 答对的金/星/心爆炸
- `burst_wrong(x, y)` —— 答错的柔和红色粉末
- `burst_stars(x, y, count, color)` —— 通用星星爆炸
- `add_text(x, y, text, color, size)` —— 浮字（如 `+1 ⭐`）
- `add_shake(amount, duration)` / `add_flash(color, alpha)` —— 屏幕级反馈

绘制时把所有内容画到一个 `pygame.Surface`，再用 `effects.get_shake_offset()` 偏移整体 blit 到主屏幕。

### 5. 设计 token 集中在 `theme.py`

颜色、间距（`SPACE_*`）、圆角（`RADIUS_*`）、字号（`FONT_*`）都在 `game/theme.py`。**新代码用 token，不要写死数值**，方便日后调整。

旧代码里的 `CANDY_*` / `BG_COLOR` / `WHITE` 等是 legacy alias，已经映射到星露谷色板上，**新代码优先用 `theme.SV_BLUE` / `theme.GOLD` / `theme.PARCHMENT` 等语义化名称**。

### 6. UI 文字必须用 `render_text_outlined`

`ui_components.render_text_outlined(text, size, color, outline_color, outline_w, bold)` 给文字加描边——这是星露谷风格的关键。**别用裸 `font.render()`**，会显得平淡。

### 7. 字体 fallback

`get_font()` 三层 fallback：bundled `assets/fonts/font.ttf` → 系统字体路径 → `pygame.font.SysFont` → `Font(None, size)`。
- 当前内置 `font.ttf` 是 Nunito Round（圆体英文）
- 如果以后要做中文 UI，必须**先换成含中文字形的字体**，否则 macOS Helvetica 等 fallback 不含中文字形会显示豆腐

### 8. PyInstaller 路径处理

凡是要读 `data/` 或 `assets/` 下的文件，必须用 `getattr(sys, 'frozen', False)` 判断：
- 开发：`<repo>/data`
- 打包：`sys._MEIPASS/data`（PyInstaller 临时解压目录）

加新资源目录时**必须**：
1. 在 `build.bat` 的 `--add-data` 里加（Windows 写法 `"src;dest"` 用分号）
2. 在加载代码里复用 `_MEIPASS` 判断
否则 exe 找不到文件。

`assets/` 目前没在 `build.bat` 里——加音效/图片功能时记得补上。

## 代码风格

- **不引入新依赖**：所有视觉效果用 Pygame 几何绘制完成（参考 `icons.py` / `decorations.py`）
- **资源本地化**：图标用代码画而非 PNG，避免 PyInstaller 路径问题
- **背景/纹理必须缓存**：木板背景、羊皮纸纹理这种重渲染必须用模块级缓存 dict（参考 `decorations.get_wood_background`、`_get_parchment_texture`），别每帧重画
- **场景间不共享状态**：用 dict 通过 `run()` 返回值传递
- **动画修改属性而非派发事件**：`AnimationManager` 直接改 `Cup.x` / `lift_offset` / `glow` / `shake_offset`
- **状态机切换前检查 `state`**：避免动画期间响应误点击
- **跨平台路径**：永远 `os.path.join`，永远不硬编码分隔符
- 默认不写注释，除非 *Why* 不显然（参考根 `~/CLAUDE.md` 全局规则）

## 禁止事项

1. **禁止引入新的 Python 依赖**——任何视觉/音效需求先尝试用 Pygame 内置能力实现
2. **禁止把 PNG/JPG 当成必须资源**——图标走 `icons.py` 几何绘制，避免 exe 打包丢资源
3. **禁止改 `build.bat` 的路径分隔符**——`"data;data"` 是 Windows 写法，改成冒号会让 Windows 打包失败
4. **禁止在 macOS 上跑 `pyinstaller`**——这个项目的 exe 验证只在 Windows 端做
5. **禁止使用 `pygame.font.SysFont` 作为唯一字体源**——必须经过 `ui_components.get_font()` 走 fallback 链
6. **禁止裸 `font.render()` 画 UI 文字**——必须用 `render_text_outlined` 保持星露谷描边风格
7. **禁止在 `AnimationManager` 队列里塞并行需求**——并行特效用 `EffectsManager`，队列动画串行执行
8. **禁止跳过 `state` 检查直接处理点击**——会触发动画期间误响应的 bug
9. **禁止删除 `data/custom/` 或 `assets/sounds/` 等空目录**——里面 `.gitkeep` 占位是为了 Git 跟踪结构，未来要用
10. **禁止在场景类构造器里启动事件循环**——事件循环必须在 `run()` 里，构造器只做初始化

## 已知尚未实现 / TODO

- **音效系统**：`assets/sounds/` 是空的，`build.bat` 也还没加 `--add-data "assets;assets"`，待加
- **题库 JSON 加载**：今天已删除"Load Bank"模式，目前只有手动输入。题库格式仍约定为 `[{"type": "text"|"image", "content": str, "hint": str}]`，等用户决定如何重新引入（可能改成自动扫 `data/custom/` 下的 JSON）
- **更多游戏**：项目命名是复数 `ClassTeachingGames`，未来加新游戏建议在 `game/` 下开新模块 + `main.py` 前加游戏选择菜单
