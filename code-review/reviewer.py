"""
小 Q 代码审查器 - 自动化代码质量检查

用法:
    from skills.code_review.reviewer import CodeReviewer
    
    reviewer = CodeReviewer()
    result = reviewer.review_file('src/api.py')
    print(result.report)

或者命令行:
    python -m skills.code_review.reviewer src/api.py
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class CodeReviewer:
    """代码审查器 - 自动检查代码质量、安全问题、性能问题"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化代码审查器
        
        Args:
            config: 配置选项
                - max_function_length: 函数最大行数（默认 50）
                - min_score_for_deploy: 部署最低分数（默认 80）
                - ignore_patterns: 忽略的文件模式（默认 ['test_*', '*_test.py']）
                - verbose: 详细输出（默认 False）
        """
        self.config = config or {}
        self.max_function_length = self.config.get('max_function_length', 50)
        self.min_score_for_deploy = self.config.get('min_score_for_deploy', 80)
        self.ignore_patterns = self.config.get('ignore_patterns', ['test_*', '*_test.py'])
        self.verbose = self.config.get('verbose', False)
        
        self.issues = []
        self.filepath = None
        self.source_code = None
        
        print(f"✅ 代码审查器已初始化")
    
    def review_file(self, filepath: str) -> Dict[str, Any]:
        """
        审查单个文件
        
        Args:
            filepath: 文件路径
            
        Returns:
            {'score': int, 'report': str, 'issues': list}
        """
        self.issues = []
        self.filepath = Path(filepath)
        
        if not self.filepath.exists():
            return {
                'score': 0,
                'report': f"❌ 文件不存在：{filepath}",
                'issues': []
            }
        
        # 读取文件内容
        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.source_code = f.read()
        
        # 根据文件类型选择审查方式
        if self.filepath.suffix == '.py':
            self._review_python_file()
        elif self.filepath.suffix in ['.js', '.ts', '.vue']:
            self._review_javascript_file()
        else:
            self.issues.append({
                'severity': 'INFO',
                'type': 'UNSUPPORTED_FILE_TYPE',
                'message': f'不支持的文件类型：{self.filepath.suffix}',
                'line': 0
            })
        
        return self._generate_report()
    
    def review_directory(self, dirpath: str, pattern: str = "*.py") -> Dict[str, Dict]:
        """
        审查整个目录
        
        Args:
            dirpath: 目录路径
            pattern: 文件匹配模式
            
        Returns:
            {filepath: {'score': int, 'report': str, 'issues': list}}
        """
        results = {}
        dirpath = Path(dirpath)
        
        for filepath in dirpath.glob(pattern):
            # 跳过忽略的文件
            if any(filepath.match(p) for p in self.ignore_patterns):
                continue
            
            result = self.review_file(str(filepath))
            results[str(filepath)] = result
        
        return results
    
    def _review_python_file(self):
        """审查 Python 文件"""
        # 1. 检查 SQL 注入
        self._check_sql_injection()
        
        # 2. 检查硬编码密码
        self._check_hardcoded_secrets()
        
        # 3. 检查函数长度
        self._check_function_length()
        
        # 4. 检查重复代码
        self._check_duplicate_code()
        
        # 5. 检查导入
        self._check_imports()
        
        # 6. 检查注释
        self._check_comments()
        
        # 7. 检查异常处理
        self._check_exception_handling()
    
    def _review_javascript_file(self):
        """审查 JavaScript/TypeScript 文件"""
        # 1. 检查 SQL 注入（如果有）
        self._check_sql_injection()
        
        # 2. 检查硬编码密码
        self._check_hardcoded_secrets()
        
        # 3. 检查 console.log
        self._check_console_log()
        
        # 4. 检查 var 使用
        self._check_var_usage()
        
        # 5. 检查回调地狱
        self._check_callback_hell()
    
    def _check_sql_injection(self):
        """检查 SQL 注入风险"""
        # 检测 f-string 拼接 SQL
        patterns = [
            r'execute\s*\(\s*f["\'].*SELECT.*\{.*\}.*["\']\s*\)',
            r'execute\s*\(\s*f["\'].*INSERT.*\{.*\}.*["\']\s*\)',
            r'execute\s*\(\s*f["\'].*UPDATE.*\{.*\}.*["\']\s*\)',
            r'execute\s*\(\s*f["\'].*DELETE.*\{.*\}.*["\']\s*\)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, self.source_code, re.IGNORECASE)
            if matches:
                line_num = self._find_line_number(matches[0])
                self.issues.append({
                    'severity': 'CRITICAL',
                    'type': 'SQL_INJECTION',
                    'message': '发现 SQL 注入风险，使用参数化查询',
                    'line': line_num,
                    'code': matches[0][:100],
                    'suggestion': '使用参数化查询：cursor.execute("SELECT * FROM t WHERE id = ?", (id,))'
                })
    
    def _check_hardcoded_secrets(self):
        """检查硬编码密码/API Key"""
        patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', '密码'),
            (r'passwd\s*=\s*["\'][^"\']+["\']', '密码'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'API Key'),
            (r'apikey\s*=\s*["\'][^"\']+["\']', 'API Key'),
            (r'secret\s*=\s*["\'][^"\']+["\']', '密钥'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'Token'),
            (r'auth_token\s*=\s*["\'][^"\']+["\']', 'Auth Token'),
        ]
        
        for pattern, secret_type in patterns:
            matches = re.findall(pattern, self.source_code, re.IGNORECASE)
            if matches:
                line_num = self._find_line_number(matches[0])
                self.issues.append({
                    'severity': 'CRITICAL',
                    'type': 'HARDCODED_SECRET',
                    'message': f'发现硬编码{secret_type}，应使用环境变量',
                    'line': line_num,
                    'code': matches[0][:100],
                    'suggestion': f'使用 os.environ.get("{secret_type.upper()}")'
                })
    
    def _check_function_length(self):
        """检查函数长度"""
        try:
            tree = ast.parse(self.source_code)
        except SyntaxError:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 计算函数行数
                start_line = node.lineno
                end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 50
                func_length = end_line - start_line + 1
                
                if func_length > self.max_function_length:
                    self.issues.append({
                        'severity': 'MEDIUM',
                        'type': 'FUNCTION_TOO_LONG',
                        'message': f'函数过长（{func_length}行），建议拆分为多个小函数',
                        'line': start_line,
                        'code': f'def {node.name}(...)',
                        'suggestion': '将函数拆分为多个职责单一的小函数'
                    })
    
    def _check_duplicate_code(self):
        """检查重复代码（简单版：检测重复行）"""
        lines = self.source_code.split('\n')
        line_counts = {}
        
        for i, line in enumerate(lines):
            line = line.strip()
            if len(line) > 20:  # 忽略短行
                line_counts[line] = line_counts.get(line, 0) + 1
        
        for line, count in line_counts.items():
            if count >= 3:  # 同样的代码出现 3 次以上
                line_num = self._find_line_number(line)
                self.issues.append({
                    'severity': 'LOW',
                    'type': 'DUPLICATE_CODE',
                    'message': f'发现重复代码（出现{count}次），建议提取为函数',
                    'line': line_num,
                    'code': line[:100],
                    'suggestion': '提取为公共函数或循环'
                })
    
    def _check_imports(self):
        """检查导入语句"""
        # 检查未使用的导入
        try:
            tree = ast.parse(self.source_code)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imports.append(alias.name)
            
            # 简单检查：如果导入的模块名没在代码中出现（除了导入行）
            for imp in imports:
                module_name = imp.split('.')[0]
                # 计算出现次数（减去导入语句本身）
                count = len(re.findall(rf'\b{module_name}\b', self.source_code))
                if count <= 1:
                    self.issues.append({
                        'severity': 'LOW',
                        'type': 'UNUSED_IMPORT',
                        'message': f'可能未使用的导入：{imp}',
                        'line': 0,
                        'code': f'import {imp}',
                        'suggestion': '移除未使用的导入'
                    })
        except SyntaxError:
            pass
    
    def _check_comments(self):
        """检查注释"""
        # 检查类/函数是否有文档字符串
        try:
            tree = ast.parse(self.source_code)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    docstring = ast.get_docstring(node)
                    if not docstring and node.name[0].isupper():
                        self.issues.append({
                            'severity': 'LOW',
                            'type': 'MISSING_DOCSTRING',
                            'message': f'{"类" if isinstance(node, ast.ClassDef) else "函数"}缺少文档字符串',
                            'line': node.lineno,
                            'code': f'{"class" if isinstance(node, ast.ClassDef) else "def"} {node.name}(...)',
                            'suggestion': '添加文档字符串说明用途'
                        })
        except SyntaxError:
            pass
    
    def _check_exception_handling(self):
        """检查异常处理"""
        # 检查空的 except
        pattern = r'except\s*:'
        matches = re.findall(pattern, self.source_code)
        if matches:
            self.issues.append({
                'severity': 'MEDIUM',
                'type': 'BARE_EXCEPT',
                'message': '发现空的 except 子句，会捕获所有异常（包括 SystemExit、KeyboardInterrupt）',
                'line': 0,
                'code': 'except:',
                'suggestion': '使用 except Exception: 或指定具体异常类型'
            })
        
        # 检查 except 后不处理
        pattern = r'except.*:\s*\n\s*pass\s*\n'
        matches = re.findall(pattern, self.source_code, re.MULTILINE)
        if matches:
            self.issues.append({
                'severity': 'LOW',
                'type': 'EMPTY_EXCEPTION_HANDLER',
                'message': '异常被静默忽略，可能导致问题难以调试',
                'line': 0,
                'code': 'except ...:\n    pass',
                'suggestion': '添加日志记录或重新抛出异常'
            })
    
    def _check_console_log(self):
        """检查 JavaScript 中的 console.log"""
        matches = re.findall(r'console\.log\(', self.source_code)
        if matches:
            self.issues.append({
                'severity': 'LOW',
                'type': 'CONSOLE_LOG',
                'message': '发现 console.log，生产环境应移除或使用正式日志库',
                'line': 0,
                'code': 'console.log(...)',
                'suggestion': '使用正式日志库（如 winston、log4js）'
            })
    
    def _check_var_usage(self):
        """检查 JavaScript 中的 var 使用"""
        matches = re.findall(r'\bvar\b', self.source_code)
        if matches:
            self.issues.append({
                'severity': 'LOW',
                'type': 'VAR_USAGE',
                'message': '发现 var 关键字，建议使用 let 或 const',
                'line': 0,
                'code': 'var x = ...',
                'suggestion': '使用 let（可变）或 const（不可变）'
            })
    
    def _check_callback_hell(self):
        """检查 JavaScript 回调地狱"""
        # 简单检测：统计嵌套的 .then( 或回调
        depth = self.source_code.count('.then(')
        if depth >= 5:
            self.issues.append({
                'severity': 'MEDIUM',
                'type': 'CALLBACK_HELL',
                'message': f'发现深度嵌套的 Promise（{depth}层），建议使用 async/await',
                'line': 0,
                'code': '.then(...).then(...)...',
                'suggestion': '使用 async/await 语法简化代码'
            })
    
    def _find_line_number(self, code_snippet: str) -> int:
        """查找代码片段所在的行号"""
        lines = self.source_code.split('\n')
        for i, line in enumerate(lines, 1):
            if code_snippet[:50] in line:
                return i
        return 0
    
    def _generate_report(self) -> Dict[str, Any]:
        """生成审查报告"""
        report = "## 🔍 代码审查报告\n\n"
        report += f"**文件**: {self.filepath}\n"
        report += f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if not self.issues:
            report += "✅ 没有发现问题！代码质量良好。\n"
            return {'score': 100, 'report': report, 'issues': []}
        
        # 按严重程度分组
        critical = [i for i in self.issues if i['severity'] == 'CRITICAL']
        high = [i for i in self.issues if i['severity'] == 'HIGH']
        medium = [i for i in self.issues if i['severity'] == 'MEDIUM']
        low = [i for i in self.issues if i['severity'] == 'LOW']
        info = [i for i in self.issues if i['severity'] == 'INFO']
        
        if critical:
            report += "### ❌ 严重问题\n"
            for issue in critical:
                report += f"**{issue['type']}**: {issue['message']}\n"
                if issue.get('line'):
                    report += f"- 位置：第{issue['line']}行\n"
                if issue.get('suggestion'):
                    report += f"- 建议：{issue['suggestion']}\n\n"
        
        if high:
            report += "### ⚠️ 警告\n"
            for issue in high:
                report += f"**{issue['type']}**: {issue['message']}\n"
                if issue.get('line'):
                    report += f"- 位置：第{issue['line']}行\n"
                if issue.get('suggestion'):
                    report += f"- 建议：{issue['suggestion']}\n\n"
        
        if medium:
            report += "### ℹ️ 建议\n"
            for issue in medium:
                report += f"**{issue['type']}**: {issue['message']}\n"
                if issue.get('suggestion'):
                    report += f"- 建议：{issue['suggestion']}\n\n"
        
        if low or info:
            report += "### 📝 其他\n"
            for issue in low + info:
                report += f"- {issue['message']}\n"
        
        # 计算分数
        score = 100
        score -= len(critical) * 25
        score -= len(high) * 15
        score -= len(medium) * 5
        score -= len(low) * 2
        score = max(0, score)
        
        report += f"\n---\n\n## 总体评分：**{score}/100**\n"
        
        if score >= self.min_score_for_deploy:
            report += "\n✅ **可以部署**\n"
        else:
            report += f"\n⚠️ **建议修复严重问题后再部署**（最低要求：{self.min_score_for_deploy}分）\n"
        
        return {
            'score': score,
            'report': report,
            'issues': self.issues,
            'passed': score >= self.min_score_for_deploy
        }


# ========== 命令行入口 ==========

if __name__ == '__main__':
    import sys

    reviewer = CodeReviewer()
    
    if len(sys.argv) < 2:
        print("用法：python reviewer.py <文件路径>")
        print("示例：python reviewer.py src/api.py")
        sys.exit(1)
    
    filepath = sys.argv[1]
    result = reviewer.review_file(filepath)

    print(result['report'])

# ========== 技能统计自动更新 ==========
from pathlib import Path
def update_stats():
    import subprocess
    try:
        qwen_dir = Path(__file__).parent.parent.parent
        subprocess.run(
            [sys.executable, "skills/update_stats.py", "code-review", "1.0.0"],
            capture_output=True, text=True, cwd=qwen_dir
        )
    except: pass

update_stats()
