# 测试体系

项目使用结构化行为样例验证规则和 Skills，不把固定措辞当作通过条件。

每个样例至少包含：

- 唯一编号和被测能力；
- 关联规则编号；
- 用户输入及必要背景；
- 预期结论、严重程度和必须识别的问题；
- 不允许出现的行为；
- 判断方式和是否需要人工确认。

`fixtures/core-cases.yaml` 保存高风险样例，覆盖 `coverage.yaml` 确定的当前版本核心规则。后续自动化测试应验证可观察行为，例如是否识别一文多事、是否拒绝编造文号，而不是匹配模型输出的固定句子。

## 执行

安装开发依赖后运行：

```bash
python -m pytest
python scripts/validate_repository.py
```

开发验证允许新增规则处于 `source_checked` 或 `human_approved`。准备正式发布时还必须运行严格门禁：

```bash
python scripts/validate_repository.py --release
```

严格门禁要求全部规则均为 `active`；它在开发中的候选规则尚未完成人工签核时失败是预期行为。

未安装 `pytest` 时，也可以使用标准库测试入口：

```bash
python -m unittest discover -s tests
```

当前自动化验证规则总数、编号唯一性、复核状态、核心规则覆盖、样例引用、来源门禁、插件结构，以及部分确定性样例的触发条件。需要理解机关关系、语义或写作质量的样例继续依靠人工签核；在目标 Agent 中建立可重复执行的行为评测前，不将其标记为 `automated`。

## 状态

- `draft`：样例已建立，尚未复核；
- `source_checked`：与规则和来源定位一致；
- `human_approved`：项目维护者已经确认；
- `automated`：已经纳入可重复执行的自动化测试。
