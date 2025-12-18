# Certmonger Integration

This document explains how certmonger and cepces work together to automate
certificate enrollment from Microsoft Active Directory Certificate Services
(AD CS) on Linux systems.

## Overview

[Certmonger](https://pagure.io/certmonger) is a service that monitors
certificates, tracks their expiration, and automatically renews them before
they expire. It uses "CA helpers" (external programs) to communicate with
different Certificate Authorities.

cepces provides a CA helper called `cepces-submit` that enables certmonger to
request and renew certificates from Microsoft AD CS using the MS-XCEP
(Certificate Enrollment Policy) and MS-WSTEP (Certificate Enrollment via SOAP)
protocols.

## How It Works

```
+-------------+     environment      +---------------+      SOAP/HTTPS      +--------+
| certmonger  | ---- variables ----> | cepces-submit | ------------------> | AD CS  |
|   daemon    | <--- exit code ----- |   (helper)    | <------------------ | server |
|             | <--- stdout -------- |               |      XML response   |        |
+-------------+                      +---------------+                      +--------+
```

1. **Certmonger** calls `cepces-submit` with the operation type set in the
   `CERTMONGER_OPERATION` environment variable
2. **cepces-submit** reads the operation and any required data from environment
   variables (e.g., `CERTMONGER_CSR` for certificate signing requests)
3. **cepces** communicates with the AD CS server using SOAP over HTTPS
4. **cepces-submit** outputs results to stdout and returns an exit code that
   certmonger understands

## Environment Variables

Certmonger passes data to the helper via environment variables:

| Variable | Description |
|----------|-------------|
| `CERTMONGER_OPERATION` | The operation to perform (see below) |
| `CERTMONGER_CSR` | PEM-encoded Certificate Signing Request |
| `CERTMONGER_CERTIFICATE` | Existing certificate (for renewals) |
| `CERTMONGER_CA_COOKIE` | Cookie from a previous deferred request |
| `CERTMONGER_CA_PROFILE` | Certificate template name |

## Exit Codes

The helper returns these exit codes to certmonger:

| Code | Name | Meaning |
|------|------|---------|
| 0 | `ISSUED` / `DEFAULT` | Success (certificate issued or operation completed) |
| 1 | `WAIT` | Wait and retry later |
| 2 | `REJECTED` | Request was rejected |
| 3 | `CONNECTERROR` | Could not connect to the CA |
| 4 | `UNDERCONFIGURED` | Missing required configuration |
| 5 | `WAITMORE` | Wait longer, cookie provided for polling |
| 6 | `UNSUPPORTED` | Operation not supported |

## Operations

### IDENTIFY

Returns version information about the helper.

**Output:**
- Helper name and version (e.g., "cepces 0.3.12")

**Exit code:** `DEFAULT` (0)

### FETCH-ROOTS

Retrieves the CA certificate chain. This is useful for populating the trust
store with the CA certificates.

The operation queries the policy endpoint for CA certificates and follows the
Authority Information Access (AIA) extension to build the complete chain up to
the root CA.

**Output:**
- For each certificate in the chain: nickname (Common Name) followed by the
  PEM-encoded certificate

**Exit code:** `DEFAULT` (0)

**Note:** If the complete chain cannot be retrieved (e.g., missing AIA
extension), a partial chain is returned.

### GET-SUPPORTED-TEMPLATES

Returns a list of certificate templates available from the CA. This queries the
AD CS policy endpoint to retrieve all configured templates.

**Output:**
- One template name per line

**Exit code:** `DEFAULT` (0)

### GET-DEFAULT-TEMPLATE

Returns the default certificate template. Since MS-XCEP doesn't specify a
default template, this operation produces no output.

**Output:** (none)

**Exit code:** `DEFAULT` (0)

### GET-NEW-REQUEST-REQUIREMENTS

Returns the list of environment variables required for a new certificate
request.

**Output:**
- `CERTMONGER_CA_PROFILE` (the certificate template name)

**Exit code:** `DEFAULT` (0)

### GET-RENEW-REQUEST-REQUIREMENTS

Returns the list of environment variables required for a certificate renewal.

**Output:**
- `CERTMONGER_CA_PROFILE` (the certificate template name)

**Exit code:** `DEFAULT` (0)

### SUBMIT

Submits a new certificate signing request (CSR) to the CA.

**Required environment variables:**
- `CERTMONGER_CSR`: The PEM-encoded CSR

**Optional environment variables:**
- `CERTMONGER_CERTIFICATE`: If present, indicates this is a renewal request

**Output:**
- On success: The issued certificate in PEM format
- On deferral: Poll interval and a cookie (request_id,reference) for later polling

**Exit codes:**
- `ISSUED` (0): Certificate was issued immediately
- `WAITMORE` (5): Request is pending, poll later using the cookie
- `REJECTED` (2): Request was rejected by the CA

### POLL

Polls the status of a previously deferred certificate request.

**Required environment variables:**
- `CERTMONGER_CA_COOKIE`: The cookie returned from a previous SUBMIT or POLL

**Output:**
- On success: The issued certificate in PEM format
- On deferral: Poll interval and updated cookie

**Exit codes:**
- `ISSUED` (0): Certificate was issued
- `WAITMORE` (5): Still pending, poll again later
- `REJECTED` (2): Request was rejected

## Usage with Certmonger

### Verifying the CA is Configured

After installation, certmonger should have the cepces CA configured:

```bash
$ getcert list-cas
...
CA 'cepces':
   is-default: no
   ca-type: EXTERNAL
   helper-location: /usr/libexec/certmonger/cepces-submit
```

### Adding the CA

```bash
getcert add-ca -c cepces -e /usr/libexec/certmonger/cepces-submit
```

You can also pass configuration options directly:

```bash
getcert add-ca -c cepces -e '/usr/libexec/certmonger/cepces-submit \
    --server=ca.example.com \
    --keytab=/etc/krb5.keytab \
    --principals=HOST/myhost.example.com@EXAMPLE.COM'
```

### Requesting a Certificate

```bash
getcert request -c cepces -T Machine \
    -k /etc/pki/tls/private/machine.key \
    -f /etc/pki/tls/certs/machine.crt
```

With a request ID for easier tracking:

```bash
$ getcert request -c cepces -T Machine -I MachineCertificate \
    -k /etc/pki/tls/private/machine.key \
    -f /etc/pki/tls/certs/machine.crt
New signing request "MachineCertificate" added.
```

### Checking Status

```bash
getcert list -c cepces
```

While submitting:

```
Request ID 'MachineCertificate':
        status: SUBMITTING
        stuck: no
        key pair storage: type=FILE,location='/etc/pki/tls/private/machine.key'
        certificate: type=FILE,location='/etc/pki/tls/certs/machine.crt'
        CA: cepces
```

After the certificate is issued:

```
Request ID 'MachineCertificate':
        status: MONITORING
        stuck: no
        key pair storage: type=FILE,location='/etc/pki/tls/private/machine.key'
        certificate: type=FILE,location='/etc/pki/tls/certs/machine.crt'
        CA: cepces
        issuer: CN=My CA
        subject: CN=myhost.example.com
        expires: 2025-08-15 17:37:02 UTC
        certificate template/profile: Machine
        track: yes
        auto-renew: yes
```

## Configuration

cepces reads its configuration from:

- `/etc/cepces/cepces.conf` - Main configuration file
- `/etc/cepces/logging.conf` - Logging configuration

See the main documentation for configuration options including:

- AD CS server endpoint
- Authentication method (Kerberos, Certificate, etc.)
- Kerberos keytab and principal settings
- Poll interval for deferred requests
