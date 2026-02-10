# Copyright (c) 2026 Brothertown Language
"""
Upload Service for MDF file upload, staging, matching, and commit operations.
"""
import unicodedata
import uuid
from typing import Optional

from src.database import get_session, MatchupQueue, Record, EditHistory, SearchEntry, Source
from src.mdf.parser import parse_mdf, normalize_nt_record, format_mdf_record
from src.logging_config import get_logger

logger = get_logger("snea.upload")


def _strip_diacritics(text: str) -> str:
    """Strip Unicode diacritics (combining marks) from text for base-form comparison."""
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(ch for ch in nfd if unicodedata.category(ch) != 'Mn')


class UploadService:
    """
    Service for MDF file upload workflow: parse, stage, match, review, and commit.
    All matchup_queue operations are scoped by batch_id.
    """

    @staticmethod
    def parse_upload(file_content: str) -> list[dict]:
        """Parse MDF file content and return list of parsed entries.

        Raises ValueError if the file is empty or contains no valid entries.
        """
        if not file_content or not file_content.strip():
            raise ValueError("File is empty")
        entries = parse_mdf(file_content)
        if not entries:
            raise ValueError("No valid MDF entries found in file")
        return entries

    @staticmethod
    def assign_homonym_numbers(entries: list[dict]) -> list[dict]:
        """Detect intra-batch homonyms and assign \\hm numbers.

        Groups entries by diacritics-stripped lx base form. For groups with
        multiple entries, assigns sequential \\hm values (preserving any
        existing \\hm tags). Updates both the parsed dict and raw mdf_data.
        """
        from collections import defaultdict

        # Group entries by diacritics-stripped base form
        groups = defaultdict(list)
        for entry in entries:
            base = _strip_diacritics(entry['lx'])
            groups[base].append(entry)

        for base, group in groups.items():
            if len(group) < 2:
                continue

            # Find already-assigned hm values (hm defaults to 1 in parser,
            # but we only treat it as "explicitly set" if \hm appears in mdf_data)
            used = set()
            has_explicit_hm = []
            for entry in group:
                lines = entry['mdf_data'].split('\n')
                explicit = False
                for line in lines:
                    stripped = line.lstrip()
                    if stripped.startswith('\\hm '):
                        val = stripped[len('\\hm '):].strip()
                        if val.isdigit():
                            used.add(int(val))
                            explicit = True
                            break
                has_explicit_hm.append(explicit)

            # Assign sequential hm to entries without explicit \hm
            next_hm = 1
            for i, entry in enumerate(group):
                if has_explicit_hm[i]:
                    continue
                while next_hm in used:
                    next_hm += 1
                used.add(next_hm)
                entry['hm'] = next_hm

                # Insert \hm line after \lx in mdf_data
                lines = entry['mdf_data'].split('\n')
                new_lines = []
                inserted = False
                for line in lines:
                    new_lines.append(line)
                    if not inserted and line.lstrip().startswith('\\lx '):
                        new_lines.append(f'\\hm {next_hm}')
                        inserted = True
                entry['mdf_data'] = '\n'.join(new_lines)
                next_hm += 1

        return entries

    @staticmethod
    def stage_entries(user_email: str, source_id: int, entries: list[dict],
                      filename: Optional[str] = None) -> str:
        """Stage parsed entries into matchup_queue with a new batch_id.

        Returns the generated batch_id (UUID string).
        """
        batch_id = str(uuid.uuid4())
        session = get_session()
        try:
            for entry in entries:
                row = MatchupQueue(
                    user_email=user_email,
                    source_id=source_id,
                    batch_id=batch_id,
                    filename=filename,
                    status='pending',
                    lx=entry.get('lx', ''),
                    mdf_data=format_mdf_record(entry['mdf_data']),
                )
                session.add(row)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
        return batch_id

    @staticmethod
    def list_pending_batches(user_email: str) -> list[dict]:
        """Return all distinct pending upload batches for this user.

        Each dict: {batch_id, source_id, source_name, filename, entry_count, uploaded_at}.
        Ordered by uploaded_at descending.
        """
        from sqlalchemy import func as sa_func
        session = get_session()
        try:
            rows = (
                session.query(
                    MatchupQueue.batch_id,
                    MatchupQueue.source_id,
                    Source.name.label('source_name'),
                    MatchupQueue.filename,
                    sa_func.count(MatchupQueue.id).label('entry_count'),
                    sa_func.min(MatchupQueue.created_at).label('uploaded_at'),
                )
                .join(Source, Source.id == MatchupQueue.source_id)
                .filter(MatchupQueue.user_email == user_email)
                .group_by(
                    MatchupQueue.batch_id,
                    MatchupQueue.source_id,
                    Source.name,
                    MatchupQueue.filename,
                )
                .order_by(sa_func.min(MatchupQueue.created_at).desc())
                .all()
            )
            return [
                {
                    'batch_id': r.batch_id,
                    'source_id': r.source_id,
                    'source_name': r.source_name,
                    'filename': r.filename,
                    'entry_count': r.entry_count,
                    'uploaded_at': r.uploaded_at,
                }
                for r in rows
            ]
        finally:
            session.close()

    @staticmethod
    def suggest_matches(batch_id: str) -> list[dict]:
        """Run match suggestions for all pending rows in a batch.

        Returns list of {queue_id, lx, suggested_record_id, suggested_lx,
        match_type, cross_source_matches, record_id_conflict,
        record_id_conflict_sources}.
        """
        session = get_session()
        try:
            rows = (
                session.query(MatchupQueue)
                .filter_by(batch_id=batch_id, status='pending')
                .all()
            )
            if not rows:
                return []

            source_id = rows[0].source_id

            # Load all records for the same source (for matching)
            same_source_records = (
                session.query(Record)
                .filter_by(source_id=source_id, is_deleted=False)
                .all()
            )

            # Build lookup structures for same-source records
            # exact lx -> list of records
            from collections import defaultdict
            exact_map = defaultdict(list)
            base_map = defaultdict(list)
            id_map = {}  # record.id -> record
            for rec in same_source_records:
                exact_map[rec.lx].append(rec)
                base_map[_strip_diacritics(rec.lx)].append(rec)
                id_map[rec.id] = rec

            # Load all records from OTHER sources for cross-source checks
            other_records = (
                session.query(Record)
                .filter(Record.source_id != source_id, Record.is_deleted == False)
                .all()
            )
            other_exact_map = defaultdict(list)
            other_base_map = defaultdict(list)
            other_id_map = defaultdict(list)  # record_id -> list of (record, source_name)
            # Cache source names
            source_names = {}
            for rec in other_records:
                if rec.source_id not in source_names:
                    src = session.get(Source, rec.source_id)
                    source_names[rec.source_id] = src.name if src else str(rec.source_id)
                sname = source_names[rec.source_id]
                other_exact_map[rec.lx].append(sname)
                other_base_map[_strip_diacritics(rec.lx)].append(sname)
                other_id_map[rec.id].append(sname)

            results = []
            for row in rows:
                suggested_record_id = None
                suggested_lx = None
                match_type = None

                # Parse record_id from uploaded entry
                uploaded_record_id = None
                for line in row.mdf_data.split('\n'):
                    stripped = line.lstrip()
                    if stripped.startswith('\\nt Record:'):
                        val = stripped[len('\\nt Record:'):].strip()
                        if val.isdigit():
                            uploaded_record_id = int(val)

                # 1. Try record_id match first (if uploaded entry has \nt Record:)
                if uploaded_record_id and uploaded_record_id in id_map:
                    rec = id_map[uploaded_record_id]
                    suggested_record_id = rec.id
                    suggested_lx = rec.lx
                    match_type = 'exact'

                # 2. Exact lx match
                if not suggested_record_id and row.lx in exact_map:
                    candidates = exact_map[row.lx]
                    # Prefer hm match if available
                    parsed_hm = None
                    for line in row.mdf_data.split('\n'):
                        s = line.lstrip()
                        if s.startswith('\\hm '):
                            v = s[len('\\hm '):].strip()
                            if v.isdigit():
                                parsed_hm = int(v)
                    best = None
                    for c in candidates:
                        if parsed_hm is not None and c.hm == parsed_hm:
                            best = c
                            break
                    if best is None:
                        best = candidates[0]
                    suggested_record_id = best.id
                    suggested_lx = best.lx
                    match_type = 'exact'

                # 3. Diacritics-stripped fallback
                if not suggested_record_id:
                    base = _strip_diacritics(row.lx)
                    if base in base_map:
                        best = base_map[base][0]
                        suggested_record_id = best.id
                        suggested_lx = best.lx
                        match_type = 'base_form'

                # Cross-source indicator
                cross_sources = set()
                if row.lx in other_exact_map:
                    cross_sources.update(other_exact_map[row.lx])
                base_lx = _strip_diacritics(row.lx)
                if base_lx in other_base_map:
                    cross_sources.update(other_base_map[base_lx])
                cross_source_matches = sorted(cross_sources) if cross_sources else []

                # Record-id conflict check
                record_id_conflict = False
                record_id_conflict_sources = []
                if uploaded_record_id and uploaded_record_id in other_id_map:
                    record_id_conflict = True
                    record_id_conflict_sources = sorted(set(other_id_map[uploaded_record_id]))

                # Update the queue row
                row.suggested_record_id = suggested_record_id
                row.match_type = match_type

                results.append({
                    'queue_id': row.id,
                    'lx': row.lx,
                    'suggested_record_id': suggested_record_id,
                    'suggested_lx': suggested_lx,
                    'match_type': match_type,
                    'cross_source_matches': cross_source_matches,
                    'record_id_conflict': record_id_conflict,
                    'record_id_conflict_sources': record_id_conflict_sources,
                })

            session.commit()
            return results
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def _strip_nt_record_lines(mdf_text: str) -> str:
        """Remove all \\nt Record: lines from MDF text for comparison."""
        lines = mdf_text.split('\n')
        return '\n'.join(
            line for line in lines
            if not (line.lstrip().startswith('\\nt Record:')
                    and line.lstrip()[len('\\nt Record:'):].strip().isdigit())
        )

    @staticmethod
    def auto_remove_exact_duplicates(batch_id: str) -> dict:
        """Remove matchup_queue rows that are exact duplicates of existing records.

        Returns {removed_count: int, headwords: list[str]}.
        """
        session = get_session()
        try:
            rows = (
                session.query(MatchupQueue)
                .filter_by(batch_id=batch_id)
                .filter(MatchupQueue.suggested_record_id.isnot(None))
                .all()
            )

            removed = []
            for row in rows:
                record = session.get(Record, row.suggested_record_id)
                if not record:
                    continue
                uploaded_clean = UploadService._strip_nt_record_lines(row.mdf_data)
                existing_clean = UploadService._strip_nt_record_lines(record.mdf_data)
                if uploaded_clean == existing_clean:
                    removed.append(row.lx)
                    session.delete(row)

            session.commit()
            return {'removed_count': len(removed), 'headwords': removed}
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def _strip_nt_record_and_hm_lines(mdf_text: str) -> str:
        """Remove \\nt Record: and \\hm lines from MDF text for comparison."""
        lines = mdf_text.split('\n')
        result = []
        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith('\\nt Record:') and stripped[len('\\nt Record:'):].strip().isdigit():
                continue
            if stripped.startswith('\\hm ') and stripped[len('\\hm '):].strip().isdigit():
                continue
            result.append(line)
        return '\n'.join(result)

    @staticmethod
    def _extract_hm_from_mdf(mdf_text: str):
        """Extract \\hm value from MDF text, or None if absent."""
        for line in mdf_text.split('\n'):
            stripped = line.lstrip()
            if stripped.startswith('\\hm '):
                val = stripped[len('\\hm '):].strip()
                if val.isdigit():
                    return int(val)
        return None

    @staticmethod
    def flag_hm_mismatches(batch_id: str) -> list[dict]:
        """Flag entries identical to existing records except for \\hm number.

        Returns list of flagged entries with hm_mismatch details.
        """
        session = get_session()
        try:
            rows = (
                session.query(MatchupQueue)
                .filter_by(batch_id=batch_id)
                .filter(MatchupQueue.suggested_record_id.isnot(None))
                .all()
            )

            flagged = []
            for row in rows:
                record = session.get(Record, row.suggested_record_id)
                if not record:
                    continue
                uploaded_stripped = UploadService._strip_nt_record_and_hm_lines(row.mdf_data)
                existing_stripped = UploadService._strip_nt_record_and_hm_lines(record.mdf_data)
                if uploaded_stripped != existing_stripped:
                    continue
                # Content identical excluding \nt Record: and \hm — check if \hm differs
                uploaded_hm = UploadService._extract_hm_from_mdf(row.mdf_data)
                existing_hm = UploadService._extract_hm_from_mdf(record.mdf_data)
                if uploaded_hm != existing_hm:
                    detail = f"uploaded \\hm {uploaded_hm}, existing \\hm {existing_hm}"
                    flagged.append({
                        'queue_id': row.id,
                        'lx': row.lx,
                        'hm_mismatch': True,
                        'hm_mismatch_detail': detail,
                    })

            return flagged
        finally:
            session.close()

    @staticmethod
    def _levenshtein(s1: str, s2: str) -> int:
        """Compute Levenshtein edit distance between two strings."""
        if len(s1) < len(s2):
            return UploadService._levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
        prev_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                cost = 0 if c1 == c2 else 1
                curr_row.append(min(
                    curr_row[j] + 1,
                    prev_row[j + 1] + 1,
                    prev_row[j] + cost,
                ))
            prev_row = curr_row
        return prev_row[-1]

    @staticmethod
    def flag_headword_distance(batch_id: str, threshold: int = 3) -> list[dict]:
        """Flag record-number matches where headword edit distance exceeds threshold.

        Returns list of flagged entries with headword_distance details.
        """
        session = get_session()
        try:
            rows = (
                session.query(MatchupQueue)
                .filter_by(batch_id=batch_id)
                .filter(MatchupQueue.suggested_record_id.isnot(None))
                .all()
            )

            flagged = []
            for row in rows:
                # Only check entries matched via \nt Record: id
                uploaded_record_id = None
                for line in row.mdf_data.split('\n'):
                    stripped = line.lstrip()
                    if stripped.startswith('\\nt Record:'):
                        val = stripped[len('\\nt Record:'):].strip()
                        if val.isdigit():
                            uploaded_record_id = int(val)

                if uploaded_record_id is None or uploaded_record_id != row.suggested_record_id:
                    continue

                record = session.get(Record, row.suggested_record_id)
                if not record:
                    continue

                # Compare NFD-normalized forms (diacritics preserved)
                import unicodedata
                uploaded_nfd = unicodedata.normalize('NFD', row.lx)
                existing_nfd = unicodedata.normalize('NFD', record.lx)
                dist = UploadService._levenshtein(uploaded_nfd, existing_nfd)

                if dist > threshold:
                    detail = (
                        f"uploaded '{row.lx}', existing '{record.lx}' "
                        f"— edit distance {dist}"
                    )
                    flagged.append({
                        'queue_id': row.id,
                        'lx': row.lx,
                        'headword_distance': dist,
                        'headword_distance_detail': detail,
                    })

            return flagged
        finally:
            session.close()

    @staticmethod
    def rematch_batch(batch_id: str) -> list[dict]:
        """Re-run match suggestions for an existing batch.

        Clears and re-executes matching logic for all pending rows.
        Returns the same summary list as suggest_matches.
        """
        session = get_session()
        try:
            rows = (
                session.query(MatchupQueue)
                .filter_by(batch_id=batch_id)
                .filter(MatchupQueue.status != 'committed')
                .all()
            )
            for row in rows:
                row.status = 'pending'
                row.suggested_record_id = None
                row.match_type = None
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
        return UploadService.suggest_matches(batch_id)

    @staticmethod
    def search_records_for_override(source_id: int, query: str, limit: int = 20) -> list[dict]:
        """Search existing records by lx or ge for manual match override.

        Returns a list of dicts with id, lx, hm, and ge fields.
        """
        if not query or not query.strip():
            return []
        session = get_session()
        try:
            pattern = f"%{query.strip()}%"
            from sqlalchemy import or_
            rows = (
                session.query(Record)
                .filter_by(source_id=source_id, is_deleted=False)
                .filter(or_(
                    Record.lx.ilike(pattern),
                    Record.ge.ilike(pattern),
                ))
                .order_by(Record.lx, Record.hm)
                .limit(limit)
                .all()
            )
            return [
                {"id": r.id, "lx": r.lx, "hm": r.hm or 1, "ge": r.ge or ""}
                for r in rows
            ]
        finally:
            session.close()

    @staticmethod
    def confirm_match(queue_id: int, record_id: Optional[int] = None) -> None:
        """Mark a matchup_queue row as 'matched'.

        If record_id is provided, override the suggestion.
        """
        session = get_session()
        try:
            row = session.get(MatchupQueue, queue_id)
            if not row:
                raise ValueError(f"Queue entry {queue_id} not found")
            if record_id is not None:
                record = session.get(Record, record_id)
                if not record:
                    raise ValueError(f"Record {record_id} not found")
                row.suggested_record_id = record_id
            row.status = 'matched'
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def approve_all_new_source(batch_id: str, user_email: str,
                               language_id: int,
                               session_id: str,
                               progress_callback: Optional[callable] = None) -> int:
        """Bulk-approve and apply all pending rows as new records for new sources.

        Targets all rows in the batch that are 'pending'. Sets them to
        'create_new' and applies them via apply_single.

        Returns count of rows applied.
        """
        # First mark all pending as create_new
        session = get_session()
        try:
            session.query(MatchupQueue).filter_by(
                batch_id=batch_id,
                status='pending',
            ).update({'status': 'create_new'})
            session.commit()

            # Collect IDs to apply
            rows = (
                session.query(MatchupQueue)
                .filter_by(batch_id=batch_id, status='create_new')
                .all()
            )
            queue_ids = [r.id for r in rows]

            applied = 0
            total = len(queue_ids)
            for i, qid in enumerate(queue_ids, 1):
                UploadService.apply_single(
                    queue_id=qid,
                    user_email=user_email,
                    language_id=language_id,
                    session_id=session_id,
                    session=session
                )
                applied += 1
                
                if progress_callback:
                    progress_callback(i, total)

            session.commit()
            return applied
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def approve_all_by_record_match(batch_id: str, user_email: str,
                                     language_id: int,
                                     session_id: str,
                                     progress_callback: Optional[callable] = None) -> int:
        """Bulk-apply matched rows to the records table.

        Targets rows with a suggested_record_id and an exact or base_form
        match_type that are still 'pending' or already 'matched' (the UI
        selectbox may have defaulted them to 'matched' before the user
        clicks the bulk button).

        Each matched row is applied via apply_single (updates the existing
        record, writes edit_history, populates search entries, and removes
        the queue row).

        Returns count of rows applied.
        """
        # First ensure all qualifying rows have status='matched'
        session = get_session()
        try:
            session.query(MatchupQueue).filter_by(
                batch_id=batch_id,
            ).filter(
                MatchupQueue.status.in_(['pending', 'matched']),
                MatchupQueue.match_type.in_(['exact', 'base_form']),
                MatchupQueue.suggested_record_id.isnot(None),
            ).update({'status': 'matched'}, synchronize_session='fetch')
            session.commit()

            # Collect IDs of matched rows to apply
            matched_rows = (
                session.query(MatchupQueue)
                .filter_by(batch_id=batch_id, status='matched')
                .filter(MatchupQueue.suggested_record_id.isnot(None))
                .all()
            )
            queue_ids = [r.id for r in matched_rows]

            applied = 0
            total = len(queue_ids)
            for i, qid in enumerate(queue_ids, 1):
                UploadService.apply_single(
                    queue_id=qid,
                    user_email=user_email,
                    language_id=language_id,
                    session_id=session_id,
                    session=session
                )
                applied += 1
                
                if progress_callback:
                    progress_callback(i, total)

            session.commit()
            logger.info(
                "approve_all_by_record_match: batch=%s, applied %d of %d matched rows",
                batch_id, applied, len(queue_ids),
            )
            return applied
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def approve_non_matches_as_new(batch_id: str, user_email: str,
                                    language_id: int,
                                    session_id: str,
                                    progress_callback: Optional[callable] = None) -> int:
        """Bulk-apply unmatched rows as new records.

        Targets rows with no suggested_record_id that are still 'pending'
        or already 'create_new' (the UI selectbox may have defaulted them
        to 'create_new' before the user clicks the bulk button).

        Each qualifying row is set to 'create_new' then applied via
        apply_single (creates a new record, writes edit_history, populates
        search entries, and removes the queue row).

        Returns count of rows actually applied.
        """
        # First ensure all qualifying rows have status='create_new'
        session = get_session()
        try:
            session.query(MatchupQueue).filter_by(
                batch_id=batch_id,
            ).filter(
                MatchupQueue.status.in_(['pending', 'create_new']),
                MatchupQueue.suggested_record_id.is_(None),
            ).update({'status': 'create_new'}, synchronize_session='fetch')
            session.commit()

            # Collect IDs of create_new rows to apply
            rows = (
                session.query(MatchupQueue)
                .filter_by(batch_id=batch_id, status='create_new')
                .filter(MatchupQueue.suggested_record_id.is_(None))
                .all()
            )
            queue_ids = [r.id for r in rows]

            applied = 0
            total = len(queue_ids)
            for i, qid in enumerate(queue_ids, 1):
                UploadService.apply_single(
                    queue_id=qid,
                    user_email=user_email,
                    language_id=language_id,
                    session_id=session_id,
                    session=session
                )
                applied += 1
                
                if progress_callback:
                    progress_callback(i, total)

            session.commit()
            logger.info(
                "approve_non_matches_as_new: batch=%s, applied %d of %d rows",
                batch_id, applied, len(queue_ids),
            )
            return applied
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def mark_as_homonym(queue_id: int) -> None:
        """Mark a matchup_queue row as 'create_homonym'."""
        session = get_session()
        try:
            row = session.get(MatchupQueue, queue_id)
            if not row:
                raise ValueError(f"Queue entry {queue_id} not found")
            row.status = 'create_homonym'
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def ignore_entry(queue_id: int) -> None:
        """Mark a matchup_queue row as 'ignored' (leave alone for later review)."""
        session = get_session()
        try:
            row = session.get(MatchupQueue, queue_id)
            if not row:
                raise ValueError(f"Queue entry {queue_id} not found")
            row.status = 'ignored'
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def mark_as_discard(queue_id: int) -> None:
        """Mark a matchup_queue row as 'discard'."""
        session = get_session()
        try:
            row = session.get(MatchupQueue, queue_id)
            if not row:
                raise ValueError(f"Queue entry {queue_id} not found")
            row.status = 'discard'
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def apply_single(queue_id: int, user_email: str, language_id: int,
                     session_id: str, session=None) -> dict:
        """Apply a single matchup_queue row immediately.

        Returns {action, record_id, lx}.
        """
        _provided_session = session is not None
        if not _provided_session:
            session = get_session()
        
        try:
            row = session.get(MatchupQueue, queue_id)
            if not row:
                raise ValueError(f"Queue entry {queue_id} not found")

            if row.status in ('pending', 'ignored'):
                raise ValueError(
                    f"Cannot apply entry with status '{row.status}'. "
                    "Set a valid actionable status first."
                )

            # Discard: just remove from queue without creating/updating records
            if row.status == 'discard':
                lx = row.lx
                session.delete(row)
                if not _provided_session:
                    session.commit()
                return {'action': 'discarded', 'record_id': None, 'lx': lx}

            from src.mdf.parser import parse_mdf as _parse, format_mdf_record, normalize_nt_record
            parsed = _parse(row.mdf_data)
            entry = parsed[0] if parsed else {'lx': row.lx, 'hm': 1, 'ps': '', 'ge': '', 'lg': []}

            from src.database.models.core import RecordLanguage, Language

            # Helper to manage languages
            def _update_languages(record, lg_entries, default_lang_id):
                # 1. Clear existing
                session.query(RecordLanguage).filter_by(record_id=record.id).delete()
                
                # 2. Add new from MDF if present, else fallback to UI selected language
                if lg_entries:
                    for i, lg in enumerate(lg_entries):
                        lg_name = lg['name']
                        lg_code = lg['code']
                        
                        # Find by name first
                        lang = session.query(Language).filter_by(name=lg_name).first()
                        
                        # If not found by name, try to find by code if we have one
                        if not lang and lg_code:
                            lang = session.query(Language).filter_by(code=lg_code).first()
                            
                        if not lang:
                            # Use provided code or fallback to name-based dummy code
                            final_code = lg_code if lg_code else lg_name[:10]
                            lang = Language(name=lg_name, code=final_code)
                            session.add(lang)
                            session.flush()
                        elif lg_code and not lang.code:
                            # Update existing language with code if it was missing
                            lang.code = lg_code
                            session.flush()
                        
                        session.add(RecordLanguage(
                            record_id=record.id,
                            language_id=lang.id,
                            is_primary=(i == 0)
                        ))
                else:
                    session.add(RecordLanguage(
                        record_id=record.id,
                        language_id=default_lang_id,
                        is_primary=True
                    ))

            if row.status == 'matched':
                record = session.get(Record, row.suggested_record_id)
                if not record:
                    raise ValueError(f"Suggested record {row.suggested_record_id} not found")
                prev_data = record.mdf_data
                formatted = format_mdf_record(row.mdf_data)
                normalized = normalize_nt_record(formatted, record.id)
                record.mdf_data = normalized
                record.lx = entry['lx']
                record.hm = entry.get('hm', 1)
                record.ps = entry.get('ps', '')
                record.ge = entry.get('ge', '')
                record.updated_by = user_email
                
                _update_languages(record, entry.get('lg', []), language_id)

                # current_version is auto-incremented by SQLAlchemy optimistic locking
                next_version = record.current_version + 1
                session.add(EditHistory(
                    record_id=record.id,
                    user_email=user_email,
                    session_id=session_id,
                    version=next_version,
                    change_summary="MDF upload: updated from matchup_queue",
                    prev_data=prev_data,
                    current_data=normalized,
                ))
                record_id = record.id
                action = 'updated'

            elif row.status == 'create_homonym':
                # Find highest hm for this lx in same source
                from sqlalchemy import func as sa_func
                max_hm = (
                    session.query(sa_func.max(Record.hm))
                    .filter_by(source_id=row.source_id, lx=entry['lx'])
                    .scalar()
                ) or 0
                new_hm = max_hm + 1
                new_record = Record(
                    lx=entry['lx'],
                    hm=new_hm,
                    ps=entry.get('ps', ''),
                    ge=entry.get('ge', ''),
                    source_id=row.source_id,
                    mdf_data=row.mdf_data,
                )
                session.add(new_record)
                session.flush()
                
                _update_languages(new_record, entry.get('lg', []), language_id)

                formatted = format_mdf_record(row.mdf_data)
                normalized = normalize_nt_record(formatted, new_record.id)
                new_record.mdf_data = normalized
                session.add(EditHistory(
                    record_id=new_record.id,
                    user_email=user_email,
                    session_id=session_id,
                    version=1,
                    change_summary=f"MDF upload: new homonym created (hm {new_hm})",
                    prev_data=None,
                    current_data=normalized,
                ))
                record_id = new_record.id
                action = 'created_homonym'

            elif row.status == 'create_new':
                new_record = Record(
                    lx=entry['lx'],
                    hm=entry.get('hm', 1),
                    ps=entry.get('ps', ''),
                    ge=entry.get('ge', ''),
                    source_id=row.source_id,
                    mdf_data=row.mdf_data,
                )
                session.add(new_record)
                session.flush()
                
                _update_languages(new_record, entry.get('lg', []), language_id)

                formatted = format_mdf_record(row.mdf_data)
                normalized = normalize_nt_record(formatted, new_record.id)
                new_record.mdf_data = normalized
                session.add(EditHistory(
                    record_id=new_record.id,
                    user_email=user_email,
                    session_id=session_id,
                    version=1,
                    change_summary="MDF upload: new record created",
                    prev_data=None,
                    current_data=normalized,
                ))
                record_id = new_record.id
                action = 'created'
            else:
                raise ValueError(f"Unexpected status '{row.status}'")

            session.delete(row)
            if not _provided_session:
                session.commit()

            # Populate search entries
            UploadService.populate_search_entries([record_id], session=session)

            return {'action': action, 'record_id': record_id, 'lx': entry['lx']}
        except Exception:
            if not _provided_session:
                session.rollback()
            raise
        finally:
            if not _provided_session:
                session.close()

    @staticmethod
    def discard_all(batch_id: str) -> int:
        """Delete all matchup_queue rows for a batch. Returns count deleted."""
        session = get_session()
        try:
            count = (
                session.query(MatchupQueue)
                .filter_by(batch_id=batch_id)
                .delete()
            )
            session.commit()
            return count
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def discard_marked(batch_id: str, progress_callback: Optional[callable] = None) -> int:
        """Delete all 'discard' status matchup_queue rows for a batch. Returns count deleted."""
        session = get_session()
        try:
            count = (
                session.query(MatchupQueue)
                .filter_by(batch_id=batch_id, status='discard')
                .delete()
            )
            session.commit()
            if progress_callback:
                progress_callback(count, count)
            return count
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def get_pending_batch_mdf(batch_id: str) -> str:
        """Retrieve all pending records in a batch and return them as MDF text.

        Pending records are those that have not yet been applied to the live records
        table and are not marked for discard.
        """
        session = get_session()
        try:
            rows = (
                session.query(MatchupQueue)
                .filter(MatchupQueue.batch_id == batch_id)
                .filter(MatchupQueue.status.in_(['pending', 'matched', 'create_new', 'create_homonym', 'ignored']))
                .order_by(MatchupQueue.id)
                .all()
            )
            return "\n\n".join([row.mdf_data for row in rows])
        finally:
            session.close()

    @staticmethod
    def commit_matched(batch_id: str, user_email: str,
                       session_id: str,
                       progress_callback: Optional[callable] = None) -> int:
        """Commit all 'matched' rows: update records + edit_history. Returns count."""
        session = get_session()
        try:
            rows = (
                session.query(MatchupQueue)
                .filter_by(batch_id=batch_id, status='matched')
                .all()
            )
            count = 0
            total = len(rows)
            updated_record_ids = []
            for idx, row in enumerate(rows, 1):
                record = session.get(Record, row.suggested_record_id)
                if not record:
                    continue
                prev_data = record.mdf_data
                formatted = format_mdf_record(row.mdf_data)
                normalized = normalize_nt_record(formatted, record.id)
                record.mdf_data = normalized
                # Re-parse to update indexed fields
                from src.mdf.parser import parse_mdf as _parse
                parsed = _parse(row.mdf_data)
                if parsed:
                    e = parsed[0]
                    record.lx = e['lx']
                    record.hm = e.get('hm', 1)
                    record.ps = e.get('ps', '')
                    record.ge = e.get('ge', '')
                record.updated_by = user_email
                # current_version is auto-incremented by SQLAlchemy optimistic locking
                next_version = record.current_version + 1
                session.add(EditHistory(
                    record_id=record.id,
                    user_email=user_email,
                    session_id=session_id,
                    version=next_version,
                    change_summary="MDF upload: updated from matchup_queue",
                    prev_data=prev_data,
                    current_data=normalized,
                ))
                session.delete(row)
                updated_record_ids.append(record.id)
                count += 1
                if progress_callback:
                    progress_callback(idx, total)
            session.commit()

            # Rebuild search entries so the browse/search table reflects updates
            if updated_record_ids:
                UploadService.populate_search_entries(updated_record_ids, session=session)

            return count
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def commit_homonyms(batch_id: str, user_email: str, language_id: int,
                        session_id: str,
                        progress_callback: Optional[callable] = None) -> int:
        """Commit all 'create_homonym' rows: create new homonym records. Returns count."""
        session = get_session()
        try:
            rows = (
                session.query(MatchupQueue)
                .filter_by(batch_id=batch_id, status='create_homonym')
                .all()
            )
            count = 0
            total = len(rows)
            for idx, row in enumerate(rows, 1):
                from src.mdf.parser import parse_mdf as _parse
                parsed = _parse(row.mdf_data)
                entry = parsed[0] if parsed else {'lx': row.lx, 'hm': 1, 'ps': '', 'ge': ''}

                from sqlalchemy import func as sa_func
                max_hm = (
                    session.query(sa_func.max(Record.hm))
                    .filter_by(source_id=row.source_id, lx=entry['lx'])
                    .scalar()
                ) or 0
                new_hm = max_hm + 1

                # Ensure existing records without \hm get \hm 1
                existing_no_hm = (
                    session.query(Record)
                    .filter_by(source_id=row.source_id, lx=entry['lx'], hm=1)
                    .all()
                )
                for existing in existing_no_hm:
                    if UploadService._extract_hm_from_mdf(existing.mdf_data) is None:
                        lines = existing.mdf_data.split('\n')
                        new_lines = []
                        inserted = False
                        for line in lines:
                            new_lines.append(line)
                            if not inserted and line.lstrip().startswith('\\lx '):
                                new_lines.append('\\hm 1')
                                inserted = True
                        existing.mdf_data = '\n'.join(new_lines)

                new_record = Record(
                    lx=entry['lx'],
                    hm=new_hm,
                    ps=entry.get('ps', ''),
                    ge=entry.get('ge', ''),
                    source_id=row.source_id,
                    mdf_data=row.mdf_data,
                )
                session.add(new_record)
                session.flush()

                from src.database import RecordLanguage
                session.add(RecordLanguage(
                    record_id=new_record.id,
                    language_id=language_id,
                    is_primary=True
                ))
                formatted = format_mdf_record(row.mdf_data)
                normalized = normalize_nt_record(formatted, new_record.id)
                new_record.mdf_data = normalized
                session.add(EditHistory(
                    record_id=new_record.id,
                    user_email=user_email,
                    session_id=session_id,
                    version=1,
                    change_summary=f"MDF upload: new homonym created (hm {new_hm})",
                    prev_data=None,
                    current_data=normalized,
                ))
                session.delete(row)
                count += 1
                if progress_callback:
                    progress_callback(idx, total)
            
            # Rebuild search entries
            session.flush()
            homonym_record_ids = [r.id for r in session if isinstance(r, Record) and r.id is not None]
            if homonym_record_ids:
                UploadService.populate_search_entries(homonym_record_ids, session=session)

            session.commit()
            return count
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def commit_new(batch_id: str, user_email: str, language_id: int,
                   session_id: str,
                   progress_callback: Optional[callable] = None) -> int:
        """Commit all 'create_new' rows: insert new records. Returns count."""
        session = get_session()
        try:
            rows = (
                session.query(MatchupQueue)
                .filter_by(batch_id=batch_id, status='create_new')
                .all()
            )
            count = 0
            total = len(rows)
            for idx, row in enumerate(rows, 1):
                from src.mdf.parser import parse_mdf as _parse
                parsed = _parse(row.mdf_data)
                entry = parsed[0] if parsed else {'lx': row.lx, 'hm': 1, 'ps': '', 'ge': ''}

                new_record = Record(
                    lx=entry['lx'],
                    hm=entry.get('hm', 1),
                    ps=entry.get('ps', ''),
                    ge=entry.get('ge', ''),
                    source_id=row.source_id,
                    mdf_data=row.mdf_data,
                )
                session.add(new_record)
                session.flush()

                from src.database import RecordLanguage
                session.add(RecordLanguage(
                    record_id=new_record.id,
                    language_id=language_id,
                    is_primary=True
                ))
                formatted = format_mdf_record(row.mdf_data)
                normalized = normalize_nt_record(formatted, new_record.id)
                new_record.mdf_data = normalized
                session.add(EditHistory(
                    record_id=new_record.id,
                    user_email=user_email,
                    session_id=session_id,
                    version=1,
                    change_summary="MDF upload: new record created",
                    prev_data=None,
                    current_data=normalized,
                ))
                session.delete(row)
                count += 1
                if progress_callback:
                    progress_callback(idx, total)
            
            # Rebuild search entries
            session.flush()
            new_record_ids = [r.id for r in session if isinstance(r, Record) and r.id is not None]
            if new_record_ids:
                UploadService.populate_search_entries(new_record_ids, session=session)

            session.commit()
            return count
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def populate_search_entries(record_ids: list[int], session=None) -> int:
        """Rebuild search_entries for given record ids. Returns count created."""
        _provided_session = session is not None
        if not _provided_session:
            session = get_session()
        try:
            total = 0
            for rid in record_ids:
                record = session.get(Record, rid)
                if not record:
                    continue
                # Delete existing search entries
                session.query(SearchEntry).filter_by(record_id=rid).delete()

                # Re-parse MDF to extract searchable fields
                from src.mdf.parser import parse_mdf as _parse
                parsed = _parse(record.mdf_data)
                if not parsed:
                    continue
                entry = parsed[0]

                # Insert lx
                if entry.get('lx'):
                    session.add(SearchEntry(record_id=rid, term=entry['lx'], entry_type='lx'))
                    total += 1
                # Insert va, se, cf, ve lists
                for field in ('va', 'se', 'cf', 've'):
                    for val in entry.get(field, []):
                        if val:
                            session.add(SearchEntry(record_id=rid, term=val, entry_type=field))
                            total += 1

            if not _provided_session:
                session.commit()
            return total
        except Exception:
            if not _provided_session:
                session.rollback()
            raise
        finally:
            if not _provided_session:
                session.close()
