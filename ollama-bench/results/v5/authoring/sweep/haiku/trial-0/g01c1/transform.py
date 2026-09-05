def transform(text):
    """Transform path records according to the specification.

    Each record is a path with '/' as the segment separator.
    Paths starting with '/' are absolute; others are relative.
    Empty segments and '.' are ignored.
    '..' removes the most recently retained ordinary segment.
    """
    records = text.split('\n')
    transformed_records = []

    for record in records:
        transformed = _transform_record(record)
        transformed_records.append(transformed)

    return '\n'.join(transformed_records)


def _transform_record(record):
    """Transform a single path record."""
    if not record:
        return ""

    is_absolute = record.startswith('/')
    ends_with_slash = record.endswith('/')

    # Split by '/' to get segments
    segments = record.split('/')

    # Remove the empty first segment for absolute paths
    if is_absolute:
        segments = segments[1:]

    # Process segments to build retained list
    retained = []
    for seg in segments:
        if seg == '' or seg == '.':
            # Ignore empty segments and '.'
            continue
        elif seg == '..':
            # Find the most recently retained ordinary segment (not '..')
            found = False
            for i in range(len(retained) - 1, -1, -1):
                if retained[i] != '..':
                    # Found an ordinary segment, remove it
                    retained.pop(i)
                    found = True
                    break

            if not found:
                # No ordinary segment found to remove
                if not is_absolute:
                    # For relative records, retain the '..'
                    retained.append('..')
                # For absolute records, discard the '..'
        else:
            # Ordinary segment - retain it
            retained.append(seg)

    # Build the result string
    if not retained:
        # No segments retained
        if is_absolute:
            return "/"
        else:
            # For relative records with segments that reduced to nothing,
            # return '.' only if the original record was nonempty
            return "."

    # Join retained segments with '/'
    result = '/'.join(retained)

    # Add leading '/' for absolute paths
    if is_absolute:
        result = '/' + result

    # Preserve trailing '/' if original record ended with one
    if ends_with_slash:
        result += '/'

    return result
