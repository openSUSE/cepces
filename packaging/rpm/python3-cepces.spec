%global app_name cepces

Name:           python%{python3_pkgversion}-%{app_name}
Version:        0.2.0
Release:        1%{?dist}
Summary:        Certificate Enrollment through CEP/CES

License:        GPLv3+
URL:            https://github.com/ufven/%{app_name}
Source0:        %{app_name}-%{version}.tar.gz
BuildArch:      noarch

Requires:       python%{python3_pkgversion}-cement >= 2.8
Requires:       python%{python3_pkgversion}-requests
Requires:       python%{python3_pkgversion}-requests-kerberos

BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools

%{?python_provide:%python_provide python%{python3_pkgversion}-%{app_name}}

%description
CEPCES is an application for enrolling certificates through CEP and CES. This
package provides the Python library for CEP and CES interaction.

%prep
%setup -n %{app_name}-%{version}

%build
%py3_build

%install
%py3_install

%check
%{__python3} setup.py test

%files
%doc README.rst LICENSE
%{python3_sitelib}/%{app_name}
%{python3_sitelib}/%{app_name}-%{version}-py?.?.egg-info

%changelog
* Mon Jul 04 2016 Daniel Uvehag - 0.2.0-1
- Initial package.
