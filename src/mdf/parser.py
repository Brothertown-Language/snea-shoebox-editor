# Copyright (c) 2026 Brothertown Language
# <!-- CRITICAL: NO EDITS WITHOUT APPROVED PLAN (Wait for "Go", "Proceed", or "Approved") -->


def _extract_tag(line, tag):
    """If line starts with \\tag (optionally indented), return the value after it, else None."""
    stripped = line.lstrip()
    prefix = '\\' + tag + ' '
    if stripped.startswith(prefix):
        return stripped[len(prefix):].strip()
    return None


def _is_nt_record_line(line):
    """Return True if line is a \\nt Record: <digits> line."""
    stripped = line.lstrip()
    if not stripped.startswith('\\nt Record:'):
        return False
    value = stripped[len('\\nt Record:'):].strip()
    return value.isdigit()


def parse_mdf(content):
    """
    Parses MDF content where records are separated by blank lines.
    Returns a list of dictionaries representing records with full raw data.

    Linguistic fields (\\lx, \\hm, \\ps, \\ge) are extracted for database indexing
    and list views, while mdf_data remains the source of truth.

    Includes logic for detecting the \\nt Record: <id> tag
    to maintain synchronization with the PostgreSQL database.
    """
    blocks = content.strip().split('\n\n')

    parsed_records = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        mdf_data = block

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

        for line in mdf_data.split('\n'):
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

            val = _extract_tag(line, 'lg')
            if val is not None:
                # Handle cases like "Wampanoag [wam]" -> name="Wampanoag", code="wam"
                # If no brackets, name is full value, code is None
                import re
                match = re.search(r'^(.*?)\[(.*?)\]', val)
                if match:
                    name = match.group(1).strip()
                    code = match.group(2).strip()
                    record['lg'].append({'name': name, 'code': code})
                else:
                    record['lg'].append({'name': val.strip(), 'code': None})
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

            if _is_nt_record_line(line):
                value = line.lstrip()[len('\\nt Record:'):].strip()
                record['record_id'] = int(value)

        if record['lx']:
            parsed_records.append(record)

    return parsed_records


def format_mdf_record(mdf_text: str) -> str:
    """
    Normalize formatting of an MDF record for storage:
    - Remove all leading indentation from lines.
    - Add one blank line before each \\se line (subentry).
    - Add one blank line before each \\xv line (example vernacular).
    - Add one blank line before the \\nt Record: line.
    - Remove any other consecutive blank lines.
    """
    lines = mdf_text.split('\n')
    result = []
    for line in lines:
        stripped = line.lstrip()
        if not stripped:
            continue
        is_se = stripped.startswith('\\se ')
        is_xv = stripped.startswith('\\xv ')
        is_nt_rec = _is_nt_record_line(stripped)
        if (is_se or is_xv or is_nt_rec) and result and result[-1] != '':
            result.append('')
        result.append(stripped)
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
