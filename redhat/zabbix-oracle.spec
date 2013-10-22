Name		: zabbix
Version		: 2.0.9
Release		: 1%{?dist}
Summary		: Enterprise-class open source distributed monitoring solution.

Group		: Applications/Internet
License		: GPLv2+
URL		: http://www.zabbix.com/
Source0		: %{name}-%{version}.tar.gz

Buildroot	: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


# Avoid creation of Requires for libs that they are not xplicitly provided by
# the Oracle packages
%filter_from_requires /^libnnz11.*/d
%filter_from_requires /^libclntsh.*/d
%filter_setup

BuildRequires	: oracle-instantclient11.2-devel
BuildRequires	: net-snmp-devel
BuildRequires	: openldap-devel
BuildRequires	: gnutls-devel
BuildRequires	: iksemel-devel
BuildRequires	: unixODBC-devel
BuildRequires	: curl-devel >= 7.13.1
BuildRequires	: rpm-macros-rpmforge

%description
Zabbix is software that monitors numerous parameters of a network and
the health and integrity of servers. Zabbix uses a flexible
notification mechanism that allows users to configure e-mail based
alerts for virtually any event.  This allows a fast reaction to server
problems. Zabbix offers excellent reporting and data visualisation
features based on the stored data. This makes Zabbix ideal for
capacity planning.

Zabbix supports both polling and trapping. All Zabbix reports and
statistics, as well as configuration parameters are accessed through a
web-based front end. A web-based front end ensures that the status of
your network and the health of your servers can be assessed from any
location. Properly configured, Zabbix can play an important role in
monitoring IT infrastructure. This is equally true for small
organisations with a few servers and for large companies with a
multitude of servers.

%package server-oracle
Summary		: Zabbix server compiled to use Oracle database
Group		: Applications/Internet
Requires	: zabbix = %{version}-%{release}
Requires	: zabbix-server = %{version}-%{release}
Provides	: zabbix-server-implementation = %{version}-%{release}
Obsoletes	: zabbix <= 1.5.3-0.1
Conflicts	: zabbix-server-mysql
Conflicts	: zabbix-server-pgsql

%description server-oracle
Zabbix server compiled with Oracle database support.

%prep server-oracle
%setup0 -q -n %{name}-%{version}

%build server-oracle

common_flags="
    --enable-dependency-tracking
    --sysconfdir=/etc/zabbix
    --enable-server
    --enable-ipv6
    --with-net-snmp
    --with-ldap
    --with-libcurl
    --with-jabber
    --with-unixodbc
"

%configure $common_flags --with-oracle --with-oracle-lib=/usr/lib/oracle/11.2/client64/lib/ --with-oracle-include=/usr/include/oracle/11.2/client64/
make %{?_smp_mflags}
mv src/zabbix_server/zabbix_server src/zabbix_server/zabbix_server_oracle

touch src/zabbix_server/zabbix_server

%install server-oracle
rm -rf $RPM_BUILD_ROOT

# install 
make DESTDIR=$RPM_BUILD_ROOT install

# install docs
docdir=$RPM_BUILD_ROOT%{_docdir}/%{name}-server-oracle-%{version}
install -dm 755 $docdir
cp -pR database/oracle $docdir/create
cp -pR --parents upgrades/dbpatches/1.6/oracle $docdir
cp -pR --parents upgrades/dbpatches/1.8/oracle $docdir
cp -pR --parents upgrades/dbpatches/2.0/oracle $docdir

install -m 0755 -p src/zabbix_server/zabbix_server_oracle $RPM_BUILD_ROOT%{_sbindir}/

# clean up
rm -rf $RPM_BUILD_ROOT/usr/share/zabbix
rm -rf $RPM_BUILD_ROOT/usr/share/man
rm -rf $RPM_BUILD_ROOT/etc
rm -f $RPM_BUILD_ROOT/%{_sbindir}/zabbix_server

%clean server-oracle
rm -rf $RPM_BUILD_ROOT

%post server-oracle
/usr/sbin/update-alternatives --install %{_sbindir}/zabbix_server zabbix-server %{_sbindir}/zabbix_server_oracle 10
:

%preun server-oracle
if [ "$1" = 0 ]
then
  /usr/sbin/update-alternatives --remove zabbix-server %{_sbindir}/zabbix_server_oracle
fi
:

%files server-oracle
%defattr(-,root,root,-)
%{_sbindir}/zabbix_server_oracle
%{_docdir}/%{name}-server-oracle-%{version}/

%changelog
* Tue Oct 22 2013 Roberto Moreda <moreda@allenta.com> - 2.0.9-1
- created minimalistic package zabbix-server-oracle based in the original 
  spec file by Kodai Terashima <kodai.terashima@zabbix.com> from the Zabbix
  official repo
- added rpm-macros-rpmforge as build dependency to filter out Oracle lib 
  dependencies
 
