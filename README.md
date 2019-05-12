# kano-i18n-sync

Scripts to allow bi-directional synchronization between [Kano
Linux](https://kano.me/) and the [Zanata](http://zanata.org/) translation
service. Upload strings to the translation server and pull latest translated
files from it into your Kano distribution.

We've created Zanata translation projects for the following apps:

* [kano-app-launcher](https://translate.zanata.org/project/view/kano-app-launcher/)
* [kano-apps](https://translate.zanata.org/project/view/kano-apps/)
* [kano-dashboard](https://translate.zanata.org/project/view/kano-dashboard/)
* [kano-feedback](https://translate.zanata.org/project/view/kano-feedback/)
* [kano-greeter](https://translate.zanata.org/project/view/kano-greeter/)
* [kano-init](https://translate.zanata.org/project/view/kano-init/)
* [kano-overworld](https://translate.zanata.org/project/view/kano-overworld/)
* [kano-peripherals](https://translate.zanata.org/project/view/kano-peripherals/)
* [kano-profile](https://translate.zanata.org/project/view/kano-profile/)
* [kano-settings](https://translate.zanata.org/project/view/kano-settings/)
* [kano-toolset](https://translate.zanata.org/project/view/kano-toolset/)
* [kano-updater](https://translate.zanata.org/project/view/kano-updater/)
* [kano-vnc](https://translate.zanata.org/project/view/kano-vnc/)
* [kano-widgets](https://translate.zanata.org/project/view/kano-widgets/)
* [make-snake](https://translate.zanata.org/project/view/make-snake/)
* [terminal-quest](https://translate.zanata.org/project/view/terminal-quest/)


## Setup

The scripts depend on
[zanata-python-client](https://github.com/zanata/zanata-python-client) to
communicate with the Zanata server. To install this executable on Fedora, run:

```
sudo dnf install python3-zanata-client
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
