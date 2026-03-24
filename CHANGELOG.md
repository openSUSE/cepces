# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-03-24

### Added

- User certificate enrollment support: new `user` module, `cepces-user` and
  `cepces-user-autoenroll` scripts, and configuration options for user
  certificates.
- `--endpoint` CLI option for `cepces-submit` with HTTPS URL validation.
- Auth module now supports using the default principal from the credential
  cache when no principal is explicitly configured.
- `cepces-submit --install` mode to register cepces as a certmonger CA helper
  automatically.
- XCEP now sends `clientVersion`/`serverVersion` to retrieve all available
  certificate templates from the server.
- `nillable` property on XML binding nodes.
- `poll_interval` property on the `Service` class.
- Documentation for user certificate enrollment and auto-enrollment.
- `doc/DEBUGGING.md`, `doc/PROTOCOLS.md`, and testing setup guide.

### Changed

- `run_pinentry`, `detect_display_type`, and XML element properties made
  public.
- Dropped support for Python 3.9 (end of life).

### Fixed

- Missing `/usr/etc/cepces/conf.d` entry in `DEFAULT_CONFIG_DIRS`.
- `Submit` certmonger operation no longer crashes when the WSTEP response
  contains no result.
- `Service` properties now handle nil policies and CAs returned by the server.
- `XMLElementList` now correctly handles `xsi:nil="true"` elements.
- `XMLElementList` no longer skips elements when a sibling is missing.
- GSSAPI authentication now catches and reports krb5 errors at init time.
- Keytab path is now encoded to bytes before being passed to the GSSAPI store.
- Certmonger operations that do not require authentication no longer attempt
  to authenticate, avoiding spurious failures.

## [0.3.17] - 2026-01-22

### Fixed

- XCEP now sends `clientVersion`/`serverVersion` to retrieve all available
  certificate templates from the server.

## [0.3.16] - 2025-12-22

### Added

- `cepces-submit --install` mode to register cepces as a certmonger CA helper
  automatically.

## [0.3.15] - 2025-12-22

### Fixed

- Certmonger operations that do not require authentication no longer attempt
  to authenticate, avoiding spurious failures.

## [0.3.14] - 2025-12-19

### Added

- Script to verify that version numbers are in sync across project files.

### Fixed

- `Submit` certmonger operation no longer crashes when the WSTEP response
  contains no result.
- `Service` properties now handle nil policies and CAs returned by the server.
- `XMLElementList` now correctly handles `xsi:nil="true"` elements.
- `XMLElementList` no longer skips elements when a sibling is missing.
- GSSAPI authentication now catches and reports krb5 errors at init time.

## [0.3.13] - 2025-12-07

### Fixed

- Keytab path is now encoded to bytes before being passed to the GSSAPI store,
  fixing a crash on Python 3.

## [0.3.12] - 2025-11-12

No notable user-facing changes.

## [0.3.11] - 2025-11-06

### Added

- New `keyctl`-based keyring handler (`KeyringHandler`) replacing the
  `keyring` library dependency.
- Pinentry-based credentials handler, replacing zenity.
- Fallback credential prompt support using kdialog or zenity when pinentry is
  unavailable.
- `get_default_keytab_name()` helper in the krb5 module.
- Config option `display` to explicitly set the `DISPLAY` environment variable
  for GUI credential prompts.
- Allow configuring the OpenSSL ciphers string via configuration.
- Test suite migrated to pytest.

### Changed

- `KerberosAuthenticationHandler` renamed to `GSSAPIAuthenticationHandler`.
- GSSAPI authentication now uses the system default keytab when none is
  configured.

## [0.3.10] - 2025-06-26

### Added

- GSSAPI channel bindings support in SOAP authentication.
- Python 3.14 added to the test matrix.
- Keyring support for username/password authentication (stores credentials
  securely and adds WS-Security nonce/timestamp to SOAP requests).

### Changed

- Migrated from `setup.py` to `pyproject.toml`.
- SOAP authentication now uses GSSAPI directly instead of the `kerberos`
  library functions.

### Fixed

- Boolean value parsing in the configuration file.

## [0.3.9] - 2024-03-18

### Fixed

- Failure to parse DER-encoded certificates.

## [0.3.8] - 2023-02-15

### Changed

- Migrated SOAP authentication to SPNEGO mechanism.

### Fixed

- Incorrect XML namespaces on `BinarySecurityToken` attributes in WSTEP
  requests.

## [0.3.7] - 2022-12-01

### Added

- Configurable OpenSSL security level via the configuration file.

## [0.3.6] - 2022-10-20

### Added

- Configurable Kerberos delegation (enabled/disabled via config).
- Replaced `requests_kerberos` with `requests_gssapi`.

### Fixed

- `cepces-submit` crash: `TypeError: option values must be strings`.

## [0.3.5] - 2022-06-01

### Added

- Certificate-based client authentication method.
- Configurable polling interval reported to certmonger.
- GitHub Actions CI workflow.

### Fixed

- `poll_interval` config value not available in `Submit` and `Poll` operations.
- Configuration file missing `[global]` section handling.
- Python 3.10 compatibility fix for import paths.

## [0.3.4] - 2021-07-12

### Added

- Command-line options to override server, auth method, keytab, and principal.
- Kerberos delegation support.
- SELinux permissions for RHEL 6.

## [0.3.3] - 2021-07-12

### Fixed

- Removed reference to non-existent `PKCS7Converter`; use `StringConverter`
  instead.
- Support lowercase Kerberos principal names.

## [0.3.2] - 2019-06-03

### Fixed

- Missing SELinux type requirement in the policy module.

## [0.3.1] - 2019-06-03

### Added

- Support for bypassing the CEP endpoint (direct WSTEP enrollment).
- Default log file configuration.

### Fixed

- Certificate renewal flow.

## [0.3.0] - 2018-02-05

### Added

- Full certmonger CA helper integration (`cepces-submit`).
- MS-XCEP protocol support for policy endpoint discovery.
- MS-WSTEP protocol support for certificate enrollment and renewal.
- Kerberos/GSSAPI, username/password, certificate, and anonymous
  authentication methods.
- XML binding framework (`XMLNode`, `XMLElement`, `XMLValue`, descriptors).

## [0.2.0] - 2016-08-17

### Added

- Initial SOAP service support.
- Basic XML binding and type converters.
- krb5 credential cache integration.

[0.4.0]: https://github.com/openSUSE/cepces/compare/v0.3.17...v0.4.0
[0.3.17]: https://github.com/openSUSE/cepces/compare/v0.3.16...v0.3.17
[0.3.16]: https://github.com/openSUSE/cepces/compare/v0.3.15...v0.3.16
[0.3.15]: https://github.com/openSUSE/cepces/compare/v0.3.14...v0.3.15
[0.3.14]: https://github.com/openSUSE/cepces/compare/v0.3.13...v0.3.14
[0.3.13]: https://github.com/openSUSE/cepces/compare/v0.3.12...v0.3.13
[0.3.12]: https://github.com/openSUSE/cepces/compare/v0.3.11...v0.3.12
[0.3.11]: https://github.com/openSUSE/cepces/compare/v0.3.10...v0.3.11
[0.3.10]: https://github.com/openSUSE/cepces/compare/v0.3.9...v0.3.10
[0.3.9]: https://github.com/openSUSE/cepces/compare/v0.3.8...v0.3.9
[0.3.8]: https://github.com/openSUSE/cepces/compare/v0.3.7...v0.3.8
[0.3.7]: https://github.com/openSUSE/cepces/compare/v0.3.6...v0.3.7
[0.3.6]: https://github.com/openSUSE/cepces/compare/v0.3.5...v0.3.6
[0.3.5]: https://github.com/openSUSE/cepces/compare/v0.3.4...v0.3.5
[0.3.4]: https://github.com/openSUSE/cepces/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/openSUSE/cepces/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/openSUSE/cepces/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/openSUSE/cepces/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/openSUSE/cepces/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/openSUSE/cepces/releases/tag/v0.2.0
