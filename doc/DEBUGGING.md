# Debugging cepces

This document explains how to debug cepces when troubleshooting certificate
enrollment issues.

## Enabling Debug Logging

Edit `/etc/cepces/logging.conf` and change the log level from `INFO` to
`DEBUG`, using only stderr for output:

```ini
[loggers]
keys=root

[handlers]
keys=consoleHandler

[formatters]
keys=defaultFormatter

[logger_root]
level=DEBUG
handlers=consoleHandler

[handler_consoleHandler]
class=StreamHandler
level=DEBUG
formatter=defaultFormatter
args=(sys.stderr,)

[formatter_defaultFormatter]
format=%(asctime)s %(name)s:%(levelname)s:%(message)s
datefmt=
```

When running commands manually, debug output will appear on stderr. When
running under systemd (e.g., via certmonger), logs will be captured by
journalctl.

## Running Operations from the Command Line

You can run cepces operations directly without certmonger by setting the
`CERTMONGER_OPERATION` environment variable:

```bash
CERTMONGER_OPERATION=IDENTIFY \
    /usr/bin/python3 /usr/libexec/certmonger/cepces-submit \
    --server=ca.example.com \
    --auth=Kerberos
```

### Available Operations

- `IDENTIFY` - Show version information
- `FETCH-ROOTS` - Fetch CA certificate chain
- `GET-SUPPORTED-TEMPLATES` - List available certificate templates
- `GET-DEFAULT-TEMPLATE` - Get default template
- `GET-NEW-REQUEST-REQUIREMENTS` - List required variables for new requests
- `GET-RENEW-REQUEST-REQUIREMENTS` - List required variables for renewals
- `SUBMIT` - Submit a CSR (requires `CERTMONGER_CSR` environment variable)
- `POLL` - Poll for deferred request (requires `CERTMONGER_CA_COOKIE`)

### Examples

Fetch CA roots:

```bash
CERTMONGER_OPERATION=FETCH-ROOTS \
    /usr/bin/python3 /usr/libexec/certmonger/cepces-submit \
    --server=win-ca01.example.com \
    --auth=Kerberos
```

List available templates:

```bash
CERTMONGER_OPERATION=GET-SUPPORTED-TEMPLATES \
    /usr/bin/python3 /usr/libexec/certmonger/cepces-submit \
    --server=win-ca01.example.com \
    --auth=Kerberos
```

## Debugging Kerberos Authentication

If you're having issues with Kerberos authentication, enable Kerberos tracing
by setting the `KRB5_TRACE` environment variable:

```bash
KRB5_TRACE=/dev/stderr \
    CERTMONGER_OPERATION=FETCH-ROOTS \
    /usr/bin/python3 /usr/libexec/certmonger/cepces-submit \
    --server=win-ca01.example.com \
    --auth=Kerberos
```

This will output detailed information about the Kerberos authentication
process, including:

- Credential cache lookups
- Ticket requests and responses
- Encryption type negotiations
- Service principal resolution

### Common Kerberos Issues

1. **No valid credentials** - Run `kinit` or verify your keytab is configured
2. **Clock skew** - Ensure system time is synchronized with the domain
3. **Wrong principal** - Use `--principals` to specify the correct principal
4. **Keytab issues** - Use `--keytab` to specify the keytab path

Example with keytab and principal:

```bash
KRB5_TRACE=/dev/stderr \
    CERTMONGER_OPERATION=FETCH-ROOTS \
    /usr/bin/python3 /usr/libexec/certmonger/cepces-submit \
    --server=win-ca01.example.com \
    --auth=Kerberos \
    --keytab=/etc/krb5.keytab \
    --principals='HOST/myhost.example.com@EXAMPLE.COM'
```

## Viewing Logs with journalctl

When running under systemd (via certmonger), view logs with:

```bash
journalctl -u certmonger -f
```

With debug logging enabled, you'll see the SOAP XML messages exchanged with
the AD CS server.
