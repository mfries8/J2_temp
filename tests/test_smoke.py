def test_import_all_modules():
    import importlib
    modules = [
        'meteor_darkflight.event_ingest',
        'meteor_darkflight.physics_core',
        'meteor_darkflight.atmos_source',
        'meteor_darkflight.sim_kernel',
        'meteor_darkflight.geospatial_export',
    ]
    for m in modules:
        importlib.import_module(m)
