# Migaku Japanese Addon Updated
This project is an unofficial fork of the [Migaku Japanese Addon](https://github.com/migaku-official/Migaku-Japanese-Addon) aiming to be compatible with Anki 2.1.50+ (Qt6).
The plan for this project is to regularly update the addon to be compatible with the latest Anki version.   
I personally don't want to make any big improvements or implement new features, though feel free to create a PR/issue if you want to :).

## Changes
Changes from original project:
- Updated code to be compatible with Anki 2.1.50+ (QT6 version).
- Removed the Migaku message popup at startup.
- Added better descriptions to the generation buttons in the edit-card view.
- In the card browser under 'Edit', changed the name of the generation action to include `(Migaku Japanese)` so it's clear this action is from this addon.
- Changed the About page to make it clear this is a fork. Also include the new version at the title of the Migaku window.

Currently, the following functionality is broken (not sure if these were already broken in the original):
- (linux) Generation of Pitch Graphs.
- (linux) Generation of audio to Clipboard.

## Installation
### Uninstalling the previous version and installing the new Anki version
Note: all settings, except for the Overwrite Rules, will be removed during process. Make sure you have noted down your current settings or made screenshots before
proceeding.
1. Uninstall the previous Migaku Japanese Addon: go to `Tools` > `Add-ons`, select Migaku Japanese Addon and click `Delete`.  
1.1. You can also open the addons folder in this screen which we will use in step 5, click on `View Files`.
2. Close Anki
3. Download and install Anki 2.1.54 (Qt6) or newer from [their website](https://apps.ankiweb.net/).

### Installation of this addon
4. Download the Zip file and move the `Migaku-Japanese-Addon-Updated` folder into the `addons21` folder (you may have opened this folder in step 1.1).
5. Start Anki.
6. Go to `Migaku` > `Japanese Settings` to configure your settings.

## Contributing and bug reports
Contributions are welcome! Feel free to:
- Create an issue if you found a bug (please make sure you are using Anki version 2.1.50 or later in the QT6 edition)
- Create pull requests
- Participate in the Discussions 

## Credits
I would like to sincerely thank Migaku for creating the original addon and releasing the code under GPL-V3. 
Please check out their [website](https://www.migaku.io/), [patreon](https://www.patreon.com/Migaku) and [YouTube channel](https://www.youtube.com/c/ImmersewithMigaku).

## Licence
*Migaku Japanese Addon Updated* is

*Copyright © 2022 Mike Moolenaar  
*Copyright © 2020 Migaku ltd.

Migaku Japanese is free and open-source software. The add-on code that runs within Anki is released under the GNU AGPLv3 license, extended by a number of additional terms.  
Just like the original project, this fork is licenced under GPL-3.0. Please see the [LICENSE](https://github.com/MikeMoolenaar/Migaku-Japanese-Addon/blob/master/LICENSE) file that is accompanied by this program.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY.