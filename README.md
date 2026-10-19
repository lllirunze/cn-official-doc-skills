# cn-official-doc-skills

`cn-official-doc-skills`（Chinese Official Document Skills）是一个面向中文机关文稿的 Agent Skills 能力库。项目通过结构化规范、写作流程、审核规则、公开案例和表达语料，帮助 AI Agent 更规范、可靠地编写与审核中文机关文稿。

项目不提供独立聊天应用，也不绑定特定模型或智能体框架。其核心价值在于建立可追溯的规范体系、可执行的质量审核机制，以及可持续维护的中文机关表达知识。

## 安装

本项目可作为 Codex 插件从 GitHub 安装：

```bash
codex plugin marketplace add lllirunze/cn-official-doc-skills
codex plugin add cn-official-doc-skills@cn-official-doc-skills
```

安装后新建一个 Codex 对话，可以直接描述起草或审核任务，也可以显式调用 `$official-document-drafting` 或 `$official-document-review`。完整说明见 [安装与使用](docs/installation.md)。

## 当前状态

项目已发布 `v0.1.0`，提供以下首版能力：

- 基于规范编写通知、报告和请示；
- 审核文种、结构、语言、逻辑和事实可靠性；
- 对正式交付文稿执行中文成稿检查；
- 将确定性规则交由程序验证，将语义问题交由 Agent 判断；
- 对关键规范、判断依据和待核实内容提供可追溯说明。

当前仓库已完成首批四份权威材料的结构化提取、Agent逐条来源对照、项目维护者人工签核、可重复验证和真实 Codex 安装验收；两个核心 Skills 及其 173 条规则已正式启用。项目输出仍不能替代机关内部审核、审批或签发。

## 设计原则

- **规范优先：** 权威规范优先于模型自身的生成习惯。
- **事实可靠：** 不编造政策、文号、数据、资金、决策或工作成果。
- **中文成稿：** 正式交付文稿执行项目定义的中文语言门禁。
- **能力模块化：** 写作、审核和知识资源相互独立并可组合使用。
- **结果可验证：** 能够确定性判断的规则应通过程序测试和验证。
- **来源可追溯：** 正式规范和案例资料应记录来源、效力与核验信息。

## 仓库结构

```text
cn-official-doc-skills/
├── skills/       # 面向用户任务的 Agent Skills
├── standards/    # 规范知识、文种规则及权威来源
├── corpus/       # 经来源与许可审查的公开案例
├── lexicon/      # 规范术语、表达及易错用语
├── scripts/      # 确定性校验与辅助工具
├── tests/        # 程序测试和 Skills 行为样例
├── docs/         # 设计、架构、开发及路线图文档
├── plugin.json   # 可移植插件清单
├── .agents/      # GitHub 插件市场清单
├── .codex-plugin/# Codex 插件兼容清单
└── .github/      # GitHub 自动化流程
```

开发仓库和插件包共享 `standards/`、`corpus/` 和 `lexicon/` 中的资源。若将某个 Skill 脱离本插件单独发布，必须同时打包其必要资源并调整引用路径，保证发布包可以独立使用。

## 文档

- [项目总体设计](docs/design.md)
- [安装与使用](docs/installation.md)
- [Standards 规范知识体系设计](docs/standards-design.md)
- [规范来源与外部材料导入说明](standards/sources/README.md)
- [贡献指南](CONTRIBUTING.md)
- [更新日志](CHANGELOG.md)

## v0.1.0 规划

首个版本计划提供两个核心 Skill：

1. `official-document-drafting`：根据事实与适用规范编写、修改和优化机关文稿；
2. `official-document-review`：对文种、结构、语言、逻辑、事实和中文合规性进行审核。

首批支持通知、报告、请示三类文稿。大型案例库、完整表达语料库、Word 导出、MCP 服务和 Web 管理界面不属于首个版本范围。

两个 Skill 已完成首版发布验收。规则被标记为 `active` 只表示通过本项目的来源、复核和测试门禁，不表示具体文稿已经通过机关内部审核、审批或签发。

## 使用边界

- 项目生成或审核的内容不代表已经通过机关内部审核、审批或签发；
- 使用者仍需根据职责、真实业务背景和现行有效规范进行人工复核；
- 不应向未经授权的第三方服务上传涉密、敏感、内部或包含个人信息的材料；
- 无法核实的政策、数据和事实应明确标注待核实，不得作为已知事实输出；
- 一般工作材料不应机械套用法定公文规则。

## 参与贡献

欢迎提交规范勘误、文种规则、测试样例、Skill 改进和具有合法来源的公开资料。规范类贡献必须附权威来源；案例和语料贡献必须说明来源及许可情况。具体要求见 [贡献指南](CONTRIBUTING.md)。

提交前运行：

```bash
python -m pytest
python scripts/validate_repository.py
```

## 开源许可

本项目原创代码和原创文档采用 [Apache License 2.0](LICENSE) 许可。

该许可不自动覆盖仓库引用或收录的第三方规范、标准、案例和其他资料。第三方内容仍受其原始权利声明和适用法律约束。
