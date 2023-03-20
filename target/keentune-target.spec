%define anolis_release 2

Name:           keentune-target
Version:        2.0.1
Release:        %{?anolis_release}%{?dist}
Url:            https://gitee.com/anolis/keentune_target
Summary:        Parameters setting, reading and backup models for KeenTune
Vendor:         Alibaba
License:        MulanPSLv2
Group:          Development/Languages/Python
Source:         %{name}-%{version}.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BUildRequires:	systemd

BuildArch:      noarch

Requires:       python3-tornado, python3-pyudev
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
Parameters setting, reading and backup models for KeenTune

%prep
%autosetup -n %{name}-%{version}

%build
%{__python3} setup.py build

%install
%{__python3} setup.py install --single-version-externally-managed -O1 --prefix=%{_prefix} --root=%{buildroot} --record=INSTALLED_FILES
mkdir -p ${RPM_BUILD_ROOT}/usr/lib/systemd/system/
mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/keentune/script
cp -f ./keentune-target.service ${RPM_BUILD_ROOT}/usr/lib/systemd/system/
install -D -m 0644 man/keentune-target.domain.7 ${RPM_BUILD_ROOT}%{_mandir}/man7/keentune-target.domain.7
install -D -m 0644 man/keentune-target.8 ${RPM_BUILD_ROOT}%{_mandir}/man8/keentune-target.8
install -D -m 0644 man/keentune-target.conf.5 ${RPM_BUILD_ROOT}%{_mandir}/man5/keentune-target.conf.5
install -D -m 0755 agent/scripts/cpu-partitioning.sh ${RPM_BUILD_ROOT}%{_sysconfdir}/keentune/script
install -D -m 0755 agent/scripts/powersave.sh ${RPM_BUILD_ROOT}%{_sysconfdir}/keentune/script
install -D -m 0755 agent/scripts/realtime.sh ${RPM_BUILD_ROOT}%{_sysconfdir}/keentune/script
install -D -m 0755 agent/scripts/spindown-disk.sh ${RPM_BUILD_ROOT}%{_sysconfdir}/keentune/script
install -D -m 0755 agent/scripts/tuned-pre-udev.sh ${RPM_BUILD_ROOT}%{_sysconfdir}/keentune/script
install -D -m 0755 agent/scripts/functions ${RPM_BUILD_ROOT}%{_sysconfdir}/keentune/script

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post keentune-target.service

%preun
%systemd_preun keentune-target.service

%postun
%systemd_postun keentune-target.service

%files -f INSTALLED_FILES
%defattr(-,root,root)
%license LICENSE
%{_prefix}/lib/systemd/system/keentune-target.service
%{_mandir}/man7/keentune-target.domain.7*
%{_mandir}/man8/keentune-target.8*
%{_mandir}/man5/keentune-target.conf.5*
%{_sysconfdir}/keentune/script/cpu-partitioning.sh
%{_sysconfdir}/keentune/script/powersave.sh
%{_sysconfdir}/keentune/script/realtime.sh
%{_sysconfdir}/keentune/script/spindown-disk.sh
%{_sysconfdir}/keentune/script/tuned-pre-udev.sh
%{_sysconfdir}/keentune/script/functions

%changelog
* Mon Jan 16 2023 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 2.0.1-2
- modify default domain to sysctl, net
- add requires of 'pyudev'
- remove disk config param 'apm' and 'spindown'

* Thu Dec 15 2022 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 2.0.1-1
- disable backup all and rollback all in this version
- modify xps/rps code of param value 'different'
- init partial domain when target start

* Thu Dec 15 2022 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 2.0.0-0
- add tuned domain
- add basic domain class 
- add basic benchmark domain class
- modify installation directory

* Mon Oct 31 2022 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 1.4.0-1
- fix: domain 'my_cnf' actived without mysql sevice
- fix: fix the problem that cannot be rolled back normally

* Mon Oct 17 2022 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 1.3.3-1
- fix: interrupts bonding because of virtio2/virtio3
- fix: service type to 'forking' from 'simple'

* Thu Jul 21 2022 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 1.3.2-0
- fix some bugs

* Thu Jul 21 2022 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 1.3.0-1
- fix: missing of man dir  

* Thu Jun 30 2022 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 1.3.0-0
- rename target to agent
- add RESTful API /available
- refactor original configuration backup

* Mon Jun 20 2022 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 1.2.1-1
- update docs
- fix bug: tuning stoped because of serival knobs setting failed.

* Mon Apr 04 2022 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 1.2.0-2
- Wrong version index in python
- Control checking range of settable target for 'profile set'
- add function of all rollback

* Thu Mar 03 2022 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 1.1.0-2
- fix bug: update version to 1.1.0 in setup.py script.

* Thu Mar 03 2022 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 1.1.0-1
- Add support for GP (in iTuned) in sensitizing algorithms
- Add support for lasso in sensitizing algorithms
- refactor tornado module: replace await by threadpool
- lazy load domain in keentune-target
- fix other bugs

* Sat Jan 01 2022 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 1.0.1-1
- Verify input arguments of command 'param tune'
- Supporting of multiple target tuning
- Fix bug which cause keentune hanging after command 'param stop'
- Add verification of conflicting commands such as 'param dump', 'param delete' when a tuning job is runing.
- Remove version limitation of tornado
- Refactor sysctl domain to improve stability of parameter setting
- Fix some user experience issues

* Sun Dec 12 2021 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 1.0.0-5
- fix bug: can not running in alinux2 and centos7
- change modify codeup address to gitee

* Wed Dec 01 2021 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 1.0.0-4
- add keentune to systemd

* Wed Nov 24 2021 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 1.0.0-3
- fix: wrong license in setup.py
- add nginx conf parameter domain

* Wed Nov 10 2021 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 1.0.0-2
- use '%license' macro
- update license to MulanPSLv2

* Wed Aug 18 2021 Runzhe Wang <runzhe.wrz@alibaba-inc.com> - 1.0.0-1
- Initial KeenTune-target
