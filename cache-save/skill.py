# cache-save skill - main program
"""
缓存保存技能入口 (v1.3.0)
职责：更新调用统计 + 引导 AI 读取 SKILL.md 执行流程
"""

import subprocess
import sys
from pathlib import Path


def update_stats():
    """自动更新技能调用统计"""
    try:
        qwen_dir = Path(__file__).parent.parent.parent
        result = subprocess.run(
            [sys.executable, str(qwen_dir / "skills" / "update_stats.py"), "cache-save", "1.2.0"],
            capture_output=True,
            text=True,
            encoding='utf-8',  # 修复 Windows 下的 GBK 编码报错
            cwd=qwen_dir
        )
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"⚠️ 统计更新失败：{result.stderr}")
    except Exception as e:
        print(f"⚠️ 统计更新异常：{e}")


def main():
    """主入口"""
    # 1. 更新统计
    update_stats()
    
    # 2. 引导 AI
    print("\n📖 请读取 skills/cache-save/SKILL.md 了解完整缓存保存流程（六步防遗漏）。")
    print("💡 提示：后续步骤由 AI 在对话中按规范执行（找锚点 -> 补全缺失 -> 写入 -> 验证）。")


if __name__ == "__main__":
    main()
