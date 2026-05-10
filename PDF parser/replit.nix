{ pkgs }: {
    deps = [
        pkgs.python310
        pkgs.tesseract
        pkgs.leptonica
        pkgs.pkg-config
    ];
    env = {
        PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.tesseract
            pkgs.leptonica
        ];
        TESSDATA_PREFIX = "${pkgs.tesseract}/share/tesseract-ocr-4.1.1/tessdata";
    };
}
