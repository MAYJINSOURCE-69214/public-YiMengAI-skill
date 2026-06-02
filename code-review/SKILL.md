# Code Review Skill - 代码审查

> 小 Q 专属技能 - 自动检查代码质量、安全问题、性能问题

**版本**: v1.3.0
**作者**: 小 Q
**语言**: Python

---

## 🎯 用途

自动审查代码，发现：
- 🔴 **安全问题**（SQL 注入、硬编码密码、XSS 风险）
- 🟡 **代码质量问题**（函数过长、重复代码、命名不规范）
- 🟠 **性能问题**（N+1 查询、不必要的循环）
- 🟢 **规范问题**（缺少注释、类型注解、文档字符串）

---

## 🚀 快速开始

### 方式 1：直接调用（推荐）

```python
from skills.code_review.reviewer import CodeReviewer

reviewer = CodeReviewer()
result = reviewer.review_file('src/api.py')
print(result.report)
```

### 方式 2：命令行

```bash
python -m skills.code_review.reviewer src/api.py
```

### 方式 3：小 Q 自动调用

```
你说："审查一下 src/api.py"
小 Q：自动调用 code-review 技能并返回结果
```

---

## 📋 审查清单

### 1️⃣ 安全性（最高优先级）

| 检查项 | 说明 | 严重程度 |
|--------|------|----------|
| SQL 注入 | 检测 f-string 拼接 SQL | 🔴 严重 |
| 硬编码密码 | 检测 password/api_key/secret | 🔴 严重 |
| XSS 风险 | 检测未转义的用户输入 | 🟠 高 |
| 路径遍历 | 检测文件路径未验证 | 🟠 高 |

### 2️⃣ 代码质量

| 检查项 | 说明 | 严重程度 |
|--------|------|----------|
| 函数长度 | 函数超过 50 行 | 🟡 中 |
| 重复代码 | 检测复制粘贴代码 | 🟡 中 |
| 命名规范 | 变量/函数命名是否有意义 | 🟡 中 |
| 注释缺失 | 关键逻辑没有注释 | 🟢 低 |

### 3️⃣ 性能

| 检查项 | 说明 | 严重程度 |
|--------|------|----------|
| N+1 查询 | 循环内查询数据库 | 🟠 高 |
| 内存泄漏 | 未关闭文件/连接 | 🟠 高 |
| 低效循环 | 不必要的嵌套循环 | 🟡 中 |

### 4️⃣ 错误处理

| 检查项 | 说明 | 严重程度 |
|--------|------|----------|
| 缺少 try-except | 没有异常处理 | 🟠 高 |
| 空 except | except: 不处理 | 🟡 中 |
| 日志缺失 | 错误没有日志记录 | 🟡 中 |

---

## 📊 审查报告格式

```markdown
## 🔍 代码审查报告

### ❌ 严重问题
**SQL_INJECTION**: 发现 SQL 注入风险，使用参数化查询
- 位置：src/api.py:15
- 建议：cursor.execute("SELECT * FROM t WHERE id = ?", (id,))

### ⚠️ 警告
**HARDCODED_SECRET**: 发现硬编码密码
- 位置：src/config.py:8
- 建议：使用环境变量 os.environ.get('DB_PASSWORD')

### ℹ️ 建议
**FUNCTION_TOO_LONG**: 函数过长（120 行）
- 位置：src/utils.py:45
- 建议：拆分为多个小函数

## 总体评分：65/100
**建议**: 修复严重问题后再部署
```

---

## 💡 使用示例

### 示例 1：审查 Python 文件

```python
from skills.code_review.reviewer import CodeReviewer

reviewer = CodeReviewer()

# 审查单个文件
result = reviewer.review_file('src/api.py')
print(result.report)

# 审查整个目录
results = reviewer.review_directory('src/')
for filepath, result in results.items():
    if result['score'] < 80:
        print(f"{filepath}: {result['score']}分")
```

### 示例 2：审查 Vue/JS 文件

```python
result = reviewer.review_file('src/components/UserList.vue')
print(result.report)
```

### 示例 3：Git 提交前审查

```bash
# 提交前自动审查变更的文件
git diff --name-only HEAD | xargs python -m skills.code_review.reviewer
```

---

## 🔧 配置选项

在 `reviewer.py` 中可配置：

```python
reviewer = CodeReviewer(
    max_function_length=50,      # 函数最大行数
    min_score_for_deploy=80,     # 部署最低分数
    ignore_patterns=['test_*'],  # 忽略的文件模式
    verbose=True                 # 详细输出
)
```

---

## 📁 文件结构

```
skills/code-review/
├── _meta.json           # 技能元数据
├── SKILL.md             # 本文档
├── reviewer.py          # 审查器主程序
├── checklists/          # 审查清单
│   ├── python.md
│   ├── vue.md
│   └── javascript.md
└── examples/            # 使用示例
    ├── python_review.py
    └── vue_review.py
```

---

## 🎯 自动调用规则

小 Q 会在以下情况自动调用此技能：

| 用户指令 | 自动调用 |
|----------|----------|
| "审查这个文件" | ✅ review_file() |
| "检查代码质量" | ✅ review_file() |
| "有安全问题吗" | ✅ review_security() |
| "准备部署了" | ✅ review_for_deploy() |
| "看看这段代码" | ⚠️ 需要上下文 |

---

## 📝 更新日志

### v1.0.0 (2026-04-07)
- ✅ 初始版本
- ✅ Python 代码审查
- ✅ SQL 注入检测
- ✅ 硬编码密码检测
- ✅ 函数长度检查

---

**最后更新**: 2026-04-07  
**维护者**: 小 Q
