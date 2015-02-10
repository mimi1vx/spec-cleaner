#
# spec file for package susekmp
#
# Copyright (c) 2013 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#


%package guest-KMP
Summary:        Guest kernel modules for VirtualBox
Group:          System/Emulators/PC
#SUSE specify macro to define guest kmp package
%{?suse_kernel_module_package:%suse_kernel_module_package -p %{SOURCE8} -n %{name}-guest -f %{SOURCE6} kdump um xen xenpae}

