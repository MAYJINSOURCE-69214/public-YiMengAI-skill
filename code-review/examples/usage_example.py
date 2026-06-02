"""
code-review 技能使用示例

演示如何使用小 Q 的代码审查技能
"""

from skills.code_review.reviewer import CodeReviewer


def example_1_review_single_file():
    """示例 1：审查单个文件"""
    reviewer = CodeReviewer()
    
    # 审查 Python 文件
    result = reviewer.review_file('src/api.py')
    
    print(result['report'])
    print(f"得分：{result['score']}/100")
    print(f"是否通过：{result['passed']}")


def example_2_review_directory():
    """示例 2：审查整个目录"""
    reviewer = CodeReviewer()
    
    # 审查 src 目录下所有 Python 文件
    results = reviewer.review_directory('src/', pattern='*.py')
    
    for filepath, result in results.items():
        print(f"\n{'='*50}")
        print(f"文件：{filepath}")
        print(f"得分：{result['score']}/100")
        
        if not result['passed']:
            print("⚠️ 需要修复")


def example_3_custom_config():
    """示例 3：自定义配置"""
    reviewer = CodeReviewer(config={
        'max_function_length': 30,      # 函数超过 30 行就警告
        'min_score_for_deploy': 90,     # 90 分以上才能部署
        'ignore_patterns': ['test_*', '*_test.py', 'temp/*'],
        'verbose': True
    })
    
    result = reviewer.review_file('src/main.py')
    print(result['report'])


def example_4_security_focus():
    """示例 4：专注安全检查"""
    reviewer = CodeReviewer()
    
    # 审查敏感文件（数据库、API 等）
    sensitive_files = [
        'src/database.py',
        'src/api/auth.py',
        'src/config.py'
    ]
    
    for filepath in sensitive_files:
        result = reviewer.review_file(filepath)
        
        # 只显示严重问题
        critical_issues = [i for i in result['issues'] if i['severity'] == 'CRITICAL']
        
        if critical_issues:
            print(f"\n🚨 {filepath} 发现严重安全问题：")
            for issue in critical_issues:
                print(f"  - {issue['type']}: {issue['message']}")


def example_5_git_pre_commit():
    """示例 5：Git 提交前审查"""
    import subprocess
    
    reviewer = CodeReviewer()
    
    # 获取 Git 变更的文件
    result = subprocess.run(
        ['git', 'diff', '--name-only', 'HEAD'],
        capture_output=True,
        text=True
    )
    
    changed_files = result.stdout.strip().split('\n')
    
    print("=== Git 提交前代码审查 ===\n")
    
    all_passed = True
    for filepath in changed_files:
        if filepath.endswith('.py') or filepath.endswith('.js'):
            result = reviewer.review_file(filepath)
            
            if not result['passed']:
                print(f"❌ {filepath} - {result['score']}分（未通过）")
                all_passed = False
            else:
                print(f"✅ {filepath} - {result['score']}分（通过）")
    
    if not all_passed:
        print("\n⚠️ 有文件未通过审查，建议修复后再提交")
    else:
        print("\n✅ 所有文件通过审查，可以提交")


# ========== 运行示例 ==========

if __name__ == '__main__':
    print("=" * 60)
    print("小 Q 代码审查技能 - 使用示例")
    print("=" * 60)
    
    # 选择要运行的示例
    example = input("\n选择示例 (1-5): ")
    
    if example == '1':
        example_1_review_single_file()
    elif example == '2':
        example_2_review_directory()
    elif example == '3':
        example_3_custom_config()
    elif example == '4':
        example_4_security_focus()
    elif example == '5':
        example_5_git_pre_commit()
    else:
        print("无效选择")
