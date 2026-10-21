import random
from datetime import date, timedelta


CLASSIC_COOLDOWN_DAYS = 60

# 适合精读的公开经典小项目：体量可控、代码质量高、读完能直接用到日常工作里。
CLASSICS = {
    "C": [
        ("antirez/linenoise", "几百行的 readline 替代，命令行交互的教科书级小实现"),
        ("antirez/sds", "Redis 的动态字符串库，两个文件讲清 C 的内存管理"),
        ("DaveGamble/cJSON", "零依赖的单文件 JSON 解析器，适合学手写解析器"),
        ("nothings/stb", "一批单文件图像/字体库，看资深作者如何组织头文件库"),
        ("munificent/craftinginterpreters", "《Crafting Interpreters》配套 C 实现，完整可跑的解释器"),
        ("lua/lua", "小巧优雅的解释器源码，公认最适合读的 C 项目之一"),
        ("skywind3000/kcp", "百行级 ARQ 可靠 UDP 协议，网络编程入门经典"),
        ("Tencent/libco", "不到 200 行的协程切换库，读懂上下文切换原理"),
        ("cstack/db_tutorial", "《Let's Build a Simple Database》配套代码，从零写存储引擎"),
        ("Cyan4973/xxHash", "高性能哈希函数，能学到位运算与缓存友好优化"),
        ("cesanta/mongoose", "单文件嵌入式 HTTP 服务器，学 socket 与 HTTP 状态机"),
        ("raysan5/raylib", "游戏向图形库，API 简洁，适合读渲染主循环"),
        ("richgel999/miniz", "单文件 zlib 兼容压缩实现，读 deflate 的最佳入口"),
    ],
    "C++": [
        ("nlohmann/json", "单文件 JSON 库，现代 C++ API 与模板设计范本"),
        ("yhirose/cpp-httplib", "单文件 HTTP 服务器/客户端，读线程与 socket 的好材料"),
        ("doctest/doctest", "轻量单头测试框架，宏与模板技巧密集"),
        ("catchorg/Catch2", "自注册测试框架，看 C++ 如何做声明式 API"),
        ("fmtlib/fmt", "格式化库，编译期检查与性能优化的代表作"),
        ("google/googletest", "测试框架的标准实现，工程结构清晰"),
        ("ocornut/imgui", "即时模式 GUI，理解渲染循环与状态管理的最佳样本"),
        ("zeux/pugixml", "小巧 XML 解析库，内存池与迭代器设计干净"),
        ("Neargye/magic_enum", "编译期枚举反射，理解模板元编程的趣味项目"),
        ("cameron314/readerwriterqueue", "单生产单消费无锁队列，并发编程入门"),
        ("simdjson/simdjson", "SIMD 加速 JSON 解析，性能优化进阶读物"),
        ("ericniebler/range-v3", "Range 库实现，读 STL 扩展与组合子设计"),
        ("wolfpld/tracy", "实时性能分析器，客户端/服务端结构值得一读"),
    ],
    "Python": [
        ("bottlepy/bottle", "单文件微框架，几千行读懂 WSGI 路由与模板"),
        ("psf/requests", "被引用最多的 Python 库之一，API 设计教科书"),
        ("pallets/click", "CLI 框架，装饰器驱动的命令行组织方式"),
        ("pallets/werkzeug", "WSGI 工具库，HTTP 语义实现最全的参考"),
        ("encode/starlette", "小型 ASGI 框架，async 路由与中间件范例"),
        ("encode/uvicorn", "ASGI 服务器，读事件循环与 HTTP 协议解析"),
        ("tiangolo/fastapi", "类型驱动的 API 框架，看依赖注入怎么用"),
        ("Textualize/rich", "终端富文本库，颜色、表格、进度的实现都值得学"),
        ("dbader/schedule", "百行人话版定时任务库，入门级源码"),
        ("tomerfiliba/plumbum", "Shell 操作库，运算符重载设计巧妙"),
        ("httpie/httpie", "友好的 curl，读 CLI 分层与插件架构"),
        ("pyparsing/pyparsing", "纯 Python 解析器组合子，DSL 设计经典"),
        ("yt-dlp/yt-dlp", "视频下载器，上千站点提取器的插件式抽象"),
    ],
}

LANGS = list(CLASSICS)


def pick_languages(today: date, k: int = 2) -> list[str]:
    """同一天固定同一组语言，重跑不会变。"""
    return sorted(random.Random(today.isoformat()).sample(LANGS, k), key=LANGS.index)


def last_shown(entry_name: str, shown: dict[str, str]) -> date:
    value = shown.get(entry_name)
    return date.fromisoformat(value) if value else date.min


def candidates(lang: str, shown: dict[str, str], today: date, limit: int = 3) -> list[tuple[str, str]]:
    """返回该语言最久未推荐的前几项，供 main 逐个取实时数据（仓库改名/删除时自动跳过）。"""
    cutoff = today - timedelta(days=CLASSIC_COOLDOWN_DAYS)
    entries = list(CLASSICS[lang])
    fresh = [e for e in entries if last_shown(e[0], shown) < cutoff]
    pool = fresh or entries
    return sorted(pool, key=lambda e: (last_shown(e[0], shown), entries.index(e)))[:limit]
