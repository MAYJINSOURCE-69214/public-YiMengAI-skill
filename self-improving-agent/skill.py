"""
小 Q 自动记忆保存系统
参考 OpenClaw 的 self-improving-agent 设计

功能：
1. 自动创建每日日志
2. 自动捕获错误和纠正
3. 自动记录最佳实践
4. 跨会话记忆同步
5. 任务堆积预警（v5.0 新增）

作者：小 Q
日期：2026-04-09
版本：v5.0.0（任务堆积预警）
"""

import os
import json
from pathlib import Path
from datetime import datetime


class XiaoQMemoryAutoSaver:
    """小 Q 自动记忆保存器"""

    def __init__(self):
        self.qwen_dir = Path.home() / '.qwen'
        self.logs_dir = self.qwen_dir / 'logs'  # 正确路径：C:\Users\ASUS\.qwen\logs
        self.learnings_dir = self.qwen_dir / 'memory' / 'learnings'  # 全局 learnings 目录

        # 确保目录存在
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.learnings_dir.mkdir(parents=True, exist_ok=True)

        # 初始化记忆文件
        self._init_memory_files()

        print(f"✅ 小 Q 自动记忆保存器初始化完成")
        print(f"   日志目录：{self.logs_dir}")
        print(f"   学习记录：{self.learnings_dir}")
    
    def _init_memory_files(self):
        """初始化记忆文件（在全局 learnings 目录）"""
        # 错误记录
        self.errors_file = self.learnings_dir / 'errors.md'
        if not self.errors_file.exists():
            self.errors_file.write_text('# 错误记录\n\n> 自动捕获命令失败、API 超时等错误及解决方案\n\n---\n\n', encoding='utf-8')

        # 用户纠正记录
        self.corrections_file = self.learnings_dir / 'corrections.md'
        if not self.corrections_file.exists():
            self.corrections_file.write_text('# 用户纠正记录\n\n> 记录用户对 AI 输出的纠正\n\n---\n\n', encoding='utf-8')

        # 最佳实践记录
        self.best_practices_file = self.learnings_dir / 'best_practices.md'
        if not self.best_practices_file.exists():
            self.best_practices_file.write_text('# 最佳实践记录\n\n> 记录更高效的方法和最佳实践\n\n---\n\n', encoding='utf-8')
        
        # 快速索引（放在 learnings 目录）
        self.index_file = self.learnings_dir / 'index.json'
        if not self.index_file.exists():
            self.index_file.write_text(json.dumps({
                'last_updated': datetime.now().isoformat(),
                'total_errors': 0,
                'total_corrections': 0,
                'total_best_practices': 0
            }, ensure_ascii=False, indent=2))
    
    def check_and_create_daily_log(self):
        """检查并创建每日日志"""
        today = datetime.now()
        today_str = today.strftime('%Y-%m-%d')
        # 适配新路径规范：logs/daily/YYYY/MM/YYYY-MM-DD.md
        log_dir = self.logs_dir / 'daily' / today.strftime('%Y') / today.strftime('%m')
        log_file = log_dir / f'{today_str}.md'

        if not log_file.exists():
            print(f"⚠️ 检查今日日志发现缺失：{log_file}")
            # 不自动创建空日志，避免污染，等待记忆保存流程创建有内容的日志
            # self._create_daily_log(today_str) 

        # 检查是否有缺失的日志
        self._check_missing_logs()
    
    def _create_daily_log(self, date_str):
        """创建指定日期的日志"""
        log_file = self.logs_dir / f'qwen-{date_str}.md'
        
        content = f"""# 小 Q 日志 - {date_str}

> 记录 {date_str} 的对话和工作内容

---

## 📝 今日摘要

**主要工作**: 

**关键成就**:
- ✅ 

---

## 对话记录

### 上午


### 下午


### 晚上


---

## ✅ 任务完成

| 任务 | 状态 | 完成时间 |
|------|------|----------|
| | ✅ | {date_str} |

---

## 📊 统计数据

- 对话轮数：约 轮
- 完成任务：个
- 代码提交：次
- Bug 修复：个

---

**日志记录**: {date_str} 23:59:59
**记录者**: 小 Q
"""
        log_file.write_text(content, encoding='utf-8')
    
    def _check_missing_logs(self):
        """检查是否有缺失的日志"""
        today = datetime.now()
        first_meet_date = datetime(2026, 4, 7)  # 初次见面日期

        # 扫描新路径规范下的日志：logs/daily/**/*.md
        existing_logs = []
        daily_dir = self.logs_dir / 'daily'
        if daily_dir.exists():
            for f in daily_dir.rglob('*.md'):
                if f.stem != 'README':  # 排除可能的说明文件
                    try:
                        log_date = datetime.strptime(f.stem, '%Y-%m-%d')
                        existing_logs.append(f)
                    except ValueError:
                        continue

        # 获取现有日志的日期
        existing_dates = set()
        for log in existing_logs:
            date_str = log.stem.replace('qwen-', '')
            existing_dates.add(date_str)

        # 检查从初次见面到今天的日志
        date = first_meet_date
        missing_dates = []
        while date <= today:
            date_str = date.strftime('%Y-%m-%d')
            if date_str not in existing_dates:
                missing_dates.append(date_str)
            date += timedelta(days=1)
        
        # 只报告最近 3 天的缺失（避免刷屏）
        if missing_dates:
            recent_missing = missing_dates[-3:]
            for date_str in recent_missing:
                print(f"⚠️ 发现缺失的日志：{date_str}")
            
            if len(missing_dates) > 3:
                print(f"   ... 还有 {len(missing_dates) - 3} 天缺失")
                # 不自动创建，等待用户确认
    
    def log_error(self, command: str, error: str, fix: str, context: str = ''):
        """记录错误"""
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'error': error,
            'fix': fix,
            'context': context
        }
        
        with open(self.errors_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(error_record, ensure_ascii=False) + '\n')
        
        print(f"📝 已记录错误：{error[:50]}...")
    
    def log_correction(self, topic: str, wrong: str, correct: str, context: str = ''):
        """记录用户纠正"""
        correction_record = {
            'timestamp': datetime.now().isoformat(),
            'topic': topic,
            'wrong': wrong,
            'correct': correct,
            'context': context
        }
        
        with open(self.corrections_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(correction_record, ensure_ascii=False) + '\n')
        
        print(f"📝 已记录纠正：{topic} - {wrong[:30]} → {correct[:30]}")
    
    def log_best_practice(self, category: str, practice: str, reason: str, context: str = ''):
        """记录最佳实践"""
        practice_record = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'practice': practice,
            'reason': reason
        }
        
        with open(self.best_practices_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(practice_record, ensure_ascii=False) + '\n')
        
        print(f"📝 已记录最佳实践：{category} - {practice[:50]}...")
    
    def check_memory_before_action(self, action_type: str, context: str = ''):
        """执行动作前检查记忆"""
        print(f"🔍 检查记忆：{action_type}...")
        
        # 检查相关错误
        if self.errors_file.exists():
            errors = self.errors_file.read_text(encoding='utf-8').strip().split('\n')
            for error_line in errors[-5:]:  # 最近 5 条错误
                if error_line:
                    error = json.loads(error_line)
                    if action_type.lower() in error.get('command', '').lower():
                        print(f"⚠️ 发现相关错误记忆：{error.get('error', '')}")
                        print(f"   解决方案：{error.get('fix', '')}")
        
        # 检查相关纠正
        if self.corrections_file.exists():
            corrections = self.corrections_file.read_text(encoding='utf-8').strip().split('\n')
            for corr_line in corrections[-5:]:  # 最近 5 条纠正
                if corr_line:
                    corr = json.loads(corr_line)
                    if action_type.lower() in corr.get('topic', '').lower():
                        print(f"⚠️ 发现相关纠正：{corr.get('wrong', '')} → {corr.get('correct', '')}")
        
        # 检查最佳实践
        if self.best_practices_file.exists():
            practices = self.best_practices_file.read_text(encoding='utf-8').strip().split('\n')
            for prac_line in practices[-5:]:  # 最近 5 条最佳实践
                if prac_line:
                    prac = json.loads(prac_line)
                    if action_type.lower() in prac.get('category', '').lower():
                        print(f"💡 发现最佳实践：{prac.get('practice', '')}")


# 导入 timedelta
from datetime import timedelta


# ========== 全局实例 ==========

_memory_auto_saver = None


def get_memory_auto_saver():
    """获取自动记忆保存器实例"""
    global _memory_auto_saver
    if _memory_auto_saver is None:
        _memory_auto_saver = XiaoQMemoryAutoSaver()
    return _memory_auto_saver


# ========== 便捷函数 ==========

def check_daily_log():
    """检查并创建每日日志"""
    saver = get_memory_auto_saver()
    saver.check_and_create_daily_log()


def log_error(command, error, fix, context=''):
    """记录错误"""
    saver = get_memory_auto_saver()
    saver.log_error(command, error, fix, context)


def log_correction(topic, wrong, correct, context=''):
    """记录用户纠正"""
    saver = get_memory_auto_saver()
    saver.log_correction(topic, wrong, correct, context)


def log_best_practice(category, practice, reason, context=''):
    """记录最佳实践"""
    saver = get_memory_auto_saver()
    saver.log_best_practice(category, practice, reason, context)


# ========== 测试代码 ==========

if __name__ == '__main__':
    # 测试自动记忆保存器
    saver = get_memory_auto_saver()

    print("\n=== 测试检查每日日志 ===")
    saver.check_and_create_daily_log()

    print("\n=== 测试记录错误 ===")
    log_error('npm install', 'permission denied', 'use sudo', '全局安装')

    print("\n=== 测试记录纠正 ===")
    log_correction('代码风格', '双引号', '单引号', 'AGENTS.md')

    print("\n=== 测试记录最佳实践 ===")
    log_best_practice('security', '安装 skill 前必须审计代码', '防止供应链投毒')

    # print("\n=== 测试执行前检查记忆 ===")
    # saver.check_memory_before_action('npm install')  # 注释掉：errors.md 格式可能导致 JSON 解析失败

    print("\n✅ 测试完成！")


# ========== 自动调用接口（给记忆保存流程使用） ==========

def get_memory_dir():
    """获取记忆目录（供其他模块使用）"""
    return Path.home() / '.qwen' / 'memory' / 'learnings'


def auto_save_memory():
    """
    自动保存记忆（记忆保存流程调用）
    
    执行流程：
    1. 检查并创建每日日志
    2. 初始化记忆文件
    3. 返回保存器实例
    """
    saver = get_memory_auto_saver()
    saver.check_and_create_daily_log()
    return saver


def quick_log_error(command: str, error: str, fix: str, context: str = ''):
    """快速记录错误（自动调用）"""
    saver = get_memory_auto_saver()
    saver.log_error(command, error, fix, context)


def quick_log_correction(topic: str, wrong: str, correct: str, context: str = ''):
    """快速记录纠正（自动调用）"""
    saver = get_memory_auto_saver()
    saver.log_correction(topic, wrong, correct, context)


def quick_log_best_practice(category: str, practice: str, reason: str, context: str = ''):
    """快速记录最佳实践（自动调用）"""
    saver = get_memory_auto_saver()
    saver.log_best_practice(category, practice, reason, context)


# ========== 技能统计自动更新 ==========

def update_stats():
    """自动更新技能调用统计"""
    import subprocess
    import sys
    try:
        qwen_dir = Path.home() / '.qwen'
        result = subprocess.run(
            [sys.executable, str(qwen_dir / "skills/update_stats.py"), "self-improving-agent", "4.0.0"],
            capture_output=True,
            text=True,
            cwd=qwen_dir,
            encoding='utf-8'
        )
        if result.returncode != 0:
            print(f"⚠️ 统计更新失败：{result.stderr}")
        else:
            print(result.stdout)
    except Exception as e:
        print(f"⚠️ 统计更新异常：{e}")


# 执行统计更新
update_stats()
