"""A function for splitting a line into parts of a given length."""

def split_chunks(string, stride):
    """Split line into chunks of length stride."""

    chunks = []
    for idx in xrange(0, len(string), stride):
        chunks.append(string[idx:min(idx+stride, len(string))])
    return chunks
