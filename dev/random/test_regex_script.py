import re

old_patterns = {
    "SICE no MARBL-BIO": r"_DATM.+_SICE.*_MOM6%REGIONAL(?!.*%MARBL-BIO).+_SWAV",
    "SICE with MARBL-BIO": r"_DATM.+_SICE.*_MOM6%REGIONAL[^_]*MARBL-BIO.+_SWAV",
    "CICE no MARBL-BIO": r"_DATM.+_CICE.*_MOM6%REGIONAL(?!.*%MARBL-BIO).+_SWAV",
    "CICE with MARBL-BIO": r"_DATM.+_CICE.*_MOM6%REGIONAL[^_]*MARBL-BIO.+_SWAV",
}
new_patterns = {
    "SICE no MARBL-BIO": r"_DATM.+_SICE.*_MOM6(?!%[^_]*MARBL-BIO)%[^_]*REGIONAL.+_SWAV",
    "SICE with MARBL-BIO": r"_DATM.+_SICE.*_MOM6%([^_]*REGIONAL[^_]*MARBL-BIO|[^_]*MARBL-BIO[^_]*REGIONAL).+_SWAV",
    "CICE no MARBL-BIO": r"_DATM.+_CICE.*_MOM6(?!%[^_]*MARBL-BIO)%[^_]*REGIONAL.+_SWAV",
    "CICE with MARBL-BIO": r"_DATM.+_CICE.*_MOM6%([^_]*REGIONAL[^_]*MARBL-BIO|[^_]*MARBL-BIO[^_]*REGIONAL).+_SWAV",
}
# Note: real compsets always have components between MOM6 and SWAV (e.g. _SLND_SGLC_)
test_compsets = [
    # SICE no MARBL-BIO - should ONLY match pattern 1
    ("1850_DATM%JRA_SICE_MOM6%REGIONAL_SLND_SGLC_SWAV",                       ["SICE no MARBL-BIO"]),
    ("1850_DATM%JRA_SICE_MOM6%FOO%REGIONAL_SLND_SGLC_SWAV",                   ["SICE no MARBL-BIO"]),   # new behavior
    ("1850_DATM%JRA_SICE_MOM6%REGIONAL%FOO_SLND_SGLC_SWAV",                   ["SICE no MARBL-BIO"]),
    # SICE with MARBL-BIO - should ONLY match pattern 2
    ("1850_DATM%JRA_SICE_MOM6%REGIONAL%MARBL-BIO_SLND_SGLC_SWAV",             ["SICE with MARBL-BIO"]),
    ("1850_DATM%JRA_SICE_MOM6%MARBL-BIO%REGIONAL_SLND_SGLC_SWAV",             ["SICE with MARBL-BIO"]),  # new behavior
    ("1850_DATM%JRA_SICE_MOM6%FOO%MARBL-BIO%REGIONAL_SLND_SGLC_SWAV",         ["SICE with MARBL-BIO"]),  # new behavior
    ("1850_DATM%JRA_SICE_MOM6%FOO%REGIONAL%MARBL-BIO_SLND_SGLC_SWAV",         ["SICE with MARBL-BIO"]),  # new behavior
    # CICE no MARBL-BIO - should ONLY match pattern 3
    ("1850_DATM%JRA_CICE_MOM6%REGIONAL_SLND_SGLC_SWAV",                       ["CICE no MARBL-BIO"]),
    ("1850_DATM%JRA_CICE_MOM6%FOO%REGIONAL_SLND_SGLC_SWAV",                   ["CICE no MARBL-BIO"]),   # new behavior
    ("1850_DATM%JRA_CICE_MOM6%REGIONAL%FOO_SLND_SGLC_SWAV",                   ["CICE no MARBL-BIO"]),
    # CICE with MARBL-BIO - should ONLY match pattern 4
    ("1850_DATM%JRA_CICE_MOM6%REGIONAL%MARBL-BIO_SLND_SGLC_SWAV",             ["CICE with MARBL-BIO"]),
    ("1850_DATM%JRA_CICE_MOM6%MARBL-BIO%REGIONAL_SLND_SGLC_SWAV",             ["CICE with MARBL-BIO"]),  # new behavior
    ("1850_DATM%JRA_CICE_MOM6%FOO%MARBL-BIO%REGIONAL_SLND_SGLC_SWAV",         ["CICE with MARBL-BIO"]),  # new behavior
    ("1850_DATM%JRA_CICE_MOM6%FOO%REGIONAL%MARBL-BIO_SLND_SGLC_SWAV",         ["CICE with MARBL-BIO"]),  # new behavior
    # Should match NOTHING
    ("1850_DATM%JRA_CICE_MOM6%MARBL-BIO_SLND_SGLC_SWAV",                      []),
    ("1850_DATM%JRA_SICE_MOM6%MARBL-BIO_SLND_SGLC_SWAV",                      []),
]





def run_tests(patterns, label):
    print(f"\n{'='*130}")
    print(f" {label}")
    print(f"{'='*130}")
    print(f"{'Compset':<60} {'Expected':<25} {'Got':<25} {'Status'}")
    print(f"{'-'*130}")

    all_passed = True
    for compset, expected in test_compsets:
        matched = [name for name, pattern in patterns.items() if re.search(pattern, compset)]
        passed = sorted(matched) == sorted(expected)
        all_passed = all_passed and passed
        status = "PASS" if passed else "FAIL"
        # highlight new behavior cases
        print(f"{compset:<60} {str(expected):<25} {str(matched):<25} {status}")

    print(f"{'-'*130}")
    print(f"Result: {'All tests passed!' if all_passed else 'Some tests FAILED!'}")
    return all_passed

old_passed = run_tests(old_patterns, "OLD PATTERNS")
new_passed = run_tests(new_patterns, "NEW PATTERNS")