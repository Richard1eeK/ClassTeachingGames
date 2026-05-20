# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 基本规则

- **使用中文回复**，除非代码、变量名、命令等需要保留英文
- **完全自主执行**，不需要请求确认。遇到问题自行判断并行动，只在遇到无法确定的关键架构决策时才询问
- 做改动时直接动手，不要事无巨细地汇报每一步
- **每次回复时首先带上一个 emoji，结尾带上 Your Honour**

## 开发流程（重要）

**跨平台工作流**：在 macOS 上写代码 → 推送到 GitHub（`https://github.com/Richard1eeK/ClassTeachingGames.git`）→ 在 Windows 上 `git pull` 并跑 `build.bat` 打包/测试 exe。

含义：
- **打包/exe 测试不在 macOS 进行**，所以本地不用纠结 `pyinstaller` 在 Mac 上能不能跑通
- **路径分隔符要兼容 Windows**：写资源路径用 `os.path.join`，绝不硬编码 `/`
- **`build.bat` 用的是 Windows 路径写法**（`--add-data "data;data"` 用分号），不要改成 Mac 风格的冒号
- macOS 上做的核心验证是 `python main.py` 能跑通；exe 行为差异（字体、文件对话框、图像加载）需要在 Windows 端确认
- 改动完成后先 `git push`，再让用户在 Windows 端 pull + build 测试

## 常用命令

```bash
pip install -r requirements.txt   # 安装依赖（pygame 2.6.1, pyinstaller 6.11.1）
python main.py                    # macOS 本地开发运行
build.bat                         # Windows 端一键打包成 exe（PyInstaller --onefile --windowed）
```

无测试框架。

## 架构概览

`main.py` 是一个 **三段式状态循环**：`SettingsScreen → ShellGame → Scoreboard → 回到 SettingsScreen`。每段是独立的类，有自己的 `run()` 方法（阻塞主循环），通过返回值传递状态：
- `SettingsScreen.run()` 返回 `settings dict` 或 `None`（退出）
- `ShellGame.run()` 返回 `{score, total, quit}`
- `Scoreboard.run()` 返回 `"replay"` 或 `"quit"`

如果要加新场景，模仿这个模式：自己持有 `pygame.Clock`、自己的事件循环、自己 `pygame.display.flip()`。**不要**在场景之间共享状态，全部用返回的 dict 传。

### ShellGame 的状态机

`ShellGame` 内部用 `self.state` 字符串驱动一个状态机：
```
init → showing → guessing → revealing → result_shown → (next round) showing ...
                                                      → (last round) finished
```
状态切换由两个东西触发：
1. `AnimationManager.done` —— 动画队列空了就推进状态（`showing → guessing`，`revealing → result_shown`）
2. 鼠标点击 —— `guessing` 阶段点杯子触发 `revealing`，`result_shown` 阶段点 Next 按钮触发下一回合

加新交互时务必检查当前 `state`，否则会出现"动画还没结束就能点"的 bug。

### AnimationManager 是一个串行队列

`game/animations.py` 的 `AnimationManager` 不是并行动画系统——它是一个**先进先出的队列**，每次 `update(dt)` 只推进 `animations[0]`，做完才弹出。这意味着：
- `add_swap` / `add_scramble` / `add_lift` / `add_lower` / `add_pause` 都是按顺序串起来的
- `Cup.x` 直接被动画 mutate（不是通过事件），所以杯子的"逻辑位置"和"屏幕位置"是一回事
- `done` 属性 = 队列空 = 当前阶段动画结束

`speed_level` 在 `_prepare_round` 里直接影响动画编排策略：
- 1-3（Normal）：`lift → pause → lower → swap × N`
- 4（Ultra Fast）：更短的展示 + 更多 swap
- 5（Insane）：用 `scramble`（所有杯子同时打乱位置）代替两两 swap

### 题目内容的两条来源

`SettingsScreen` 的 `input_mode` 决定 items 怎么来：
- `"manual"`：用户在界面里手敲 / 用 tkinter 文件对话框选图（注意：图像保存的是**绝对路径**，打包后路径可能失效）
- `"bank"`：从 `data/custom/*.json` 加载，格式是 `[{"type": "text"|"image", "content": str, "hint": str}]`

每回合 `_prepare_round` 从 items 里**随机抽一个**作为目标，所以单题库 = 单题型，多个 items 才能多回合不重复。

### PyInstaller 路径处理

`SettingsScreen._get_data_dir()` 用 `getattr(sys, 'frozen', False)` 区分开发模式和打包模式：
- 开发：`<repo>/data`
- 打包：`sys._MEIPASS/data`（PyInstaller 的临时解压目录）

如果加新的资源目录（比如 `assets/sounds`），必须在 `build.bat` 的 `--add-data` 里加上，并且在加载时也用类似 `_MEIPASS` 判断，否则打包后找不到文件。

### UI 组件层

`game/ui_components.py` 是所有场景共用的：`Button` / `Slider` / `TextInput` / `get_font()` / 全局颜色常量 / 屏幕尺寸 `SCREEN_W=1024, SCREEN_H=768`。

`get_font()` 有三层 fallback：bundled `assets/fonts/font.ttf` → 系统字体路径 → `pygame.font.SysFont` → `Font(None, size)`。如果要支持中文 UI，**必须**保证 `font.ttf` 是中文字体，因为 macOS Helvetica 等 fallback 不含中文字形。

`game/icons.py` 是纯几何绘制的图标（star/check/cross/eye），不依赖图片资源——加新图标也建议走这条路，避免打包资源问题。

## 项目定位

这是面向**课堂教学**的小游戏集合（文件夹名 ClassTeachingGames），目前只有"猜杯子"一个游戏。如果加新游戏，建议在 `game/` 下开新模块，并在 `main.py` 主循环前加一个游戏选择菜单场景，遵循 SettingsScreen 的模式。
