try:
    from yt_dlp.extractor.youtube.jsc._builtin import ejs
    print("Import successful!")
    print("_EJS_WIKI_URL:", getattr(ejs, '_EJS_WIKI_URL', 'NOT FOUND'))
except Exception as e:
    import traceback
    traceback.print_exc()
