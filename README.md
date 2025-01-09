# Running Linux on the Lenovo Yoga Pro 9i Gen 9 (16IMH9)

Here are some notes for running Linux on this laptop. This guide was primarily designed for the Gen 9 with the MiniLED screen, but it may also be helpful for the Gen 8 or similar laptops from Lenovo.

This guide was done on the Fedora 40 based distribution [Aurora](https://getaurora.dev/) using Wayland.

Both GNOME and Plasma 6 work great with wayland, any other DE/WM should work as well.

## Feature Compatibility Table

| Feature                 | Status                          | Notes                                                                                                  |
| ----------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Screen                  | Will soon work\*                | Requires linux kernel 6.11 or newer; or alternatively KDE Plasma                                       |
| Speakers                | Needs configuring               | Subwoofer is disabled by default due to a bug                                                          |
| Nvidia GPU              | Needs configuring               | Install drivers and enable suspend services (depending on distrobution)                                |
| Windows Hello IR Camera | Needs configuring               | Detected out of the box; configuring [howdy](https://github.com/boltgolt/howdy) can be a bit difficult |
| Battery                 | Works                           | Good battery life; better with refresh rate set to 60Hz; conservative battery limit can be enabled     |
| Keyboard                | Works                           | Includes backlight adjustment in GNOME and KDE                                                         |
| Camera                  | Works                           |                                                                                                        |
| Touchpad                | Works                           |                                                                                                        |
| Intel GPU               | Works, with some instability    | with MESA version >24.1.1                                                                              |
| Microphone              | Works\*                         | Add Speech processor via EasyEffects for higher volume                                                 |
| Ports                   | Works                           |                                                                                                        |
| Wifi/Bluetooth          | Works                           |                                                                                                        |
| Proximity Sensor        | Not supported                   |

## Screen

This laptop is produced in some configurations with the same model number, but slightly different internal components.
Some configurations already work in prior versions, but others have oversaturated colors (especially red).

This problem will presumably be fixed in the linux kernel version 6.11 (tested on drm-tip). The screen now (on drm-tip) works correctly, including working HDR support.

If you experience issues with colors and do not have a kernel prior to 6.11, you can use [this](https://github.com/maximmaxim345/yoga_pro_9i_gen9_linux/raw/main/LEN160_3_2K_cal-linux.icc) icc profile (only works on KDE Plasma) which transform everything on screen to bt.2020. Save it somewhere safe, and select it under `Display & Monitor > Color Profile`. After the update to 6.10 or newer, just remove the icc profile again.

The screen supports VRR from 48-165Hz. I have Adaptive Sync set to "Always," which results in slightly better battery life.

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
   RemainAfterExit=yes
   ExecStart=/bin/sh -c "/usr/local/bin/2pa-byps.sh | logger"

   [Install]
   WantedBy=multi-user.target
   EOF
   ```

2. Install or ensure the `i2c-tools` package is installed

   Depending on your Linux distribution, use one of the following commands:

   For Debian/Ubuntu based distributions:

   ```bash
   sudo apt update
   sudo apt install i2c-tools
   ```

   For Fedora:

   ```bash
   sudo dnf install i2c-tools
   ```

   For Fedora Atomic Desktop:

   ```bash
   sudo rpm-ostree install i2c-tools
   ```

   For Arch Linux:

   ```bash
   sudo pacman -Sy i2c-tools
   ```

3. Create the script `/usr/local/bin/2pa-byps.sh`, copy the following command into a terminal:

   ```bash
   sudo tee /usr/local/bin/2pa-byps.sh <<'EOF'
   #!/bin/bash

   export TERM=linux
   # Some distros don't have i2c-dev module loaded by default, so we load it manually

   modprobe i2c-dev
   # Function to find the correct I2C bus (third DesignWare adapter)
   find_i2c_bus() {
       local adapter_description="Synopsys DesignWare I2C adapter"
       local dw_count=$(i2cdetect -l | grep -c "$adapter_description")
       if [ "$dw_count" -lt 3 ]; then
           echo "Error: Less than 3 DesignWare I2C adapters found." >&2
           return 1
       fi
       local bus_number=$(i2cdetect -l | grep "$adapter_description" | awk '{print $1}' | sed 's/i2c-//' | sed -n '3p')
       echo "$bus_number"
   }
   i2c_bus=$(find_i2c_bus)
   if [ -z "$i2c_bus" ]; then
       echo "Error: Could not find the third DesignWare I2C bus for the audio IC." >&2
       exit 1
   fi
   echo "Using I2C bus: $i2c_bus"
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
   EOF
   ```

4. Make the script executable:

   ```bash
   sudo chmod +x /usr/local/bin/2pa-byps.sh
   ```

5. Enable and start the service:

   ```bash

   sudo systemctl daemon-reload
   sudo systemctl enable --now yoga-16imh9-speakers.service
   ```

For better audio quality, you can also use [this EasyEffects profile](https://github.com/maximmaxim345/yoga_pro_9i_gen9_linux/raw/main/Yoga%20Pro%209i%20gen%209%20v2.json). If you have problems with too much vibrations use [this profile](https://github.com/maximmaxim345/yoga_pro_9i_gen9_linux/raw/main/Yoga%20Pro%209i%20gen%209%20v2%20less%20bass.json) instead.

If the file opens in your browser, right-click the link and select "Save link as..." to download it. You can get EasyEffects from [Flathub](https://flathub.org/apps/com.github.wwmm.easyeffects). Select the json file under `Presets > Import a preset` button, when in the `Output` tab, and load it.

<details>
    <summary>Details about the profile</summary>

    Measured in two accustically different rooms while sitting on a desk using a calibrated Sonarworks SoundID microphone.
    Made using REW.

    Measures flat from 400Hz with a 12dB/oct falloff (18dB/oct for the less bass version)

</details>

## Nvidia GPU

Works. Both KDE and GNOME tested (with wayland).

Fix suspend issues by running:

```bash
sudo systemctl enable nvidia-hibernate.service nvidia-resume.service nvidia-suspend.service
```

## Windows Hello IR Camera

The IR camera is detected out of the box. Configuring [howdy](https://github.com/boltgolt/howdy) is rather complicated. See [here](https://copr.fedorainfracloud.org/coprs/principis/howdy-beta/) or [here](https://wiki.archlinux.org/title/Howdy) for setup instructions. I have had success running the beta version. You will also need [linux-enable-ir-emitter](https://github.com/EmixamPP/linux-enable-ir-emitter) for the IR emitter to work.

## Battery

I have good battery life, more or less equal to Windows. If you need more battery, set the refresh rate to 60Hz. This results in:

| Activity               | Battery Life |
| ---------------------- | ------------ |
| Idle                   | 10h          |
| Light use              | 8h           |
| Programming            | 6h 30m       |
| YouTube video playback | 6h 30m       |

### Limit battery charging threshold

You can enable the battery conservation mode, which limits the maximum battery charge level to around 80%, to prolong battery lifespan.

You can setup a service by running:

```bash
sudo tee /etc/systemd/system/yoga-16imh9-battery-limit.service <<EOF
[Unit]
Description=Battery Conservation Mode

[Service]
User=root
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c 'echo 1 > /sys/bus/platform/drivers/ideapad_acpi/VPC2004:*/conservation_mode'
ExecStop=/bin/bash -c 'echo 0 > /sys/bus/platform/drivers/ideapad_acpi/VPC2004:*/conservation_mode'

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
```

After that, run this command anytime you want to enable conservative mode (will also be automatically applied on boot):

```bash

sudo systemctl enable --now yoga-16imh9-battery-limit.service
```

And to disable it again, run:

```bash

sudo systemctl disable --now yoga-16imh9-battery-limit.service
```

## Keyboard

Everything works out of the box, including backlight adjustment in GNOME and KDE.

## Camera

Works out of the box.

## Touchpad

Works out of the box with good palm rejection.

## Intel GPU

Works with MESA version 24.1.1 and later.
Some hangs may occur from time to time (tested on Plasma), [this is a known issue in mesa](https://gitlab.freedesktop.org/drm/i915/kernel/-/issues/10395).
No issues on GNOME.

This is issue easily reproducible:

1. Start KDE Plasma with Wayland and the [kzones](https://github.com/gerritdevriese/kzones) kwin script enabled.
2. Connect/disconnect an external monitor. Or alternatively change the Scale of the laptop screen.
3. Try to move a window.
4. Observe the indefinite hang. If it does not hang, try again from step 2.

## Microphone

A bit quiet by default, add a `Speech Processor` via EasyEffects to boost the volume.
This laptop has a quad mic array, further investigation is needed for noise cancellation.

## Ports

Works out of the box.

## Thunderbolt

Tested on the [DELL WD19TB](https://www.dell.com/support/home/en-us/product-support/product/dell-wd19tb-dock/overview) and works out of the box (network, ports etc).  
However, eventhough the laptop appears to be charging, the battery status on PopOS does not say so.

## Wifi/Bluetooth

Works out of the box.

## Proximity Sensor

This laptop also has a proximity sensor, which can be used to lock the screen when you walk away from it. This is not yet supported on Linux.
