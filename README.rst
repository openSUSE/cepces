==============================
CEP/CES Certificate Enrollment
==============================

``cepces`` is an application for enrolling certificates through CEP and CES. It
requires `certmonger`_ to operate.

Only simple deployments using Microsoft Active Directory Certificate Services
have been tested.

For more up-to-date information and further documentation, please visit the
project's home page at: https://github.com/openSUSE/cepces

Requirements
============

This application uses two SOAP endpoints over HTTPS provided by Microsoft
Active Directory Certificate Services. The following authentication methods are
supported:

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

``cepces`` is currently supported on any system running `certmonger`_. It
requires Python 3.10 or later.

If available, it is recommended to use a repository for installing the
application and all dependencies. Please consult the project's wiki for more
information on what distributions are supported and have repositories provided.

Download and unpack a release tarball and issue this command from within the
extracted directory:

.. code-block:: bash

    # pip3 install .

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

.. _certmonger: https://pagure.io/certmonger
.. _doc/CERTMONGER.md: doc/CERTMONGER.md
