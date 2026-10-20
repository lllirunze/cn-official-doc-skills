"""Validate the rule catalog, behavior fixtures, and plugin package."""

from __future__ import annotations

import argparse
import json
import re
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import yaml


ROOT = Path(__file__).resolve().parents[1]
RULE_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
ALLOWED_REVIEW_STATUSES = {"source_checked", "human_approved", "active"}


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def iter_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from iter_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_dicts(child)


def load_rule_catalog() -> dict[str, dict[str, Any]]:
    rules: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    for path in sorted((ROOT / "standards").rglob("*.yaml")):
        if "sources" in path.parts:
            continue
        for item in iter_dicts(load_yaml(path)):
            rule_id = item.get("id")
            if not isinstance(rule_id, str) or not RULE_ID_RE.fullmatch(rule_id):
                continue
            if not isinstance(item.get("review"), dict):
                continue
            if rule_id in rules:
                duplicates.append(rule_id)
            rules[rule_id] = {"path": path, "rule": item}
    if duplicates:
        raise AssertionError(f"重复规则编号：{sorted(set(duplicates))}")
    return rules


def load_required_rule_ids() -> list[str]:
    coverage = load_yaml(ROOT / "tests" / "coverage.yaml")
    groups = coverage["required_rule_ids"]
    return [rule_id for values in groups.values() for rule_id in values]


def load_behavior_cases() -> list[dict[str, Any]]:
    payload = load_yaml(ROOT / "tests" / "fixtures" / "core-cases.yaml")
    return payload["cases"]


def evaluate_deterministic_case(case: dict[str, Any]) -> set[str]:
    """Return rule IDs whose deterministic trigger is observable in a fixture."""
    rule_ids = set(case.get("rule_ids", []))
    text = case.get("input", "")
    context = case.get("context", {})
    findings: set[str] = set()

    if "PUNCT-ANNEX-A09" in rule_ids and re.search(r"…….*等", text):
        findings.add("PUNCT-ANNEX-A09")
    if "FORMAT-DOC-NUMBER-001" in rule_ids:
        if "第" in text or re.search(r"〔\d{4}〕0\d+号", text):
            findings.add("FORMAT-DOC-NUMBER-001")
    if "NUMBER-DATE-001" in rule_ids and re.search(r"(?<!\d)\d{2}年", text):
        findings.add("NUMBER-DATE-001")
    if "NUMBER-DECIMAL-001" in rule_ids and re.search(r"(?<!\d)\.\d+", text):
        findings.add("NUMBER-DECIMAL-001")
    if "NUMBER-RANGE-001" in rule_ids and re.search(r"\d+~\d+%", text):
        findings.add("NUMBER-RANGE-001")
    if "NUMBER-ARABIC-MEASURE-001" in rule_ids and re.search(
        r"[一二三四五六七八九十百千万亿]+(?:克|千克|米|千米|升)", text
    ):
        findings.add("NUMBER-ARABIC-MEASURE-001")
    if (
        "ROUTING-UPWARD-001" in rule_ids
        and context.get("direction") == "upward"
        and context.get("copied_organizations")
    ):
        findings.add("ROUTING-UPWARD-001")
    if (
        "FORMAT-SIGNER-001" in rule_ids
        and context.get("direction") == "upward"
        and context.get("signer_present") is False
    ):
        findings.add("FORMAT-SIGNER-001")
    if "FORMAT-TITLE-LAYOUT-001" in rule_ids and context.get("title_position") != "版心居中":
        findings.add("FORMAT-TITLE-LAYOUT-001")
    if "FORMAT-ADDRESSEE-LAYOUT-001" in rule_ids and context.get("addressee_position") == "标题同一行":
        findings.add("FORMAT-ADDRESSEE-LAYOUT-001")
    if "FORMAT-BODY-001" in rule_ids and context.get("body_first_line_indent_chars") == 0:
        findings.add("FORMAT-BODY-001")
    if "FORMAT-ATTACHMENT-001" in rule_ids:
        note = context.get("attachment_note", "")
        heading = context.get("actual_attachment_heading", "")
        note_number = re.search(r"附件[：:]?(\d+)", note)
        heading_number = re.search(r"附件[：:]?(\d+)", heading)
        if note_number and heading_number and note_number.group(1) != heading_number.group(1):
            findings.update({"FORMAT-ATTACHMENT-001", "FORMAT-ATTACHMENT-NOTE-001"} & rule_ids)
    if "FORMAT-DATE-001" in rule_ids and re.search(r"[〇一二三四五六七八九十]+年", context.get("date_text", "")):
        findings.add("FORMAT-DATE-001")
    if "FORMAT-PAGE-NUMBER-001" in rule_ids and context.get("blank_page_has_page_number") is True:
        findings.add("FORMAT-PAGE-NUMBER-001")

    return findings


def validate_rule_catalog() -> dict[str, dict[str, Any]]:
    rules = load_rule_catalog()
    if len(rules) < 173:
        raise AssertionError(f"规则总数不得少于v0.1.0基线的173条，实际为{len(rules)}")
    for rule_id, entry in rules.items():
        review = entry["rule"].get("review")
        if not isinstance(review, dict) or review.get("status") not in ALLOWED_REVIEW_STATUSES:
            raise AssertionError(f"{rule_id} 缺少有效复核状态")
    return rules


def validate_behavior_coverage(rules: dict[str, dict[str, Any]]) -> None:
    required = load_required_rule_ids()
    if len(required) != len(set(required)):
        repeated = [key for key, count in Counter(required).items() if count > 1]
        raise AssertionError(f"核心规则清单存在重复：{repeated}")
    cases = load_behavior_cases()
    case_ids = [case["id"] for case in cases]
    if len(cases) < 39 or len(case_ids) != len(set(case_ids)):
        raise AssertionError("行为样例不得少于v0.1.0基线的39个且编号必须唯一")

    referenced = {rule_id for case in cases for rule_id in case.get("rule_ids", [])}
    unknown = referenced - set(rules)
    if unknown:
        raise AssertionError(f"行为样例引用了不存在的规则：{sorted(unknown)}")
    missing = set(required) - referenced
    if missing:
        raise AssertionError(f"核心规则缺少行为样例：{sorted(missing)}")

    allowed_evaluations = {
        "deterministic",
        "deterministic_and_semantic",
        "deterministic_with_context",
        "deterministic_with_layout_context",
        "context_required",
        "semantic",
        "semantic_and_context_required",
        "semantic_and_deterministic",
        "semantic_and_human_review",
        "semantic_with_context",
    }
    for case in cases:
        if case.get("evaluation") not in allowed_evaluations:
            raise AssertionError(f"{case['id']} 的 evaluation 无效")
        expected = case.get("expected")
        if not isinstance(expected, dict) or not expected.get("outcome"):
            raise AssertionError(f"{case['id']} 缺少预期结果")


def validate_source_gate() -> None:
    coverage = load_yaml(ROOT / "standards" / "sources" / "coverage.yaml")
    sources = coverage["sources"]
    if len(sources) < 4:
        raise AssertionError("规范来源不得少于v0.1.0基线的四份")
    for source in sources:
        if source.get("extraction_status") != "complete":
            raise AssertionError(f"{source['source_id']} 尚未完成提取")
        if source.get("review_status") not in {
            "source_checked",
            "human_approved",
            "active",
        }:
            raise AssertionError(f"{source['source_id']} 缺少有效复核状态")
    baseline = {source["source_id"]: source for source in sources}
    for source_id in {"SOURCE-001", "SOURCE-002", "SOURCE-003", "SOURCE-004"}:
        if baseline.get(source_id, {}).get("review_status") not in {
            "human_approved",
            "active",
        }:
            raise AssertionError(f"{source_id} 的v0.1.0基线尚未人工签核")


def validate_example_catalog() -> None:
    payload = load_yaml(ROOT / "corpus" / "examples" / "v0.2-examples.yaml")
    examples = payload.get("examples", [])
    example_ids = [item.get("id") for item in examples]
    if len(examples) != 8 or len(example_ids) != len(set(example_ids)):
        raise AssertionError("v0.2.0公开实例应为8份且编号唯一")
    expected_types = {"通报", "批复", "函"}
    actual_types = {item.get("document_type") for item in examples}
    if actual_types != expected_types:
        raise AssertionError(f"公开实例文种不完整：{sorted(actual_types)}")
    for item in examples:
        required = {
            "title",
            "authority",
            "official_url",
            "local_file",
            "sha256",
            "pages",
            "observed_patterns",
        }
        missing = sorted(key for key in required if not item.get(key))
        if missing:
            raise AssertionError(f"{item['id']} 缺少元数据：{missing}")


def validate_release_gate(rules: dict[str, dict[str, Any]]) -> None:
    inactive = sorted(
        rule_id
        for rule_id, entry in rules.items()
        if entry["rule"]["review"].get("status") != "active"
    )
    if inactive:
        raise AssertionError(f"正式发布仍有非active规则：{inactive}")

    coverage = load_yaml(ROOT / "standards" / "sources" / "coverage.yaml")
    unavailable = [
        source["source_id"]
        for source in coverage["sources"]
        if source.get("usable") is not True
    ]
    if unavailable:
        raise AssertionError(f"正式发布仍有不可用来源：{unavailable}")

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    expected_version = project["project"]["version"]
    manifests = [
        ROOT / "plugin.json",
        ROOT / ".codex-plugin" / "plugin.json",
    ]
    for path in manifests:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if manifest.get("version") != expected_version:
            raise AssertionError(f"{path.relative_to(ROOT)} 与项目版本不一致")


def validate_plugin_package() -> None:
    manifest_path = ROOT / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("name") != ROOT.name:
        raise AssertionError("插件名称必须与仓库目录名称一致")
    skills_path = ROOT / manifest.get("skills", "")
    if not skills_path.is_dir():
        raise AssertionError("插件 skills 路径不存在")
    skill_names = {
        path.parent.name for path in skills_path.glob("*/SKILL.md") if path.is_file()
    }
    expected = {"official-document-drafting", "official-document-review"}
    if skill_names != expected:
        raise AssertionError(f"插件 Skill 集合不符合v0.1范围：{sorted(skill_names)}")


def validate_all(*, release: bool = False) -> None:
    rules = validate_rule_catalog()
    validate_behavior_coverage(rules)
    validate_source_gate()
    validate_example_catalog()
    validate_plugin_package()
    if release:
        validate_release_gate(rules)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release",
        action="store_true",
        help="同时执行仅允许active规则的正式发布门禁",
    )
    args = parser.parse_args()
    validate_all(release=args.release)
    mode = "release" if args.release else "development"
    print(f"repository {mode} validation passed")
