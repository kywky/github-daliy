import json
import sys
from pathlib import Path
sys.path.insert(0, '/root/github-daily')
from render import render

SUMMARIES = {
  "Gathin23/cleanyourtv": "- **解决什么**：智能电视预装广告无法彻底卸载；通过 Wi-Fi + ADB 远程给 Android/Google TV 做 debloat，还附赠类 Apple TV 桌面。\n- **适合谁**：被小米/索尼/TCL 等电视广告折磨的家庭用户，不想拆机刷机的场景。\n- **亮点**：全程 Wi-Fi 操作、一键恢复原状，主打「反悔友好」。",
  "deepseek-ai/DeepInfer": "- **解决什么**：DeepSeek 系列模型高并发部署时的推理效率和工程复杂度问题。\n- **适合谁**：自托管 DeepSeek 的团队、云服务商、研究机构。\n- **亮点**：官方出品，针对 MoE 架构深度优化，性能可预期。",
  "feder-cr/git-ai": "- **解决什么**：Git 是给人类设计的，AI agent 频繁 commit/merge 会踩锁、身份、并发等一系列坑。\n- **适合谁**：做 coding agent、agent swarm、自动化重构的团队。\n- **亮点**：底层基于 SCION 网络协议，走「机器优先版本控制」路线。",
  "ly05010419/MacNativeGames": "- **解决什么**：仓库描述缺失，从名称与 C 语言推测是 Mac 原生游戏移植/合集类项目。\n- **适合谁**：Mac 玩家、想在 macOS 上跑老游戏的人。\n- **亮点**：一周 2500 星说明社区需求真实存在（详情需自行进 README 核对）。",
  "ahwootech/BRUTAL": "- **解决什么**：C# 开发者想直接调 Vulkan/原生 API 做游戏引擎时，缺少一层不封装过头的框架。\n- **适合谁**：自研引擎、做商业游戏的团队；用惯 C# 但不想被 MonoGame 束缚的人。\n- **亮点**：RimWorld 的 Waylith 引擎和 Kitten Space Agency 的底座，工业级验证过。",
  "chenglou/handwired": "- **解决什么**：把普通 JavaScript 函数直接编译成神经网络，让 JS 逻辑跑在推理上。\n- **适合谁**：探索「代码即模型」边界的研究者、爱尝鲜的前端。\n- **亮点**：作者 chenglou（React Native/OkMeter 老兵），思路非常先锋。",
  "Leonxlnx/earshot": "- **解决什么**：coding agent 听不见声音，无法审音效或做音频相关工作。\n- **适合谁**：游戏/短视频/音效工作流的开发者，需要 agent 评估音频质量时。\n- **亮点**：MCP 协议封装，纯 CPU 运行不需要 GPU。",
  "Supermedo/uncharted_pc": "- **解决什么**：把 PS 独占的《神秘海域：内森·德雷克合集》原生移植到 Windows。\n- **适合谁**：没 PS5 又想玩这套经典剧情的 PC 玩家。\n- **亮点**：民间移植硬核案例，一周冲到 1600+ 星。",
  "xiaoyang111222/cn-math-taxonomy": "- **解决什么**：K12 数学缺少对齐课标的、结构化、可诊断的知识图谱数据。\n- **适合谁**：EdTech 团队、老师、家长、做 AI 家教产品的人。\n- **亮点**：人教版小初高全覆盖，802 知识点 + 3355 题 + 自适应诊断，直接可接进 RAG。",
  "Caho1/open-claude-ui": "- **解决什么**：Claude 官方桌面端的 UI 与动效细节没有可参考的开源实现。\n- **适合谁**：做 AI 客户端产品的设计师与前端。\n- **亮点**：30 个 React 组件 + 8 个动效物理算法，附 3000+ 行逆向手册，教材价值大于代码。",
  "aicodeking/leanrea": "- **解决什么**：MCP 太重，逆向工程类工具需要更轻的调用方式。\n- **适合谁**：想让 agent 轻装上阵、讨厌 MCP 依赖的开发者。\n- **亮点**：8 KB 一个 skill 顶掉整个 REA，官方基准 38% 更快、35% 更省。",
  "OpenMOSS/MOSS-Image": "- **解决什么**：扩散模型在中文/精确文字渲染和版面控制上的老问题。\n- **适合谁**：需要生成海报、封面、UI mockup 里准确文字的产品和设计团队。\n- **亮点**：复旦 MOSS 团队 5B DiT 底座，官方开源权重、支持高效微调。",
  "alchaincyf/huashu-motion": "- **解决什么**：产品宣传片外包贵、迭代慢，改一帧要来回沟通。\n- **适合谁**：独立开发者、创业团队做 launch video。\n- **亮点**：基于 GSAP，agent 生成 + 指着画面改，动效工作流搬进对话。",
  "simbasjungles/free-my-tv": "- **解决什么**：Google TV 主屏广告卡顿，需要第三方启动器替代。\n- **适合谁**：Google TV 设备用户。\n- **亮点**：整个项目本身就是用 Claude Code vibe-coded 出来，主打一键撤销。",
  "xscreensaver-official/xscreensaver": "- **解决什么**：仿冒 XScreenSaver 的仓库在 GitHub 上钓鱼；作者用同名仓库做防伪声明。\n- **适合谁**：所有还想在 GitHub 搜 xscreensaver 的人。\n- **亮点**：一周 1000+ 星说明真有人上过当，属于行为艺术级的安全提醒。",
}

data = json.load(open('/root/github-daily/dist/repos.json'))
for r in data['repos']:
    if r['full_name'] in SUMMARIES:
        r['summary'] = SUMMARIES[r['full_name']]
    else:
        print('MISS:', r['full_name'])

json.dump(data, open('/root/github-daily/dist/repos.json','w'), ensure_ascii=False, indent=2)
open('/root/github-daily/dist/index.html','w').write(render(data['repos'], data['window_start'], data['window_end']))
print('✓ 已用本地生成的中文摘要重写 dist')
