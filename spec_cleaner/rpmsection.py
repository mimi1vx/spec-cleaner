# vim: set ts=4 sw=4 et: coding=UTF-8

import re

class Section(object):
    """
    Basic object for parsing each section of spec file.
    It stores the lines in a list and remembers content of
    previous line at hand.
    The unbrace_keywords content is passed from creating
    object to reduce calculation price.
    Various functions do replacement of common typos to
    unificate all the content.
    """


    def __init__(self, re_unbrace_keywords):
        self.lines = []
        self.previous_line = None
        self.re_unbrace_keywords = re_unbrace_keywords


    def add(self, line):
        # cleanup all known troubles
        line = line.rstrip()
        line = self.embrace_macros(line)
        line = self.replace_buildroot(line)
        line = self.replace_optflags(line)
        line = self.replace_known_dirs(line)
        line = self.replace_utils(line)
        line = self.replace_buildservice(line)
        line = self.replace_preamble_macros(line)

        # append to the file
        self.lines.append(line)
        self.previous_line = line


    def output(self, fout):
        for line in self.lines:
            fout.write(line + '\n')


    def strip_useless_spaces(self, line):
        """
        Function to remove useless multiple spaces in some areas.
        It can't be called everywhere so we have to call it in
        children classes where fit.
        """
        return ' '.join(line.split())


    def embrace_macros(self, line):
        """
        Add {} around known macros that have no arguments and are not
        on whitelist.
        Whitelist is passed from caller object
        """
        re_macro = re.compile(r'(^|([^%]))%(\w+)(|(\W]))')

        # I don't think that this can be done within one regexp replacement
        # if you have idea, send me a patch :)

        # work only with non-commented part
        sp = line.split('#')
        # so, for now, put braces around everything, what looks like macro,
        sp[0] = re_macro.sub(r'\1%{\3}\4', sp[0])

        # and replace back known keywords to braceless state again
        sp[0] = self.re_unbrace_keywords.sub(r'%\1', sp[0])
        # re-create the line back
        return '#'.join(sp)


    def replace_buildroot(self, line):
        """
        Replace RPM_BUILD_ROOT for buildroot
        Replace few hard written dirs for further processing with their macro names.
        """
        # FIXME: use regexp to prevent $RPM_BUILD_ROOT_REPLACEMENT
        line = line.replace('${RPM_BUILD_ROOT}', '%{buildroot}')
        line = line.replace('$RPM_BUILD_ROOT', '%{buildroot}')
        line = line.replace('%{buildroot}/etc/init.d/', '%{buildroot}%{_initddir}/')
        line = line.replace('%{buildroot}/etc/', '%{buildroot}%{_sysconfdir}/')
        line = line.replace('%{buildroot}/usr/', '%{buildroot}%{_prefix}/')
        line = line.replace('%{buildroot}/var/', '%{buildroot}%{_localstatedir}/')
        line = line.replace('"%{buildroot}"', '%{buildroot}')
        return line


    def replace_optflags(self, line):
        """
        Replace RPM_OPT_FLAGS for %{optflags}
        """
        line = line.replace('${RPM_OPT_FLAGS}', '%{optflags}')
        line = line.replace('$RPM_OPT_FLAGS', '%{optflags}')
        return line


    def replace_known_dirs(self, line):
        """
        Replace hardcoded stuff like /usr/share -> %{_datadir}
        """
        re_bindir = re.compile('%{_prefix}/bin([/\s$])')
        re_sbindir = re.compile('%{_prefix}/sbin([/\s$])')
        re_includedir = re.compile('%{_prefix}/include([/\s$])')
        re_datadir = re.compile('%{_prefix}/share([/\s$])')
        re_mandir = re.compile('%{_datadir}/man([/\s$])')
        re_infodir = re.compile('%{_datadir}/info([/\s$])')
        re_docdir = re.compile('%{_datadir}/doc([/\s$])')

        line = line.replace('%{_usr}', '%{_prefix}')
        line = line.replace('%{_prefix}/%{_lib}', '%{_libdir}')
        # old typo in rpm macro
        line = line.replace('%_initrddir', '%{_initddir}')
        line = line.replace('%{_initrddir}', '%{_initddir}')

        line = re_bindir.sub(r'%{_bindir}\1', line)
        line = re_sbindir.sub(r'%{_sbindir}\1', line)
        line = re_includedir.sub(r'%{_includedir}\1', line)
        line = re_datadir.sub(r'%{_datadir}\1', line)
        line = re_mandir.sub(r'%{_mandir}\1', line)
        line = re_infodir.sub(r'%{_infodir}\1', line)
        line = re_docdir.sub(r'%{_docdir}\1', line)

        return line


    def replace_utils(self, line):
        """
        Remove the macro calls for utilities and rather use direct commands.
        OBS ensures there is only one anyway.
        """
        r = {'id_u': 'id -u', 'ln_s': 'ln -s', 'lzma': 'xz --format-lzma', 'mkdir_p': 'mkdir -p', 'awk':'gawk', 'cc':'gcc', 'cpp':'gcc -E', 'cxx':'g++', 'remsh':'rsh', }
        for i in r:
            line = line.replace('%{__' + i + '}', r[i])

        for i in [ 'aclocal', 'ar', 'as', 'autoconf', 'autoheader', 'automake', 'bzip2', 'cat', 'chgrp', 'chmod', 'chown', 'cp', 'cpio', 'file', 'gpg', 'grep', 'gzip', 'id', 'install', 'ld', 'libtoolize', 'make', 'mkdir', 'mv', 'nm', 'objcopy', 'objdump', 'patch', 'perl', 'python', 'ranlib', 'restorecon', 'rm', 'rsh', 'sed', 'semodule', 'ssh', 'strip', 'tar', 'unzip', 'xz', ]:
            line = line.replace('%{__' + i + '}', i)

        return line


    def replace_buildservice(self, line):
        """
        Pretty format the conditions for distribution/version detection.
        Replace %{suse_version} for 0%{?suse_version}
        """
        for i in ['centos', 'debian', 'fedora', 'mandriva', 'meego', 'rhel', 'sles', 'suse', 'ubuntu']:
            line = line.replace('%{' + i + '_version}', '0%{?' + i + '_version}').replace('00%{','0%{')
        return line


    def replace_preamble_macros(self, line):
        """
        Replace %{S:0} for %{SOURCE:0} and so on.
        """
        for i in map(str,range(100)):
            line = line.replace('%{P:' + i + '}', '%{PATCH' + i + '}')
            line = line.replace('%{S:' + i + '}', '%{SOURCE' + i + '}')
        return line