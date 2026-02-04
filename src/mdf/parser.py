# Copyright (c) 2026 Brothertown Language
import re

def parse_mdf(content):
    """
    Parses MDF content where records are separated by double newlines.
    Returns a list of dictionaries representing records with full raw data.
    """
    # Split by double newlines (or more)
    raw_records = re.split(r'\n\s*\n', content.strip())
    
    parsed_records = []
    for raw in raw_records:
        if not raw.strip():
            continue
            
        # The entire raw record is preserved exactly as is
        mdf_data = raw.strip()
        
        record = {
            'mdf_data': mdf_data,
            'lx': '',
            'hm': 1,
            'ps': '',
            'ge': ''
        }
        
        # Extract metadata fields (\lx, \ps, \ge, \hm) for UI/indexing only
        # The mdf_data itself remains the source of truth
        lx_match = re.search(r'^\\lx\s+(.+)$', mdf_data, re.MULTILINE)
        if lx_match:
            record['lx'] = lx_match.group(1).strip()
            
        hm_match = re.search(r'^\\hm\s+(\d+)$', mdf_data, re.MULTILINE)
        if hm_match:
            try:
                record['hm'] = int(hm_match.group(1).strip())
            except ValueError:
                record['hm'] = 1
            
        ps_match = re.search(r'^\\ps\s+(.+)$', mdf_data, re.MULTILINE)
        if ps_match:
            record['ps'] = ps_match.group(1).strip()
            
        ge_match = re.search(r'^\\ge\s+(.+)$', mdf_data, re.MULTILINE)
        if ge_match:
            record['ge'] = ge_match.group(1).strip()
            
        if record['lx']:
            parsed_records.append(record)
            
    return parsed_records
