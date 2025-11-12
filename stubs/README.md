# Type stubs

This directory contains type stubs for packages used by cepces.

## Contents

- **cepces/krb5/** - Stubs for internal krb5 wrapper modules
- **requests_gssapi/** - Stubs for the requests-gssapi package

## Regenerating stubs

The stubs have been generated with mypy's [stubgen](https://mypy.readthedocs.io/en/stable/stubgen.html).

To regenerate all stubs, run:

```bash
tox -e stubgen
```

This will regenerate stubs for both `cepces.krb5` and `requests_gssapi` packages.
