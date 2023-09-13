server = dict(
    address = "http://192.168.0.109",
    port = "8096",
    api_key = "a30c9b33ef5b4368bfca89489d2f62aa",
    content_dir = "/Volumes/Bifrost/Yggdrasil/Movies",
    library_id = "f137a2dd21bbc1b99aa5c0f6bf02a805",
    log_file = "/Users/mafshari/Documents/jellyfin_logs/log.txt",
    refresh_delay = "15"
)

refresh_mode = dict(
    default = "Refresh",
    missing = "Refresh?Recursive=true&ImageRefreshMode=FullRefresh&MetadataRefreshMode=FullRefresh&ReplaceAllImages=false&ReplaceAllMetadata=false",
    replace_images = "Refresh?Recursive=true&ImageRefreshMode=FullRefresh&MetadataRefreshMode=FullRefresh&ReplaceAllImages=true&ReplaceAllMetadata=false",
    replace_metadata = "Refresh?Recursive=true&ImageRefreshMode=FullRefresh&MetadataRefreshMode=FullRefresh&ReplaceAllImages=false&ReplaceAllMetadata=true",
    replace_all = "Refresh?Recursive=true&ImageRefreshMode=FullRefresh&MetadataRefreshMode=FullRefresh&ReplaceAllImages=true&ReplaceAllMetadata=true"
)