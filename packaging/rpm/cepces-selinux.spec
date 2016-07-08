%global app_name cepces
%global selinux_variants targeted

Name:           %{app_name}-selinux
Version:        0.2.0
Release:        1%{?dist}
Summary:        SELinux support for CEPCES

License:        GPLv3+
URL:            https://github.com/ufven/%{app_name}
Source0:        %{app_name}-%{version}.tar.gz
BuildArch:      noarch

Requires:          selinux-policy
Requires(post):    selinux-policy-targeted
BuildRequires:     selinux-policy-devel

%description
SELinux support for CEPCES.

%prep
%setup -q -n %{app_name}-%{version}

%build
# Build the SELinux module(s).
for SELINUXVARIANT in %{selinux_variants}
do
	make -C selinux clean all
	mv -v selinux/%{app_name}.pp \
		selinux/%{app_name}-${SELINUXVARIANT}.pp
done

%install
# Install the SELinux module(s).
for SELINUXVARIANT in %{selinux_variants}
do
	install -d %{buildroot}%{_datadir}/selinux/${SELINUXVARIANT}
	install -p -m 644 selinux/%{app_name}-${SELINUXVARIANT}.pp \
            %{buildroot}%{_datadir}/selinux/${SELINUXVARIANT}/%{app_name}.pp
done

%post
for SELINUXVARIANT in %{selinux_variants}
do
	%{_sbindir}/semodule -n -s ${SELINUXVARIANT} \
		-i %{_datadir}/selinux/${SELINUXVARIANT}/%{app_name}.pp

	if %{_sbindir}/selinuxenabled
	then
		%{_sbindir}/load_policy
	fi
done

%postun
if [ $1 -eq 0 ]
then
	for SELINUXVARIANT in %{selinux_variants}
	do
		%{_sbindir}/semodule -n -s ${SELINUXVARIANT} -r %{app_name} > /dev/null || :

		if %{_sbindir}/selinuxenabled
		then
			%{_sbindir}/load_policy
		fi
	done
fi

%check

%files
%defattr(0644,root,root,0755)
%{_datadir}/selinux

%changelog
* Mon Jun 27 2016 Daniel Uvehag - 0.2.0-1
- Initial package.
