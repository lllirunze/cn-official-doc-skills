# 安装与使用

本项目以 Codex 插件形式发布，插件内包含两个可独立触发的 Skill，并随包携带其所依赖的规范库。推荐通过 GitHub 仓库市场安装，以便后续更新。

## 安装

在终端中执行：

```bash
codex plugin marketplace add lllirunze/cn-official-doc-skills
codex plugin add cn-official-doc-skills@cn-official-doc-skills
```

安装完成后新建一个 Codex 对话，使插件和 Skills 完成加载。

如使用 Codex 桌面应用，也可以先添加上述 GitHub 市场，再从插件目录中搜索“中文机关公文 Skills”并安装。

## 使用

可以直接描述任务，让 Codex 根据任务自动选择 Skill：

- “根据这些事实起草一份通知。”
- “审核这份请示的文种、行文关系和格式。”
- “把这份报告改得更准确、精练，但不要增加新事实。”

需要明确指定时，可以使用：

- `$official-document-drafting`：起草、修改或优化通知、报告、请示及相关机关文稿；
- `$official-document-review`：审核文种、行文关系、结构格式、标点数字和事实可靠性。

## 更新

更新已添加的市场及插件：

```bash
codex plugin marketplace update cn-official-doc-skills
codex plugin add cn-official-doc-skills@cn-official-doc-skills
```

卸载可在 Codex 的插件管理界面完成。不同 Codex 版本的命令可能发生变化；如命令不可用，请以 OpenAI 官方插件文档和 `codex plugin --help` 为准。

## 使用边界

- `v0.1.0` 的首批规则已经完成来源核验、人工签核、可重复验证和真实安装验收，并转为 `active`；
- 输出不能替代机关内部审核、审批或签发；
- 不要向未经授权的服务提交涉密、内部敏感或含个人信息的材料；
- 对政策、文号、数据、资金、决定和工作成果等事实，使用者仍需人工核实。

## 仓库开发方式

参与项目开发时，可克隆仓库并在仓库目录中使用其中的 Skills。开发仓库中的 `standards/`、`corpus/` 和 `lexicon/` 是共享资源，不应只复制单个 Skill 目录后独立使用。
