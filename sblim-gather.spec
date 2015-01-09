# TODO: PLDify init script
#
# Conditional build:
%bcond_without	static_libs	# don't build static libraries
#
Summary:	SBLIM Performance Data Gatherer and Provider
Summary(pl.UTF-8):	Narzędzie SBLIM do zbierania i dostarczania danych o wydajności
Name:		sblim-gather
Version:	2.2.9
Release:	1
License:	Eclipse Public License v1.0
Group:		Libraries
Source0:	http://downloads.sourceforge.net/sblim/%{name}-%{version}.tar.bz2
# Source0-md5:	9525751f776fe3579cd17a5d00e67f00
URL:		http://sblim.sourceforge.net/
BuildRequires:	libvirt-devel
BuildRequires:	sblim-cmpi-devel
BuildRequires:	sblim-cmpi-base-devel
BuildRequires:	sysfsutils-devel
BuildRequires:	xmlto
Requires:	%{name}-libs = %{version}-%{release}
Requires:	sblim-cmpi-base
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# hiccup symbol is provided by binary
%define		skip_post_check_so	libgather.so.*

%description
The purpose of this package is to implement the DMTF CIM Metrics Model
for Linux, making it available via a CIMOM supporting/supported by the
CMPI provider interface. 

The package consists of three parts:
1. The Gatherer Component
2. The Metric Plugins
3. The Performance Data Providers

%description -l pl.UTF-8
Ten pakiet ma być implementacją specyfikacji DMTF CIM Metrics Model
(modelu metryk CIM DMTF) dla Linuksa, udostępniając ją poprzez demon
CIMOM obsługujący interfejs dostarczycieli CMPI.

Pakiet składa się z trzech elementów:
1. Zbierającego dane (Gatherera)
2. Wtyczek metryk
3. Dostarczycieli danych o wydajności

%package libs
Summary:	SBLIM Gatherer shared libraries
Summary(pl.UTF-8):	Biblioteki współdzielone SBLIM Gatherera
Group:		Libraries

%description libs
SBLIM Gatherer shared libraries.

%description libs -l pl.UTF-8
Biblioteki współdzielone SBLIM Gatherera.

%package devel
Summary:	Header files for SBLIM Gatherer libraries
Summary(pl.UTF-8):	Pliki nagłówkowe bibliotek SBLIM Gatherera
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Requires:	sysfsutils-devel

%description devel
Header files for SBLIM Gatherer libraries.

%description devel -l pl.UTF-8
Pliki nagłówkowe bibliotek SBLIM Gatherera.

%package static
Summary:	SBLIM Gatherer static libraries
Summary(pl.UTF-8):	Biblioteki statyczne SBLIM Gatherera
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
SBLIM Gatherer static libraries.

%description static -l pl.UTF-8
Biblioteki statyczne SBLIM Gatherera.

%prep
%setup -q

%build
%configure \
	%{?with_static_libs:--enable-static} \
	--enable-z

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -j1 install \
	DESTDIR=$RPM_BUILD_ROOT \
	initdir=/etc/rc.d/init.d

# common library for modules, noinst header
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libOSBase_MetricUtil.{so,la}
# modules
%{__rm} $RPM_BUILD_ROOT%{_libdir}/cmpi/libOSBase_*.la \
	$RPM_BUILD_ROOT%{_libdir}/gather/*plug/*.la
%if %{with static_libs}
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libOSBase_MetricUtil.a \
	$RPM_BUILD_ROOT%{_libdir}/{cmpi,gather/*plug}/*.a
%endif

install -d $RPM_BUILD_ROOT/usr/lib/tmpfiles.d
cat >$RPM_BUILD_ROOT/usr/lib/tmpfiles.d/sblim-gather.conf <<EOF
d /var/run/gather 0755 root root -
EOF

# packaged as %doc
%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS COPYING ChangeLog NEWS README README.TEST reposd2csv.pl plugin/*.readme
%attr(754,root,root) /etc/rc.d/init.d/gatherer
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/gatherd.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/reposd.conf
%attr(755,root,root) %{_bindir}/gatherctl
%attr(755,root,root) %{_bindir}/reposctl
%attr(755,root,root) %{_bindir}/reposdump
%attr(755,root,root) %{_sbindir}/gatherd
%attr(755,root,root) %{_sbindir}/reposd
# common library for modules
%attr(755,root,root) %{_libdir}/libOSBase_MetricUtil.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libOSBase_MetricUtil.so.0
# CMPI providers
%attr(755,root,root) %{_libdir}/cmpi/libOSBase_Metric*Provider.so
# gather plugins
%dir %{_libdir}/gather
%dir %{_libdir}/gather/cplug
%attr(755,root,root) %{_libdir}/gather/cplug/libcimplug*.so
%dir %{_libdir}/gather/mplug
%attr(755,root,root) %{_libdir}/gather/mplug/libmetric*.so
%dir %{_libdir}/gather/rplug
%attr(755,root,root) %{_libdir}/gather/rplug/librepository*.so
%dir %{_datadir}/sblim-gather
%{_datadir}/sblim-gather/Linux_*.mof
%{_datadir}/sblim-gather/Linux_*.registration
%attr(755,root,root) %{_datadir}/sblim-gather/provider-register.sh
%attr(755,root,root) %{_datadir}/sblim-gather/start_gathering.sh
%attr(755,root,root) %{_datadir}/sblim-gather/stop_gathering.sh
%dir /var/run/gather
/usr/lib/tmpfiles.d/sblim-gather.conf
%{_mandir}/man1/reposdump.1*
%{_mandir}/man5/gatherd.conf.5*
%{_mandir}/man5/reposd.conf.5*
%{_mandir}/man8/gatherctl.8*
%{_mandir}/man8/gatherd.8*
%{_mandir}/man8/reposctl.8*
%{_mandir}/man8/reposd.8*

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libchannelutil.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libchannelutil.so.0
%attr(755,root,root) %{_libdir}/libgather.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgather.so.0
%attr(755,root,root) %{_libdir}/libgatherutil.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libgatherutil.so.0
%attr(755,root,root) %{_libdir}/libhypfs.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libhypfs.so.0
%attr(755,root,root) %{_libdir}/liblparutil.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/liblparutil.so.0
%attr(755,root,root) %{_libdir}/libmcserv.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libmcserv.so.0
%attr(755,root,root) %{_libdir}/librcserv.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/librcserv.so.0
%attr(755,root,root) %{_libdir}/librepos.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/librepos.so.0
%attr(755,root,root) %{_libdir}/librgather.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/librgather.so.0
%attr(755,root,root) %{_libdir}/librrepos.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/librrepos.so.0
%attr(755,root,root) %{_libdir}/libsysfswrapper.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libsysfswrapper.so.0

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libchannelutil.so
%attr(755,root,root) %{_libdir}/libgather.so
%attr(755,root,root) %{_libdir}/libgatherutil.so
%attr(755,root,root) %{_libdir}/libhypfs.so
%attr(755,root,root) %{_libdir}/liblparutil.so
%attr(755,root,root) %{_libdir}/libmcserv.so
%attr(755,root,root) %{_libdir}/librcserv.so
%attr(755,root,root) %{_libdir}/librepos.so
%attr(755,root,root) %{_libdir}/librgather.so
%attr(755,root,root) %{_libdir}/librrepos.so
%attr(755,root,root) %{_libdir}/libsysfswrapper.so
%{_libdir}/libchannelutil.la
%{_libdir}/libgather.la
%{_libdir}/libgatherutil.la
%{_libdir}/libhypfs.la
%{_libdir}/liblparutil.la
%{_libdir}/libmcserv.la
%{_libdir}/librcserv.la
%{_libdir}/librepos.la
%{_libdir}/librgather.la
%{_libdir}/librrepos.la
%{_libdir}/libsysfswrapper.la
%{_includedir}/gather

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libchannelutil.a
%{_libdir}/libgather.a
%{_libdir}/libgatherutil.a
%{_libdir}/libhypfs.a
%{_libdir}/liblparutil.a
%{_libdir}/libmcserv.a
%{_libdir}/librcserv.a
%{_libdir}/librepos.a
%{_libdir}/librgather.a
%{_libdir}/librrepos.a
%{_libdir}/libsysfswrapper.a
%endif
