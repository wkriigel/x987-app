def test_smoke_import():
    import x987  # noqa: F401

def test_doctor_runs():
    # Importing main entry and doing a dry run that shouldn't error
    import runpy
    runpy.run_module("x987", run_name="__main__")
