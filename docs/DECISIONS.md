# 技术决策记录 - DECISIONS

> 这里只记录有"为什么这么选"的决策，不重复显然实现细节。
> 已搁置 / 推翻的方案也写出来，方便未来回顾。

---

## 2026-05-20

### D-001: 视觉风格选用"星露谷木质"而非纯候选三方案

**背景**：用户原始反馈"现在 UI 太简陋但要保持小朋友友好"。

**候选**：
- A. 加深 candy 配色，做粉嫩童趣 → 容易腻味、和"教学严肃感"冲突
- B. **星露谷木质 + 羊皮纸 + 暖色调** ← 选定
- C. 做成 pixel art / 16-bit 完整像素风 → 与现有 Nunito 圆体字冲突

**选定 B 的理由**：
- 暖色调＋木质纹理对小学生友好，又比 candy 色更耐看
- 不需要替换现有字体（Nunito 圆体配星露谷温暖调性正合适）
- 完全可以用 Pygame 几何绘制 + 缓存实现，**不引入新资源**

**当前局限**（用户已指出）：纯几何绘制天花板低，"丑感"实质是缺真实素材。下一步可能要走 B 方案的扩展（加纹理 PNG）。

---

### D-002: UI 文字保持英文

**背景**：项目是中文老师录中文题目用的课堂教具，但用户明确指示"保留全英文"。

**理由**：
- 课堂场景多为英语启蒙 / 双语教学
- 英文短词（Cups / Rounds / Speed / Find / Correct）孩子容易认
- 字体 fallback 链已绑定 Nunito，不引入中文字体可少一个潜在的打包问题
- 如未来要本地化，记得**先换成含中文字形的字体**，否则 macOS Helvetica 等 fallback 不含中文字形会显示豆腐

---

### D-003: 删除 Load Bank 模式

**背景**：v1.0-stardew 重做时删除了"从 `data/custom/*.json` 加载题库"的输入模式。

**理由**：
- 用户原话："一会再讨论怎么能够加这个文件进去让他自己完成"——意思是希望 UI 自动扫描 + 选择，而不是必须先打开文件管理器
- 当前界面只剩"手动输入"一种模式，更简单
- 题库格式约定保留：`[{"type": "text"|"image", "content": str, "hint": str}]`
- `data/custom/` 目录保留（含 `.gitkeep`）方便后续重新引入

**遗留任务**：自动扫描 + UI 选择题库文件的功能未实现。

---

### D-004: 不引入新依赖（Pygame 几何绘制做所有视觉）

**背景**：所有图标、装饰、纹理都是用 `pygame.draw.*` 画的，不依赖任何外部图片。

**理由**：
- PyInstaller 打包时少一类潜在问题（资源路径、`_MEIPASS` 处理）
- 跨平台一致（Mac 开发 / Windows 部署）
- 纯代码资源 = git diff 友好

**已知代价**（用户已指出）：视觉天花板低，"看起来像几何拼图而不是真实材质"。如果未来要引入 PNG 纹理，需要：
1. `build.bat` 加 `--add-data "assets;assets"`（Windows 用分号）
2. 加载时复用 `_MEIPASS` 判断
3. 这两步不能漏，否则 exe 跑不起来找不到资源

---

### D-005: AnimationManager 是串行 FIFO 队列；EffectsManager 是并行特效层

**背景**：游戏里同时存在两类视觉变化——杯子洗牌（必须按顺序）和粒子爆炸（可并发）。

**架构选择**：
- `AnimationManager`：FIFO 队列，每次 `update(dt)` 只推进 `animations[0]`，做完才弹。所有 cup 移动 / lift / lower / shake / glow / intro 都走这条
- `EffectsManager`：并行更新所有粒子 / 浮字 / 屏幕震动 / 闪光

**理由**：
- 洗牌动画必须串行——`add_swap → add_pause → add_swap` 写法直观，开发体验好
- 粒子和屏幕震动天然并行——硬塞进队列反而难受
- 两者各司其职，互不干扰

**禁止事项**（已写进 CLAUDE.md）：
- 别往 `AnimationManager` 队列塞并行需求
- 别用 `EffectsManager` 做有先后依赖的动作

---

### D-006: ShellGame 用字符串 state 字段做状态机

**背景**：游戏内有 `init / intro / showing / guessing / revealing / result_shown / finished` 七个阶段。

**理由**：
- 字符串够用，不需要 enum 类（项目规模小）
- 状态切换由两个驱动源：`AnimationManager.done` 推进 / 鼠标点击触发
- **关键约束**：所有点击处理必须先 check `self.state`，否则会触发"动画期间能误点"的 bug——这是已写进 CLAUDE.md 的禁止事项

---

### D-007: v1.2 加 IntroBall 而不是直接放大杯子里的 ball

**背景**：图片目标在杯子里太小看不清。

**候选**：
- A. 直接放大杯子里的小球 → 牵涉 `Cup._draw_ball` 和动画系统耦合，回退期间还要恢复
- B. **新建独立 `IntroBall` 类**，单独放大 → 单独飞入 → 单独消失 ← 选定

**选定 B 的理由**：
- 关注点分离：杯子里的 ball 是"游戏内容"，IntroBall 是"展示动画"
- IntroBall 可以渲染在杯子图层之上（飞行轨迹会跨过杯子）
- 失败回退干净（图片加载失败 fallback 到 text，IntroBall 跟着 fallback）

**节奏**：2000ms 停留（用户从 1500/2000/2500 三选项里选了 2000）。

---

### D-008: v1.3 三按钮（Same Again / Adjust / Quit）而非二级弹窗

**背景**：v1.2 之前 Scoreboard 只有 Play Again / Quit，且 Play Again 语义模糊（用户问"为什么中途结束没回主页面"——其实就是 Play Again 但名字不直白）。

**候选**：
- A. **Same Again（重玩同题同难度，跳过设置页）/ Adjust（回设置页保留题目）/ Quit** ← 选定
- B. 加 Quick Settings 抽屉，运行中也可调
- C. 持久化到本地 session.json

**选定 A 的理由**（用户从三选项里选）：
- 实现路径清晰，一次改动就能落地
- 三按钮 UI 比"二级弹窗"更明示，符合"对小朋友友好"
- 抽屉方案 B 更复杂——动画暂停、是否当回合作废还是下回合生效，绕（已写进 PROJECT_STATE 作为后续候选）

**实现要点**：
- `SettingsScreen.__init__(screen, initial_settings=None)` 接收上次设置
- `main.py` 主循环维护 `last_settings`
- `skip_settings` 标志位控制 `Same Again` 跳过 SettingsScreen

---

### D-011: v1.4 选择 B2：本地像素 PNG 素材皮肤层

**背景**：用户反馈当前 UI 只是"简陋模仿"，希望更紧致，至少真正接近星露谷像素风。

**候选**：
- A. 纯代码像素化紧致版 → 快，但仍像几何 UI
- B1. 先代码生成像素质感 → 风险低，但真实素材感有限
- B2. **引入少量本地 PNG 像素素材 + 9-slice 皮肤层** ← 选定
- C. 全场景 sprite 重皮 → 最像完整游戏，但范围过大

**选定 B2 的理由**：
- 真正像游戏 UI 的关键是像素材质、硬边 9-slice、有限色阶，而不是继续加圆角/柔光
- 少量 PNG 就能覆盖面板、按钮、输入框、木纹背景和杯子 sprite，性价比高
- 新增 `game/assets.py` 后，未来可直接替换 `assets/pixel/*.png` 升级素材质量，不必重写三屏逻辑
- `build.bat` 同步加入 `--add-data "assets;assets"`，为后续音效系统也铺好资源打包路径

**约束**：
- 素材先使用项目内生成的本地 PNG，避免外部素材版权不清
- Windows exe 真实视觉仍需用户端 `build.bat` 验证

---

### D-009: 跨平台开发流程（Mac 开发 + Windows 打包）

**背景**：用户开发机是 macOS，但目标用户用 Windows。

**约定**（已写进 CLAUDE.md）：
- 路径分隔符必须 `os.path.join`，绝不硬编码
- `build.bat` 里 `--add-data "data;data"` 用分号是 Windows 写法，**不要改**
- macOS 端的核心验证只是 `python main.py` 能跑通；exe 行为差异交给 Windows 端
- 改动完成后默认假设需要 `git push`

**Mac 端无法跑真实窗口的限制**（今天发现）：
- 用户机器是 Python 3.14，pygame 2.6.1 在 3.14 上没 font 模块（编译问题）
- AI 端验证用临时 venv + pygame-ce + `SDL_VIDEODRIVER=dummy` 做 headless smoke test
- 真实视觉验证只能 Windows 端 `build.bat` 后实测

---

### D-010: 用 git tag 做版本锚点（v1.0-stardew / v1.1 / v1.2 / v1.3）

**背景**：用户提出"做一个 git commit 方便我们回滚项目"。

**做法**：
- 重要 milestone 打 annotated tag，注释里写明回滚命令
- v1.x.y 风格命名（v1.0 用了语义后缀 `-stardew` 标记重做版本）

**好处**：
- `git reset --hard v1.2` 比 `git reset --hard 6c80d89` 易记
- GitHub 自动把 tag 当成 Release，未来可以挂 exe 附件
