%global selinux_variants targeted
%global logdir %{_localstatedir}/log/%{name}
%global modulename %{name}
%global selinux_package_dir %{_datadir}/selinux/packages

Name:           cepces
Version:        0.3.5
Release:        3%{?dist}
Summary:        Certificate Enrollment through CEP/CES

License:        GPLv3+
URL:            https://github.com/openSUSE/%{name}
Source0:        https://github.com/openSUSE/%{name}/archive/v%{version}/%{name}-%{version}.tar.gz

# cepces.conf.dist: server should be pointed to actual CEP host
# https://github.com/openSUSE/cepces/issues/15
# Merged to master after ver 0.3.5
Patch0:         https://patch-diff.githubusercontent.com/raw/openSUSE/%{name}/pull/16.patch

# Use /usr/libexec and /etc instead
Patch1:         https://patch-diff.githubusercontent.com/raw/openSUSE/%{name}/pull/17.patch
BuildArch:      noarch

Requires:       python%{python3_pkgversion}-%{name} == %{version}
Requires:       %{name}-certmonger == %{version}
Requires:       %{name}-selinux == %{version}

Suggests:       logrotate

%description
cepces is an application for enrolling certificates through CEP and CES.
It requires certmonger to operate.

Only simple deployments using Microsoft Active Directory Certificate Services
have been tested.

%package -n python%{python3_pkgversion}-%{name}
Summary:        Python part of %{name}

BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(cryptography) >= 1.2
BuildRequires:  python3dist(requests)
BuildRequires:  python3dist(requests-kerberos) >= 0.9
BuildRequires:  python3-devel

Requires:       python3dist(setuptools)
Requires:       python3dist(cryptography) >= 1.2
Requires:       python3dist(requests)

%description -n python%{python3_pkgversion}-%{name}
%{name} is an application for enrolling certificates through CEP and CES.
This package provides the Python part for CEP and CES interaction.

%package certmonger
Summary:        certmonger integration for %{name}

Requires:       certmonger

%description certmonger
Installing %{name}-certmonger adds %{name} as a CA configuration.
Uninstall revert the action.

%package selinux
Summary:        SELinux support for %{name}

BuildRequires:  selinux-policy-devel

Requires:       selinux-policy
Requires(post): selinux-policy-targeted

%description selinux
SELinux support for %{name}

%prep
%autosetup -p1

%build
%py3_build

# Build the SELinux module(s).
for SELINUXVARIANT in %{selinux_variants}; do
  make -C selinux clean all
  mv -v selinux/%{name}.pp selinux/%{name}-${SELINUXVARIANT}.pp
done

%install
%py3_install

install -d  %{buildroot}%{logdir}

# Install the SELinux module(s).
rm -fv selinux-files.txt

for SELINUXVARIANT in %{selinux_variants}; do
  install -d -m 755 %{buildroot}%{selinux_package_dir}/${SELINUXVARIANT}
  bzip2 selinux/%{name}-${SELINUXVARIANT}.pp
  MODULE_PATH=%{selinux_package_dir}/${SELINUXVARIANT}/%{modulename}.pp.bz2
  install -p -m 644 selinux/%{name}-${SELINUXVARIANT}.pp.bz2 \
    %{buildroot}$MODULE_PATH

  echo $MODULE_PATH >> selinux-files.txt
done

# Configuration files
install -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/
install -m 644  conf/cepces.conf.dist  %{buildroot}%{_sysconfdir}/%{name}/cepces.conf
install -m 644  conf/logging.conf.dist %{buildroot}%{_sysconfdir}/%{name}/logging.conf

# Default logrotate file
install -d -m 0755 %{buildroot}%{_sysconfdir}/logrotate.d
cat <<EOF>%{buildroot}%{_sysconfdir}/logrotate.d/%{name}
/var/log/%{name}/*.log {
    compress
    delaycompress
    missingok
    rotate 4
}
EOF

%pre selinux
for SELINUXVARIANT in %{selinux_variants}; do
  %selinux_relabel_pre -s %{SELINUXVARIANT}
done

%post selinux
semodule -d %{modulename} &> /dev/null || true;
for SELINUXVARIANT in %{selinux_variants}; do
  MODULE_PATH=%{selinux_package_dir}/${SELINUXVARIANT}/%{modulename}.pp.bz2
  %selinux_modules_install -s %{SELINUXVARIANT} ${MODULE_PATH}
done

%postun selinux
if [ $1 -eq 0 ]; then
  for SELINUXVARIANT in %{selinux_variants}; do
    %selinux_modules_uninstall -s %{SELINUXVARIANT} %{modulename}
    semodule -e %{modulename}  &> /dev/null || true;
  done
fi

%posttrans selinux
for SELINUXVARIANT in %{selinux_variants}; do
  %selinux_relabel_post -s %{SELINUXVARIANT}
done

%post certmonger
# Install the CA into certmonger.
if [[ "$1" == "1" ]]; then
  getcert add-ca -c %{name} \
    -e %{_libexecdir}/certmonger/%{name}-submit >/dev/null || :
fi

%preun certmonger
# Remove the CA from certmonger, unless it's an upgrade.
if [[ "$1" == "0" ]]; then
  getcert remove-ca -c %{name} >/dev/null || :
fi

%check
# Create a symlink so test can locate cepces_test
ln -s tests/cepces_test .
%{__python3} setup.py test

%files
%license LICENSE
%doc README.rst
%dir %{_sysconfdir}/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}/logging.conf
%attr(0700,-,-) %dir %{logdir}
%dir %{_sysconfdir}/logrotate.d
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}

%files -n python%{python3_pkgversion}-%{name}
%{python3_sitelib}/%{name}
%{python3_sitelib}/%{name}-%{version}-py?.*.egg-info

%files certmonger
%{_libexecdir}/certmonger/%{name}-submit

%files selinux -f selinux-files.txt
%defattr(0644,root,root,0755)

%changelog
* Thu Jun 23 2022 Ding-Yi Chen <dchen@redhat.com> - 0.3.5-3
- Review comment #4 addressed

* Wed Jun 22 2022 Ding-Yi Chen <dchen@redhat.com> - 0.3.5-2
- Review comment #1 addressed

* Thu Jun 16 2022 Ding-Yi Chen <dchen@redhat.com> - 0.3.5-1
- Initial import to Fedora
- Add logrotate
- Applied patch for https://github.com/openSUSE/cepces/issues/15

* Fri Oct 01 2021 Daniel Uvehag <daniel.uvehag@gmail.com> - 0.3.4-1
- Fix collections deprecation

* Fri Oct 01 2021 Daniel Uvehag <daniel.uvehag@gmail.com> - 0.3.4-1
- Fix collections deprecation

* Mon Jul 29 2019 Daniel Uvehag <daniel.uvehag@gmail.com> - 0.3.3-2
- Add missing log directory

* Mon Jul 29 2019 Daniel Uvehag <daniel.uvehag@gmail.com> - 0.3.3-1
- Update to version 0.3.3-1

* Mon Feb 05 2018 Daniel Uvehag <daniel.uvehag@gmail.com> - 0.3.0-1
- Update to version 0.3.0-1

* Thu Feb 01 2018 Daniel Uvehag <daniel.uvehag@gmail.com> - 0.2.1-1
- Update to version 0.2.1-1

* Mon Jun 27 2016 Daniel Uvehag <daniel.uvehag@gmail.com> - 0.1.0-1
- Initial package.
