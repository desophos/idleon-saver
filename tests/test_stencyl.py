from idleon_save_editor.stencyl import StencylDecoder, StencylEncoder
from idleon_save_editor.utility import chunk


def test_inversion(stencylsave):
    decoded = StencylDecoder(stencylsave).result
    encoded = StencylEncoder(decoded).result
    # pytest uses difflib for equality assertions,
    # which is extremely slow in this case:
    # at least several minutes for 400k+ length strings.
    # Splitting these strings into lines helps execution time
    # and produces a more useful diff.
    assert chunk(stencylsave, 50) == chunk(encoded, 50)
