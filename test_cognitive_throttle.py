"""Tests for cognitive_throttle.py.

Runnable two ways:
    python -m pytest tests/
    python tests/test_cognitive_throttle.py   (no pytest needed)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cognitive_throttle import (  # noqa: E402
    CognitiveThrottle,
    ResponseMode,
    cab_interpretation,
    flag_pitfalls,
    triage,
)


# --- the 2x2 reliance-spectrum table --------------------------------------

def test_triage_table():
    assert triage(False, False) is ResponseMode.PUSH_BACK
    assert triage(False, True) is ResponseMode.SCAFFOLD
    assert triage(True, True) is ResponseMode.ENCOURAGE_HINT
    assert triage(True, False) is ResponseMode.VERIFY


def test_bare_neutral_question_pushes_back():
    t = CognitiveThrottle()
    d = t.decide("How do I decide if a correlation is real or just noise?")
    assert d.mode is ResponseMode.PUSH_BACK
    assert not d.priority_0


def test_attempt_plus_frustration_encourages():
    t = CognitiveThrottle()
    d = t.decide(
        "I split the data by group because pooling hid the trend, "
        "but the effect vanished and I don't get why this keeps happening")
    assert d.mode is ResponseMode.ENCOURAGE_HINT


def test_attempt_neutral_verifies_only():
    t = CognitiveThrottle()
    d = t.decide(
        "I ran the subgroup analysis and the correlation held in two of "
        "three groups. Does that match what you'd expect?")
    assert d.mode is ResponseMode.VERIFY


def test_no_attempt_frustrated_scaffolds():
    t = CognitiveThrottle()
    d = t.decide("I don't get joins at all, this makes no sense")
    assert d.mode is ResponseMode.SCAFFOLD


# --- Priority 0 ------------------------------------------------------------

def test_priority0_exhaustion_language():
    t = CognitiveThrottle()
    d = t.decide("can not. too much. done for today")
    assert d.priority_0
    assert d.mode is ResponseMode.DIRECT_ANSWER


def test_priority0_fragmentation_dropoff():
    t = CognitiveThrottle()
    t.decide("I have been working through the normalization chapter and "
             "taking notes on each functional dependency as I go along")
    t.decide("The examples with composite keys finally made sense once "
             "I drew out the tables by hand on paper yesterday evening")
    d = t.decide("idk")
    assert d.priority_0
    assert d.mode is ResponseMode.DIRECT_ANSWER


def test_priority0_does_not_latch():
    t = CognitiveThrottle()
    t.decide("can not. too much. done for today")
    d = t.decide("How do I decide if a correlation is real or just noise?")
    assert not d.priority_0


def test_bare_lever_is_not_a_fragment_signal():
    t = CognitiveThrottle()
    t.decide("I have been working through the normalization chapter and "
             "taking notes on each functional dependency as I go along")
    t.decide("The examples with composite keys finally made sense once "
             "I drew out the tables by hand on paper yesterday evening")
    d = t.decide("shift down")
    assert not d.priority_0


# --- overrides --------------------------------------------------------------

def test_just_tell_me_override():
    t = CognitiveThrottle()
    d = t.decide("just tell me the formula")
    assert d.mode is ResponseMode.DIRECT_ANSWER


def test_factual_lookup_override():
    t = CognitiveThrottle()
    d = t.decide("What is a p-value?")
    assert d.mode is ResponseMode.DIRECT_ANSWER


def test_time_pressure_override():
    t = CognitiveThrottle()
    d = t.decide("This is due in 20 minutes, quick — which join keeps "
                 "unmatched rows?")
    assert d.mode is ResponseMode.DIRECT_ANSWER


def test_repeat_question_never_nudged_twice():
    t = CognitiveThrottle()
    q = "How do I decide if a correlation is real or just noise?"
    first = t.decide(q)
    assert first.mode is ResponseMode.PUSH_BACK
    second = t.decide(q)
    assert second.mode is ResponseMode.DIRECT_ANSWER


# --- neurodivergent carve-out ----------------------------------------------

def test_stall_routes_to_scaffold():
    t = CognitiveThrottle()
    d = t.decide("I don't know where to start on the joins homework")
    assert d.mode is ResponseMode.SCAFFOLD
    assert not d.priority_0


# --- levers ------------------------------------------------------------------

def test_shift_up_increases_friction_one_step():
    t = CognitiveThrottle()
    # Attempt + neutral lands on VERIFY; a held shift-up moves it one step.
    d = t.decide("shift up for this thread")
    d2 = t.decide(
        "I ran the subgroup analysis and the correlation held in two of "
        "three groups. Does that match what you'd expect?")
    assert d2.mode is ResponseMode.ENCOURAGE_HINT


def test_shift_down_decreases_friction_one_step():
    t = CognitiveThrottle()
    d = t.decide("shift down — How do I decide if a correlation is real?")
    assert d.mode is ResponseMode.SCAFFOLD  # push_back stepped down once


def test_back_to_normal_releases_held_lever():
    t = CognitiveThrottle()
    t.decide("shift up for this thread")
    t.decide("back to normal")
    d = t.decide(
        "I ran the subgroup analysis and the correlation held in two of "
        "three groups. Does that match what you'd expect?")
    assert d.mode is ResponseMode.VERIFY


# --- CAB bridge + pitfalls ---------------------------------------------------

def test_cab_interpretation_covers_spectrum():
    assert "substitution" in cab_interpretation(False, False)
    assert "frustration" in cab_interpretation(False, True)
    assert "struggle" in cab_interpretation(True, True)
    assert "independent" in cab_interpretation(True, False)


def test_flag_pitfalls():
    hits = flag_pitfalls(
        "It worked for me, and I've already spent too much to quit now")
    assert "anecdote_as_data" in hits
    assert "sunk_cost" in hits


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
