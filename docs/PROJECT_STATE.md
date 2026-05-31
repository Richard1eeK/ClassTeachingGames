# 项目状态 - PROJECT_STATE

> 最后更新：2026-05-27

## 当前版本

**最新 tag**：`v3.5.1` — Manually Type-in 常驻触摸滚动条可见性修复

**素材库基准版本（无素材库）**：`v2.4`

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

### 游戏图标（v2.0）
- 新增可爱暖色 Shell Cup Game 图标：三只木杯 + 金色星星球 + 羊皮纸徽章
- `assets/images/shell_cup_game_icon.png` 用于 Pygame 窗口图标
- `assets/images/shell_cup_game.ico` 用于 Windows exe 图标
- `build.bat` 增加 `--icon "assets\images\shell_cup_game.ico"`，Windows 端打包后 exe 会带图标

### 双语帮助说明（v2.1）
- 设置页右上角新增 `Need Help? ->` 和圆形 `i` 按钮
- 点击后打开羊皮纸帮助弹窗，支持 `EN` / `中文` 切换
- 内容覆盖设置游戏、添加题目、怎么玩三段
- TXT 导入说明明确要求每行带序号，并提示可截图单词表后用 AI 整理成带序号文本
- 中文说明优先使用系统中文字体，避免内置英文字体显示方块字

### 自由拖拽窗口缩放（v2.2）
- Pygame display 改为 `RESIZABLE`，用户可像普通软件一样拖动窗口边框调整大小
- 新增逻辑画布包装层：内部仍按 1024×768 绘制，实际窗口等比缩放并居中显示
- 鼠标位置和点击事件统一从真实窗口坐标反算回逻辑坐标，避免按钮、滑块和杯子点击偏移
- 非 4:3 窗口会出现左右或上下留边，以避免界面拉伸变形和布局错乱

### 性能优化（v2.3-perf）
- **字体和文字渲染缓存**：`get_font()` 和 `render_text_outlined()` 添加 LRU 缓存，消除每帧重复字体加载和文字渲染
- **图片预处理**：导入图片时立即 `convert_alpha()` 并预缩放到 360×360，避免每帧 smoothscale 大原图
- **Cup sprite 缓存**：杯子贴图缩放结果缓存，避免每帧重复 transform.scale
- **窗口缩放优化**：`ScaledWindow.present()` 跳过窗口=逻辑画布时的无效缩放和填充
- **事件过滤**：`pygame.event.set_allowed()` 只接收必要事件，减少事件队列开销
- 图片加载失败时显示文件名而非完整路径，提升可读性

### 内置材料库（v3.0+）
- Settings 页新增 `Built-in` / `My Library` 标签页，老师可以直接从 `data/library/` 加载内置材料
- Bright Spark flashcards 改为按词汇类别展示：Activities、Adjectives、Animal Parts、Body Parts、Characters、Classroom Items、Clothes、Colours、Days、Directions、Family、Farm Animals、Feelings、Foods and Drinks、Fruits、Household Items、Jobs and Responsibilities、Jobs、Months、Natural World、Numbers、Pets、Places、Prepositions、Pronouns、Rooms、Routines、Seasons、Shapes、Short Answers、Sports、Time of Day、Toys、Vegetables、Verbs、Weather、Wild Animals
- Phonics 相关目录/文件不会进入 Bright Spark 类别列表
- Bright Spark 空分类目录保留为可填充货架；只有分类里实际有图片时才允许 `Use this material`

## 当前项目状态

- **代码版本**：`main` 位于 v3.5.1，素材库和课堂交互打磨基本完成
- **素材库**：Bright Spark 284 张闪卡（33/37 类有内容）+ High Flyer 1,233 张图片 + 42 个词库文件
- **macOS 验证**：全天所有改动通过 py_compile + smoke test
- **Windows 验证**：用户下次 `git pull` + `build.bat` 需重点确认 Manually Type-in 右侧常驻触摸条清晰可见，导入大量词汇后可拖动滚动
- **版本号**：v3.5.1 显示于主界面右下角

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

**主线**：Windows 端 build.bat 实测 v3.5.1，确认 Manually Type-in 右侧常驻触摸条不导入也可见，导入大量词汇后可拖动滚动，删除按钮点击正常。

**后续候选方向**：
1. Animal Parts / Days / Jobs & Responsibilities / Shapes 四类 BS 闪卡补充
2. Phonics 内容如需纳入，可单独开系列
3. 音效系统（assets/sounds/ 已预留，build.bat 已打包）
4. Strict 模式（多答案点错立即失败）
5. 更多游戏类型

## 版本回滚速查

```bash
git reset --hard v3.5.1        # Manually Type-in 常驻触摸滚动条可见性修复
git reset --hard v3.5          # Manually Type-in 词汇列表触摸滚动修复
git reset --hard v2.2          # 自由拖拽窗口缩放
git reset --hard v2.1          # 双语帮助说明
git reset --hard v2.0          # Shell Cup Game 图标
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
