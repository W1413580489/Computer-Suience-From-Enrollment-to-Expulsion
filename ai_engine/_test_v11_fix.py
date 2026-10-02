# -*- coding: utf-8 -*-
"""v1.1 JSON 容错加固冒烟测试（离线，mock _call，不联网、不烧 key）。

运行：python _test_v11_fix.py
覆盖：
  T1 _extract_json 的 json-repair 第二防线（截断/缺逗号）
  T2 review 语义校验（未知 rubric_id / 空 criteria / 缺 evidence / 漏判）
  T3 teach 截断（finish_reason=length）→ 加大 max_tokens 完整重请求
  T4 teach 连续失败 → 纯文本兜底（不再抛 EngineError / 不再 500）
"""
import asyncio
import json
import sys

sys.path.insert(0, ".test_deplibs")  # 本地临时依赖（服务器上走正常 pip install）

from schemas import Mode
from llm_client import LLMClient, _extract_json, _semantic_validate_review, ReviewLLMOutput  # noqa

passed = {"n": 0, "fail": 0}


def check(name, cond):
    if cond:
        passed["n"] += 1
        print(f"  [PASS] {name}")
    else:
        passed["fail"] += 1
        print(f"  [FAIL] {name}")


def t1_extract_json():
    print("T1 _extract_json 容错")
    # markdown 围栏 + 正常 JSON
    ok1 = _extract_json("```json\n{\"a\": 1}\n```") == {"a": 1}
    check("markdown 围栏剥离", ok1)
    # 截断（缺右括号）→ repair 补齐
    try:
        r = _extract_json('{"a": 1, "b": "x')
        check("截断 JSON 由 repair 补齐", r.get("a") == 1 and r.get("b") == "x")
    except Exception as e:
        check("截断 JSON 由 repair 补齐（未触发：%r）" % e, False)
    # 缺逗号 → repair 修复
    try:
        r = _extract_json('{"a": 1 "b": 2}')
        check("缺逗号 JSON 由 repair 修复", r.get("a") == 1 and r.get("b") == 2)
    except Exception as e:
        check("缺逗号 JSON 由 repair 修复（未触发：%r）" % e, False)


def t2_semantic_review():
    print("T2 review 语义校验")
    allowed = ["rb_1", "rb_2", "rb_3"]
    # 合法
    from schemas import ReviewCriterion
    ok = _semantic_validate_review(ReviewLLMOutput(criteria=[
        ReviewCriterion(rubric_id="rb_1", status="PASS", evidence="代码", reason="达标"),
        ReviewCriterion(rubric_id="rb_2", status="FAIL", evidence="CI", reason="未过"),
        ReviewCriterion(rubric_id="rb_3", status="NEED_REVIEW", evidence="自述", reason="缺证据"),
    ]), allowed)
    check("合法输出 → 通过", ok is None)
    # 未知 rubric_id
    bad = _semantic_validate_review(ReviewLLMOutput(criteria=[
        ReviewCriterion(rubric_id="rb_999", status="PASS", evidence="e", reason="r"),
    ]), allowed)
    check("未知 rubric_id 被拒", bad is not None and "rb_999" in bad)
    # 空 criteria
    bad = _semantic_validate_review(ReviewLLMOutput(criteria=[]), allowed)
    check("空 criteria 被拒", bad is not None and "criteria 为空" in bad)
    # 缺 evidence
    bad = _semantic_validate_review(ReviewLLMOutput(criteria=[
        ReviewCriterion(rubric_id="rb_1", status="PASS", evidence="", reason="r"),
    ]), allowed)
    check("缺 evidence 被拒", bad is not None and "evidence" in bad)
    # 漏判（只判了 1 条）
    bad = _semantic_validate_review(ReviewLLMOutput(criteria=[
        ReviewCriterion(rubric_id="rb_1", status="PASS", evidence="e", reason="r"),
    ]), allowed)
    check("漏判被拒（提示补判 rb_2/rb_3）", bad is not None and "未给出判定" in bad)


def t3_teach_truncation():
    print("T3 teach 截断 → 完整重请求")
    calls = []

    async def fake_call(messages, **kw):
        calls.append((kw.get("max_tokens"), [m["content"][:40] for m in messages]))
        n = len(calls)
        if n == 1:
            return {"content": '{"mode":"tutor","message":"卡在第一步","nex', "finish_reason": "length"}
        return {"content": json.dumps({"message": "卡在第一步，先确认依赖装好", "mode": "tutor"}),
                "finish_reason": "stop"}

    client = LLMClient("k"); client._call = fake_call
    out = asyncio.run(client.teach([{"role": "system", "content": "sys json"}], Mode.tutor, max_tokens=1500))
    check("截断后重试成功，返回合法 AiResponse", out.message.startswith("卡在第一步"))
    check("第二次调用 max_tokens 已加大（3000）", calls[1][0] == 3000)
    check("第二次请求不带残缺 JSON（回到原始 prompt）", "nex" not in (calls[1][1]))


def t4_teach_windfall():
    print("T4 teach 连续失败 → 纯文本兜底")
    calls = []

    async def fake_call(messages, **kw):
        calls.append(1)
        if len(calls) == 3:  # 第三次 = 兜底调用
            return {"content": "先确认依赖装好，再运行 pytest 看结果。", "finish_reason": "stop"}
        return {"content": '{"mode" "tutor" broken', "finish_reason": "stop"}

    client = LLMClient("k"); client._call = fake_call
    out = asyncio.run(client.teach([{"role": "system", "content": "sys json"},
                                     {"role": "user", "content": "我报错了"}], Mode.tutor))
    check("兜底返回纯文本回答", out.message.startswith("先确认依赖"))
    check("总调用次数 = 2 次结构化 + 1 次兜底", len(calls) == 3)


if __name__ == "__main__":
    t1_extract_json()
    t2_semantic_review()
    t3_teach_truncation()
    t4_teach_windfall()
    print(f"\n结果：{passed['n']} 通过 / {passed['fail']} 失败")
    sys.exit(1 if passed["fail"] else 0)