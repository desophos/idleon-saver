from idleon_saver.stencyl.decoder import StencylDecoder
from idleon_saver.stencyl.encoder import StencylEncoder
from idleon_saver.utility import chunk


def test_inversion(datafiles):
    decoded = StencylDecoder(datafiles["stencyl"]).result.wrapped
    encoded = StencylEncoder(decoded).result
    # pytest uses difflib for equality assertions,
    # which is extremely slow in this case:
    # at least several minutes for 400k+ length strings.
    # Splitting these strings into lines helps execution time
    # and produces a more useful diff.
    assert chunk(datafiles["stencyl"], 50) == chunk(encoded, 50)
