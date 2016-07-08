%global app_name cepces

Name:           %{app_name}
Version:        0.2.0
Release:        1%{?dist}
Summary:        Certificate Enrollment through CEP/CES

License:        GPLv3+
URL:            https://github.com/ufven/%{app_name}
Source0:        %{app_name}-%{version}.tar.gz
BuildArch:      noarch

Requires:       cepces-selinux
Requires:       certmonger
Requires:       python%{python3_pkgversion}-cepces

%description
CEPCES is an application for enrolling certificates through CEP and CES.

%prep
%setup -q -n %{app_name}-%{version}

%build

%install
install -d %{buildroot}%{_sysconfdir}/%{app_name}
install -p -m 644 conf/cepces.conf.dist \
	%{buildroot}%{_sysconfdir}/%{app_name}/cepces.conf
install -p -m 644 conf/cepces-submit.conf.dist \
	%{buildroot}%{_sysconfdir}/%{app_name}/cepces-submit.conf

install -d %{buildroot}%{_sbindir}
install -p -m 755 bin/cepces %{buildroot}%{_sbindir}/cepces
install -p -m 755 bin/cepces-submit %{buildroot}%{_sbindir}/cepces-submit

%post
# Install the CA into certmonger.
getcert add-ca -c %{app_name} -e %{_sbindir}/cepces-submit >/dev/null

%postun
# Remove the CA from certmonger.
getcert remove-ca -c %{app_name} >/dev/null

%check

%files
%doc LICENSE
%dir %{_sysconfdir}/%{app_name}/
%config %{_sysconfdir}/%{app_name}/cepces.conf
%config %{_sysconfdir}/%{app_name}/cepces-submit.conf
%{_sbindir}/cepces
%{_sbindir}/cepces-submit

%changelog
* Mon Jun 27 2016 Daniel Uvehag - 0.1.0-1
- Initial package.
