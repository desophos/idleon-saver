from idleon_save_editor.stencyl import StencylDecoder, StencylEncoder


def test_inversion(stencylsave):
    assert stencylsave == StencylEncoder(StencylDecoder(stencylsave).result).result
