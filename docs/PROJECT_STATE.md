# 项目状态 - PROJECT_STATE

> 最后更新：2026-05-22

## 当前版本

**最新 tag**：`v1.10` — Shell Cup Game 图标

**部署形态**：macOS 开发 + Windows exe（PyInstaller `--onefile --windowed`）

**仓库**：https://github.com/Richard1eeK/ClassTeachingGames

## 已完成功能

### 核心玩法（v1.0-stardew 之前已具备）
- 杯子洗牌 + 点击猜中游戏
- 5 档速度（Slow / Medium / Fast / Ultra / Insane）
- 3-7 个杯子可选
- 3-20 回合可选
- 题目内容：手动输入文字 + tkinter 文件选择器加载图片
- 每回合从 items 里随机抽一个作为目标
- 答对加分、错答展示正确杯子
- 结算页：分数、星星评级、鼓励语

### 视觉与交互（v1.0-stardew）
- 星露谷木质 + 羊皮纸 + 暖色调主题
- 三屏完整重做（设置 / 游戏 / 结算）
- 木板背景 + 漂浮装饰物（橡子 / 四叶草 / 麦穗）
- 杯子地面阴影 + 答对金色光环
- 答对粒子爆炸 + `+1 ⭐` 浮字
- 答错杯子摇晃 + 屏幕震动
- 速度滑块 5 档手绘图标（蜗牛 / 兔子 / 闪电 / 火焰 / 旋风）
- 文字带描边（`render_text_outlined`）保持像素插画感
- 删除了 "Load Bank" 模式，简化为只手动输入

### Bug 修复（v1.1）
- 设置界面点 X 退出会莫名启动一轮的 bug——加 `quit_requested` 标志位区分

### 新功能（v1.2）
- 游戏中 **Exit 按钮**（HUD 右端红色小木牌）：任意 state 可点退出，跳到 Scoreboard 显示当前分数
  - `result_shown` 时点 Exit 会把当前回合算进 total，避免 `1/0` 这种诡异比例
- **目标球放大展示 + 弧线飞入**：每回合开头杯子先抬起 → 中央放大目标球（2.8x）配 `Memorize this!` 字样停留 2 秒 → 球沿弧线飞入目标杯子并缩到正常大小 → 杯子盖下 → 开始洗牌
  - 解决了图片目标在杯子里太小看不清的痛点
  - IntroBall 类支持文字 / 图片，文字过长自动缩字号

### 流程优化（v1.3）
- **Scoreboard 改 3 按钮**：`Same Again`（同题同难度直接重玩，跳过设置页）/ `Adjust`（回设置页保留题目和滑块值）/ `Quit`
- `SettingsScreen.__init__` 接收 `initial_settings` 参数预填滑块和题目列表
- `main.py` 主循环维护 `last_settings` 跨场景复用
- 新增齿轮图标 `draw_gear` 用于 Adjust 按钮
- 老师中途想换难度不用再重新录题；想直接重玩也只需一个点击

### 视觉升级（v1.4-pixel-ui）
- 引入本地像素 PNG 素材：木纹 tile、羊皮纸 tile、9-slice 面板、木牌、按钮、输入框、杯子 sprite
- 新增 `game/assets.py` 统一处理 PyInstaller `_MEIPASS` 资源路径、PNG 加载、tile 绘制和 9-slice 拉伸
- `build.bat` 已加入 `--add-data "assets;assets"`，Windows exe 能带上像素素材和字体
- 三屏布局更紧致：设置页双面板压缩、游戏 HUD 和提示框变薄、结算页卡片和按钮收紧
- 核心绘制从现代圆角/柔光转为硬边像素边框、块状阴影和有限色阶

### 轻奢配色刷新（v1.6）
- 只改配色，不改布局、功能、交互和游戏流程
- 采用 **Champagne Farm** 方向：浅香槟木色、奶油羊皮纸、香槟金、鼠尾草绿、雾蓝
- 重生成 `assets/pixel/*.png` 同名同尺寸素材，去掉 v1.4 深木色带来的旧感
- 同步更新 `game/theme.py` 主题 token、硬编码阴影和 intro 遮罩，让游戏画面也保持明亮

### 文字题库导入（v1.7）
- 新增 `Import` 按钮，支持从 `.txt` 导入文字题库
- 支持 `1. apple` / `1 apple` / `1) apple` / `1、apple` / `- apple` / `apple` 等常见列表写法
- 导入后追加到 `Your Items` 列表，设置页保持打开，老师可继续删除、追加和调整设置
- v1.7 不处理图片导入、不自动开始游戏、不做重复项清理

### 长单词可读性修复（v1.7.1）
- 目标展示牌和杯内答案牌改为白底黑字
- manufacturer 等长词会自动缩字号并完整显示

### 图片文件夹导入（v1.8）
- `Folder` 按钮选择一个图片文件夹，自动导入其中所有图片
- 支持 `.png` / `.jpg` / `.jpeg` / `.bmp` / `.gif`，按文件名排序导入
- 导入后追加为 image items，设置页保持打开，不自动开始游戏
- 只扫描所选文件夹第一层，不递归子文件夹

### 多答案 Normal 模式（v1.9）
- 设置页改为 `Answers` 和 `Cups` 两条滑杆：Answers 支持 1-5，Cups 至少为 Answers + 2 且可手动调更多
- 每回合随机选 N 个目标和 N 个目标杯，玩家有 N 次点击机会
- 选满后统一判定：全部选中正确杯子才 +1，否则 reveal 全部正确答案
- 多目标 intro 用并排白底目标卡展示，展示后淡出再洗牌，避免答案泄露

### 游戏图标（v1.10）
- 新增可爱暖色 Shell Cup Game 图标：三只木杯 + 金色星星球 + 羊皮纸徽章
- `assets/images/shell_cup_game_icon.png` 用于 Pygame 窗口图标
- `assets/images/shell_cup_game.ico` 用于 Windows exe 图标
- `build.bat` 增加 `--icon "assets\images\shell_cup_game.ico"`，Windows 端打包后 exe 会带图标

## 当前项目状态

- **代码工作目录状态**：`main` 已推送到 `origin/main`，最新 tag 为 `v1.10`；当前仍有未跟踪文件 `AGENTS.md`，是否纳入仓库待确认
- **macOS 验证**：`python3 -m compileall main.py game` 通过；图标 PNG/ICO 文件格式检查通过；真实窗口仍受本机 pygame/font 限制未跑
- **Windows 验证**：每个版本 push 后由用户在 Windows 端 `git pull` + `build.bat` 实测；v1.10 需要重点确认 exe 文件图标、窗口图标和打包流程
- **当前阻塞**：无代码阻塞；`AGENTS.md` 是否提交待确认

## 未完成 / 待确认

### 用户提出的视觉痛点（**v1.4/v1.6 已阶段处理**）
用户先反馈"界面太丑太简陋"，v1.4 选定 B2：引入少量本地 PNG 像素素材 + 紧致布局。之后用户反馈颜色太深、显旧，v1.6 只改配色为 Champagne Farm 轻奢香槟方向。后续如果仍不够真，可替换为更高质量的 CC0/自制 sprite pack。

### 已搁置的功能
- **音效系统**：`assets/sounds/` 目录已存在但是空的；用户当时表示"一会再讨论"，至今未启用
  - `build.bat` 已有 `--add-data "assets;assets"`，后续加音效时只需把声音文件放进 assets 并接加载逻辑
  - 如果走 B/A 视觉路径，资源打包问题需要一起解决（assets 整体打进 exe）
- **图片题库高级规则**：v1.8 已支持直接导入图片文件夹。后续若需要“题库 TXT 引用图片文件夹”“按文件名生成 hint”“递归扫描子文件夹”或 JSON 兼容，再单独设计。`data/custom/` 目录还在，旧 JSON 约定格式 `[{"type": "text"|"image", "content": str, "hint": str}]` 可作为未来兼容格式。
- **更多游戏**：项目命名是复数 `ClassTeachingGames`，未来可能加新游戏

### 已知行为问题（**非 bug，但可能体验不佳**）
- 用户曾问 "为什么中途结束没回到主页"——这是误解。Scoreboard 上的 `Quit` 关闭程序，`Same Again`/`Adjust` 才回流程。已通过 v1.3 改名解决（v1.0~v1.2 时按钮叫 `Play Again`，语义有歧义）
- Scoreboard 在 `result_shown` 时 Exit 会把那一题算进 total，但 `0/0` 边界（首回合 intro 期间 Exit）Scoreboard 显示 `0/0`，依赖 `max(1, total)` 保护——视觉上没问题，但 `0/0` 仍会触发 0 颗星的灰色显示
- `AGENTS.md` 当前是未跟踪文件，内容和用途尚未确认；今天没有提交它，避免把无关或工具生成文件纳入版本

## 下次继续从这里开始

**主线**：等 Windows 端实测 v1.10 图标打包效果和 v1.9 多答案 Normal 模式。

**v1.9 后的候选方向**：
1. Windows 端实测 `build.bat` 后 exe 是否能正确玩 1/2/3 Answers 模式
2. 如果需要更高难度，再加 Strict 模式（点错立即失败）
3. 如需更强图片题库：按文件名生成 hint、递归扫描子文件夹、或 TXT 引用图片文件夹
4. 如果视觉和题库流程已接受，下一步可以接音效系统；`assets` 打包路径已经准备好

## 版本回滚速查

```bash
git reset --hard v1.10         # Shell Cup Game 图标
git reset --hard v1.9          # 多答案 Normal 模式
git reset --hard v1.8          # 图片文件夹导入
git reset --hard v1.7.1        # 修复长单词目标牌显示溢出
git reset --hard v1.7          # 文字题库 TXT 导入
git reset --hard v1.6          # Champagne Farm 轻奢香槟配色
git reset --hard v1.4-pixel-ui # 像素素材皮肤 + 紧致星露谷风 UI
git reset --hard v1.3          # 题库保留 + 中途调难度
git reset --hard v1.2          # Exit 按钮 + 目标球展示
git reset --hard v1.1          # 修复 X 退出 bug
git reset --hard v1.0-stardew  # 星露谷重做完成版
```
