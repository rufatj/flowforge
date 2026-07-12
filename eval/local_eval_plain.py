import argparse, json, re, torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def gates(text):
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-z]*\n?", "", t)
        t = re.sub(r"\n?```$", "", t).strip()
    try:
        obj = json.loads(t)
    except Exception:
        return False, False
    if not isinstance(obj, dict):
        return True, False
    nodes = obj.get("nodes")
    conns = obj.get("connections")
    ok = (isinstance(nodes, list) and len(nodes) > 0 and isinstance(conns, dict))
    if ok:
        for n in nodes:
            if not isinstance(n, dict) or "name" not in n or "type" not in n:
                ok = False
                break
    return True, ok

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="auto")
    model.eval()
    print(f"[eval] loaded {a.model}", flush=True)

    rows = []
    with open("/workspace/flowforge/data/out/heldout.jsonl", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= a.limit:
                break
            m = json.loads(line)["messages"]
            system = next(x["content"] for x in m if x["role"] == "system")
            user = next(x["content"] for x in m if x["role"] == "user")
            rows.append((system, user))

    g1 = g2 = 0
    for i, (system, user) in enumerate(rows, 1):
        enc = tok.apply_chat_template(
            [{"role": "user", "content": system + "\n\n" + user}],
            tokenize=True, add_generation_prompt=True, return_tensors="pt")
        ids = (enc.input_ids if hasattr(enc, "input_ids") else enc).to(model.device)
        with torch.no_grad():
            out = model.generate(
                input_ids=ids,
                max_new_tokens=6144,
                do_sample=False,
                repetition_penalty=1.1,
                no_repeat_ngram_size=6,
            )
        text = tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)
        j, s = gates(text)
        g1 += j
        g2 += s
        print(f"  [{i}/{len(rows)}] json={j} schema={s} len={len(out[0]) - ids.shape[1]}", flush=True)

    res = {
        "label": a.label,
        "model": a.model,
        "total": len(rows),
        "gate1": round(g1 / len(rows), 4),
        "gate2": round(g2 / len(rows), 4),
        "gate3": None,
    }
    with open(a.out, "w") as f:
        json.dump(res, f, indent=2)
    print(f"[eval] {a.label}: gate1={100 * g1 / len(rows):.1f}% gate2={100 * g2 / len(rows):.1f}% -> {a.out}", flush=True)

if __name__ == "__main__":
    main()