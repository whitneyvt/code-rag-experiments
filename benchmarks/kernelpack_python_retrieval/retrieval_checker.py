"""Score provenance-oriented RAG submissions against kernelpack-python tasks."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT_KP_ROOT = Path("/home/ramansh/KP/kernelpack-python")
TASK_MANIFESTS = {
    "easy": HERE / "manifest_easy.json",
    "easy_2": HERE / "manifest_easy_2.json",
    "easy_3": HERE / "manifest_easy_3.json",
    "medium": HERE / "manifest_medium.json",
    "medium_2": HERE / "manifest_medium_2.json",
    "medium_3": HERE / "manifest_medium_3.json",
}


def _kernelpack_root() -> Path:
    candidate = os.environ.get("KERNELPACK_PYTHON_ROOT")
    if candidate:
        return Path(candidate).resolve()
    return DEFAULT_KP_ROOT.resolve()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_ref(ref: str, repo_root: Path) -> bool:
    try:
        rel, linespec = ref.split(":")
        start, _, end = linespec.partition("-")
        start_i = int(start)
        end_i = int(end or start)
    except Exception:
        return False
    fp = repo_root / rel
    if not fp.exists():
        return False
    line_count = len(fp.read_text(encoding="utf-8").splitlines())
    return 1 <= start_i <= end_i <= line_count


def _symbol_in_refs(symbol: str, refs: list[str], repo_root: Path) -> bool:
    for ref in refs:
        rel, _ = ref.split(":")
        fp = repo_root / rel
        if fp.exists() and symbol in fp.read_text(encoding="utf-8"):
            return True
    return False


def _run_script(script: Path, output_dir: Path, repo_root: Path) -> None:
    env = os.environ.copy()
    env["MPLBACKEND"] = "Agg"
    env["RAGSYSTEM_OUTPUT_DIR"] = str(output_dir)
    src_path = str((repo_root / "src").resolve())
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src_path if not existing else f"{src_path}{os.pathsep}{existing}"
    subprocess.run([sys.executable, str(script)], check=True, env=env, cwd=str(script.parent))


def _find_component(entries: list[dict], component_id: str) -> dict | None:
    for entry in entries:
        if entry.get("component_id") == component_id:
            return entry
    return None


def _markers_cover(required_markers: list[str], claimed_markers: list[str], script_text: str) -> bool:
    """Treat manifest markers as required substrings, not exact thought-log literals."""
    for required in required_markers:
        if required not in script_text:
            return False
        if not any(required in claimed or claimed in required for claimed in claimed_markers):
            return False
    return True


def _validate_repo_entry(entry: dict, repo_root: Path, script_text: str) -> tuple[bool, bool]:
    refs = entry.get("repo_refs", [])
    symbols = entry.get("repo_symbols", [])
    markers = entry.get("code_markers", [])
    refs_ok = bool(refs) and all(isinstance(r, str) and _validate_ref(r, repo_root) for r in refs)
    symbols_ok = bool(symbols) and all(isinstance(s, str) and _symbol_in_refs(s, refs, repo_root) for s in symbols)
    alignment_ok = bool(markers) and all(isinstance(m, str) and m in script_text for m in markers)
    return refs_ok and symbols_ok and alignment_ok, alignment_ok


def _score_submission(manifest: dict, thought: dict, script_text: str, repo_root: Path) -> dict[str, object]:
    entries = thought.get("entries", [])
    if not isinstance(entries, list):
        raise RuntimeError("thought_process entries must be a list")

    required = manifest["required_repo_components"]
    innate_allowed = set(manifest["allowed_innate_components"])

    repo_claim_total = 0
    verified_repo_claims = 0
    aligned_repo_claims = 0
    hallucinated_repo_claims = 0
    matched_required = 0
    missed_required: list[str] = []
    innate_claim_total = 0
    correct_innate_claims = 0

    for req in required:
        entry = _find_component(entries, req["component_id"])
        if entry is None:
            missed_required.append(req["component_id"])
            continue
        if entry.get("origin") not in {"repo", "hybrid"}:
            missed_required.append(req["component_id"])
            continue
        repo_claim_total += 1
        valid_repo, aligned = _validate_repo_entry(entry, repo_root, script_text)
        if aligned:
            aligned_repo_claims += 1
        refs = set(entry.get("repo_refs", []))
        symbols = set(entry.get("repo_symbols", []))
        markers = entry.get("code_markers", [])
        req_ref_ok = bool(refs.intersection(req["allowed_repo_refs"]))
        req_sym_ok = set(req["required_repo_symbols"]).issubset(symbols)
        req_marker_ok = _markers_cover(req["required_code_markers"], markers, script_text)
        if valid_repo:
            verified_repo_claims += 1
        else:
            hallucinated_repo_claims += 1
        if valid_repo and req_ref_ok and req_sym_ok and req_marker_ok:
            matched_required += 1
        else:
            missed_required.append(req["component_id"])

    required_ids = {req["component_id"] for req in required}
    for entry in entries:
        origin = entry.get("origin")
        cid = entry.get("component_id")
        if cid in required_ids:
            continue
        if origin in {"repo", "hybrid"}:
            repo_claim_total += 1
            valid_repo, aligned = _validate_repo_entry(entry, repo_root, script_text)
            if aligned:
                aligned_repo_claims += 1
            if valid_repo:
                verified_repo_claims += 1
            else:
                hallucinated_repo_claims += 1
        elif origin == "innate":
            innate_claim_total += 1
            repo_refs = entry.get("repo_refs", [])
            repo_symbols = entry.get("repo_symbols", [])
            if cid in innate_allowed and not repo_refs and not repo_symbols:
                correct_innate_claims += 1

    repo_recall = matched_required / len(required) if required else 1.0
    repo_precision = verified_repo_claims / repo_claim_total if repo_claim_total else 0.0
    repo_f1 = 0.0 if repo_precision + repo_recall == 0 else 2.0 * repo_precision * repo_recall / (repo_precision + repo_recall)
    innate_precision = correct_innate_claims / innate_claim_total if innate_claim_total else 0.0
    code_alignment = aligned_repo_claims / repo_claim_total if repo_claim_total else 0.0
    final_score = (repo_f1 + innate_precision + code_alignment) / 3.0

    return {
        "task_id": manifest["task_id"],
        "required_repo_components": len(required),
        "matched_required_repo_components": matched_required,
        "missed_required_repo_components": sorted(set(missed_required)),
        "repo_claim_total": repo_claim_total,
        "verified_repo_claims": verified_repo_claims,
        "hallucinated_repo_claims": hallucinated_repo_claims,
        "innate_claim_total": innate_claim_total,
        "correct_innate_claims": correct_innate_claims,
        "repo_recall": repo_recall,
        "repo_precision": repo_precision,
        "repo_f1": repo_f1,
        "innate_precision": innate_precision,
        "code_alignment": code_alignment,
        "final_score": final_score,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Score provenance-oriented kernelpack-python RAG submissions.")
    parser.add_argument("task", choices=sorted(TASK_MANIFESTS))
    parser.add_argument("script", type=Path)
    parser.add_argument("--min-final-score", type=float, default=None)
    args = parser.parse_args()

    repo_root = _kernelpack_root()
    manifest = _load_json(TASK_MANIFESTS[args.task])
    script = args.script.resolve()

    with tempfile.TemporaryDirectory(prefix=f"ragprov_{args.task}_") as tmp:
        output_dir = Path(tmp)
        _run_script(script, output_dir, repo_root)
        summary_path = output_dir / manifest["summary_filename"]
        thought_path = output_dir / manifest["thought_filename"]
        if not summary_path.exists():
            raise FileNotFoundError(f"Missing summary output: {summary_path.name}")
        if not thought_path.exists():
            raise FileNotFoundError(f"Missing thought-process output: {thought_path.name}")
        thought = _load_json(thought_path)
        script_text = script.read_text(encoding="utf-8")
        score = _score_submission(manifest, thought, script_text, repo_root)
        score["script"] = str(script)
        score["summary_file"] = str(summary_path)
        score["thought_file"] = str(thought_path)
        print(json.dumps(score, indent=2))
        if args.min_final_score is not None and score["final_score"] < args.min_final_score:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
