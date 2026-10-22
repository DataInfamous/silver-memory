"""Tests for ds_tutor.py — the data-science-scoped throttle fork.

Runnable two ways:
    python -m pytest tests/
    python tests/test_ds_tutor.py   (no pytest needed)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ds_tutor import DSTutor, ResponseMode, flag_pitfalls  # noqa: E402


# --- the topic gate ---------------------------------------------------------

def test_inactive_outside_ds_scope():
    t = DSTutor()
    d = t.decide("What's a good marinade for chicken thighs?")
    assert d.mode is ResponseMode.INACTIVE
    assert not d.active
    assert not d.priority_0


def test_bare_ds_question_activates_and_pushes_back():
    t = DSTutor()
    d = t.decide("How do I test whether two groups differ on a measurement?")
    assert d.active
    assert d.mode is ResponseMode.PUSH_BACK


def test_gate_stickiness_keeps_short_followups_in_scope():
    t = DSTutor()
    t.decide("How do I test whether two groups differ on a measurement?")
    d = t.decide("I still don't get it")
    assert d.active
    assert d.mode is ResponseMode.SCAFFOLD  # no attempt + frustrated


# --- the shared engine still applies inside scope ---------------------------

def test_ds_attempt_plus_frustration_encourages():
    t = DSTutor()
    d = t.decide(
        "I ran a t-test because the data looked roughly normal, but the "
        "p-value is 0.08 and I don't get why it's not significant")
    assert d.mode is ResponseMode.ENCOURAGE_HINT


def test_factual_lookup_inside_scope_is_direct():
    t = DSTutor()
    d = t.decide("What does a p-value mean, exactly?")
    assert d.active
    assert d.mode is ResponseMode.DIRECT_ANSWER


def test_stall_inside_scope_scaffolds():
    t = DSTutor()
    d = t.decide("I don't know where to start on the survival "
                 "analysis assignment")
    assert d.mode is ResponseMode.SCAFFOLD


def test_priority0_still_wins_inside_ds_session():
    t = DSTutor()
    t.decide("How do I test whether two groups differ on a measurement?")
    d = t.decide("can not. brain is fried")
    assert d.priority_0
    assert d.mode is ResponseMode.DIRECT_ANSWER


def test_lever_still_works_inside_scope():
    t = DSTutor()
    d = t.decide("shift down — how do I test whether two groups differ?")
    assert d.active
    assert d.mode is ResponseMode.SCAFFOLD  # push_back stepped down once


# --- the data-science pitfalls ----------------------------------------------

def test_pitfall_p_hacking():
    hits = flag_pitfalls("I kept testing until it was significant")
    assert "p_hacking" in hits


def test_pitfall_mishandled_censoring():
    hits = flag_pitfalls(
        "I dropped the censored patients and ran the model on the rest")
    assert "mishandled_censoring" in hits


def test_pitfall_unchecked_proportional_hazards():
    hits = flag_pitfalls("I ran a Cox model; the hazard ratio was 0.62")
    assert "unchecked_proportional_hazards" in hits


def test_checked_proportional_hazards_not_flagged():
    hits = flag_pitfalls(
        "I ran a Cox model and checked the Schoenfeld residuals — "
        "the assumption holds")
    assert "unchecked_proportional_hazards" not in hits


def test_pitfall_kaplan_meier_misread():
    hits = flag_pitfalls("The survival curve proves the treatment works")
    assert "kaplan_meier_misread" in hits


def test_general_pitfalls_are_not_in_the_fork():
    # The fork swapped the general list for the data-science list.
    hits = flag_pitfalls("I've already spent too much money to quit now")
    assert hits == []


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in sorted(globals().items())
             if name.startswith("test_") and callable(fn)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {name}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
