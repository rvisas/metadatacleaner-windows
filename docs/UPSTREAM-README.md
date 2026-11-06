<!--
SPDX-FileCopyrightText: Metadata Cleaner contributors
SPDX-License-Identifier: CC-BY-SA-4.0
-->

<div align="center">
  <img alt="A rectangle with a fingerprint on it being wiped using a sponge" width="160" src="./data/icons/io.gitlab.metadatacleaner.metadatacleaner.svg">
  <h1 align="center">Metadata Cleaner</h1>
  <h3 align="center">View and clean metadata in files</h3>
  <p align="center">
    <br />
      <a href="./CODE_OF_CONDUCT.md"><img src="https://img.shields.io/badge/Code%20of%20Conduct-GNOME-f5c211.svg?style=for-the-badge&labelColor=f9f06b" alt="GNOME Code of Conduct" /></a>
      <a href="./LICENSE.md"><img src="https://img.shields.io/badge/LICENSE-GPL--3.0-f5c211.svg?style=for-the-badge&labelColor=f9f06b" alt="License GPL-3.0" /></a>
      <a href='https://stopthemingmy.app'><img width='193.455' alt='Please do not theme this app' src='https://stopthemingmy.app/badge.svg'/></a>
  </p>

  <p align="center">
      <img alt="Screenshot of the Metadata Cleaner app in light mobile. A bunch of files are ready to be cleaned. gnome-story.webp is open and has 4 metadata visible in a side panel." src="./data/screenshots/1.png">
  </p>

  <p align="left">Metadata within a file can tell a lot about you. Cameras record data about when and where a picture was taken and which camera was used. Office applications automatically add author and company information to documents and spreadsheets. This is sensitive information and you may not want to disclose it. Metadata Cleaner allows you to view metadata in your files and to get rid of it, as much as possible.</p>
</div>

# Install

## Release

<a href="https://flathub.org/apps/details/io.gitlab.metadatacleaner.metadatacleaner" rel="noreferrer noopener" target="_blank"><img loading="lazy" draggable="false" width='240' alt='Download on Flathub' src='https://flathub.org/api/badge?svg&locale=en' /></a>

<!-- add third-parties once we make a release -->

## From Source

<details>
<summary>Dependencies</summary>

Package Name | Required
:--- | ---:
meson | ✅
python3 | ✅
libadwaita-1.0-dev | ✅
mat2 | ✅

</details>

### Makefile

```
$ make
$ make install
```

### GNOME Builder

- Clone
- Open in GNOME Builder

# Acknowledgements

- Metadata cleaning is being done using [mat2](https://github.com/jvoisin/mat2)
- This is a fork of [rmnvgr/metadata-cleaner](https://gitlab.com/rmnvgr/metadata-cleaner)

[![Translation status](https://hosted.weblate.org/widget/metadata-cleaner/287x66-white.png)](https://hosted.weblate.org/engage/metadata-cleaner/)


# Contributing

You can contribute to the documentation, translation or code, see [`CONTRIBUTING.md`](./CONTRIBUTING.md).
