Name:           helix
Version:        24.07
Release:        1%{?dist}
Summary:        Post-modern modal text editor with built-in LSP
License:        MPL-2.0
URL:            https://github.com/helix-editor/helix
Source0:        %{url}/archive/%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cargo >= 1.70
BuildRequires:  gcc
BuildRequires:  git

%description
A Kakoune/Neovim-inspired modal editor with built-in LSP support,
tree-sitter integration, and multiple selections.

%prep
%autosetup

%build
cargo build --release --locked

%install
install -Dm755 target/release/hx %{buildroot}%{_bindir}/hx
mkdir -p %{buildroot}%{_datadir}/helix
cp -r runtime %{buildroot}%{_datadir}/helix/runtime

%files
%license LICENSE
%{_bindir}/hx
%{_datadir}/helix/

%changelog
* Mon Mar 09 2026 Linta Project <dev@lintalinux.org> - 24.07-1
- Initial Linta package
