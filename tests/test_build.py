"""Tests for dashboard/build.py parsers and build pipeline.

Run: python -m pytest tests/test_build.py -v
"""
import json
import os
import sys
import tempfile
import shutil

import pytest

# Add project root to path so we can import build
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "dashboard"))

import build

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures", "data")


@pytest.fixture(autouse=True)
def patch_data_dir(monkeypatch):
    """Point build.DATA_DIR at our test fixtures."""
    monkeypatch.setattr(build, "DATA_DIR", FIXTURES)


# ---------------------------------------------------------------------------
# Parser tests
# ---------------------------------------------------------------------------

class TestParseRocks:
    def test_loads_q1_rocks(self):
        rocks = build.load_rocks("2026-Q1")
        assert len(rocks) == 2

    def test_rock_fields(self):
        rocks = build.load_rocks("2026-Q1")
        r = rocks[0]  # rock-001
        assert r["id"] == "rock-001"
        assert r["title"] == "Launch Beta Program"
        assert r["owner"] == "Alice"
        assert r["quarter"] == "2026-Q1"
        assert r["status"] == "on_track"
        assert r["due"] == "2026-03-31"

    def test_rock_outcome(self):
        rocks = build.load_rocks("2026-Q1")
        assert "Beta program launched" in rocks[0]["outcome"]

    def test_rock_milestones(self):
        rocks = build.load_rocks("2026-Q1")
        ms = rocks[0]["milestones"]
        assert len(ms) == 3
        assert ms[0]["done"] is True
        assert ms[0]["text"] == "Set up staging environment"
        assert ms[1]["done"] is False

    def test_rock_status_values(self):
        rocks = build.load_rocks("2026-Q1")
        assert rocks[0]["status"] == "on_track"
        assert rocks[1]["status"] == "off_track"

    def test_draft_status(self):
        rocks = build.load_rocks("2026-Q2")
        assert len(rocks) == 1
        assert rocks[0]["status"] == "draft"

    def test_empty_quarter(self):
        rocks = build.load_rocks("2099-Q4")
        assert rocks == []

    def test_file_path_relative(self):
        rocks = build.load_rocks("2026-Q1")
        assert rocks[0]["file"].startswith("tests/fixtures/data/rocks/")


class TestLoadAllRocks:
    def test_finds_quarters(self):
        result = build.load_all_rocks()
        assert "2026-Q1" in result["quarters"]
        assert "2026-Q2" in result["quarters"]

    def test_current_quarter(self):
        result = build.load_all_rocks()
        # Current quarter should be valid format
        assert result["current_quarter"].startswith("202")
        assert "-Q" in result["current_quarter"]

    def test_quarter_window_max_six(self):
        result = build.load_all_rocks()
        assert len(result["quarters"]) <= 6

    def test_rocks_by_quarter(self):
        result = build.load_all_rocks()
        assert len(result["rocks_by_quarter"]["2026-Q1"]) == 2
        assert len(result["rocks_by_quarter"]["2026-Q2"]) == 1


class TestParseScorecard:
    def test_loads_metrics(self):
        metrics = build.load_scorecard()
        assert len(metrics) == 3

    def test_metric_fields(self):
        metrics = build.load_scorecard()
        m = metrics[0]
        assert m["metric"] == "Revenue calls"
        assert m["owner"] == "Alice"
        assert m["goal"] == "5/week"
        assert m["frequency"] == "Weekly"
        assert m["green"] == ">= 5"
        assert m["red"] == "< 3"

    def test_all_metrics_have_required_fields(self):
        metrics = build.load_scorecard()
        for m in metrics:
            assert m["metric"], "Metric name should not be empty"
            assert m["owner"], "Owner should not be empty"
            assert m["goal"], "Goal should not be empty"


class TestParseAccountability:
    def test_loads_seats(self):
        seats = build.load_accountability()
        assert len(seats) == 2

    def test_seat_fields(self):
        seats = build.load_accountability()
        s = seats[0]
        assert s["seat"] == "Visionary"
        assert s["owner"] == "Alice"
        assert len(s["roles"]) == 5

    def test_role_structure(self):
        seats = build.load_accountability()
        role = seats[0]["roles"][0]
        assert role["num"] == 1
        assert role["role"] == "Big relationships"

    def test_skips_non_seat_headings(self):
        seats = build.load_accountability()
        seat_names = [s["seat"] for s in seats]
        assert "Test Company" not in seat_names
        assert "How to Use This Chart" not in seat_names


class TestParseVision:
    def test_loads_vision(self):
        v = build.load_vision()
        assert v is not None
        assert len(v) > 0

    def test_core_values(self):
        v = build.load_vision()
        assert len(v["core_values"]) == 3
        assert v["core_values"][0]["name"] == "Integrity"

    def test_core_focus(self):
        v = build.load_vision()
        assert "tools that make teams better" in v["core_focus"]["purpose"]
        assert "SaaS" in v["core_focus"]["niche"]

    def test_ten_year_target(self):
        v = build.load_vision()
        assert "10,000" in v["ten_year_target"]

    def test_marketing(self):
        v = build.load_vision()
        m = v["marketing"]
        assert len(m["uniques"]) == 3
        assert m["uniques"][0]["name"] == "AI-native"
        assert len(m["process"]) == 3

    def test_three_year_picture(self):
        v = build.load_vision()
        labels = [i["label"] for i in v["three_year_picture"] if i["type"] == "labeled"]
        assert "Revenue" in labels
        assert "Profit" in labels

    def test_one_year_plan(self):
        v = build.load_vision()
        assert len(v["one_year_plan"]) >= 2


class TestParseL10:
    def test_loads_l10(self):
        l10 = build.load_l10()
        assert l10 is not None

    def test_attendees(self):
        l10 = build.load_l10()
        assert "Alice" in l10["attendees"]
        assert "Bob" in l10["attendees"]
        assert "Carol" in l10["attendees"]

    def test_sections(self):
        l10 = build.load_l10()
        assert len(l10["sections"]) == 7

    def test_section_structure(self):
        l10 = build.load_l10()
        s = l10["sections"][0]
        assert s["num"] == 1
        assert s["title"] == "Segue"
        assert s["minutes"] == 5

    def test_ids_section(self):
        l10 = build.load_l10()
        ids = [s for s in l10["sections"] if s["num"] == 6][0]
        assert ids["title"] == "IDS"
        assert ids["minutes"] == 60


class TestParseCalendar:
    def test_loads_events(self):
        events = build.load_calendar()
        assert len(events) == 4

    def test_event_fields(self):
        events = build.load_calendar()
        e = events[0]
        assert e["date"] == "2026-01-15"
        assert e["event"] == "CES 2026"
        assert e["type"] == "market"
        assert e["owner"] == "Alice"
        assert e["status"] == "past"

    def test_event_types(self):
        events = build.load_calendar()
        types = {e["type"] for e in events}
        assert "market" in types
        assert "partner" in types
        assert "fundraising" in types
        assert "constraint" in types

    def test_event_statuses(self):
        events = build.load_calendar()
        statuses = {e["status"] for e in events}
        assert "past" in statuses
        assert "upcoming" in statuses


class TestLoadTeam:
    def test_loads_team(self):
        names, cls = build.load_team()
        assert "Alice" in names
        assert "Bob" in names
        assert "Carol" in names

    def test_color_classes(self):
        names, cls = build.load_team()
        assert "Alice" in cls
        assert "bg-blue-100" in cls["Alice"]


class TestParseFrontmatter:
    def test_basic(self):
        fm, body = build.parse_frontmatter('---\ntitle: "Hello"\nstatus: active\n---\n\nBody text')
        assert fm["title"] == "Hello"
        assert fm["status"] == "active"
        assert "Body text" in body

    def test_no_frontmatter(self):
        fm, body = build.parse_frontmatter("Just text")
        assert fm == {}
        assert body == "Just text"

    def test_empty_frontmatter(self):
        fm, body = build.parse_frontmatter("---\n---\nBody")
        assert fm == {}
        assert "Body" in body


class TestParseMilestones:
    def test_checked(self):
        ms = build.parse_milestones("- [x] Done task\n- [ ] Open task")
        assert len(ms) == 2
        assert ms[0]["done"] is True
        assert ms[1]["done"] is False

    def test_text(self):
        ms = build.parse_milestones("- [ ] My milestone")
        assert ms[0]["text"] == "My milestone"

    def test_no_milestones(self):
        ms = build.parse_milestones("No checkboxes here")
        assert ms == []


class TestQuarterHelpers:
    def test_next_quarter(self):
        assert build._next_quarter("2026-Q1") == "2026-Q2"
        assert build._next_quarter("2026-Q4") == "2027-Q1"

    def test_prev_quarter(self):
        assert build._prev_quarter("2026-Q2") == "2026-Q1"
        assert build._prev_quarter("2026-Q1") == "2025-Q4"


# ---------------------------------------------------------------------------
# Integration test
# ---------------------------------------------------------------------------

class TestBuildIntegration:
    def test_full_build(self, monkeypatch, tmp_path):
        """Run the full build pipeline and verify the HTML output."""
        monkeypatch.setattr(build, "DOCS_DIR", str(tmp_path))
        monkeypatch.setattr(build, "DATA_DIR", FIXTURES)
        # Don't set password — test unprotected build
        monkeypatch.delenv("DASHBOARD_PASSWORD", raising=False)
        monkeypatch.delenv("GITHUB_WRITE_TOKEN", raising=False)

        build.build()

        out = tmp_path / "index.html"
        assert out.exists(), "index.html should be created"

        html = out.read_text(encoding="utf-8")

        # Check all tabs are present
        assert "tab-rocks" in html
        assert "tab-scorecard" in html
        assert "tab-accountability" in html
        assert "tab-l10" in html
        assert "tab-strategic-planning" in html
        assert "tab-calendar" in html

        # Check data is embedded
        assert "DASHBOARD_DATA" in html
        assert "Launch Beta Program" in html
        assert "Revenue calls" in html
        assert "Visionary" in html
        assert "CES 2026" in html

        # Check quarter chooser
        assert "2026-Q1" in html
        assert "2026-Q2" in html

        # Check it's valid-ish HTML
        assert html.startswith("<!DOCTYPE html>")
        assert "</html>" in html

    def test_build_with_password(self, monkeypatch, tmp_path):
        """Build with password protection enabled."""
        monkeypatch.setattr(build, "DOCS_DIR", str(tmp_path))
        monkeypatch.setattr(build, "DATA_DIR", FIXTURES)
        monkeypatch.setenv("DASHBOARD_PASSWORD", "testpass123")
        monkeypatch.delenv("GITHUB_WRITE_TOKEN", raising=False)

        try:
            build.build()
            out = tmp_path / "index.html"
            html = out.read_text(encoding="utf-8")
            # Password-protected page has the login form
            assert 'type="password"' in html
            # Raw data should NOT be visible
            assert "Launch Beta Program" not in html
        except ImportError:
            pytest.skip("cryptography package not installed")

    def test_data_json_valid(self, monkeypatch, tmp_path):
        """Verify the embedded JSON is valid."""
        monkeypatch.setattr(build, "DOCS_DIR", str(tmp_path))
        monkeypatch.setattr(build, "DATA_DIR", FIXTURES)
        monkeypatch.delenv("DASHBOARD_PASSWORD", raising=False)
        monkeypatch.delenv("GITHUB_WRITE_TOKEN", raising=False)

        build.build()
        html = (tmp_path / "index.html").read_text(encoding="utf-8")

        # Extract the JSON blob
        import re
        m = re.search(r"window\.DASHBOARD_DATA\s*=\s*(\{.*?\});\s*\n", html, re.DOTALL)
        assert m, "Should find DASHBOARD_DATA JSON in HTML"
        data = json.loads(m.group(1))

        assert "rocks" in data
        assert "scorecard" in data
        assert "accountability" in data
        assert "l10" in data
        assert "vision" in data
        assert "calendar" in data
        assert "rocks_by_quarter" in data
        assert "quarters" in data
        assert "current_quarter" in data


# ---------------------------------------------------------------------------
# Missing-data resilience
# ---------------------------------------------------------------------------

class TestMissingDataGraceful:
    """Loaders must degrade gracefully when data files are absent.

    The public repo ships without the private data/ tree, so the dashboard
    workflow builds against an empty data dir. Regression: the build failed at
    load_scorecard with FileNotFoundError on data/scorecard/metrics.md.
    """

    def test_scorecard_missing_returns_empty(self, monkeypatch, tmp_path):
        monkeypatch.setattr(build, "DATA_DIR", str(tmp_path))
        assert build.load_scorecard() == []

    def test_accountability_missing_returns_empty(self, monkeypatch, tmp_path):
        monkeypatch.setattr(build, "DATA_DIR", str(tmp_path))
        assert build.load_accountability() == []

    def test_l10_missing_returns_empty_shape(self, monkeypatch, tmp_path):
        monkeypatch.setattr(build, "DATA_DIR", str(tmp_path))
        assert build.load_l10() == {"schedule": "", "attendees": [], "sections": []}

    def test_full_build_with_no_data(self, monkeypatch, tmp_path):
        """The whole pipeline must complete against an empty data dir (the CI scenario)."""
        data_dir = tmp_path / "data"  # deliberately not created → fully empty
        docs_dir = tmp_path / "docs"
        monkeypatch.setattr(build, "DATA_DIR", str(data_dir))
        monkeypatch.setattr(build, "DOCS_DIR", str(docs_dir))
        monkeypatch.delenv("DASHBOARD_PASSWORD", raising=False)
        monkeypatch.delenv("GITHUB_WRITE_TOKEN", raising=False)

        build.build()

        out = docs_dir / "index.html"
        assert out.exists(), "index.html should still be produced with no data"
        html = out.read_text(encoding="utf-8")
        assert html.startswith("<!DOCTYPE html>")
        assert "tab-scorecard" in html  # tabs render even with empty datasets
