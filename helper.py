import urlparse


def validateReturnURL(base_path, to_validate_path):
    parsed = urlparse.urlparse(to_validate_path)
    if parsed.scheme != 'http' and parsed.scheme != 'https':
        # This URL does is not a valid url. Probably a relative path
        # We join the two paths together.
        return urlparse.urljoin(base_path, to_validate_path)
    else:
        return to_validate_path