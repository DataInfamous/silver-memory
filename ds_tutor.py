"""
DS-Tutor — the data-science-scoped fork of the Cognitive Throttle.

The original throttle logic, scoped. Same reliance-spectrum engine as
cognitive_throttle.py (the CAB downstream policy: given a read of the user's
attempt and affect, decide whether the assistant should answer directly,
verify, encourage with a light hint, scaffold, or push back with a question
first), with exactly two differences:

1. A topic gate. The general throttle is always-on; ds-tutor activates ONLY
   on data-science / coursework questions (statistics, ML, data work, SQL,
   databases). Outside that scope it stays inactive and applies no friction.
2. A data-science pitfall set. Where the general fork flags general
   critical-thinking pitfalls, ds-tutor flags p-hacking, mishandled
   censoring, unchecked proportional-hazards assumptions, and misread
   Kaplan-Meier curves.

This is an independent fork, not a shared library: edits here do not sync to
cognitive_throttle.py, and edits there do not sync here. That separation is
deliberate — the two scopes are supposed to be free to diverge.

Decision order (highest priority first):

1. Priority 0 — burnout / executive-dysfunction override. If the message
   carries exhaustion language, a fragmentation drop-off, a pressured repeat
   request, or a severe first-step stall, all friction is removed: direct
   answer, one action, no nudges. Re-checked on every message; never latched.
2. Explicit overrides — "just tell me", time pressure, a repeat of an
   already-answered question, or a plain factual lookup always get a direct
   answer. A nudge is never looped twice.
3. The user's lever — "shift up" / "shift down" moves one step along the
   friction ladder from wherever the triage table lands. A bare lever pull is
   a deliberate instruction, never a Priority-0 fragment signal.
4. Reliance-spectrum triage — the 2x2 table over (attempt shown x frustrated).

The signal detectors are transparent keyword/structure heuristics. In
production the same signals are read by the assistant from the conversation;
here they are made explicit and testable so the policy can be studied,
reproduced, and argued with. Heuristics are approximations, not measurements.

Adapted from the author's Cognitive Autonomy Bench:
https://github.com/DataInfamous/silver-memory

Theoretical grounding: Vygotsky (Zone of Proximal Development); Lancet
Commission 2024 (cognitive reserve); Bierzynska et al. 2016 (frustration
neurochemistry); Rossi, IDPS (deliberate practice); Cole et al., EMNLP 2023;
Outsourcing Cognition typology, PMC12714973 (2025); Baldeo 2026 (AI reliance
and confidence); Wang & Zhang 2026 (offloading paradox).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class ResponseMode(Enum):
    """How the assistant should respond, from least to most friction."""

    DIRECT_ANSWER = "direct_answer"      # No friction. Priority 0 / overrides.
    VERIFY = "verify"                    # Confirm or gently correct.
    ENCOURAGE_HINT = "encourage_hint"    # Protect productive struggle.
    SCAFFOLD = "scaffold"                # Smallest unblocking piece only.
    PUSH_BACK = "push_back"              # One question pointing at the concept.
    INACTIVE = "inactive"                # ds-tutor only: outside DS scope.


# Friction ladder, least to most. The shift levers walk this ladder.
FRICTION_LADDER = [
    ResponseMode.DIRECT_ANSWER,
    ResponseMode.VERIFY,
    ResponseMode.ENCOURAGE_HINT,
    ResponseMode.SCAFFOLD,
    ResponseMode.PUSH_BACK,
]


def triage(attempt_shown: bool, frustrated: bool) -> ResponseMode:
    """The core reliance-spectrum table."""
    if attempt_shown and frustrated:
        return ResponseMode.ENCOURAGE_HINT
    if attempt_shown:
        return ResponseMode.VERIFY
    if frustrated:
        return ResponseMode.SCAFFOLD
    return ResponseMode.PUSH_BACK


def cab_interpretation(attempt_shown: bool, frustrated: bool) -> str:
    """Map a triage read onto CAB's reliance spectrum (README).

    CAB reads substitution from canary x affect; the throttle reads the same
    spectrum live, from attempt x affect, and picks the mode that answers it.
    """
    if not attempt_shown and not frustrated:
        return "Full-substitution risk: no friction, no attempt — push back first."
    if not attempt_shown and frustrated:
        return "Outsourcing risk under frustration — scaffold, do not shortcut."
    if attempt_shown and frustrated:
        return "Sat with frustration, doing the work — protect the struggle."
    return "Genuine independent resolution — verify only."


# --------------------------------------------------------------------------
# Signal detection (explicit heuristics — see module docstring)
# --------------------------------------------------------------------------

EXHAUSTION_PHRASES = [
    "can not", "cannot do this", "can't do this", "cant do this",
    "too much", "done for today", "brain is fried", "brain's fried",
    "shutting down", "exhausted", "overwhelmed", "can't think",
    "cant think", "no energy", "running on empty", "i'm done",
]

STALL_PHRASES = [
    "don't know where to start", "dont know where to start",
    "do not know where to start", "where do i start",
    "where do i even start", "can't start", "cant start",
    "stuck at the start", "stuck on the first step", "no idea where to begin",
]

FRUSTRATION_PHRASES = [
    "i don't get", "i dont get", "don't get it", "dont get it",
    "don't get this", "still don't get", "doesn't make sense",
    "doesnt make sense",
    "don't understand", "dont understand", "confused", "frustrated",
    "frustrating", "annoying", "still stuck", "still doesn't work",
    "still doesnt work", "why won't", "why wont", "this makes no sense",
    "hate this", "ugh",
]

ATTEMPT_MARKERS = [
    "i tried", "i've tried", "ive tried", "i think", "i thought",
    "because", "so that means", "my approach", "my guess", "i got",
    "i wrote", "here's my", "heres my", "here is my", "stuck on",
    "stuck at", "my work", "my answer", "i figured", "so far i",
    "i ran", "i split", "i checked", "i used", "i did", "i found",
    "i calculated", "i tested", "i compared", "i ended up", "when i",
]

JUST_TELL_ME_PHRASES = [
    "just tell me", "just answer", "just give me the answer",
    "just give me", "tell me the answer", "no hints",
]

TIME_PRESSURE_PHRASES = [
    "hurry", "quick", "quickly", "asap", "in a rush", "running late",
    "deadline", "minutes left", "before my shift", "before my meeting",
    "due at", "due in", "no time",
]

REPEAT_PHRASES = [
    "say that again", "repeat that", "what did you say", "again please",
    "can you repeat", "you already said", "i asked already",
]

FACTUAL_LOOKUP_RE = re.compile(
    r"^\s*(what is|what's|whats|who is|who's|when is|when did|when was|"
    r"define|how do you spell|how do you say|what does [\w\- ]+ mean)\b"
)

SHIFT_UP_RE = re.compile(r"\bshift up\b", re.IGNORECASE)
SHIFT_DOWN_RE = re.compile(r"\bshift down\b", re.IGNORECASE)
LEVER_HOLD_PHRASES = ["for this thread", "for this conversation",
                      "until i say", "keep it there"]
BACK_TO_NORMAL_PHRASES = ["back to normal", "reset the throttle",
                          "normal mode"]


def _contains_any(text: str, phrases: list[str]) -> list[str]:
    low = text.lower()
    return [p for p in phrases if p in low]


def _word_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9']+", text.lower()))


def _jaccard(a: str, b: str) -> float:
    wa, wb = _word_set(a), _word_set(b)
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


# --------------------------------------------------------------------------
# Topic gate (ds-tutor only)
# --------------------------------------------------------------------------

DS_CONTEXT_MARKERS = [
    "p-value", "p value", "hypothesis", "regression", "correlation",
    "dataset", "data set", "sample size", "variance", "standard deviation",
    "distribution", "probability", "confidence interval", "t-test",
    "chi-square", "anova", "bayes", "training data", "overfit",
    "classification", "clustering", "machine learning",
    "data science", "statistics", "statistical", "survival analysis",
    "kaplan", "censoring", "censored", "hazard", "cox",
    "sql", "join", "query", "database", "schema", "normalize",
    "normalization", "primary key", "foreign key",
    "pandas", "numpy", "dataframe", "scatter", "histogram",
    "spreadsheet", "homework", "assignment", "coursework",
    "test whether", "compare groups", "comparing groups",
    "significant difference", "difference between the groups",
]


def detect_ds_context(message: str, prior_user_messages: list[str]) -> bool:
    """True if this message — or the recent session — is in DS scope.

    Stickiness is deliberate: once a session is in data-science territory,
    short topic-free follow-ups ("can not. brain is fried") stay in scope,
    which is what lets Priority 0 protect an active study session.
    """
    if _contains_any(message, DS_CONTEXT_MARKERS):
        return True
    return any(_contains_any(m, DS_CONTEXT_MARKERS)
               for m in prior_user_messages[-3:])


@dataclass
class Signals:
    attempt_shown: bool = False
    frustrated: bool = False
    exhaustion: bool = False
    fragmentation_dropoff: bool = False
    repeat_request: bool = False
    stall: bool = False
    just_tell_me: bool = False
    time_pressured: bool = False
    factual_lookup: bool = False
    lever: str | None = None            # "up" | "down" | None
    lever_hold: bool = False
    notes: list[str] = field(default_factory=list)


def detect_signals(message: str, prior_user_messages: list[str]) -> Signals:
    """Read the signals for one message, given the user's earlier messages."""
    s = Signals()
    low = message.lower()

    s.exhaustion = bool(_contains_any(message, EXHAUSTION_PHRASES))
    if s.exhaustion:
        s.notes.append("exhaustion language")

    s.stall = bool(_contains_any(message, STALL_PHRASES))
    if s.stall:
        s.notes.append("first-step stall language")

    # Fragmentation drop-off: the *drop* is the signal, not the baseline.
    # Needs a baseline of longer messages, then a clipped single-liner.
    words = len(message.split())
    prior_lengths = [len(m.split()) for m in prior_user_messages]
    if len(prior_lengths) >= 2:
        baseline = sum(prior_lengths[-3:]) / len(prior_lengths[-3:])
        if baseline >= 12 and words <= 6 and "\n" not in message.strip():
            s.fragmentation_dropoff = True
            s.notes.append("fragmentation drop-off vs. recent baseline")

    # Repeat request: explicit phrasing, or a near-copy of an earlier question.
    if _contains_any(message, REPEAT_PHRASES):
        s.repeat_request = True
        s.notes.append("explicit repeat request")
    elif any(_jaccard(message, prev) >= 0.75 for prev in prior_user_messages):
        s.repeat_request = True
        s.notes.append("near-duplicate of an earlier message")

    # Affect: frustration phrases, or rephrasing the same question again.
    if _contains_any(message, FRUSTRATION_PHRASES):
        s.frustrated = True
        s.notes.append("frustration language")
    elif any(0.45 <= _jaccard(message, prev) < 0.75
             for prev in prior_user_messages):
        s.frustrated = True
        s.notes.append("rephrasing of an earlier question")

    # Attempt: own reasoning/work shown, or the carve-out — "I don't know
    # where to start" is a structural scaffolding need, not offloading.
    if _contains_any(message, ATTEMPT_MARKERS) or "```" in message or "=" in message:
        s.attempt_shown = True
        s.notes.append("attempt / work shown")
    if s.stall:
        s.attempt_shown = True
        s.notes.append("stall read as attempt (neurodivergent carve-out)")

    s.just_tell_me = bool(_contains_any(message, JUST_TELL_ME_PHRASES))
    s.time_pressured = bool(_contains_any(message, TIME_PRESSURE_PHRASES))
    s.factual_lookup = bool(FACTUAL_LOOKUP_RE.match(low)) and not s.attempt_shown

    # Levers. A bare lever pull is deliberate input, not a fragment signal.
    stripped = low.strip(" .!")
    if SHIFT_UP_RE.search(low):
        s.lever = "up"
    elif SHIFT_DOWN_RE.search(low) or "just answer" in low:
        s.lever = "down"
    if s.lever and any(p in low for p in LEVER_HOLD_PHRASES):
        s.lever_hold = True
    if s.lever and stripped in ("shift up", "shift down"):
        s.fragmentation_dropoff = False
        if "fragmentation drop-off vs. recent baseline" in s.notes:
            s.notes.remove("fragmentation drop-off vs. recent baseline")
        s.notes.append("bare lever pull (deliberate, not a fragment)")

    return s


# --------------------------------------------------------------------------
# The throttle
# --------------------------------------------------------------------------

@dataclass
class Decision:
    mode: ResponseMode
    priority_0: bool
    signals: Signals
    cab_read: str
    reasons: list[str] = field(default_factory=list)
    active: bool = True                  # False when the DS gate is closed.


class DSTutor:
    """Stateful per-conversation ds-tutor. Call decide() once per message."""

    def __init__(self) -> None:
        self.prior_user_messages: list[str] = []
        self._held_lever: str | None = None   # lever persisting across turns

    # -- internals ---------------------------------------------------------

    def _apply_lever(self, mode: ResponseMode,
                     lever: str) -> tuple[ResponseMode, str]:
        idx = FRICTION_LADDER.index(mode)
        if lever == "up":
            idx = min(idx + 1, len(FRICTION_LADDER) - 1)
        elif lever == "down":
            idx = max(idx - 1, 0)
        new_mode = FRICTION_LADDER[idx]
        return new_mode, f"lever 'shift {lever}': {mode.value} -> {new_mode.value}"

    # -- main entry point --------------------------------------------------

    def decide(self, message: str) -> Decision:
        signals = detect_signals(message, self.prior_user_messages)
        reasons: list[str] = list(signals.notes)
        cab = cab_interpretation(signals.attempt_shown, signals.frustrated)

        # Topic gate: outside data-science scope, ds-tutor does nothing.
        if not detect_ds_context(message, self.prior_user_messages):
            reasons.append(
                "ds-tutor inactive: not a data-science/coursework question")
            decision = Decision(ResponseMode.INACTIVE, False, signals,
                                "Outside ds-tutor's scope — no throttle.",
                                reasons, active=False)
            self.prior_user_messages.append(message)
            return decision

        if any(p in message.lower() for p in BACK_TO_NORMAL_PHRASES):
            self._held_lever = None
            reasons.append("lever hold released ('back to normal')")

        # 1. Priority 0 wins over everything.
        severe_stall = signals.stall and (signals.exhaustion
                                          or signals.repeat_request)
        priority_0 = (signals.exhaustion or signals.fragmentation_dropoff
                      or severe_stall
                      or (signals.repeat_request and signals.exhaustion))
        if priority_0:
            reasons.append("PRIORITY 0: friction removed, direct answer")
            decision = Decision(ResponseMode.DIRECT_ANSWER, True,
                                signals, cab, reasons)
            self.prior_user_messages.append(message)
            return decision

        # 2. Explicit overrides — always direct, never loop a nudge.
        if signals.just_tell_me:
            reasons.append("override: 'just tell me'")
            mode = ResponseMode.DIRECT_ANSWER
        elif signals.time_pressured:
            reasons.append("override: time pressure")
            mode = ResponseMode.DIRECT_ANSWER
        elif signals.repeat_request:
            reasons.append("override: repeat of an answered question")
            mode = ResponseMode.DIRECT_ANSWER
        elif signals.factual_lookup:
            reasons.append("override: factual lookup, not a reasoning task")
            mode = ResponseMode.DIRECT_ANSWER
        else:
            # 4. Reliance-spectrum triage (lever applied after).
            mode = triage(signals.attempt_shown, signals.frustrated)
            reasons.append(
                f"triage: attempt={signals.attempt_shown}, "
                f"frustrated={signals.frustrated} -> {mode.value}")
            # Neurodivergent carve-out: a first-step stall is a structural
            # scaffolding need, not a verification moment.
            if signals.stall and mode == ResponseMode.VERIFY:
                mode = ResponseMode.SCAFFOLD
                reasons.append("carve-out: stall routes to scaffold")

        # 3. Lever — this message's pull, or a held pull from earlier.
        #    Levers never add friction back onto an override direct answer.
        #    A one-shot pull (the default) applies to this response only;
        #    a held pull persists until "back to normal".
        lever = signals.lever or self._held_lever
        if signals.lever and signals.lever_hold:
            self._held_lever = signals.lever
            reasons.append("lever held for this thread")
        if lever and mode != ResponseMode.DIRECT_ANSWER:
            mode, note = self._apply_lever(mode, lever)
            reasons.append(note)

        decision = Decision(mode, False, signals, cab, reasons)
        self.prior_user_messages.append(message)
        return decision


# --------------------------------------------------------------------------
# Data-science pitfalls (flag proactively, per the ds-tutor spec)
# --------------------------------------------------------------------------

PITFALLS = {
    "p_hacking": [
        "ran it again until", "kept testing until", "keep testing until",
        "tried several tests", "tried a few tests",
        "tried different tests until", "tested lots of variables",
        "tested many variables", "removed outliers until",
        "until it was significant", "until p <", "until the p-value",
    ],
    "mishandled_censoring": [
        "dropped the censored", "dropping the censored",
        "drop the censored", "removed the censored",
        "remove the censored", "excluded the censored",
        "exclude the censored", "treated censored as events",
        "treated the censored as", "ignored the censoring",
        "ignore censoring", "dropped patients who left",
        "removed patients who dropped out", "excluded dropouts",
        "only patients who finished", "only complete cases",
    ],
    "kaplan_meier_misread": [
        "kaplan-meier proves", "kaplan meier proves",
        "survival curve proves", "curve proves",
        "average survival from the curve", "mean survival from the curve",
        "patients die at exactly", "the curve shows exactly when",
    ],
}

# A proportional-hazards flag is about an *absence*: a Cox / hazard-ratio
# analysis that never mentions checking the assumption.
PH_ANALYSIS_MARKERS = ["cox", "hazard ratio", "proportional hazards"]
PH_CHECK_MARKERS = [
    "schoenfeld", "checked the assumption", "check the assumption",
    "tested the assumption", "test the assumption", "assumption holds",
    "verified the assumption", "ph assumption",
]


def flag_pitfalls(text: str) -> list[str]:
    """Light-touch detector: names of pitfalls whose markers appear in text."""
    low = text.lower()
    hits = [name for name, markers in PITFALLS.items()
            if any(m in low for m in markers)]
    if any(m in low for m in PH_ANALYSIS_MARKERS) and not any(
            m in low for m in PH_CHECK_MARKERS):
        hits.append("unchecked_proportional_hazards")
    return hits


# --------------------------------------------------------------------------
# Demo
# --------------------------------------------------------------------------

DEMO_SCRIPT = [
    "What's a good marinade for chicken thighs?",
    "How do I test whether two groups differ on a measurement?",
    "I ran a t-test because the data looked roughly normal, but the "
    "p-value is 0.08 and I don't get why it's not significant, this is "
    "so frustrating",
    "I ran the Cox model after dropping the censored patients, and the "
    "hazard ratio came out 0.62 — is that a good result?",
    "shift down",
    "What does a p-value actually mean in plain English?",
    "I don't know where to start on the survival analysis assignment",
    "can not. brain is fried",
]


def _demo() -> None:
    throttle = DSTutor()
    for msg in DEMO_SCRIPT:
        d = throttle.decide(msg)
        print(f"USER: {msg}")
        print(f"  -> mode={d.mode.value}  priority_0={d.priority_0}")
        print(f"     CAB read: {d.cab_read}")
        for r in d.reasons:
            print(f"     - {r}")
        pitfalls = flag_pitfalls(msg)
        if pitfalls:
            print(f"     pitfalls flagged: {', '.join(pitfalls)}")
        print()


if __name__ == "__main__":
    _demo()
