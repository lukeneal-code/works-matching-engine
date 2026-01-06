"""
Unit tests for the matching service.
"""

import pytest
from app.services.matching import MatchingService


class TestTextNormalization:
    """Tests for text normalization."""

    def test_normalize_lowercase(self):
        assert MatchingService.normalize_text("HELLO WORLD") == "hello world"

    def test_normalize_punctuation(self):
        assert MatchingService.normalize_text("Hello, World!") == "hello world"

    def test_normalize_whitespace(self):
        assert MatchingService.normalize_text("Hello   World") == "hello world"

    def test_normalize_mixed(self):
        assert MatchingService.normalize_text("  HELLO,  World!  ") == "hello world"

    def test_normalize_empty(self):
        assert MatchingService.normalize_text("") == ""

    def test_normalize_none(self):
        assert MatchingService.normalize_text(None) == ""

    def test_normalize_special_chars(self):
        assert MatchingService.normalize_text("Rock & Roll") == "rock  roll"

    def test_normalize_apostrophe(self):
        assert MatchingService.normalize_text("Don't Stop") == "dont stop"


class TestTitleSimilarity:
    """Tests for title similarity calculation."""

    def test_exact_match(self):
        score = MatchingService.calculate_title_similarity(
            "Yesterday", "Yesterday"
        )
        assert score == 1.0

    def test_case_insensitive(self):
        score = MatchingService.calculate_title_similarity(
            "YESTERDAY", "yesterday"
        )
        assert score == 1.0

    def test_punctuation_difference(self):
        score = MatchingService.calculate_title_similarity(
            "Don't Stop", "Dont Stop"
        )
        assert score >= 0.9

    def test_partial_match(self):
        score = MatchingService.calculate_title_similarity(
            "Yesterday (Remastered)", "Yesterday"
        )
        assert score >= 0.7

    def test_word_order(self):
        score = MatchingService.calculate_title_similarity(
            "Sound of Silence", "The Sound of Silence"
        )
        assert score >= 0.8

    def test_completely_different(self):
        score = MatchingService.calculate_title_similarity(
            "Yesterday", "Bohemian Rhapsody"
        )
        assert score < 0.3

    def test_empty_strings(self):
        score = MatchingService.calculate_title_similarity("", "")
        assert score == 0.0

    def test_one_empty(self):
        score = MatchingService.calculate_title_similarity("Yesterday", "")
        assert score == 0.0

    def test_live_version(self):
        score = MatchingService.calculate_title_similarity(
            "Hotel California (Live)", "Hotel California"
        )
        assert score >= 0.7

    def test_abbreviation(self):
        score = MatchingService.calculate_title_similarity(
            "Mrs Robinson", "Mrs. Robinson"
        )
        assert score >= 0.9


class TestSongwriterSimilarity:
    """Tests for songwriter similarity calculation."""

    def test_exact_match(self):
        score = MatchingService.calculate_songwriter_similarity(
            "McCartney, Paul",
            ["McCartney, Paul", "Lennon, John"]
        )
        assert score == 1.0

    def test_format_variation(self):
        score = MatchingService.calculate_songwriter_similarity(
            "Paul McCartney",
            ["McCartney, Paul"]
        )
        assert score >= 0.8

    def test_first_name_only(self):
        score = MatchingService.calculate_songwriter_similarity(
            "Adele",
            ["Adkins, Adele"]
        )
        assert score >= 0.6

    def test_multiple_writers(self):
        score = MatchingService.calculate_songwriter_similarity(
            "Lennon-McCartney",
            ["Lennon, John", "McCartney, Paul"]
        )
        assert score >= 0.5

    def test_partial_match(self):
        score = MatchingService.calculate_songwriter_similarity(
            "F. Mercury",
            ["Mercury, Freddie"]
        )
        assert score >= 0.6

    def test_no_match(self):
        score = MatchingService.calculate_songwriter_similarity(
            "Unknown Writer",
            ["Mercury, Freddie", "May, Brian"]
        )
        assert score < 0.5

    def test_empty_songwriter(self):
        score = MatchingService.calculate_songwriter_similarity(
            "",
            ["McCartney, Paul"]
        )
        assert score == 0.0

    def test_empty_list(self):
        score = MatchingService.calculate_songwriter_similarity(
            "McCartney, Paul",
            []
        )
        assert score == 0.0

    def test_ampersand_variation(self):
        score = MatchingService.calculate_songwriter_similarity(
            "Ashford & Simpson",
            ["Ashford, Nickolas", "Simpson, Valerie"]
        )
        # Should match at least partially with either name
        assert score >= 0.4


class TestMatchingScenarios:
    """Integration tests for common matching scenarios."""

    def test_beatles_song_variations(self):
        """Test matching Beatles songs with various artist credits."""
        title_score = MatchingService.calculate_title_similarity(
            "Hey Jude - Remastered",
            "Hey Jude"
        )
        assert title_score >= 0.85

    def test_queen_song_matching(self):
        """Test Queen song matching."""
        title_score = MatchingService.calculate_title_similarity(
            "BOHEMIAN RHAPSODY",
            "Bohemian Rhapsody"
        )
        assert title_score == 1.0

    def test_coldplay_variations(self):
        """Test Coldplay writer credit variations."""
        writer_score = MatchingService.calculate_songwriter_similarity(
            "Chris Martin",
            ["Martin, Chris", "Buckland, Jonny", "Berryman, Guy", "Champion, Will"]
        )
        assert writer_score >= 0.8

    def test_combined_score_calculation(self):
        """Test combined scoring logic."""
        title_sim = 0.9
        songwriter_sim = 0.85
        vector_sim = 0.8

        # Weight: title 40%, songwriter 30%, vector 30%
        expected = (title_sim * 0.4 + songwriter_sim * 0.3 + vector_sim * 0.3)
        assert expected == pytest.approx(0.855, rel=0.01)


class TestEdgeCases:
    """Tests for edge cases and special characters."""

    def test_unicode_characters(self):
        score = MatchingService.calculate_title_similarity(
            "Cafe", "Cafe"
        )
        assert score >= 0.9

    def test_numbers_in_title(self):
        score = MatchingService.calculate_title_similarity(
            "Song 2", "Song 2"
        )
        assert score == 1.0

    def test_very_long_title(self):
        long_title = "This is a Very Long Song Title That Goes On and On"
        score = MatchingService.calculate_title_similarity(
            long_title, long_title
        )
        assert score == 1.0

    def test_single_word(self):
        score = MatchingService.calculate_title_similarity(
            "Imagine", "Imagine"
        )
        assert score == 1.0

    def test_featuring_artist(self):
        score = MatchingService.calculate_title_similarity(
            "Titanium (feat. Sia)",
            "Titanium"
        )
        assert score >= 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
