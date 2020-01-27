# kano-i18n-sync

Scripts to allow bi-directional synchronization between [Kano
Linux](https://kano.me/) and the [Zanata](http://zanata.org/) translation
service. Upload strings to the translation server and pull latest translated
files from it into your Kano distribution.

We've created Zanata translation projects for the following apps:

* [kano-apps](https://translate.zanata.org/project/view/kano-apps/) - Launcher for different utilities ([code repository](https://github.com/KanoComputing/kano-apps))
* [kano-dashboard](https://translate.zanata.org/project/view/kano-dashboard/)
* [kano-feedback](https://translate.zanata.org/project/view/kano-feedback/) - Tool to report feedback and bugs ([code repository](https://github.com/KanoComputing/kano-feedback))
* [kano-greeter](https://translate.zanata.org/project/view/kano-greeter/) - Python greeter for Kano OS ([code repository](https://github.com/KanoComputing/kano-greeter))
* [kano-init](https://translate.zanata.org/project/view/kano-init/) - Initialize a fresh installation of the Kanux OS on a Kano kit ([code repository](https://github.com/KanoComputing/kano-init))
* [kano-overworld](https://translate.zanata.org/project/view/kano-overworld/)
* [kano-peripherals](https://translate.zanata.org/project/view/kano-peripherals/) - Support code for peripherals ([code repository](https://github.com/KanoComputing/kano-peripherals))
* [kano-profile](https://translate.zanata.org/project/view/kano-profile/) - Tool to communicate with Kano-World ([code repository](https://github.com/KanoComputing/kano-profile))
* [kano-settings](https://translate.zanata.org/project/view/kano-settings/) - Graphic tool to setup Kanux ([code repository](https://github.com/KanoComputing/kano-settings))
* [kano-toolset](https://translate.zanata.org/project/view/kano-toolset/) - Shared toolset for OS appsd ([code repository](https://github.com/KanoComputing/kano-toolset))
* [kano-updater](https://translate.zanata.org/project/view/kano-updater/) - Update Kano Linux ([code repository](https://github.com/KanoComputing/kano-updater))
* [kano-vnc](https://translate.zanata.org/project/view/kano-vnc/) - VNC wrapper for Kano OS ([code repository](https://github.com/KanoComputing/kano-vnc))
* [kano-widgets](https://translate.zanata.org/project/view/kano-widgets/) - Kano LXPanel widgets ([code repository](https://github.com/KanoComputing/kano-widgets))
* [make-art](https://translate.zanata.org/project/view/make-art/) - App to learn programming using a basic CoffeeScript drawing API ([code repository](https://github.com/KanoComputing/make-art))
* [make-snake](https://translate.zanata.org/project/view/make-snake/) - Snake game running on the terminal ([code repository](https://github.com/KanoComputing/make-snake))
* [terminal-quest](https://translate.zanata.org/project/view/terminal-quest/) - Introduction to terminal commands in the style of a text adventure game ([code repository](https://github.com/KanoComputing/terminal-quest))


## Setup

The scripts depend on
[zanata-python-client](https://github.com/zanata/zanata-python-client) to
communicate with the Zanata server and [polib](https://polib.readthedocs.io/)
to work with translation files. It also needs
[paramiko](http://www.paramiko.org/) to connect to the Kano computer via SSH
and [pyyaml](https://pyyaml.org/) to read yaml files.  To install these
packages on Fedora, run:

```
sudo dnf install python3-zanata-client python3-polib python3-paramiko python3-pyyaml
```

[Create yourself an account on
Zanata](https://translate.zanata.org/account/register) if you haven't done so,
[generate your API
key](https://translate.zanata.org/dashboard/settings/client), and copy the
content of `zanata.ini` that you need to place in a new file named
`$HOME/.config/zanata.ini`

Now you need to prepare your Kano computer so that the scripts can connect to
it. To turn on the SSH server on the Kano box, go to the `Advanced` setting and
enable SSH. From the computer that is going to run the scripts, add a `kano`
host to your `$HOME/.ssh/config` file, for instance:

```
Host kano
  Hostname 192.168.1.15
  User your_username
```

Finally, copy your keys to the Kano computer:
```
ssh-copy-id kano
```

Verify you're able to connect to your Kano computer with:
```
ssh kano
```

## Usage

### Upload updated translation templates upon new Kano release

The `sync_pot.py` script connects to the Kano computer to retrieve the latest
translation templates then takes care of creating the project and new versions
on Zanata, before uploading the template files to it.

It is intended for the admins for the translation projects on Zanata and should
be run each time Kano release a new version of their distribution.

The script does not take options, simply invoke it with:

```
./sync_pot.py
```

### Pull latest translations from Zanata and update Kano

The `pull_translations.py` script does more or less the opposite. It pulls the
latest translated content from Zanata and copies it to the Kano computer in
a format that Kano understands.

This is intended for Kano users and can be run any time to update translations
to their latest version.

You need to pass it a locale name that is valid on the Zanata server, for
instance:

```
./pull_translations.py fr
```
