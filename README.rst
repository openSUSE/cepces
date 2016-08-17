==============================
CEP/CES Certificate Enrollment
==============================

``cepces`` is an application for enrolling certificates through CEP and CES. It
currently requires `certmonger`_ to operate, but may eventually be extended to
a standalone application

Only simple deployments using Microsoft Active Directory Certificate Services
has been tested.

For more up-to-date information and further documentation, please visit the
project's home page at: https://github.com/ufven/cepces

Requirements
============

This application uses two SOAP endpoints over HTTPS provided by Microsoft
Active Directory Certificate Services. Currently, only Kerberos authentication
is supported. Therefore, the client has to be a Windows Domain Member with a
valid Kerberos keytab.

`cepces` is implemented in Python and requires at least Python 3.4 in order to
run, with all the required dependencies.

Installation
============

``cepces`` is currently supported on any system (well, not really) with:

* Python 3.4 or later
* Python dependencies specified in ``requirements.txt``
* `certmonger`_

If available, it is recommended to use a repository for installing the
application and all dependencies. Please consult the project's wiki for more
information on what distributions are supported and have repositories provided.

Download and unpack a release tarball and issue these commands from within the
extracted directory:

.. code-block:: bash

    # pip3 install -r requirements.txt
    # python3 setup.py install

Configuration
=============

Once installed, there are two configuration files that need to be modified in
order for the certificate enrollment to function properly, possibly along with
some external modifications of system configuration files.

Both configuration files should be available in the `/etc/cepces` directory,
possibly with a ".dist" extension. If that is the case drop the ".dist"
extension by either copying (or renaming) those files (i.e. ``cepces.conf.dist``
should be named ``cepces.conf`` and ``cepces-submit.conf.dist`` should be named
``cepces-submit.conf``).

cepces.conf
-----------

This is the main configuration file. It is fairly small and only requires two
settings to be changed (`endpoint` and `cas`).

`endpoint` should be set to the CEP endpoint, whereas `cas` should point to a
directory containing all CA certificates in your chain (if the version of the
`python-requests` package is recent enough), or preferably a bundle file
containing all CA certificates in the chain.

cepces-submit.conf
------------------

This configuration file is used by the certmonger helper. The defaults should
be sane enough, with the exception of `KINIT_REALM`. If no default realm is set
in `/etc/krb5.conf`, this value has to be set in `cepces-submit.conf` or the
application may fail when obtaining a ticket-granting ticket (TGT).

Usage
=====

`certmonger` should have a CA already configured after the packages were
installed:

.. code-block:: bash

    # getcert list-cas
    ...
    CA 'cepces':
       is-default: no
       ca-type: EXTERNAL
       helper-location: /usr/sbin/cepces-submit

Use this CA configuration as with any other. Please consult the official
`certmonger`_ documentation for instructions.

Example: Requesting a Machine Certificate
-----------------------------------------

If the current workstation is entitled to enroll "Workstation certificates" from
a CA (with the identifier ``Machine``), use the following command to issue and
track a new certificate:

.. code-block:: bash

    # getcert request -c cepces -T Machine -I MachineCertificate -k /etc/pki/tls/private/machine.key -f /etc/pki/tls/certs/machine.crt
    New signing request "MachineCertificate" added.

The certificate should now be submitted to the CA. Verify the progress with:

.. code-block:: bash

    # getcert list
    Number of certificates and requests being tracked: 1.
    Request ID 'MachineCertificate':
            status: SUBMITTING
            stuck: no
            key pair storage: type=FILE,location='/etc/pki/tls/private/machine.key'
            certificate: type=FILE,location='/etc/pki/tls/certs/machine.crt'
            CA: cepces
            issuer: 
            subject: 
            expires: unknown
            pre-save command: 
            post-save command: 
            track: yes
            auto-renew: yes
    
After a few moments when the CA has successfully processed the request, the
certificate should be issued and monitored by certmonger:

.. code-block:: bash

    # getcert list
    Number of certificates and requests being tracked: 1.
    Request ID 'MachineCertificate':
            status: MONITORING
            stuck: no
            key pair storage: type=FILE,location='/etc/pki/tls/private/machine.key'
            certificate: type=FILE,location='/etc/pki/tls/certs/machine.crt'
            CA: cepces
            issuer: CN=<My CA>
            subject: CN=<my hostname>
            expires: 2017-08-15 17:37:02 UTC
            dns: <my hostname>
            key usage: digitalSignature,keyEncipherment
            eku: id-kp-clientAuth,id-kp-serverAuth
            certificate template/profile: Machine
            pre-save command: 
            post-save command: 
            track: yes
            auto-renew: yes


.. _certmonger: https://fedorahosted.org/certmonger/
