# SPDX-FileCopyrightText: 2026 michael-conrad
# SPDX-License-Identifier: MIT
# Provenance: AI-generated
"""Semantic search seam over the pinned gte-small embeddings (SC-5, Issue #36).

`search_semantic()` ranks cosine similarity between a query vector and the
pinned embedding rows in `gloss_search_entries` (mode="gloss") or the union
of `gloss_search_entries` and `semantic_search_entries` (mode="all"). Only
rows whose `embedding_model` equals the pinned model name participate; NULL
or stale-model rows are excluded by the join. Results are returned as a
full ranked list ordered by score descending with record_id-ascending
tie-break; an explicit threshold filters rows below the cutoff while
threshold=None filters on the calibrated default floor CALIBRATED_FLOOR.

Degraded legs observable at the seam: empty_query (empty/whitespace query,
guarded before any model load), no_embeddings (zero embedded rows — remedies
via the admin backfill), stale_model (rows exist exclusively under a
non-pinned embedding_model), and ok-with-empty (all scores below the
threshold). Streamlit-import-free by design.

Co-authored with AI: OpenCode (ollama-cloud/glm-5.3-flash)
"""

from dataclasses import dataclass
from threading import Lock

from sqlalchemy import create_engine, text

from src.database.connection import get_db_url
from src.services import embedding_service

# Canonical pin lives in embedding_service; re-exported for callers.
PIN = embedding_service.PIN

# Calibrated similarity floor for the gloss-space semantic seam (Issue
# #1400, SC-1). Measured from real corpus queries against the production
# replica (6,681 embedded glosses, pin thenlper/gte-small, probe date
# 2026-10-02); evidence and full provenance:
# src/services/calibration/gloss_space_calibration.yaml
# (probe artifact: tmp/1400/artifacts/verification-probe.yaml).
# The value lies strictly within the measured interval (0.9018, 0.9753):
# above the out-of-corpus battery max ("light bulb", 0.9018) and below the
# smallest floor-clearing in-corpus anchor ("beaver", 0.9753).
CALIBRATED_FLOOR = 0.93

# Issue #1400 SC-5: pinned deficiency message for the all-below-floor /
# empty-results outcome (named constant — no magic string duplication).
BELOW_FLOOR_MESSAGE = "No gloss results meet the sensitivity floor."

status_values_or_enum = lambda: [  # noqa: E731
    "ok",
    "empty_query",
    "no_embeddings",
    "stale_model",
]


@dataclass
class SemanticSearchResult:
    """Result of a semantic search: ranked (record_id, score) pairs."""

    results: list
    status: str
    message: str


_query_encoder = None
_QUERY_ENCODER_LOCK = Lock()

_ENGINE = None
_ENGINE_LOCK = Lock()


def set_query_encoder(encoder):
    """Override the query encoder for deterministic tests (None restores)."""
    global _query_encoder
    with _QUERY_ENCODER_LOCK:
        _query_encoder = encoder


def _encode_query(query):
    with _QUERY_ENCODER_LOCK:
        encoder = _query_encoder
    if encoder is not None:
        vectors = encoder.encode([query])
    else:
        vectors = embedding_service.encode([query])
    return vectors[0]


def _get_engine():
    global _ENGINE
    with _ENGINE_LOCK:
        if _ENGINE is None:
            _ENGINE = create_engine(get_db_url())
        return _ENGINE


def _candidate_sql(mode, has_threshold, has_source, has_limit):
    tables = ["gloss_search_entries"]
    if mode == "all":
        tables.append("semantic_search_entries")
    where = "embedding_model = :pin AND embedding IS NOT NULL"
    if has_threshold:
        where += " AND (1 - (embedding <=> CAST(:qv AS vector))) >= :thr"
    if has_source:
        where += " AND record_id = :source_id"
    selects = [
        "SELECT record_id, 1 - (embedding <=> CAST(:qv AS vector)) AS score "
        f"FROM {table} WHERE {where}"
        for table in tables
    ]
    if len(selects) == 1:
        inner = f"({selects[0]})"
        thr = ""
    else:
        inner = "(" + " UNION ALL ".join(selects) + ") AS ranked"
        thr = ""
    lim = " LIMIT :lim" if has_limit else ""
    return f"SELECT record_id, score FROM {inner}{thr} ORDER BY score DESC, record_id ASC{lim}"


def search_semantic(mode="gloss", query="", threshold=None, source_id=None, limit=None):
    """Rank pinned embeddings by cosine similarity to the encoded query.

    Returns a SemanticSearchResult with `results` as a list of
    (record_id, score) pairs sorted by score descending, record_id ascending.
    """
    if not isinstance(query, str) or not query.strip():
        return SemanticSearchResult(
            results=[], status="empty_query", message="Query must be non-empty text."
        )

    try:
        query_vector = _encode_query(query.strip())
    except embedding_service.MissingModelAssetError:
        return SemanticSearchResult(
            results=[],
            status="no_embeddings",
            message="Embedding model assets are missing; cannot encode the query.",
        )

    qv = "[" + ",".join(repr(float(v)) for v in query_vector) + "]"
    params = {"qv": qv, "pin": PIN}
    # Issue #1400 SC-2: threshold=None engages the calibrated default floor
    # (named constant — no magic number in the query path).
    effective_threshold = CALIBRATED_FLOOR if threshold is None else threshold
    if effective_threshold is not None:
        params["thr"] = str(float(effective_threshold))
    if source_id is not None:
        params["source_id"] = source_id
    if limit is not None:
        params["lim"] = int(limit)
    sql = text(
        _candidate_sql(
            mode,
            has_threshold=effective_threshold is not None,
            has_source=source_id is not None,
            has_limit=limit is not None,
        )
    )

    engine = _get_engine()
    with engine.connect() as conn:
        rows = conn.execute(sql, params).all()

    results = []
    for record_id, score in rows:
        value = float(score)
        value = max(-1.0, min(1.0, value))
        results.append((int(record_id), value))

    if not results:
        with engine.connect() as conn:
            diagnostics = conn.execute(
                text(
                    "SELECT "
                    "EXISTS (SELECT 1 FROM gloss_search_entries "
                    "WHERE embedding_model = :pin AND embedding IS NOT NULL) "
                    "OR EXISTS (SELECT 1 FROM semantic_search_entries "
                    "WHERE embedding_model = :pin AND embedding IS NOT NULL) "
                    "AS pinned, "
                    "EXISTS (SELECT 1 FROM gloss_search_entries "
                    "WHERE embedding IS NOT NULL) "
                    "OR EXISTS (SELECT 1 FROM semantic_search_entries "
                    "WHERE embedding IS NOT NULL) "
                    "AS embedded"
                ),
                {"pin": PIN},
            ).one()
        if diagnostics.pinned:
            return SemanticSearchResult(
                results=[], status="ok", message=BELOW_FLOOR_MESSAGE
            )
        if diagnostics.embedded:
            return SemanticSearchResult(
                results=[],
                status="stale_model",
                message=(
                    "Embedding rows exist only under a stale model; "
                    "run the admin backfill to re-embed with "
                    f"{PIN}."
                ),
            )
        return SemanticSearchResult(
            results=[],
            status="no_embeddings",
            message=(
                "No embedded rows exist for semantic search; "
                "run the admin backfill to embed entries with "
                f"{PIN}."
            ),
        )

    return SemanticSearchResult(
        results=results, status="ok", message=f"{len(results)} match(es) ranked by cosine similarity."
    )


def backfill_embeddings(progress_callback=None, batch_size=1, session=None):
    """Re-embed stale search entries with the currently pinned model.

    Rows in gloss_search_entries whose embedding is NULL or whose
    embedding_model is stale (differs from the current PIN), and rows in
    semantic_search_entries whose embedding_model is stale, are re-embedded
    from their stored term in batches of ``batch_size`` (capped at 512).
    After a pin change, calling this re-embeds every stale row so
    search_semantic status "stale_model" / "no_embeddings" is remedied.

    Args:
        progress_callback: Optional callable(current, total) invoked as
            entries are re-embedded.
        batch_size: Batch cap for encode calls (max 512; default 1 so
            each row is embedded sequentially and RAM never balloons).
        session: Unused (kept for call-compatibility); raw SQL via engine.

    Returns:
        dict with "total" (stale rows found) and "backfilled" (rows updated).
    """
    batch_size = max(1, min(int(batch_size), 512))
    engine = _get_engine()
    stale_sql = {
        "gloss_search_entries": text(
            "SELECT id, term FROM gloss_search_entries "
            "WHERE embedding IS NULL OR embedding_model IS NULL "
            "OR embedding_model <> :pin ORDER BY id"
        ),
        "semantic_search_entries": text(
            "SELECT id, term FROM semantic_search_entries "
            "WHERE embedding_model IS NULL OR embedding_model <> :pin ORDER BY id"
        ),
    }
    update_sql = (
        "UPDATE {table} SET embedding = CAST(:vec AS vector), embedding_model = :pin "
        "WHERE id = :rid"
    )

    with engine.connect() as conn:
        stale_ids = {
            table: [(row.id, row.term) for row in conn.execute(sql, {"pin": PIN})]
            for table, sql in stale_sql.items()
        }
    total = sum(len(rows) for rows in stale_ids.values())

    backfilled = 0
    for table, rows in stale_ids.items():
        for start in range(0, len(rows), batch_size):
            batch = rows[start : start + batch_size]
            vectors = embedding_service.encode([term for _, term in batch])
            with engine.begin() as conn:
                for (rid, _term), vec in zip(batch, vectors, strict=True):
                    vec_literal = "[" + ",".join(repr(float(v)) for v in vec) + "]"
                    conn.execute(
                        text(update_sql.format(table=table)),
                        {"vec": vec_literal, "pin": PIN, "rid": rid},
                    )
            backfilled += len(batch)
            if progress_callback:
                progress_callback(backfilled, total)

    return {"total": total, "backfilled": backfilled}
