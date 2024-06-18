# Running Linux on the Lenovo Yoga Pro 9i Gen 9 (16IMH9)

Here are some notes for running Linux on this laptop. This guide was primarily designed for the Gen 9 with the MiniLED screen, but it may also be helpful for the Gen 8 or similar laptops from Lenovo. Currently, KDE Plasma is recommended (refer to the Screen section) for the optimal experience.

This guide was done on the Fedora 40 based distribution [Aurora](https://getaurora.dev/) using Wayland.

## Feature Compatibility Table

| Feature                 | Status            | Notes                                                                                                  |
| ----------------------- | ----------------- | ------------------------------------------------------------------------------------------------------ |
| Screen                  | Needs configuring | Requires KDE Plasma for correct colors                                                                 |
| Speakers                | Needs configuring | Subwoofer is disabled by default due to a bug                                                          |
| Battery                 | Works             | Good battery life; better with refresh rate set to 60Hz                                                |
| Keyboard                | Works             | Includes backlight adjustment in GNOME and KDE                                                         |
| Camera                  | Works             |                                                                                                        |
| Touchpad                | Works             |                                                                                                        |
| Intel GPU               | Works\*           | Newer Mesa version may be required                                                                     |
| Microphone              | Works\*           | Add Speech processor via EasyEffects for higher volume                                                 |
| Windows Hello IR Camera | Needs configuring | Detected out of the box; configuring [howdy](https://github.com/boltgolt/howdy) can be a bit difficult |
| Nvidia GPU              | Works\*           | Stability issues on GNOME with Fedora 40; KDE Plasma works perfectly                                   |
| Ports                   | Works             |                                                                                                        |

## Screen

This laptop features a wide gamut display. However, the display controller cannot accept an sRGB signal directly. To achieve accurate colors, a compositor with color management support is necessary. Currently, this means using KDE Plasma. Download the modified ICC profile from [here](https://github.com/maximmaxim345/yoga_pro_9i_gen9_linux/raw/main/LEN160_3_2K_cal-linux.icc), save it somewhere safe, and select it under `Display & Monitor > Color Profile`.

<details>
    <summary>More Information About the Profile and Wide Gamut Support</summary>
The issue arises because this laptop has a wide gamut display, which is closely related to HDR, a feature still under heavy development on Linux.

On this laptop under Windows, ACM (Auto Color Management) is enabled by default. ACM transforms colors from sRGB to BT.2020 (the screen's color space). As a result, calibration files created under Windows only work correctly on Windows. Even the display's built-in EDID information assumes Windows with ACM enabled (note the Gamma field, which is set to 2.2 instead of 2.4).

High gamut displays use different primary colors for their subpixels, allowing the screen to display more colors than an sRGB display. For example, the red subpixel has a higher wavelength, making 0xff0000 appear more "red" than on an sRGB display. To correct this, we need to slightly enable the green subpixel (e.g., 0xff0900). Simple color management (like in most other desktops/WMs) can only adjust each subpixel individually.

I converted the profiles using iccToXml. I took the VCGT table from NotebookCheck, the primaries (the wavelengths of the subpixels) from the BT.2020 reference profile (not exactly correct but still very good), and set the gamma to 2.46 (Windows hides the true gamma, so the NotebookCheck profile had 2.2, BT.2020 has 2.4, and I increased it to 2.46 to mimic the default Intel Control Center settings). I then converted this XML back to an ICC using iccFromXml.

Colors now look very similar to an individually calibrated screen I also have. However, this color profile will only work on KDE Plasma for now (and maybe the latest build of Sway), as transforming sRGB to BT.2020 is required.

</details>

The screen supports VRR from 48-165Hz. I have Adaptive Sync set to "Always," which results in slightly better battery life.

As I know, HDR is currently disabled for internal screens on Intel Arc GPUs due to a bug. This should change in the future.

## Speakers

Speakers require some configuration. These instructions are based on [this issue](https://github.com/karypid/YogaPro-16IMH9/issues/2) and [this discussion](https://bugzilla.kernel.org/show_bug.cgi?id=217449)

### Configuration Steps

1. Create a systemd service file by copying the following command into a terminal:

   ```bash
   sudo tee /etc/systemd/system/yoga-16imh9-speakers.service <<EOF
   [Unit]
   Description=Turn on speakers using i2c configuration

   [Service]
   User=root
   Type=oneshot
   ExecStart=/bin/sh -c "/usr/local/bin/2pa-byps.sh 2 | logger"

   [Install]
   WantedBy=multi-user.target
   EOF
   ```

2. Create the script `/usr/local/bin/2pa-byps.sh`, copy the following command into a terminal:

   ```bash
   sudo tee /usr/local/bin/2pa-byps.sh <<'EOF'
   #!/bin/sh

   clear
   function clear_stdin() {
       old_tty_settings=$(stty -g)
       stty -icanon min 0 time 0
       while read -r none; do :; done
       stty "$old_tty_settings"
   }

   if [ $# -ne 1 ]; then
       echo "Kindly specify the i2c bus number. The default i2c bus number is 3."
       echo "Command as following:"
       echo "$0 i2c-bus-number"
       i2c_bus=3
   else
       i2c_bus=$1
   fi

   echo "i2c bus is $i2c_bus"
   i2c_addr=(0x3f 0x38)

   count=0
   for value in "${i2c_addr[@]}"; do
       val=$((count % 2))
       i2cset -f -y "$i2c_bus" "$value" 0x00 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x7f 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x01 0x01
       i2cset -f -y "$i2c_bus" "$value" 0x0e 0xc4
       i2cset -f -y "$i2c_bus" "$value" 0x0f 0x40
       i2cset -f -y "$i2c_bus" "$value" 0x5c 0xd9
       i2cset -f -y "$i2c_bus" "$value" 0x60 0x10
       if [ $val -eq 0 ]; then
           i2cset -f -y "$i2c_bus" "$value" 0x0a 0x1e
       else
           i2cset -f -y "$i2c_bus" "$value" 0x0a 0x2e
       fi
       i2cset -f -y "$i2c_bus" "$value" 0x0d 0x01
       i2cset -f -y "$i2c_bus" "$value" 0x16 0x40
       i2cset -f -y "$i2c_bus" "$value" 0x00 0x01
       i2cset -f -y "$i2c_bus" "$value" 0x17 0xc8
       i2cset -f -y "$i2c_bus" "$value" 0x00 0x04
       i2cset -f -y "$i2c_bus" "$value" 0x30 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x31 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x32 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x33 0x01

       i2cset -f -y "$i2c_bus" "$value" 0x00 0x08
       i2cset -f -y "$i2c_bus" "$value" 0x18 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x19 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x1a 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x1b 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x28 0x40
       i2cset -f -y "$i2c_bus" "$value" 0x29 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x2a 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x2b 0x00

       i2cset -f -y "$i2c_bus" "$value" 0x00 0x0a
       i2cset -f -y "$i2c_bus" "$value" 0x48 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x49 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x4a 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x4b 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x58 0x40
       i2cset -f -y "$i2c_bus" "$value" 0x59 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x5a 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x5b 0x00

       i2cset -f -y "$i2c_bus" "$value" 0x00 0x00
       i2cset -f -y "$i2c_bus" "$value" 0x02 0x00
       count=$((count + 1))
   done
   clear_stdin
   EOF
   ```

3. Make the script executable:

   ```bash
   sudo chmod +x /usr/local/bin/2pa-byps.sh
   ```

4. Enable and start the service:

   ```bash

   sudo systemctl daemon-reload
   sudo systemctl enable yoga-16imh9-speakers.service
   sudo systemctl start yoga-16imh9-speakers.service
   ```

For better audio quality, you can also use [this EasyEffects profile](https://github.com/maximmaxim345/yoga_pro_9i_gen9_linux/raw/main/Yoga%20Pro%209i%20gen%209.json).

If the file opens in your browser, right-click the link and select "Save link as..." to download it. You can get EasyEffects from [Flathub](https://flathub.org/apps/com.github.wwmm.easyeffects). Select the json file under `Presets > Import a preset` button, when in the `Output` tab, and load it.

<details>
    <summary>Details about the profile</summary>

    Measured in two accustically different rooms while sitting on a desk using a calibrated Sonarworks SoundID microphone.
    Made using REW.

    Uses the Dr. Olive Toole Target curve until 271Hz. Sounds very natural and balanced. Still has some sub bass hearable.
    Pretty good for a laptop speaker.

</details>

## Battery

I have good battery life, more or less equal to Windows. If you need more battery, set the refresh rate to 60Hz. This results in:

| Activity               | Battery Life |
| ---------------------- | ------------ |
| Idle                   | 10h          |
| Light use              | 8h           |
| Programming            | 6h 30m       |
| YouTube video playback | 6h 30m       |

## Keyboard

Everything works out of the box, including backlight adjustment in GNOME and KDE.

## Camera

Works out of the box.

## Touchpad

Works out of the box with good palm rejection.

## Intel GPU

Works mostly. Mesa version 24.0.9 gives the error `MESA-INTEL: warning: cannot initialize blitter engine` when running `vulkaninfo --summary`. However, version 24.1.1 works without problems (tested in a distrobox with arch linux)

## Microphone

A bit quiet by default, add a `Speech Processor` via EasyEffects to boost the volume.
This laptop has a quad mic array, further investigation is needed for noise cancellation.

## Windows Hello IR Camera

The IR camera is detected out of the box. Configuring [howdy](https://github.com/boltgolt/howdy) is rather complicated. See [here](https://copr.fedorainfracloud.org/coprs/principis/howdy-beta/) or [here](https://wiki.archlinux.org/title/Howdy) for setup instructions. I have had success running the beta version. You will also need [linux-enable-ir-emitter](https://github.com/EmixamPP/linux-enable-ir-emitter) for the IR emitter to work.

## Nvidia GPU

Works with the appropriate drivers depending on your distribution. I have some stability issues on GNOME with Fedora 40 (opening [Mission Center](https://flathub.org/apps/io.missioncenter.MissionCenter) and some other apps crashes the session).
Plasma works perfectly with the Nvidia GPU.

## Ports

Works out of the box, could not test Thunderbolt. Should however [work](https://github.com/karypid/YogaPro-16IMH9).
