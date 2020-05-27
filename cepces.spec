%global app_name cepces
%global selinux_variants targeted
%global logdir %{_localstatedir}/log/%{app_name}

Name:           %{app_name}
Version:        0.3.3
Release:        2%{?dist}
Summary:        Certificate Enrollment through CEP/CES

License:        GPLv3+
URL:            https://github.com/ufven/%{app_name}
Source0:        https://github.com/ufven/%{app_name}/archive/v%{version}/%{app_name}-%{version}.tar.gz
BuildArch:      noarch

Requires:       python%{python3_pkgversion}-%{app_name} == %{version}
Requires:       %{app_name}-certmonger == %{version}
Requires:       %{app_name}-selinux == %{version}

%description
%{app_name} is an application for enrolling certificates through CEP and CES.
It currently only operates through certmonger.

%package -n python%{python3_pkgversion}-%{app_name}
Summary:        Python part of %{app_name}

BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  python%{python3_pkgversion}-cryptography >= 1.2
BuildRequires:  python%{python3_pkgversion}-requests
BuildRequires:  python%{python3_pkgversion}-requests-kerberos >= 0.9

Requires:       python%{python3_pkgversion}-cryptography >= 1.2
Requires:       python%{python3_pkgversion}-requests
Requires:       python%{python3_pkgversion}-requests-kerberos >= 0.9

%description -n python%{python3_pkgversion}-%{app_name}
%{app_name} is an application for enrolling certificates through CEP and CES.
This package provides the Python part for CEP and CES interaction.

%package certmonger
Summary:        certmonger integration for %{app_name}

Requires:       certmonger

%description certmonger
%{app_name} is an application for enrolling certificates through CEP and CES.
This package provides the certmonger integration.

%package selinux
Summary:        SELinux support for %{app_name}

BuildRequires:  selinux-policy-devel

Requires:       selinux-policy
Requires(post): selinux-policy-targeted

%description selinux
SELinux support for %{app_name}

%prep
%setup -q -n %{app_name}-%{version}

%build
%py3_build

# Build the SELinux module(s).
for SELINUXVARIANT in %{selinux_variants}; do
  make -C selinux clean all
  mv -v selinux/%{app_name}.pp selinux/%{app_name}-${SELINUXVARIANT}.pp
done

%install
%py3_install

install -d -m 0700 %{buildroot}%{logdir}

# Install the SELinux module(s).
rm -fv selinux-files.txt

for SELINUXVARIANT in %{selinux_variants}; do
  install -d %{buildroot}%{_datadir}/selinux/${SELINUXVARIANT}
  install -p -m 644 selinux/%{app_name}-${SELINUXVARIANT}.pp \
    %{buildroot}%{_datadir}/selinux/${SELINUXVARIANT}/%{app_name}.pp

  echo %{_datadir}/selinux/${SELINUXVARIANT}/%{app_name}.pp >> \
    selinux-files.txt
done

# Install configuration files.
install -d %{buildroot}%{_sysconfdir}/%{app_name}
install -p -m 644 conf/cepces.conf.dist \
  %{buildroot}%{_sysconfdir}/%{app_name}/cepces.conf
install -p -m 644 conf/logging.conf.dist \
  %{buildroot}%{_sysconfdir}/%{app_name}/logging.conf

install -d %{buildroot}%{_libexecdir}/certmonger
install -p -m 755 bin/%{app_name}-submit \
  %{buildroot}%{_libexecdir}/certmonger/%{app_name}-submit

# Remove unused executables and configuration files.
%{__rm} -rfv %{buildroot}/usr/local/etc
%{__rm} -rfv %{buildroot}/usr/local/libexec/certmonger

%post selinux
for SELINUXVARIANT in %{selinux_variants}; do
  %{_sbindir}/semodule -n -s ${SELINUXVARIANT} \
    -i %{_datadir}/selinux/${SELINUXVARIANT}/%{app_name}.pp

  if %{_sbindir}/selinuxenabled; then
    %{_sbindir}/load_policy
  fi
done

%postun selinux
if [ $1 -eq 0 ]
then
  for SELINUXVARIANT in %{selinux_variants}; do
    %{_sbindir}/semodule -n -s ${SELINUXVARIANT} -r %{app_name} > /dev/null || :

    if %{_sbindir}/selinuxenabled; then
      %{_sbindir}/load_policy
    fi
  done
fi

%post certmonger
# Install the CA into certmonger.
if [[ "$1" == "1" ]]; then
  getcert add-ca -c %{app_name} \
    -e %{_libexecdir}/certmonger/%{app_name}-submit >/dev/null || :
fi

%preun certmonger
# Remove the CA from certmonger, unless it's an upgrade.
if [[ "$1" == "0" ]]; then
  getcert remove-ca -c %{app_name} >/dev/null || :
fi

%check
%{__python3} setup.py test

%files
%doc LICENSE
%doc README.rst
%dir %{_sysconfdir}/%{app_name}/
%config(noreplace) %{_sysconfdir}/%{app_name}/%{app_name}.conf
%config(noreplace) %{_sysconfdir}/%{app_name}/logging.conf
%dir %{logdir}

%files -n python%{python3_pkgversion}-%{app_name}
%{python3_sitelib}/%{app_name}
%{python3_sitelib}/%{app_name}-%{version}-py?.?.egg-info

%files certmonger
%{_libexecdir}/certmonger/%{app_name}-submit

%files selinux -f selinux-files.txt
%defattr(0644,root,root,0755)

%changelog
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
