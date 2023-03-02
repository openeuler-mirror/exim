%bcond_without clamav
%{!?_hardened_build:%global _hardened_build 1}

Summary:          The exim mail transfer agent
Name:             exim
Version:          4.96
Release:          2
License:          GPLv2+
Url:              https://www.exim.org/

Provides:         MTA smtpd smtpdaemon server(smtp)
Requires(post):   /sbin/restorecon %{_sbindir}/alternatives systemd
Requires(preun):  %{_sbindir}/alternatives systemd
Requires(postun): %{_sbindir}/alternatives systemd
Requires(pre):    %{_sbindir}/groupadd, %{_sbindir}/useradd

%if %{with clamav}
BuildRequires: clamd
%endif

Source0:          https://ftp.exim.org/pub/exim/exim4/exim-%{version}.tar.xz
Source1:          exim.sysconfig
Source2:          exim.logrotate
# The exim-tidydb.sh is used to tidy up the contents of a hints database.
Source3:          exim-tidydb.sh
Source4:          exim.pam
Source5:          exim-clamav-tmpfiles.conf
Source6:          exim-greylist.conf.inc
Source7:          mk-greylist-db.sql
# The greylist-tidy.sh is used to delete expired data in greylist
Source8:          greylist-tidy.sh
Source9:          trusted-configs
Source10:         exim.service
# The exim-gen-cert is used to generate the certificate
Source11:         exim-gen-cert
Source12:         clamd.exim.service

Patch0:           exim-4.96-config.patch
Patch1:           exim-4.94-libdir.patch
Patch2:           exim-4.96-dlopen-localscan.patch
Patch3:           exim-4.96-pic.patch
# https://bugs.exim.org/show_bug.cgi?id=2728
Patch4:           exim-4.96-opendmarc-1.4-build-fix.patch
# https://bugs.exim.org/show_bug.cgi?id=2899
Patch5:           exim-4.96-build-fix.patch

Requires:         /etc/pki/tls/certs /etc/pki/tls/private
Requires:         setup
Requires:         perl
Recommends:       publicsuffix-list
BuildRequires:    gcc
BuildRequires:    libdb-devel
BuildRequires:    openssl-devel
BuildRequires:    zlib-devel
BuildRequires:    openldap-devel
BuildRequires:    pam-devel
BuildRequires:    pcre2-devel
BuildRequires:    sqlite-devel
BuildRequires:    cyrus-sasl-devel
BuildRequires:    libspf2-devel
BuildRequires:    libopendmarc-devel
BuildRequires:    openldap-devel
BuildRequires:    mariadb-connector-c-devel
BuildRequires:    libpq-devel
BuildRequires:    libXaw-devel
BuildRequires:    libXmu-devel
BuildRequires:    libXext-devel
BuildRequires:    libX11-devel
BuildRequires:    libSM-devel
BuildRequires:    perl-devel
BuildRequires:    perl-generators
BuildRequires:    libICE-devel
BuildRequires:    libXpm-devel
BuildRequires:    libXt-devel
BuildRequires:    perl(ExtUtils::Embed)
BuildRequires:    systemd-units
BuildRequires:    libgsasl-devel
BuildRequires:    mariadb-devel
BuildRequires:    libnsl2-devel
BuildRequires:    libtirpc-devel
BuildRequires:    gnupg2
BuildRequires:    grep
BuildRequires:    make

%description
Exim is a message transfer agent (MTA) developed at the University of
Cambridge for use on Unix systems connected to the Internet. It is
freely available under the terms of the GNU General Public Licence. In
style it is similar to Smail 3, but its facilities are more
general. There is a great deal of flexibility in the way mail can be
routed, and there are extensive facilities for checking incoming
mail. Exim can be installed in place of sendmail, although the
configuration of exim is quite different to that of sendmail.

%package mysql
Summary:          MySQL lookup support for Exim
Requires:         exim = %{version}-%{release}

%description mysql
This package contains the MySQL lookup module for Exim

%package pgsql
Summary:          PostgreSQL lookup support for Exim
Requires:         exim = %{version}-%{release}

%description pgsql
This package contains the PostgreSQL lookup module for Exim

%package mon
Summary:          X11 monitor application for Exim

%description mon
The Exim Monitor is an optional supplement to the Exim package. It
displays information about Exim's processing in an X window, and an
administrator can perform a number of control actions from the window
interface.

%if %{with clamav}
%package clamav
Summary:          Clam Antivirus scanner dæmon configuration for use with Exim
Requires:         clamd exim
Obsoletes:        clamav-exim <= 0.86.2

%description clamav
This package contains configuration files which invoke a copy of the
clamav dæmon for use with Exim. It can be activated by adding (or
uncommenting)

   av_scanner = clamd:%{_var}/run/clamd.exim/clamd.sock

in your exim.conf, and using the 'malware' condition in the DATA ACL,
as follows:

   deny message = This message contains malware ($malware_name)
      malware = *

For further details of Exim content scanning, see chapter 41 of the Exim
specification:
http://www.exim.org/exim-html-%{version}/doc/html/spec_html/ch41.html

%endif

%package greylist
Summary:          Example configuration for greylisting using Exim
Requires:         sqlite exim
Requires:         crontabs

%description greylist
This package contains a simple example of how to do greylisting in Exim's
ACL configuration. It contains a cron job to remove old entries from the
greylisting database, and an ACL subroutine which needs to be included
from the main exim.conf file.

To enable greylisting, install this package and then uncomment the lines
in Exim's configuration /etc/exim.conf which enable it. You need to
uncomment at least two lines -- the '.include' directive which includes
the new ACL subroutine, and the line which invokes the new subroutine.

By default, this implementation only greylists mails which appears
'suspicious' in some way. During normal processing of the ACLs we collect
a list of 'offended' which it's committed, which may include having
SpamAssassin points, lacking a Message-ID: header, coming from a blacklisted
host, etc. There are examples of these in the default configuration file,
mostly commented out. These should be sufficient for you to you trigger
greylisting for whatever 'offences' you can dream of, or even to make
greylisting unconditional.

%prep
%autosetup -p1

cp src/EDITME Local/Makefile
sed -i 's@^# LOOKUP_MODULE_DIR=.*@LOOKUP_MODULE_DIR=%{_libdir}/exim/%{version}-%{release}/lookups@' Local/Makefile
sed -i 's@^# AUTH_LIBS=-lsasl2@AUTH_LIBS=-lsasl2@' Local/Makefile
cp exim_monitor/EDITME Local/eximon.conf

# Workaround for rhbz#1791878
pushd doc
for f in $(ls -dp cve-* | grep -v '/\|\(\.txt\)$'); do
  mv "$f" "$f.txt"
done
popd

%build
%ifnarch s390 s390x sparc sparcv9 sparcv9v sparc64 sparc64v
	export PIE=-fpie
	export PIC=-fpic
%else
	export PIE=-fPIE
	export PIC=-fPIC
%endif

export LDFLAGS="%{?__global_ldflags} %{?_hardened_build:-pie -Wl,-z,relro,-z,now}"
make _lib=%{_lib} FULLECHO=

%install
mkdir -p $RPM_BUILD_ROOT%{_sbindir}
mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_libdir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pam.d
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/exim

cd build-`scripts/os-type`-`scripts/arch-type`
install -m 4775 exim $RPM_BUILD_ROOT%{_sbindir}

for i in eximon eximon.bin exim_dumpdb exim_fixdb exim_tidydb \
	exinext exiwhat exim_dbmbuild exicyclog exim_lock \
	exigrep eximstats exipick exiqgrep exiqsumm \
	exim_checkaccess convert4r4
do
	install -m 0755 $i $RPM_BUILD_ROOT%{_sbindir}
done

mkdir -p $RPM_BUILD_ROOT%{_libdir}/exim/%{version}-%{release}/lookups
for i in mysql.so pgsql.so
do
	install -m755 lookups/$i \
	 $RPM_BUILD_ROOT%{_libdir}/exim/%{version}-%{release}/lookups
done

cd ..

install -m 0644 src/configure.default $RPM_BUILD_ROOT%{_sysconfdir}/exim/exim.conf
install -m 0644 %SOURCE4 $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/exim

mkdir -p $RPM_BUILD_ROOT/usr/lib
pushd $RPM_BUILD_ROOT/usr/lib
ln -sf ../sbin/exim sendmail.exim
popd

pushd $RPM_BUILD_ROOT%{_sbindir}/
ln -sf exim sendmail.exim
popd

pushd $RPM_BUILD_ROOT%{_bindir}/
ln -sf ../sbin/exim mailq.exim
ln -sf ../sbin/exim runq.exim
ln -sf ../sbin/exim rsmtp.exim
ln -sf ../sbin/exim rmail.exim
ln -sf ../sbin/exim newaliases.exim
popd

install -d -m 0750 $RPM_BUILD_ROOT%{_var}/spool/exim
install -d -m 0750 $RPM_BUILD_ROOT%{_var}/spool/exim/db
install -d -m 0750 $RPM_BUILD_ROOT%{_var}/spool/exim/input
install -d -m 0750 $RPM_BUILD_ROOT%{_var}/spool/exim/msglog
install -d -m 0750 $RPM_BUILD_ROOT%{_var}/log/exim

mkdir -p $RPM_BUILD_ROOT%{_mandir}/man8
install -m644 doc/exim.8 $RPM_BUILD_ROOT%{_mandir}/man8/exim.8
pod2man --center=EXIM --section=8 \
	$RPM_BUILD_ROOT/usr/sbin/eximstats \
	$RPM_BUILD_ROOT%{_mandir}/man8/eximstats.8

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
install -m 644 %SOURCE1 $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/exim

# Systemd
mkdir -p %{buildroot}%{_unitdir}
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}
install -m644 %{SOURCE10} %{buildroot}%{_unitdir}
install -m755 %{SOURCE11} %{buildroot}%{_libexecdir}

%if %{with clamav}
install -m644 %{SOURCE12} %{buildroot}%{_unitdir}
%endif

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
install -m 0644 %SOURCE2 $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/exim

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily
install -m 0755 %SOURCE3 $RPM_BUILD_ROOT%{_sysconfdir}/cron.daily/exim-tidydb

# generate ghost .pem file
mkdir -p $RPM_BUILD_ROOT/etc/pki/tls/{certs,private}
touch $RPM_BUILD_ROOT/etc/pki/tls/{certs,private}/exim.pem
chmod 600 $RPM_BUILD_ROOT/etc/pki/tls/{certs,private}/exim.pem

# generate alternatives ghosts
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
for i in %{_sbindir}/sendmail %{_bindir}/{mailq,runq,rsmtp,rmail,newaliases} \
	/usr/lib/sendmail %{_sysconfdir}/pam.d/smtp
do
	touch $RPM_BUILD_ROOT$i
done
gzip < /dev/null > $RPM_BUILD_ROOT%{_mandir}/man1/mailq.1.gz

%if %{with clamav}
# Munge the clamav init and config files from clamav-devel. This really ought
# to be a subpackage of clamav, but this hack will have to do for now.
function clamsubst() {
	 sed -e "s!<SERVICE>!$3!g;s!<USER>!$4!g;""$5" %{_docdir}/clamd/"$1" >"$RPM_BUILD_ROOT$2"
}

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/clamd.d
clamsubst clamd.conf %{_sysconfdir}/clamd.d/exim.conf exim exim \
       's!^##*\(\(LogFile\|LocalSocket\|PidFile\|User\)\s\|\(StreamSaveToDisk\|ScanMail\|LogTime\|ScanArchive\)$\)!\1!;s!^Example!#Example!;'

clamsubst clamd.logrotate %{_sysconfdir}/logrotate.d/clamd.exim exim exim ''
cat <<EOF > $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/clamd.exim
CLAMD_CONFIG='%_sysconfdir/clamd.d/exim.conf'
CLAMD_SOCKET=%{_var}/run/clamd.exim/clamd.sock
EOF
ln -sf clamd $RPM_BUILD_ROOT/usr/sbin/clamd.exim

mkdir -p %{buildroot}%{_tmpfilesdir}
install -m 0644 %{SOURCE5} %{buildroot}%{_tmpfilesdir}/exim-clamav.conf
mkdir -p $RPM_BUILD_ROOT%{_var}/run/clamd.exim
mkdir -p $RPM_BUILD_ROOT%{_var}/log
touch $RPM_BUILD_ROOT%{_var}/log/clamd.exim

%endif

# Set up the greylist subpackage
install -m644 %{SOURCE6} $RPM_BUILD_ROOT/%_sysconfdir/exim/exim-greylist.conf.inc
install -m644 %{SOURCE7} $RPM_BUILD_ROOT/%_sysconfdir/exim/mk-greylist-db.sql
mkdir -p $RPM_BUILD_ROOT/%_sysconfdir/cron.daily
install -m755 %{SOURCE8} $RPM_BUILD_ROOT/%_sysconfdir/cron.daily/greylist-tidy.sh
install -m644 %{SOURCE9} $RPM_BUILD_ROOT/%_sysconfdir/exim/trusted-configs
touch $RPM_BUILD_ROOT/%_var/spool/exim/db/greylist.db

%check
build-`scripts/os-type`-`scripts/arch-type`/exim -C src/configure.default -bV

%pre
%{_sbindir}/groupadd -g 93 exim 2>/dev/null
%{_sbindir}/useradd -d %{_var}/spool/exim -s /sbin/nologin -G mail -M -r -u 93 -g exim exim 2>/dev/null
# Copy TLS certs from old location to new -- don't move them, because the
# config file may be modified and may be pointing to the old location.
if [ ! -f /etc/pki/tls/certs/exim.pem -a -f %{_datadir}/ssl/certs/exim.pem ] ; then
   cp %{_datadir}/ssl/certs/exim.pem /etc/pki/tls/certs/exim.pem
   cp %{_datadir}/ssl/private/exim.pem /etc/pki/tls/private/exim.pem
fi

exit 0

%post
%systemd_post %{name}.service

%{_sbindir}/alternatives --install %{_sbindir}/sendmail mta %{_sbindir}/sendmail.exim 10 \
	--slave %{_bindir}/mailq mta-mailq %{_bindir}/mailq.exim \
	--slave %{_bindir}/runq mta-runq %{_bindir}/runq.exim \
	--slave %{_bindir}/rsmtp mta-rsmtp %{_bindir}/rsmtp.exim \
	--slave %{_bindir}/rmail mta-rmail %{_bindir}/rmail.exim \
	--slave /etc/pam.d/smtp mta-pam /etc/pam.d/exim \
	--slave %{_bindir}/newaliases mta-newaliases %{_bindir}/newaliases.exim \
	--slave /usr/lib/sendmail mta-sendmail /usr/lib/sendmail.exim \
	--slave %{_mandir}/man1/mailq.1.gz mta-mailqman %{_mandir}/man8/exim.8.gz \
	--initscript exim

%preun
%systemd_preun %{name}.service
if [ $1 = 0 ]; then
	%{_sbindir}/alternatives --remove mta %{_sbindir}/sendmail.exim
fi

%postun
%systemd_postun_with_restart %{name}.service
if [ $1 -ge 1 ]; then
	mta=`readlink /etc/alternatives/mta`
	if [ "$mta" == "%{_sbindir}/sendmail.exim" ]; then
		/usr/sbin/alternatives --set mta %{_sbindir}/sendmail.exim
	fi
fi

%post greylist
if [ ! -r %{_var}/spool/exim/db/greylist.db ]; then
   sqlite3 %{_var}/spool/exim/db/greylist.db < %{_sysconfdir}/exim/mk-greylist-db.sql
   chown exim.exim %{_var}/spool/exim/db/greylist.db
   chmod 0660 %{_var}/spool/exim/db/greylist.db
fi

%files
%attr(4755,root,root) %{_sbindir}/exim
%{_sbindir}/exim_dumpdb
%{_sbindir}/exim_fixdb
%{_sbindir}/exim_tidydb
%{_sbindir}/exinext
%{_sbindir}/exiwhat
%{_sbindir}/exim_dbmbuild
%{_sbindir}/exicyclog
%{_sbindir}/exigrep
%{_sbindir}/eximstats
%{_sbindir}/exipick
%{_sbindir}/exiqgrep
%{_sbindir}/exiqsumm
%{_sbindir}/exim_lock
%{_sbindir}/exim_checkaccess
%{_sbindir}/convert4r4
%{_sbindir}/sendmail.exim
%{_bindir}/mailq.exim
%{_bindir}/runq.exim
%{_bindir}/rsmtp.exim
%{_bindir}/rmail.exim
%{_bindir}/newaliases.exim
/usr/lib/sendmail.exim
%{_mandir}/man8/*
%dir %{_libdir}/exim
%dir %{_libdir}/exim/%{version}-%{release}
%dir %{_libdir}/exim/%{version}-%{release}/lookups

%defattr(-,exim,exim)
%dir %{_var}/spool/exim
%dir %{_var}/spool/exim/db
%dir %{_var}/spool/exim/input
%dir %{_var}/spool/exim/msglog
%dir %{_var}/log/exim

%defattr(-,root,root)
%dir %{_sysconfdir}/exim
%config(noreplace) %{_sysconfdir}/exim/exim.conf
%config(noreplace) %{_sysconfdir}/exim/trusted-configs
%config(noreplace) %{_sysconfdir}/sysconfig/exim
%{_unitdir}/exim.service
%{_libexecdir}/exim-gen-cert
%config(noreplace) %{_sysconfdir}/logrotate.d/exim
%config(noreplace) %{_sysconfdir}/pam.d/exim
%{_sysconfdir}/cron.daily/exim-tidydb

%license LICENCE NOTICE
%doc ACKNOWLEDGMENTS README.UPDATING README
%doc doc util/unknownuser.sh
%attr(0600,root,root) %ghost %config(missingok,noreplace) %verify(not md5 size mtime) /etc/pki/tls/certs/exim.pem
%attr(0600,root,root) %ghost %config(missingok,noreplace) %verify(not md5 size mtime) /etc/pki/tls/private/exim.pem
%attr(0755,root,root) %ghost %{_sbindir}/sendmail
%attr(0755,root,root) %ghost %{_bindir}/mailq
%attr(0755,root,root) %ghost %{_bindir}/runq
%attr(0755,root,root) %ghost %{_bindir}/rsmtp
%attr(0755,root,root) %ghost %{_bindir}/rmail
%attr(0755,root,root) %ghost %{_bindir}/newaliases
%attr(0755,root,root) %ghost /usr/lib/sendmail
%ghost %{_sysconfdir}/pam.d/smtp
%ghost %{_mandir}/man1/mailq.1.gz

%files mysql
%{_libdir}/exim/%{version}-%{release}/lookups/mysql.so

%files pgsql
%{_libdir}/exim/%{version}-%{release}/lookups/pgsql.so

%files mon
%{_sbindir}/eximon
%{_sbindir}/eximon.bin

%if %{with clamav}
%post clamav
/bin/mkdir -pm 0750 %{_var}/run/clamd.exim
/bin/chown exim:exim %{_var}/run/clamd.exim
/bin/touch %{_var}/log/clamd.exim
/bin/chown exim.exim %{_var}/log/clamd.exim
/sbin/restorecon %{_var}/log/clamd.exim
if [ $1 -eq 1 ] ; then
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun clamav
if [ $1 = 0 ]; then
  /bin/systemctl --no-reload clamd.exim.service > /dev/null 2>&1 || :
  /bin/systemctl stop clamd.exim.service > /dev/null 2>&1 || :
fi

%postun clamav
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    /bin/systemctl try-restart clamd.exim.service >/dev/null 2>&1 || :
fi

%files clamav
%{_sbindir}/clamd.exim
%{_unitdir}/clamd.exim.service
%config(noreplace) %verify(not mtime) %{_sysconfdir}/clamd.d/exim.conf
%config(noreplace) %verify(not mtime) %{_sysconfdir}/sysconfig/clamd.exim
%config(noreplace) %verify(not mtime) %{_sysconfdir}/logrotate.d/clamd.exim
%{_tmpfilesdir}/exim-clamav.conf
%ghost %attr(0750,exim,exim) %dir %{_var}/run/clamd.exim
%ghost %attr(0644,exim,exim) %{_var}/log/clamd.exim
%endif

%files greylist
%config %{_sysconfdir}/exim/exim-greylist.conf.inc
%ghost %{_var}/spool/exim/db/greylist.db
%{_sysconfdir}/exim/mk-greylist-db.sql
%{_sysconfdir}/cron.daily/greylist-tidy.sh

%changelog
* Thur Feb 16 2023 zhuchao <tom_toworld@163.com> - 4.96-2
- DESC:add build requirement init

* Tue Oct 18 2022 zhuchao <tom_toworld@163.com> - 4.96-1
- DESC:Package init