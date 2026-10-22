import re
from app.models import AnalyzeRequest, AnalyzeResponse, Scores

EDUCATIONAL_TERMS = {
    "because", "therefore", "example", "explains", "means", "study",
    "research", "evidence", "experiment", "how", "why", "demonstrates",
}
CLAIM_CUES = {
    "always", "never", "guaranteed", "cure", "proven", "everyone",
    "secret", "scientists say", "100%", "miracle", "shocking truth",
}

def _words(text: str) -> list[str]:
    return re.findall(r"\b[\w'-]+\b", text.lower())

def analyze_transcript(request: AnalyzeRequest) -> AnalyzeResponse:
    text = request.transcript.strip()
    words = _words(text)
    word_set = set(words)
    interests = {w for item in request.user_interests for w in _words(item)}

    overlap = len(word_set & interests) / max(1, len(interests))
    relevance = min(1.0, overlap * 2.5) if interests else 0.5

    useful_terms = len(word_set & EDUCATIONAL_TERMS)
    substance = min(0.9, 0.25 + useful_terms * 0.09 + min(len(words), 180) / 600)
    claim_cues = [cue for cue in CLAIM_CUES if cue in text.lower()]
    needs_fact_check = bool(claim_cues)
    evidence_quality = 0.35 if needs_fact_check else 0.5
    if any(term in word_set for term in {"study", "research", "source", "evidence"}):
        evidence_quality = min(0.75, evidence_quality + 0.2)

    unique_ratio = len(set(words)) / max(1, len(words))
    originality = min(0.9, max(0.2, unique_ratio))
    clarity = min(0.9, max(0.3, 0.45 + (0.15 if len(words) >= 25 else 0) - (0.1 if len(words) > 250 else 0)))

    topic_tags = list(request.user_interests[:3])
    if not topic_tags:
        topic_tags = ["general content"]

    reasons = []
    if interests and overlap > 0:
        reasons.append("The transcript shares vocabulary with at least one stated interest.")
    elif interests:
        reasons.append("Little direct vocabulary overlap was found with stated interests.")
    else:
        reasons.append("No interests were provided, so relevance uses a neutral baseline.")
    if useful_terms:
        reasons.append("The transcript contains terms associated with explanation or evidence.")
    else:
        reasons.append("The baseline did not detect many explanation-related terms.")
    if needs_fact_check:
        reasons.append("Strong or absolute claim wording was detected; this is a prompt to verify, not proof of misinformation.")
    else:
        reasons.append("No simple high-risk claim cue was detected; this does not establish that claims are true.")

    uncertainty = "high" if len(words) < 20 or needs_fact_check else ("medium" if not interests else "low")
    return AnalyzeResponse(
        topic_tags=topic_tags,
        summary=" ".join(text.split())[:400],
        scores=Scores(
            relevance=round(relevance, 2),
            substance=round(substance, 2),
            evidence_quality=round(evidence_quality, 2),
            originality=round(originality, 2),
            clarity=round(clarity, 2),
        ),
        needs_fact_check=needs_fact_check,
        uncertainty=uncertainty,
        reasons=reasons,
        limitations=[
            "This is a transparent rules-based baseline, not a trained AI model.",
            "Scores are heuristic and have not been validated against human judgments.",
            "Transcript-only analysis cannot assess visual context, creator intent, or verify factual claims.",
        ],
        model_mode="rules_baseline",
    )
