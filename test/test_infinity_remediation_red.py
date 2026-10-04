"""RED-phase tests for SC-8 (issue #1382): seed files must contain zero U+221E.

Co-authored with AI: OpenCode (zai-org/GLM-5.3-Flash)
"""

import unittest
from pathlib import Path


class TestSeedInfinityRemediationRED(unittest.TestCase):
    """SC-8: seed data files contain zero U+221E (INFINITY) characters."""

    @classmethod
    def setUpClass(cls):
        try:
            import pgserver
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker

            import src.database.models  # noqa: F401  ensure metadata is populated
            from src.database.base import Base

            cls.test_db_path = Path("tmp/test_infinity_remediation_red_db")
            if cls.test_db_path.exists():
                import shutil

                shutil.rmtree(cls.test_db_path)
            cls.test_db_path.mkdir(parents=True, exist_ok=True)

            cls.pg_server = pgserver.get_server(str(cls.test_db_path))
            cls.db_url = cls.pg_server.get_uri()
            cls.engine = create_engine(cls.db_url)
            with cls.engine.begin() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            Base.metadata.create_all(cls.engine)
            cls.Session = sessionmaker(bind=cls.engine)
        except ImportError:
            raise unittest.SkipTest("pgserver not available") from None

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if hasattr(cls, "test_db_path") and cls.test_db_path.exists():
            import shutil

            shutil.rmtree(cls.test_db_path)

    INFINITY = "\u221e"

    def _seed_file(self, name: str) -> Path:
        path = Path("src/seed_data") / name
        self.assertTrue(path.exists(), f"missing seed file: {path}")
        return path

    def test_natick_sample_100_zero_infinity(self):
        path = self._seed_file("natick_sample_100.txt")
        content = path.read_text(encoding="utf-8")
        count = content.count(self.INFINITY)
        self.assertEqual(count, 0, f"found {count} U+221E occurrences in {path.name}")

    def test_natick_sample_100_no_diacritics_zero_infinity(self):
        path = self._seed_file("natick_sample_100_no_diacritics.txt")
        content = path.read_text(encoding="utf-8")
        count = content.count(self.INFINITY)
        self.assertEqual(count, 0, f"found {count} U+221E occurrences in {path.name}")


class TestInfinityScanFixtureRED(unittest.TestCase):
    """SC-2 + SC-10 (issue #1382): ∞ defect scan over a seeded fixture DB.

    SC-2: count_infinity_records() counts non-deleted records with ∞ in lx or
    mdf_data; list_infinity_records() returns id/lx/preview/is_locked entries.
    SC-10: locked defective records are reported separately (is_locked flag,
    locked count >= 1) and are NOT part of the remediable set; soft-deleted
    defective records are excluded entirely.
    """

    INFINITY = "∞"  # direct Unicode literal U+221E — no ASCII regex

    @classmethod
    def setUpClass(cls):
        try:
            import pgserver
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker

            import src.database.models.core  # noqa: F401  populate mapper registry
            import src.database.models.identity  # noqa: F401
            import src.database.models.iso639  # noqa: F401
            import src.database.models.meta  # noqa: F401
            import src.database.models.search  # noqa: F401
            import src.database.models.workflow  # noqa: F401
            from src.database.base import Base

            cls.test_db_path = Path("tmp/test_infinity_scan_fixture_red_db")
            if cls.test_db_path.exists():
                import shutil

                shutil.rmtree(cls.test_db_path)
            cls.test_db_path.mkdir(parents=True, exist_ok=True)

            cls.pg_server = pgserver.get_server(str(cls.test_db_path))  # pyright: ignore[reportPrivateImportUsage]
            cls.db_url = cls.pg_server.get_uri()
            cls.engine = create_engine(cls.db_url)
            with cls.engine.begin() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            Base.metadata.create_all(cls.engine)
            cls.Session = sessionmaker(bind=cls.engine)

            # Route LinguisticService's get_session() to the fixture DB.
            import src.database.connection as conn_mod

            cls._orig_db_url_cache = conn_mod._db_url_cache
            conn_mod._db_url_cache = cls.db_url

            cls._seed()
        except ImportError:
            raise unittest.SkipTest("pgserver not available") from None

    @classmethod
    def _seed(cls):
        from src.database.models.core import Record, Source
        from src.database.models.identity import User

        with cls.Session() as session:
            session.add(
                User(
                    email="test@example.com",
                    username="testuser",
                    github_id=1,
                    full_name="Test User",
                )
            )
            source = Source(name="Natick/Trumbull", short_name="N/T")
            session.add(source)
            session.flush()

            def rec(lx, mdf, **kw):
                return Record(
                    lx=lx,
                    source_id=source.id,
                    mdf_data=mdf,
                    status="draft",
                    **kw,
                )

            cls.record_a = rec(
                "k∞",
                "\\lx k∞\n\\ps n\n\\ge house\n",
            )
            cls.record_b = rec(
                "kanadi",
                "\\lx kanadi\n\\ge bucket\n\\nt ∞ defect in notes\n",
            )
            cls.record_c = rec(
                "muhkun",
                "\\lx muhkun\n\\ge axe\n",
            )
            cls.record_d = rec(
                "pa∞",
                "\\lx pa∞\n\\ge basket\n",
                is_deleted=True,
            )
            cls.record_e = rec(
                "s∞k",
                "\\lx s∞k\n\\ge plum\n",
                is_locked=True,
                locked_by="test@example.com",
            )
            session.add_all(
                [cls.record_a, cls.record_b, cls.record_c, cls.record_d, cls.record_e]
            )
            session.commit()
            cls.ids = {
                "A": cls.record_a.id,
                "B": cls.record_b.id,
                "C": cls.record_c.id,
                "D": cls.record_d.id,
                "E": cls.record_e.id,
            }

    @classmethod
    def tearDownClass(cls):
        import src.database.connection as conn_mod

        conn_mod._db_url_cache = cls._orig_db_url_cache
        # Drop the engine cached by st.cache_resource on get_engine() — it is
        # bound to this fixture's pgserver socket, which is about to be
        # removed; leaving it cached breaks any later test in the same
        # pytest session that resolves a database engine.
        import streamlit as st

        st.cache_resource.clear()
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if hasattr(cls, "test_db_path") and cls.test_db_path.exists():
            import shutil

            shutil.rmtree(cls.test_db_path)

    def test_sc2_remediable_count_is_two(self):
        from src.services.linguistic_service import LinguisticService

        self.assertEqual(LinguisticService.count_infinity_records(), 2)

    def test_sc2_list_returns_a_and_b_with_previews(self):
        from src.services.linguistic_service import LinguisticService

        entries = LinguisticService.list_infinity_records()
        ids = [e["id"] for e in entries]
        self.assertIn(self.ids["A"], ids)
        self.assertIn(self.ids["B"], ids)
        self.assertNotIn(self.ids["C"], ids)
        self.assertNotIn(self.ids["D"], ids)
        for entry in entries:
            self.assertIn("lx", entry)
            self.assertIn("preview", entry)
            self.assertTrue(entry["preview"], "preview must be non-empty")

    def test_sc2_remediable_set_excludes_locked_and_deleted(self):
        from src.services.linguistic_service import LinguisticService

        entries = LinguisticService.list_infinity_records()
        remediable = [e["id"] for e in entries if not e.get("is_locked")]
        self.assertEqual(remediable, [self.ids["A"], self.ids["B"]])
        self.assertNotIn(self.ids["E"], remediable)

    def test_sc10_locked_defective_reported_separately(self):
        from src.services.linguistic_service import LinguisticService

        entries = LinguisticService.list_infinity_records()
        locked = [e for e in entries if e.get("is_locked")]
        self.assertGreaterEqual(len(locked), 1)
        self.assertIn(self.ids["E"], [e["id"] for e in locked])
        # Locked count reported separately: E is not in the remediable count.
        self.assertEqual(LinguisticService.count_infinity_records(), 2)


class TestGenerateSortLxLigature(unittest.TestCase):
    """SC-1 + SC-9 (issue #1382): generate_sort_lx long-vowel letter handling.

    SC-9 regression pin: ∞ (U+221E) maps to "oozzz".
    SC-1 RED: ꝏ (U+A74F LATIN SMALL LETTER OO) must also map to "oozzz" —
    it currently falls through the symbol_map and fails.
    """

    def test_infinity_maps_to_oozzz(self):
        from src.services.linguistic_service import LinguisticService

        self.assertEqual(LinguisticService.generate_sort_lx("k∞"), "koozzz")

    def test_oo_ligature_maps_to_oozzz(self):
        from src.services.linguistic_service import LinguisticService

        self.assertEqual(LinguisticService.generate_sort_lx("kꝏ"), "koozzz")


class TestRemediateAllRecordsRED(unittest.TestCase):
    """SC-5 + SC-11 + SC-12 + SC-13 (issue #1382): remediate_all_records().

    SC-5: A and B remediated — lx/mdf_data contain ꝏ (U+A74F) and contain no
    ∞ (U+221E); sort_lx recomputed via generate_sort_lx; search entry term
    values remediated; current_version unchanged; NO edit_history rows created
    (maintenance framing — zero EditHistory writes).
    SC-11: locked record E's lx/mdf_data/sort_lx/current_version identical to
    pre-run values, no edit_history row for E.
    SC-12: outcome report dict == {remediated: 2, locked: 1}.
    SC-13: locked presence does not block remediation of A and B.
    """

    INFINITY = "∞"  # direct Unicode literal U+221E
    OO_LIGATURE = "ꝏ"  # direct Unicode literal U+A74F

    @classmethod
    def setUpClass(cls):
        try:
            import pgserver
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker

            import src.database.models.core  # noqa: F401  populate mapper registry
            import src.database.models.identity  # noqa: F401
            import src.database.models.iso639  # noqa: F401
            import src.database.models.meta  # noqa: F401
            import src.database.models.search  # noqa: F401
            import src.database.models.workflow  # noqa: F401
            from src.database.base import Base

            cls.test_db_path = Path("tmp/test_remediate_all_red_db")
            if cls.test_db_path.exists():
                import shutil

                shutil.rmtree(cls.test_db_path)
            cls.test_db_path.mkdir(parents=True, exist_ok=True)

            cls.pg_server = pgserver.get_server(str(cls.test_db_path))  # pyright: ignore[reportPrivateImportUsage]
            cls.db_url = cls.pg_server.get_uri()
            cls.engine = create_engine(cls.db_url)
            with cls.engine.begin() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            Base.metadata.create_all(cls.engine)
            cls.Session = sessionmaker(bind=cls.engine)

            # Route LinguisticService's get_session() to the fixture DB.
            import src.database.connection as conn_mod

            cls._orig_db_url_cache = conn_mod._db_url_cache
            conn_mod._db_url_cache = cls.db_url

            cls._seed()
        except ImportError:
            raise unittest.SkipTest("pgserver not available") from None

    @classmethod
    def _seed(cls):
        from src.database.models.core import Record, Source
        from src.database.models.identity import User
        from src.database.models.search import (
            GlossSearchEntry,
            HeadwordSearchEntry,
            SearchEntry,
        )

        with cls.Session() as session:
            session.add(
                User(
                    email="test@example.com",
                    username="testuser",
                    github_id=1,
                    full_name="Test User",
                )
            )
            source = Source(name="Natick/Trumbull", short_name="N/T")
            session.add(source)
            session.flush()

            def rec(lx, mdf, **kw):
                return Record(
                    lx=lx,
                    source_id=source.id,
                    mdf_data=mdf,
                    status="draft",
                    **kw,
                )

            cls.record_a = rec(
                "k∞",
                "\\lx k∞\n\\ps n\n\\ge house\n",
            )
            cls.record_b = rec(
                "kanadi",
                "\\lx kanadi\n\\ge bucket\n\\nt ∞ defect in notes\n",
            )
            cls.record_c = rec(
                "muhkun",
                "\\lx muhkun\n\\ge axe\n",
            )
            cls.record_d = rec(
                "pa∞",
                "\\lx pa∞\n\\ge basket\n",
                is_deleted=True,
            )
            cls.record_e = rec(
                "s∞k",
                "\\lx s∞k\n\\ge plum\n",
                is_locked=True,
                locked_by="test@example.com",
            )
            session.add_all(
                [cls.record_a, cls.record_b, cls.record_c, cls.record_d, cls.record_e]
            )
            session.flush()

            # Seed search entries containing the ∞ defect so post-run
            # assertions on term remediation are meaningful.
            session.add_all(
                [
                    SearchEntry(
                        record_id=cls.record_a.id,
                        term="k∞",
                        normalized_term="k∞",
                        entry_type="lx",
                    ),
                    SearchEntry(
                        record_id=cls.record_a.id,
                        term="k∞ synonym",
                        normalized_term="k∞ synonym",
                        entry_type="se",
                    ),
                    HeadwordSearchEntry(
                        record_id=cls.record_a.id,
                        entry_type="lx",
                        term="k∞",
                        normalized_term="k∞",
                    ),
                    GlossSearchEntry(
                        record_id=cls.record_a.id,
                        entry_type="ge",
                        term="house ∞ note",
                        normalized_term="house ∞ note",
                    ),
                    SearchEntry(
                        record_id=cls.record_b.id,
                        term="kanadi ∞",
                        normalized_term="kanadi ∞",
                        entry_type="nt",
                    ),
                    HeadwordSearchEntry(
                        record_id=cls.record_b.id,
                        entry_type="lx",
                        term="kanadi",
                        normalized_term="kanadi",
                    ),
                ]
            )
            session.commit()
            cls.ids = {
                "A": cls.record_a.id,
                "B": cls.record_b.id,
                "C": cls.record_c.id,
                "D": cls.record_d.id,
                "E": cls.record_e.id,
            }

    @classmethod
    def tearDownClass(cls):
        import src.database.connection as conn_mod

        conn_mod._db_url_cache = cls._orig_db_url_cache
        # Drop the engine cached by st.cache_resource on get_engine() — it is
        # bound to this fixture's pgserver socket, which is about to be
        # removed; leaving it cached breaks any later test in the same
        # pytest session that resolves a database engine.
        import streamlit as st

        st.cache_resource.clear()
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if hasattr(cls, "test_db_path") and cls.test_db_path.exists():
            import shutil

            shutil.rmtree(cls.test_db_path)

    @classmethod
    def _snapshot(cls, record_id):
        from src.database.models.core import Record
        from src.database.models.search import (
            GlossSearchEntry,
            HeadwordSearchEntry,
            SearchEntry,
        )
        from src.database.models.workflow import EditHistory

        with cls.Session() as session:
            record = session.get(Record, record_id)
            terms = {
                "search": [
                    t
                    for t, in session.query(SearchEntry.term)
                    .filter(SearchEntry.record_id == record_id)
                    .all()
                ],
                "headword": [
                    t
                    for t, in session.query(HeadwordSearchEntry.term)
                    .filter(HeadwordSearchEntry.record_id == record_id)
                    .all()
                ],
                "gloss": [
                    t
                    for t, in session.query(GlossSearchEntry.term)
                    .filter(GlossSearchEntry.record_id == record_id)
                    .all()
                ],
            }
            edit_count = (
                session.query(EditHistory)
                .filter(EditHistory.record_id == record_id)
                .count()
            )
            return {
                "lx": record.lx,
                "mdf_data": record.mdf_data,
                "sort_lx": record.sort_lx,
                "current_version": record.current_version,
                "terms": terms,
                "edit_history_count": edit_count,
            }

    def test_sc5_sc11_sc12_sc13_remediate_all_records(self):
        from src.services.linguistic_service import LinguisticService

        pre = {rid: self._snapshot(rid) for rid in self.ids.values()}

        outcome = LinguisticService.remediate_all_records(
            progress_callback=None, session=None
        )

        # SC-12: outcome report shape.
        self.assertEqual(
            outcome, {"remediated": 2, "locked": 1}, f"outcome was {outcome!r}"
        )

        # SC-13: locked presence did not block remediation of A and B.
        post_a = self._snapshot(self.ids["A"])
        post_b = self._snapshot(self.ids["B"])
        for label, post in (("A", post_a), ("B", post_b)):
            self.assertIn(self.OO_LIGATURE, post["mdf_data"], f"record {label} mdf_data")
            self.assertNotIn(
                self.INFINITY, post["mdf_data"], f"record {label} mdf_data"
            )
            for table_terms in post["terms"].values():
                for term in table_terms:
                    self.assertNotIn(
                        self.INFINITY,
                        term,
                        f"record {label} search term {term!r}",
                    )
            a_lx_expected = LinguisticService.generate_sort_lx(post["lx"])
            self.assertEqual(
                post["sort_lx"], a_lx_expected, f"record {label} sort_lx recomputed"
            )
            self.assertEqual(
                post["current_version"],
                pre[self.ids[label]]["current_version"],
                f"record {label} current_version unchanged",
            )
            self.assertEqual(
                post["edit_history_count"],
                0,
                f"record {label} must have zero edit_history rows",
            )

        # Column-scoped replacement: A.lx contained ∞ → remediated to ꝏ;
        # B.lx had no ∞ → unchanged ("kanadi").
        self.assertIn(self.OO_LIGATURE, post_a["lx"], "record A lx remediated to ꝏ")
        self.assertNotIn(self.INFINITY, post_a["lx"], "record A lx")
        self.assertEqual(post_b["lx"], "kanadi", "record B lx unchanged")
        self.assertNotIn(self.OO_LIGATURE, post_b["lx"], "record B lx has no ꝏ")
        self.assertNotIn(self.INFINITY, post_b["lx"], "record B lx")

        # A's remediated lx entry terms carry the ꝏ ligature.
        self.assertTrue(
            any(self.OO_LIGATURE in t for t in post_a["terms"]["search"]),
            "A's search entry terms must contain ꝏ",
        )

        # SC-11: locked record E untouched.
        post_e = self._snapshot(self.ids["E"])
        pre_e = pre[self.ids["E"]]
        for field in ("lx", "mdf_data", "sort_lx", "current_version"):
            self.assertEqual(
                post_e[field], pre_e[field], f"locked record E {field} unchanged"
            )
        self.assertIn(self.INFINITY, post_e["lx"], "locked E lx still contains ∞")
        self.assertEqual(
            post_e["edit_history_count"], 0, "locked E must have zero edit_history rows"
        )


class TestNormalizedIdentitySC6(unittest.TestCase):
    """SC-6 (issue #1382): normalized identity across remediation.

    Five-record fixture (A ∞ in lx+mdf_data, B ∞ in mdf_data only, C clean,
    D soft-deleted, E locked). Pre-remediation search-entry state is built via
    the real ingestion path (UploadService.populate_search_entries) so the
    captured normalized values reflect a genuine ingested DB state.

    Property/pin assertion: sort_lx for A and B and every normalized_term
    value across search_entries / headword_search_entries / gloss_search_entries
    for A and B must be byte-identical pre/post remediation. Both ligature
    encodings (∞ U+221E and ꝏ U+A74F) map to the same normalized form, so a
    defect-free remediation preserves every normalized value byte-for-byte.
    """

    @classmethod
    def setUpClass(cls):
        try:
            import pgserver
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker

            import src.database.models.core  # noqa: F401  populate mapper registry
            import src.database.models.identity  # noqa: F401
            import src.database.models.iso639  # noqa: F401
            import src.database.models.meta  # noqa: F401
            import src.database.models.search  # noqa: F401
            import src.database.models.workflow  # noqa: F401
            from src.database.base import Base

            cls.test_db_path = Path("tmp/test_normalized_identity_sc6_db")
            if cls.test_db_path.exists():
                import shutil

                shutil.rmtree(cls.test_db_path)
            cls.test_db_path.mkdir(parents=True, exist_ok=True)

            cls.pg_server = pgserver.get_server(str(cls.test_db_path))  # pyright: ignore[reportPrivateImportUsage]
            cls.db_url = cls.pg_server.get_uri()
            cls.engine = create_engine(cls.db_url)
            with cls.engine.begin() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            Base.metadata.create_all(cls.engine)
            cls.Session = sessionmaker(bind=cls.engine)

            # Route LinguisticService's get_session() to the fixture DB.
            import src.database.connection as conn_mod

            cls._orig_db_url_cache = conn_mod._db_url_cache
            conn_mod._db_url_cache = cls.db_url

            cls._seed()
        except ImportError:
            raise unittest.SkipTest("pgserver not available") from None

    @classmethod
    def _seed(cls):
        from src.database.models.core import Record, Source
        from src.database.models.identity import User
        from src.services.linguistic_service import LinguisticService
        from src.services.upload_service import UploadService

        with cls.Session() as session:
            session.add(
                User(
                    email="test@example.com",
                    username="testuser",
                    github_id=1,
                    full_name="Test User",
                )
            )
            source = Source(name="Natick/Trumbull", short_name="N/T")
            session.add(source)
            session.flush()

            def rec(lx, mdf, **kw):
                return Record(
                    lx=lx,
                    sort_lx=LinguisticService.generate_sort_lx(lx),
                    source_id=source.id,
                    mdf_data=mdf,
                    status="draft",
                    **kw,
                )

            cls.record_a = rec(
                "k∞",
                "\\lx k∞\n\\ps n\n\\ge house\n",
            )
            cls.record_b = rec(
                "kanadi",
                "\\lx kanadi\n\\ge bucket\n\\nt ∞ defect in notes\n",
            )
            cls.record_c = rec(
                "muhkun",
                "\\lx muhkun\n\\ge axe\n",
            )
            cls.record_d = rec(
                "pa∞",
                "\\lx pa∞\n\\ge basket\n",
                is_deleted=True,
            )
            cls.record_e = rec(
                "s∞k",
                "\\lx s∞k\n\\ge plum\n",
                is_locked=True,
                locked_by="test@example.com",
            )
            session.add_all(
                [cls.record_a, cls.record_b, cls.record_c, cls.record_d, cls.record_e]
            )
            session.commit()
            cls.ids = {
                "A": cls.record_a.id,
                "B": cls.record_b.id,
                "C": cls.record_c.id,
                "D": cls.record_d.id,
                "E": cls.record_e.id,
            }

            # Build the genuine pre-remediation ingested state for A and B
            # via the real ingestion path (rebuilt later by remediation).
            UploadService.populate_search_entries(
                [cls.ids["A"], cls.ids["B"]], session=session
            )
            session.commit()

    @classmethod
    def tearDownClass(cls):
        import src.database.connection as conn_mod

        conn_mod._db_url_cache = cls._orig_db_url_cache
        # Drop the engine cached by st.cache_resource on get_engine() — it is
        # bound to this fixture's pgserver socket, which is about to be
        # removed; leaving it cached breaks any later test in the same
        # pytest session that resolves a database engine.
        import streamlit as st

        st.cache_resource.clear()
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if hasattr(cls, "test_db_path") and cls.test_db_path.exists():
            import shutil

            shutil.rmtree(cls.test_db_path)

    @classmethod
    def _capture(cls, record_id):
        from src.database.models.core import Record
        from src.database.models.search import (
            GlossSearchEntry,
            HeadwordSearchEntry,
            SearchEntry,
        )

        with cls.Session() as session:
            record = session.get(Record, record_id)
            normalized = {
                "search": sorted(
                    t
                    for t, in session.query(SearchEntry.normalized_term)
                    .filter(SearchEntry.record_id == record_id)
                    .all()
                ),
                "headword": sorted(
                    t
                    for t, in session.query(HeadwordSearchEntry.normalized_term)
                    .filter(HeadwordSearchEntry.record_id == record_id)
                    .all()
                ),
                "gloss": sorted(
                    t
                    for t, in session.query(GlossSearchEntry.normalized_term)
                    .filter(GlossSearchEntry.record_id == record_id)
                    .all()
                ),
            }
            return {"sort_lx": record.sort_lx, "normalized": normalized}

    def test_sc6_normalized_identity_across_remediation(self):
        from src.services.linguistic_service import LinguisticService

        pre = {label: self._capture(rid) for label, rid in self.ids.items() if label in ("A", "B")}

        outcome = LinguisticService.remediate_all_records(
            progress_callback=None, session=None
        )
        self.assertEqual(
            outcome, {"remediated": 2, "locked": 1}, f"outcome was {outcome!r}"
        )

        post = {label: self._capture(rid) for label, rid in self.ids.items() if label in ("A", "B")}

        for label in ("A", "B"):
            self.assertEqual(
                post[label]["sort_lx"],
                pre[label]["sort_lx"],
                f"record {label} sort_lx must be byte-identical across remediation",
            )
            for table in ("search", "headword", "gloss"):
                self.assertEqual(
                    post[label]["normalized"][table],
                    pre[label]["normalized"][table],
                    f"record {label} {table} normalized_term values must be "
                    "byte-identical across remediation",
                )
            # Guard against vacuous comparison: A must actually have
            # normalized values in the lexeme tables to compare.
            if label == "A":
                self.assertTrue(pre[label]["normalized"]["search"])
                self.assertTrue(pre[label]["normalized"]["headword"])


class TestFTSEquivalenceSC7(unittest.TestCase):
    """SC-7 (issue #1382): FTS equivalence across ∞ → ꝏ remediation.

    Five-record fixture (A ∞ in lx+mdf_data, B ∞ in mdf_data only, C clean,
    D soft-deleted, E locked). Search entries (including fts_entries) are
    built via the real ingestion path (UploadService.populate_search_entries).

    Property/pin assertion: the result set of
        fts_entries WHERE fts_vector @@ plainto_tsquery('simple',
        generate_sort_lx("k∞"))
    pre-remediation must be byte-identical to the result set of the same
    query post-remediation with generate_sort_lx("kꝏ"). Both characters
    normalize to "oozzz", so a defect-free implementation passes this
    immediately — if it lands GREEN on first run, that is the expected
    property-pin outcome and is reported as such (never weakened to force RED).
    """

    INFINITY = "∞"  # direct Unicode literal U+221E
    OO_LIGATURE = "ꝏ"  # direct Unicode literal U+A74F

    @classmethod
    def setUpClass(cls):
        try:
            import pgserver
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker

            import src.database.models.core  # noqa: F401  populate mapper registry
            import src.database.models.identity  # noqa: F401
            import src.database.models.iso639  # noqa: F401
            import src.database.models.meta  # noqa: F401
            import src.database.models.search  # noqa: F401
            import src.database.models.workflow  # noqa: F401
            from src.database.base import Base

            cls.test_db_path = Path("tmp/test_fts_equivalence_sc7_db")
            if cls.test_db_path.exists():
                import shutil

                shutil.rmtree(cls.test_db_path)
            cls.test_db_path.mkdir(parents=True, exist_ok=True)

            cls.pg_server = pgserver.get_server(str(cls.test_db_path))  # pyright: ignore[reportPrivateImportUsage]
            cls.db_url = cls.pg_server.get_uri()
            cls.engine = create_engine(cls.db_url)
            with cls.engine.begin() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            Base.metadata.create_all(cls.engine)
            cls.Session = sessionmaker(bind=cls.engine)

            # Route LinguisticService's get_session() to the fixture DB.
            import src.database.connection as conn_mod

            cls._orig_db_url_cache = conn_mod._db_url_cache
            conn_mod._db_url_cache = cls.db_url

            cls._seed()
        except ImportError:
            raise unittest.SkipTest("pgserver not available") from None

    @classmethod
    def _seed(cls):
        from src.database.models.core import Record, Source
        from src.database.models.identity import User
        from src.services.linguistic_service import LinguisticService
        from src.services.upload_service import UploadService

        with cls.Session() as session:
            session.add(
                User(
                    email="test@example.com",
                    username="testuser",
                    github_id=1,
                    full_name="Test User",
                )
            )
            source = Source(name="Natick/Trumbull", short_name="N/T")
            session.add(source)
            session.flush()

            def rec(lx, mdf, **kw):
                return Record(
                    lx=lx,
                    sort_lx=LinguisticService.generate_sort_lx(lx),
                    source_id=source.id,
                    mdf_data=mdf,
                    status="draft",
                    **kw,
                )

            cls.record_a = rec(
                "k∞",
                "\\lx k∞\n\\ps n\n\\ge house\n",
            )
            cls.record_b = rec(
                "kanadi",
                "\\lx kanadi\n\\ge bucket\n\\nt ∞ defect in notes\n",
            )
            cls.record_c = rec(
                "muhkun",
                "\\lx muhkun\n\\ge axe\n",
            )
            cls.record_d = rec(
                "pa∞",
                "\\lx pa∞\n\\ge basket\n",
                is_deleted=True,
            )
            cls.record_e = rec(
                "s∞k",
                "\\lx s∞k\n\\ge plum\n",
                is_locked=True,
                locked_by="test@example.com",
            )
            session.add_all(
                [cls.record_a, cls.record_b, cls.record_c, cls.record_d, cls.record_e]
            )
            session.commit()
            cls.ids = {
                "A": cls.record_a.id,
                "B": cls.record_b.id,
                "C": cls.record_c.id,
                "D": cls.record_d.id,
                "E": cls.record_e.id,
            }

        # Build the genuine ingested search/FTS state via the real path.
        UploadService.populate_search_entries(list(cls.ids.values()))
        from src.database.connection import get_session

        get_session().commit()

    @classmethod
    def tearDownClass(cls):
        import src.database.connection as conn_mod

        conn_mod._db_url_cache = cls._orig_db_url_cache
        # Drop the engine cached by st.cache_resource on get_engine() — it is
        # bound to this fixture's pgserver socket, which is about to be
        # removed; leaving it cached breaks any later test in the same
        # pytest session that resolves a database engine.
        import streamlit as st

        st.cache_resource.clear()
        if hasattr(cls, "pg_server"):
            cls.pg_server.cleanup()
        if hasattr(cls, "test_db_path") and cls.test_db_path.exists():
            import shutil

            shutil.rmtree(cls.test_db_path)

    @staticmethod
    def _fts_query(session, query_text: str) -> list[int]:
        """Return record_ids whose fts_vector matches the plainto_tsquery."""
        from sqlalchemy import text

        rows = session.execute(
            text(
                "SELECT record_id FROM fts_entries "
                "WHERE fts_vector @@ plainto_tsquery('simple', :q) "
                "ORDER BY record_id"
            ),
            {"q": query_text},
        ).fetchall()
        return [r[0] for r in rows]

    def test_sc7_fts_result_set_identical_across_remediation(self):
        from src.database.models.search import FTSEntry
        from src.services.linguistic_service import LinguisticService

        # Guard: the fixture actually has FTS rows to query.
        with self.Session() as session:
            fts_count = session.query(FTSEntry).count()
        self.assertGreater(fts_count, 0, "fixture must contain fts_entries rows")

        pre_query = LinguisticService.generate_sort_lx("k∞")
        with self.Session() as session:
            pre_ids = self._fts_query(session, pre_query)

        # Non-vacuous guard: the pre-remediation ∞ query must match record A.
        self.assertIn(
            self.ids["A"], pre_ids, "pre-remediation k∞ query must match record A"
        )

        outcome = LinguisticService.remediate_all_records(
            progress_callback=None, session=None
        )
        self.assertEqual(
            outcome, {"remediated": 2, "locked": 1}, f"outcome was {outcome!r}"
        )

        post_query = LinguisticService.generate_sort_lx("kꝏ")
        with self.Session() as session:
            post_ids = self._fts_query(session, post_query)

        self.assertEqual(
            post_ids,
            pre_ids,
            "FTS result set for kꝏ post-remediation must be identical to "
            "the k∞ result set pre-remediation",
        )


if __name__ == "__main__":
    unittest.main()
