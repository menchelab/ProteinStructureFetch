from .util import Logger

log = Logger("batcher")


def batch(functions, proteins, batch_size):
    """Will execute the function which has been passed in batches of protein structures."""
    start = 0
    end = batch_size
    while len(proteins) > 0:
        for _ in range(batch_size):
            log.debug(f"Starting Batch form: {start} to {end}")
            batch_proteins = proteins[:batch_size]
            for func in functions:
                func(batch_proteins)
            start = end
            end += batch_size
        del proteins[:batch_size]
