==============================
CEP/CES Certificate Enrollment
==============================

``cepces`` is an application for enrolling certificates through CEP and CES.
For machine certificates, it requires `certmonger`_ to operate. For user
certifcates, it operates standalone.

Only simple deployments using Microsoft Active Directory Certificate Services
have been tested.

For more up-to-date information and further documentation, please visit the
project's home page at: https://github.com/openSUSE/cepces

Requirements
============

This application uses two SOAP endpoints over HTTPS provided by Microsoft
Active Directory Certificate Services. Your server needs to have the CEP/CES
SOAP API installed and configured.

The following authentication methods are supported:

* **Kerberos (GSSAPI)** - Requires the client to be a Windows Domain Member with
  a valid Kerberos keytab
* **Username and Password** - Allows authentication using domain credentials
* **Certificate** - Uses client certificates for authentication
* **Anonymous** - No authentication (for testing or specific deployments)

`cepces` is implemented in Python and requires at least Python 3.10 in order to
run, with all the required dependencies.

For credential management and secure password storage, `cepces` requires the
following system utilities:

* **keyutils** - Provides the `keyctl` utility for storing credentials in the
  Linux kernel keyring. This is the recommended method for secure credential
  storage. Install with:

  * Fedora/RHEL/CentOS: ``sudo dnf install keyutils``
  * Debian/Ubuntu: ``sudo apt install keyutils``
  * openSUSE: ``sudo zypper install keyutils``

* **pinentry** - Provides secure password prompting functionality (preferred).
  If pinentry is not available, `cepces` will automatically try to fall back to
  either ``kdialog`` or ``zenity``. Install pinentry with:

  * Fedora/RHEL/CentOS: ``sudo dnf install pinentry``
  * Debian/Ubuntu: ``sudo apt install pinentry-curses`` or ``pinentry-gtk2``
  * openSUSE: ``sudo zypper install pinentry``

These utilities are optional but highly recommended for production use. Without
them, credential storage and interactive password prompting will not be available.

Installation
============

``cepces`` is currently supported on any system with:

* Python 3.10 or later
* Python dependencies specified in ``pyproject.toml``
* `certmonger`_ (only for machine certifcates)

If available, it is recommended to use a repository for installing the
application and all dependencies. Please consult the project's wiki for more
information on what distributions are supported and have repositories provided.

Download and unpack a release tarball and issue this command from within the
extracted directory:

.. code-block:: bash

    # pip3 install .[user-submit]

Configuration
=============

Once installed, there is a configuration file that needs to be modified in
order for the certificate enrollment to function properly, possibly along with
some external modifications of system configuration files.

The configuration file should be available in the `/etc/cepces` directory,
possibly with a ".dist" extension. If that is the case drop the ".dist"
extension by either copying (or renaming) the file (i.e. ``cepces.conf.dist``
should be named ``cepces.conf``).

Alternatively, some configuration options can be specified from the command
line when adding a CA to `certmonger`_. For example:

.. code-block:: bash

    getcert add-ca -c CA-name -e '/usr/libexec/certmonger/cepces-submit --server=ca-dns-name.suse.de --keytab=/etc/krb5.keytab --principals=MY-HOST$@SUSE.DE'

cepces.conf
-----------

This is the main configuration file. It is fairly small and only requires two
settings to be changed (`server` or `endpoint`, and `cas`).

`endpoint` should be set to the CEP endpoint, whereas `cas` should point to a
directory containing all CA certificates in your chain (if the version of the
`python-requests` package is recent enough), or preferably a bundle file
containing all CA certificates in the chain.

Usage
=====

Requesting a Machine Certificate
--------------------------------

`certmonger`_ should have a CA already configured after the packages were
installed:

.. code-block:: bash

    # getcert list-cas
    ...
    CA 'cepces':
       is-default: no
       ca-type: EXTERNAL
       helper-location: /usr/libexec/certmonger/cepces-submit

Use this CA configuration as with any other. Please consult the official
`certmonger`_ documentation for instructions.

For detailed information on how cepces integrates with certmonger, including
all supported operations and usage examples, see `doc/CERTMONGER.md`_.

For references to the Microsoft protocol specifications (MS-XCEP, MS-WSTEP)
implemented by cepces, see `doc/PROTOCOLS.md`_.

.. _certmonger: https://pagure.io/certmonger
.. _doc/CERTMONGER.md: doc/CERTMONGER.md
.. _doc/PROTOCOLS.md: doc/PROTOCOLS.md

User Certificates
-----------------

User certificates are handled without ``certmonger`` by two standalone scripts:

* :code:`cepces-user`: a CLI tool for requesting certificates on demand
* :code:`cepces-user-autoenroll`: a daemon that automatically enrolls and
  renews certificates (similar to Windows auto-enrollment)

Both scripts require the ``user-submit`` optional dependencies (``pyasn1``).
Install them with:

.. code-block:: bash

    # pip3 install .[user-submit]

Both scripts also require a valid Kerberos ticket in the credential cache.
This is normally created automatically when logging in with a domain account
via `Winbind`_ or `SSSD`_. You can obtain a ticket manually with:

.. code-block:: bash

    $ kinit username@DOMAIN.TLD

Both scripts read settings from ``cepces.conf``. The ``[user]`` section
controls user-specific paths and behavior.

cepces-user
^^^^^^^^^^^

:code:`cepces-user` is a CLI tool for manually requesting user certificates
from AD CS. It supports three actions:

* ``list-templates`` — list the certificate templates available on the server
* ``request`` — generate a key (if needed) and submit a certificate signing
  request to the CA
* ``poll`` — poll the CA for a previously submitted request that is pending
  approval

If ``--server`` is not specified, the endpoint from ``cepces.conf`` is used.
The private key file is generated automatically if it does not already exist.

Options
"""""""

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description
   * - ``--server``
     - Hostname of the CA server (constructs the CEP endpoint URL automatically)
   * - ``--auth``
     - Authentication method: ``Kerberos`` (default), ``UsernamePassword``,
       ``Certificate``, ``Anonymous``
   * - ``--keytab``
     - Path to a Kerberos keytab file
   * - ``--principals``
     - Kerberos principals to try when requesting a ticket
   * - ``--openssl-seclevel``
     - OpenSSL security level override (e.g. ``1`` to allow SHA-1)
   * - ``-T`` / ``--profile``
     - Certificate template name (required for ``request``)
   * - ``-k`` / ``--keyfile``
     - Private key file; generated automatically if it does not exist
   * - ``-f`` / ``--certfile``
     - Output certificate file
   * - ``-s`` / ``--keysize``
     - RSA key size when generating a new key (default: ``4096``)
   * - ``-p`` / ``--passphrase``
     - Passphrase to decrypt an existing key or encrypt a newly generated one
   * - ``-i`` / ``--request-id``
     - Request ID returned when a request is pending approval (for ``poll``)
   * - ``-r`` / ``--reference``
     - CES endpoint URL returned when a request is pending approval (for ``poll``)

Examples
""""""""

.. code-block:: bash

    $ cepces-user list-templates
    User
    User with Approval
    .....

    $ cepces-user request -k key.pem -f cert.pem --profile "User"
    Certificate written to: cert.pem

    $ cepces-user request -k key.pem -f cert.pem --profile "User with Approval"
    Certificate approval pending. Poll later with the following info.
    Request ID: 111
    Reference: https://SERVERNAME/DOMAIN-DC-CA_CES_Kerberos/service.svc/CES

    ... later that day ...
    $ cepces-user poll -f cert.pem -i 111 -r https://SERVERNAME/DOMAIN-DC-CA_CES_Kerberos/service.svc/CES
    Certificate written to: cert.pem

cepces-user-autoenroll
^^^^^^^^^^^^^^^^^^^^^^

:code:`cepces-user-autoenroll` is a long-running process that automatically
enrolls and renews user certificates, similar to Windows auto-enrollment.
It is designed to be started at user login and runs until the session ends.

The process loops continuously, sleeping for ``poll_interval`` seconds (from
the ``[global]`` section of ``cepces.conf``) between iterations. On each
iteration it performs the following checks, in order:

1. **Pending request** — if a request file (``req_file``) exists, poll the CA
   for approval. On success the certificate is written and the request file
   is removed.
2. **Certificate due for renewal** — if the certificate file (``cert_file``)
   exists and expires within ``renew_days`` days, submit a new request.
3. **No certificate** — if no certificate file exists, request one from the CA.

Configure the ``[user]`` section in ``cepces.conf`` before using this script:

.. list-table::
   :header-rows: 1
   :widths: 20 50 30

   * - Option
     - Description
     - Default
   * - ``profile``
     - Certificate template name to request
     - ``User``
   * - ``key_file``
     - Path to the private key file
     - ``~/key.pem``
   * - ``cert_file``
     - Path where the certificate is written
     - ``~/cert.pem``
   * - ``req_file``
     - Path to the pending-request state file
     - ``~/cert.req``
   * - ``renew_days``
     - Renew the certificate when fewer than this many days remain
     - ``30``
   * - ``key_size``
     - RSA key size when generating a new key
     - ``4096``

To run :code:`cepces-user-autoenroll` automatically on login, install it as a
systemd user service. Create
``~/.config/systemd/user/cepces-user-autoenroll.service``:

.. code-block:: ini

    [Unit]
    Description=cepces user certificate auto-enrollment

    [Service]
    Type=simple
    ExecStart=cepces-user-autoenroll

    [Install]
    WantedBy=default.target

Then enable and start it:

.. code-block:: bash

    $ systemctl --user enable --now cepces-user-autoenroll.service

.. _SSSD: https://github.com/SSSD/sssd
.. _Winbind: https://samba.org/
