<h1 align="center">
	<img src="data/com.github.amikha1lov.RecApp.svg" alt="RecApp" width="128" height="128"/><br>
	RecApp
</h1>


<p align="center"><strong>Simple Screencasting Application</strong></p>

<p align="center">
  <a href="https://flathub.org/apps/details/com.github.amikha1lov.RecApp"><img width="200" alt="Download on Flathub" src="https://flathub.org/assets/badges/flathub-badge-en.png"/></a>
</p>

<p align="center">
  <img src="RecApp-screenshot.png"/>
</p>


## Description
A user-friendly and open-source screencast application for Linux written in GTK using free GStreamer modules instead of FFMPEG.


## Packaging status

[Fedora](https://src.fedoraproject.org/rpms/recapp): `sudo dnf install recapp`

[openSUSE Tumbleweed && openSUSE Leap 15.2 One-click installation](https://software.opensuse.org//download.html?project=GNOME%3AApps&package=recapp)


## Build from source

```
git clone https://github.com/amikha1lov/RecApp.git
cd RecApp
git submodule update --init --recursive
mkdir -p $HOME/Projects/flatpak/repo
flatpak-builder --repo=$HOME/Projects/flatpak/repo --force-clean --ccache build-dir com.github.amikha1lov.RecApp.yaml
flatpak remote-add --no-gpg-verify local-repo $HOME/Projects/flatpak/repo
flatpak install local-repo com.github.amikha1lov.RecApp
```


## Credits
Developed by **[Rafael Mardojai CM](https://github.com/rafaelmardojai)** and [contributors](https://github.com/rafaelmardojai/blanket/graphs/contributors).

Thanks to Jorge Toledo for the name idea.


