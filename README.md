<a name="readme-top"></a>
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<br />
<div align="center">
  <a href="https://github.com/ProtDos/Veilo">
    <img src="https://github.com/ProtDos/Veilo/assets/69071809/ffc7b679-f834-4e1d-a036-c80e9e9cf7f8" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Veilo</h3>

  <p align="center">
    Revolutionize your chats with our quantum-secure app, ensuring the highest levels of privacy and security.
    <br />
    <a href="https://github.com/ProtDos/Veilo"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/ProtDos/Veilo">View Demo</a>
    ·
    <a href="https://github.com/ProtDos/Veilo/issues">Report Bug</a>
    ·
    <a href="https://github.com/ProtDos/Veilo/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Revolutionize your chats with our quantum-secure app, ensuring the highest levels of privacy and security. The aim of this project is to create an app that is absolutely secure, but also very easy to use. Quantum-safe algorithms will help with this and (virtually) no metadata will be sent.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Warning
> **Warning**
> This project is not finished and should definetly not be used at this points. Some mentioned features are not implemented yet and the version may be unstable. This App currently only has RSA as encryption, no post quantum algorithms are implemented yet.

---

## Play Store
Link: https://play.google.com/store/apps/details?id=org.privchat.veilo <br />
Note: This project isn't listed on the App Store yet*

<a href='https://play.google.com/store/apps/details?id=org.privchat.veilo'><img alt='Get it on Google Play' src='https://play.google.com/intl/en_us/badges/images/generic/en_badge_web_generic.png' height='80px'/></a>

*this is because of the high costs.

### Built With

Here is a list of any major frameworks/libraries used to bootstrap your project

* [![React][React.js]][React-url]
* [![Vue][Vue.js]][Vue-url]
* [![Angular][Angular.io]][Angular-url]
* [![Svelte][Svelte.dev]][Svelte-url]
* [![Java][Java.l]][Java_L]

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Demo

<div style="text-align: center;" align="center">
  <img src="https://github.com/ProtDos/Veilo/assets/69071809/92792b31-55fc-48ea-8a62-6a397fcc237a" style="display: inline-block; margin-left: auto; margin-right: auto;">
  <img src="https://github.com/ProtDos/Veilo/assets/69071809/32af12b2-e823-4887-8c8e-b920d10f9a9e"style="display: inline-block; margin-left: auto; margin-right: auto;">
</div>

---
## Context
This was done in the context of a german competition.

## Features
Here is a list of all the features that my Chat App has:
- Encrypted Messaging
- Authenticated Messaging
- Keys generated locally
- Data Encryption
- more coming soon...

---

<!-- GETTING STARTED -->
## Getting Started

To get started, [download](https://github.com/ProtDos/Veilo/archive/refs/heads/main.zip) the project, unzip it and run it using
`python3 main.py`

## Exporting
To export the app, you need a linux distribution. 
```sh
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
pip3 install --user --upgrade buildozer
pip3 install --user --upgrade Cython==0.29.33 virtualenv


# add the following line at the end of your ~/.bashrc file
export PATH=$PATH:~/.local/bin/

# move the file to the current directory
cd Veilo
buildozer android debug
```
The result will be withing the bin/ directory. Note: This is only for android.

### Prerequisites

To run the app locally, execute these command. If you want to export it, visit the section above.
* python
  ```sh
  sudo apt-get install python3 python3-pip
  ```
* requirements
  ```sh
  pip install -r requrements.txt
  ```

### Installation

_Below is an example of how you can instruct your audience on installing and setting up your app. This project doesn't rely on any external dependencies or services._

1. Clone the repo
   ```sh
   git clone https://github.com/ProtDos/ProtDos.git
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Usage

To use this repo, simply type 
```sh
   cd Veilo/
   python3 main.py
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Security and Privacy
Click the links to learn more about the given Topic.
- **Meta-Data** :  [Meta-Data](https://github.com/ProtDos/Veilo/blob/main/Documentation/METADATA.md)
- **Encryption** : ⚪
- **Authentication** : ⚪
- **Sealed Sender** : ⚪
- **Sealed Receiver** : ⚪
- **Peer to Peer** : ⚪

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---


<!-- ROADMAP -->
## Roadmap

- [ ] Post Quantum
  - [ ] Encryption
  - [ ] Authentication
- [ ] Sealed Messaging
  - [ ]  Sealed Sender
  - [ ] Sealed Receiver
- [ ] Cross Platform
  - [ ] SMS
  - [ ] WhatsApp
  - [ ] Signal
  - [ ] Telegram
- [X] Loading Screen
- [ ] maybe BlockChain technology
- [ ] Group Chats
- [ ] storage management & backups
- [ ] online version -> Don't download App
- [ ] Calling
  - [ ] Audio
  - [ ] Video
- [ ] Support for more languages
  - [ ] & detect them automatically
- [ ] Use Argon2id for Password-Hashing
  - [ ] ... or completely don't use authentication via server
- [ ] PIN-Code for app
- [ ] contact search
  

See the [open issues](https://github.com/Veilo/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

CodingLive - [@codinglive](https://discord.com/users/786495827827752990) - [@xoding](https://t.me/xoding) - rootcode@duck.com

Project Link: https://github.com/ProtDos/Veilo

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/ProtDos/Veilo.svg?style=for-the-badge
[contributors-url]: https://github.com//ProtDos/Veilo/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/ProtDos/Veilo.svg?style=for-the-badge
[forks-url]: https://github.com/ProtDos/Veilo/network/members
[stars-shield]: https://img.shields.io/github/stars/ProtDos/Veilo.svg?style=for-the-badge
[stars-url]: https://github.com/ProtDos/Veilo/stargazers
[issues-shield]: https://img.shields.io/github/issues/ProtDos/Veilo.svg?style=for-the-badge
[issues-url]: https://github.com/ProtDos/Veilo/issues
[license-shield]: https://img.shields.io/github/license/ProtDos/Veilo.svg?style=for-the-badge
[license-url]: https://github.com/ProtDos/Veilo/blob/master/LICENSE.txt

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew

[product-screenshot]: images/screenshot.png

[React.js]: https://img.shields.io/badge/python-3670A0?logo=python&logoColor=ffdd54&style=for-the-badge
[React-url]: https://python.org/

[Vue.js]: https://img.shields.io/badge/flask-3670a0?style=for-the-badge&logo=python&logoColor=ffdd54
[Vue-url]: https://python.org/

[Angular.io]: https://img.shields.io/badge/kivy-3670a0?style=for-the-badge&logo=python&logoColor=ffdd54
[Angular-url]: https://python.org/

[Svelte.dev]: https://img.shields.io/badge/buildozer-3670a0?style=for-the-badge&logo=python&logoColor=ffdd54
[Svelte-url]: https://python.org/

[Java.l]: https://img.shields.io/badge/java-3670A0?logo=openjdk&logoColor=ffdd54&style=for-the-badge
[Java_L]: https://example.com
