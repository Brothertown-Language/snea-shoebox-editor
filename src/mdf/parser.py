# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->
import re
from .tag_loader import get_valid_tags


def _extract_tag(line, tag):
    """If line starts with \\tag (optionally indented), return the value after it, else None."""
    stripped = line.lstrip()
    prefix = '\\' + tag + ' '
    if stripped.startswith(prefix):
        return stripped[len(prefix):].strip()
    # Handle tag at end of line without space
    if stripped == '\\' + tag:
        return ""
    return None


def _is_nt_record_line(line):
    """Return True if line is a \\nt Record: <digits> line."""
    stripped = line.lstrip()
    if not stripped.startswith('\\nt Record:'):
        return False
    value = stripped[len('\\nt Record:'):].strip()
    return value.isdigit()


_ISO_LANG_PATTERN = re.compile(r'([A-Za-z][^\[]*?)\s*\[([a-z]{3})\]')


def _extract_iso_langs(line_value: str) -> list:
    """Return list of {'name': ..., 'code': ...} dicts found in line_value."""
    return [
        {'name': m.group(1).strip(), 'code': m.group(2)}
        for m in _ISO_LANG_PATTERN.finditer(line_value)
    ]


def _process_block_into_record(lines_buffer):
    """Internal helper to convert a list of lines into a structured record."""
    if not lines_buffer:
        return None
    
    mdf_data = "\n".join(lines_buffer).strip()
    if not mdf_data:
        return None

    record = {
        'mdf_data': mdf_data,
        'lx': '',
        'hm': 1,
        'ps': '',
        'ge': '',
        'record_id': None,
        'lg': [],
        'va': [],
        'se': [],
        'cf': [],
        've': []
    }

    in_headword = True
    for line in lines_buffer:
        # Check for structural branching tags
        if _extract_tag(line, 'se') is not None or \
           _extract_tag(line, 'sn') is not None or \
           _extract_tag(line, 'va') is not None or \
           _extract_tag(line, 'xv') is not None:
            in_headword = False

        val = _extract_tag(line, 'lx')
        if val is not None and not record['lx']:
            record['lx'] = val
            continue

        val = _extract_tag(line, 'hm')
        if val is not None and val.isdigit():
            record['hm'] = int(val)
            continue

        val = _extract_tag(line, 'ps')
        if val is not None and not record['ps']:
            record['ps'] = val
            continue

        val = _extract_tag(line, 'ge')
        if val is not None and not record['ge']:
            record['ge'] = val
            continue

        val = _extract_tag(line, 'so')
        if val is not None:
            # Capturing the full string for source_page field
            if not record.get('source_page'):
                record['source_page'] = val
            continue

        val = _extract_tag(line, 'va')
        if val is not None:
            record['va'].append(val)
            continue

        val = _extract_tag(line, 'se')
        if val is not None:
            record['se'].append(val)
            continue

        val = _extract_tag(line, 'cf')
        if val is not None:
            record['cf'].append(val)
            continue

        val = _extract_tag(line, 've')
        if val is not None:
            record['ve'].append(val)
            continue

        val = _extract_tag(line, 'ns')
        if val is not None:
            continue

        if _is_nt_record_line(line):
            value = line.lstrip()[len('\\nt Record:'):].strip()
            record['record_id'] = int(value)

    # Second pass: scan every line for ISO 639 language patterns
    seen_lg = set()
    in_headword = True
    for line in lines_buffer:
        stripped = line.lstrip()
        if _extract_tag(line, 'se') is not None or \
           _extract_tag(line, 'sn') is not None or \
           _extract_tag(line, 'va') is not None or \
           _extract_tag(line, 'xv') is not None:
            in_headword = False
        # Get value portion (after tag prefix)
        space_idx = stripped.find(' ')
        line_value = stripped[space_idx + 1:] if space_idx != -1 else ''
        for lg in _extract_iso_langs(line_value):
            key = (lg['name'], lg['code'])
            if key not in seen_lg:
                seen_lg.add(key)
                record['lg'].append({'name': lg['name'], 'code': lg['code'], 'is_primary': in_headword})

    return record


def parse_mdf(content):
    """
    Parses MDF content. 
    1. Validates that the first meaningful line starts with \\lx.
    2. Conducts a watermark audit of tags (20% threshold for unrecognized tags).
    3. Splits content into records based on \\lx markers (line-oriented).
    """
    lines = content.splitlines()
    
    # 1. Find the first meaningful line and validate \lx
    first_meaningful_line_index = -1
    for i, line in enumerate(lines):
        if line.strip():
            first_meaningful_line_index = i
            break
            
    if first_meaningful_line_index == -1:
        return []

    if not lines[first_meaningful_line_index].lstrip().startswith('\\lx '):
        raise ValueError("Fatal Error: Content detected before the first \\lx marker. Ingestion aborted.")

    # 2. Watermark Audit
    valid_tags = get_valid_tags()
    total_tags = 0
    invalid_tags = 0
    tag_pattern = re.compile(r'^\\([a-z]+)')

    for line in lines[first_meaningful_line_index:]:
        stripped = line.lstrip()
        if stripped.startswith('\\'):
            match = tag_pattern.match(stripped)
            if match:
                tag = match.group(1)
                total_tags += 1
                if tag not in valid_tags and not _is_nt_record_line(line):
                    invalid_tags += 1

    if total_tags > 0:
        watermark = invalid_tags / total_tags
        if watermark > 0.20:
            percentage = int(watermark * 100)
            raise ValueError(
                f"Fatal Error: High volume of unrecognized tags ({percentage}%). "
                f"This file appears to be legacy data or non-modern MDF. Ingestion aborted."
            )

    # 3. Line-oriented parsing
    parsed_records = []
    current_record_lines = []
    
    for line in lines[first_meaningful_line_index:]:
        stripped = line.lstrip()
        if stripped.startswith('\\lx '):
            if current_record_lines:
                record = _process_block_into_record(current_record_lines)
                if record and record['lx']:
                    parsed_records.append(record)
            current_record_lines = [line]
        else:
            current_record_lines.append(line)

    if current_record_lines:
        record = _process_block_into_record(current_record_lines)
        if record and record['lx']:
            parsed_records.append(record)

    return parsed_records


def format_mdf_record(mdf_text: str) -> str:
    """
    Normalize formatting of an MDF record for storage:
    - Remove all leading indentation from lines.
    - Normalize by stripping all existing blank lines first.
    - Add exactly one blank line before each bundle-start tag (except the first line):
      \\sn (sense), \\se (subentry), \\xv (example), \\et (etymology).
    - Add one blank line before the \\nt Record: line.
    - Idempotent: running multiple times produces the same result.
    """
    _bundle_pat = re.compile(r'^\\(?:sn|se|xv|et)(?:\s+|$)')
    # Step 1: strip indentation and remove all blank lines
    clean_lines = [line.lstrip() for line in mdf_text.split('\n') if line.strip()]
    # Step 2: insert blank lines before bundle-start tags and \nt Record:
    result = []
    for i, line in enumerate(clean_lines):
        if i > 0 and (_bundle_pat.match(line) or _is_nt_record_line(line)):
            result.append('')
        result.append(line)
    return '\n'.join(result)


def normalize_nt_record(mdf_text: str, record_id: int) -> str:
    """
    Remove all existing \\nt Record: lines from mdf_text and append
    exactly one \\nt Record: <record_id> line at the end.
    """
    lines = mdf_text.split('\n')
    filtered = [line for line in lines if not _is_nt_record_line(line)]
    while filtered and not filtered[-1].strip():
        filtered.pop()
    filtered.append(f'\\nt Record: {record_id}')
    return '\n'.join(filtered)
