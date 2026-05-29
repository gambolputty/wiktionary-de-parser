"""Unit tests for ``translate_inflection_key``.

The function is exercised indirectly by ``test_flexion.py`` (which
applies it to the test-data expected dicts) but the translation logic
itself deserves direct coverage — token classes, adjacent-duplicate
collapse, Roman-numeral handling, unknown-token passthrough.
"""

import pytest

from wiktionary_de_parser.parsers.inflection import translate_inflection_key


class TestNounCases:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("Nominativ Singular", "nominative_singular"),
            ("Genitiv Plural", "genitive_plural"),
            ("Dativ Singular", "dative_singular"),
            ("Akkusativ Plural", "accusative_plural"),
            ("Genus", "gender"),
            ("Genus 1", "gender_1"),
            ("Genus 4", "gender_4"),
        ],
    )
    def test_basic_case_and_number(self, raw, expected):
        assert translate_inflection_key(raw) == expected


class TestAdjective:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("Nominativ Singular stark", "nominative_singular_strong"),
            ("Nominativ Plural schwach", "nominative_plural_weak"),
            ("Akkusativ Singular gemischt", "accusative_singular_mixed"),
            ("Positiv", "positive"),
            ("Komparativ", "comparative"),
            ("Superlativ", "superlative"),
        ],
    )
    def test_adjective_forms(self, raw, expected):
        assert translate_inflection_key(raw) == expected


class TestVerb:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("Präsens_ich", "present_1sg"),
            ("Präsens_du", "present_2sg"),
            ("Präteritum_ich", "preterite_1sg"),
            ("Konjunktiv II_ich", "subjunctive_2_1sg"),
            ("Konjunktiv I_wir", "subjunctive_1_1pl"),
            ("Imperativ Singular", "imperative_singular"),
            ("Imperativ Plural", "imperative_plural"),
            ("Partizip II", "participle_2"),
            ("Partizip I", "participle_1"),
            ("Hilfsverb", "auxiliary"),
            ("Futur I_du", "future_1_2sg"),
        ],
    )
    def test_verb_forms(self, raw, expected):
        assert translate_inflection_key(raw) == expected

    def test_collapses_er_sie_es_to_3sg(self):
        """``er, sie, es`` all map to ``3sg``; adjacent duplicates are
        collapsed so ``Präsens_er, sie, es`` does not blow up to
        ``present_3sg_3sg_3sg``."""
        assert translate_inflection_key("Präsens_er, sie, es") == "present_3sg"
        assert (
            translate_inflection_key("Konjunktiv I_er, sie, es")
            == "subjunctive_1_3sg"
        )


class TestSpecialTokens:
    def test_kein_plural(self):
        assert translate_inflection_key("kein Plural") == "no_plural"

    def test_stamm(self):
        assert translate_inflection_key("Stamm") == "stem"

    def test_unknown_token_passes_through_lowercase(self):
        """An unknown German term keeps its lowercase form rather than
        guessing a translation. Pinning this is important so future
        Wiktionary tables don't silently produce empty keys."""
        assert (
            translate_inflection_key("Ungewöhnlich Singular")
            == "ungewöhnlich_singular"
        )

    def test_pure_numbers_pass_through(self):
        """Bare digits (gender index) must not be translated."""
        assert translate_inflection_key("Genus 2") == "gender_2"

    def test_empty_input(self):
        assert translate_inflection_key("") == ""


class TestSeparators:
    """Spaces, underscores, ``", "`` are all token separators — the
    result should be identical regardless of which one was used in the
    source string."""

    def test_space_vs_underscore_equivalent(self):
        assert translate_inflection_key(
            "Präsens ich"
        ) == translate_inflection_key("Präsens_ich")

    def test_comma_space_treated_as_separator(self):
        assert translate_inflection_key(
            "Präsens_er, sie, es"
        ) == translate_inflection_key("Präsens er sie es")
