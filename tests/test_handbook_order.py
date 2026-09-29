from scripts.build_handbook import sources


def test_directory_order_is_case_sensitive_and_platform_independent():
    # WindowsPath comparisons ignore case; documentation order must not.
    names = [
        name for _, rows in sources() for name, _ in rows if name.startswith("templates/product/")
    ]
    assert names == sorted(names)
    assert names.index("templates/product/README.md") < names.index("templates/product/app.py")
