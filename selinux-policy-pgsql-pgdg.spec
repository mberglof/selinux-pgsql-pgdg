%global selinux_variants targeted
%global selinux_policyver 3.7.19
%global modulename postgresql-pgdg

Name: selinux-policy-pgsql-pgdg
Version: 1.0.0
Release: 1
Summary: SELinux policy module for PostgreSQL from the PGDG
License: PostgreSQL
Group: System Environment/Base
Url: http://github.com/dalibo/selinux-pgsql-pgdg

Source1: %{modulename}.if
Source2: %{modulename}.te
Source3: %{modulename}.fc
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires: selinux-policy >= %{selinux_policyver}
Requires(post):   /usr/sbin/semodule, /sbin/restorecon
Requires(postun): /usr/sbin/semodule, /sbin/restorecon

%description
SELinux policy module for PostgreSQL packages provided by the
PGDG. This module adds the file contexts needed to confine a
PostgreSQL cluster.

%prep
cp -p %{SOURCE1} %{SOURCE2} %{SOURCE3} ./

%build
for selinuxvariant in %{selinux_variants}
do
  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile
  mv %{modulename}.pp %{modulename}.pp.${selinuxvariant}
  make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile clean
done

%install
for selinuxvariant in %{selinux_variants}
do
  install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
  install -p -m 644 %{modulename}.pp.${selinuxvariant} \
    %{buildroot}%{_datadir}/selinux/${selinuxvariant}/%{modulename}.pp
done

%clean
rm -rf %{buildroot}

%post
for selinuxvariant in %{selinux_variants}
do
    /usr/sbin/semodule -s ${selinuxvariant} -u \
	%{_datadir}/selinux/${selinuxvariant}/%{modulename}.pp &> /dev/null || :
done
/sbin/restorecon -R /etc/rc.d/init.d/ /usr/pgsql-*/*

%postun
if [ $1 -eq 0 ] ; then
  for selinuxvariant in %{selinux_variants}
  do
     /usr/sbin/semodule -s ${selinuxvariant} -r %{modulename} &> /dev/null || :
  done
  /sbin/restorecon -R /etc/rc.d/init.d/ /usr/pgsql-*/*
fi

%files
%defattr(-,root,root,0755)
%{_datadir}/selinux/*/%{modulename}.pp

%changelog
* Mon Sep 22 2014 Nicolas Thauvin <nicolas.thauvin@dalibo.com> 1.0.0-1
- Initial version
