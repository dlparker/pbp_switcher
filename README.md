# pbp_switcher - Monitor setup switcher tools for use with Pi Book Pro

# What does this do?

Automatically switches OS configuration to activate either Pi Book Pro or HDMI
monitor based on which is plugged in and which is "preferred". If you want to
normally run the Pi with out the Pi Book Pro attached, either headless or with
and HDMI monitor, but sometimes attach the PBP. this package is for you. Otherwise
you don't need it.

# How to do it

## For the impatient


1. Make sure your Pi Book Pro is plugged in and working as per [Pi Book Pro site setup page](https://pibookpro.com/pages/setup).
   you may want to [look here](https://github.com/dlparker/pbp_switcher#pre-install-setup-details) as well.
2. Make sure networking is working SSH is active on your Pi in case something goes wrong. 
3. Download this code:

   ```
   pi@raspberrypi:~ git clone https://github.com/dlparker/pbp_switcher.git
   ```
4. Install it:

   ```
   pi@raspberrypi:~ cd pbp_switcher
   pi@raspberrypi:~ sudo cd ./install.sh
   ```
If you like to live dangerously, you are done. If you like a little insurance,
run the [sanity check](https://github.com/dlparker/pbp_switcher#sanity-check)
before rebooting.

If the default configuration matches your Pi hardware and software
well enough, then you should be good to go. Now you can reboot your pi
with either the Pi Book Pro attached or the HDMI attached and the
switcher will detect which one is there and switch the OS config if
needed, then reboot. Then
[eventually](https://www.youtube.com/watch?v=YxBSUA5pUgg) you will see
the desktop on which ever one is attached. If both are attached the
switcher will choose the Pi Book Pro.

You can change the preference to select the HDMI monitor when both are attached with this command:

```
pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_set_mode.py -A -C hdmi
```
Or change it back with this command

```
pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_set_mode.py -A -C pibook
```

###### Why eventually?

The switch process can slow down the boot process because it has to reconfigure the system
and then reboot. It does this before the desktop is launched, so you don't see anything
on your screen until the second boot is complete.

For more details see [this](https://github.com/dlparker/pbp_switcher#why-this-stuff-this-way).

## List of command line tools

Each of these tools responds to the -h (--help) flag to provide a usage guide

1. /opt/pbp_switcher/bin/pbp_switcher.py - this switches the system
   reconfiguration to pibook or hdmi. Normally runs a boot before the
   desktop launches, but can be run manually to probe and test
   configuration or to manaully switch.
2. /opt/pbp_switcher/bin/pbp_set_mode.py - this writes the switcher
   config file telling the switcher what to do.
3. /opt/pbp_switcher/bin/pbp_detect.py - this probes the hardware and
   software configuation of your Pi to figure out what it looks like
   when Pi Book Pro and HDMI monitor are attached or detatched. Only
   needed if default configuration does not work.

## For the careful

## Sanity Check

This process is optional but highly recommended. If you skip this
sanity check everything may work fine for you, but if it doesn't you
might find it a bit of a hassel to restore things to the original
state.

After downloading and installing, do these two steps

###### Make sure pbp_switch can detect Pi Book Pro attachement

With your Pi Book Pro attached and displaying the desktop, also attach
the HDMI monitor. Remove any keyboard and mouse you have attached.

From a terminal on the Pi, or from an SSH connection, run this command sequence:

```
pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_set_mode.py -P
pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_switcher -c
```
The output of second command should look something like this:

```
need to see these lines in lsusb to confirm pi book pro attached: 
Bus 001 Device 005: ID 2e48:4293  
Bus 001 Device 004: ID 0603:0002 Novatek Microelectronics Corp. 
Bus 001 Device 006: ID 17e9:ff00 DisplayLink 
Bus 001 Device 003: ID 05e3:0610 Genesys Logic, Inc. 4-port hub
pi book pro attached state properly detected
evdi driver loaded and staged for loading at next boot
```

The last two lines are the most important. They tell you that the switcher
succeeded in detecting the Pi Book Pro hardware and that the driver
is where it needs to be in order to be loaded on next boot. 

If you do not see those last two lines, then you need to [manaully configure
the tools](https://github.com/dlparker/pbp_switcher#manual-configuration-for-when-the-default-configuration-does-not-work).

If that test worked, move on to the next test, which checks that the switcher can
detect that a monitor is attached to an HDMI port.

###### Make sure pbp_switch can detect HDMI monitor attachement

From a terminal on the Pi, or from an SSH connection, run this command sequence:

```
pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_set_mode.py -H
pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_switcher -c
```
The output of second command should look something like this:

```
need to ensure that check_for_hdmi does not look like:
 state 0x120001 [TV is off]

hdmi looks attached, tvservice says:
 state 0xa [HDMI CUSTOM RGB lim 16:9], 1280x720 @ 60.00Hz, progressive

hdmi is not in use because evdi driver is loaded
hdmi will not be used on reboot because evdi driver will be loaded

```

The details reported in the second line that begins with "state" are
likely to be different, depending your specific monitor. The main thing
is that it should not match the first "state" line.

If you do not see a difference in those two lines, then you can try to [manaully configure
the tools](https://github.com/dlparker/pbp_switcher#manual-configuration-for-when-the-default-configuration-does-not-work).

If both of these tests worked, it is likely that the auto switching operation
will work too, so you can restore the default auto switch config with this command:

```
pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_set_mode.py -A -C pibook
```


## CAVEATS

These tools and instructions have only been tested on a Raspberry Pi 4
B running Raspberry Pi OS (Raspbian) Buster as released 2020-8-24, so
make no assumptions that they will work on other hardware or
releases.

Having said that, the functions performed by the scripts are
pretty generic system configuration operations such as
installing/uninstalling kernel drivers and operating under systemd
control, so it is likely to work on any recent Raspbian distro, and
maybe on other Debian based distros too.

I know of nothing different about the Pi 3 vs the Pi 4 that should
break this code, but it has not been tested. 

[Details of the Need and Design](https://github.com/dlparker/pbp_switcher#why-this-stuff-this-way)

# What if it doesn't work

## The kill switch

If it doesn't work, and you want to return your Pi to the original state and uninstall this toolset,

   ```
   pi@raspberrypi:~ cd pbp_switcher   # (wherever you did your git clone)
   pi@raspberrypi:~ sudo ./uninstall.sh
   ```

You can try some of the stuff that follows, and you might be able to get it to work. You can always
uninstall if you get sick of fiddling with it.

## Known issues

###### The Pi Book Pro does not show the desktop

Sometimes on my setup the desktop does not show up when the Pi Book
Pro is attached at boot.  If I am running a VNC connection I can see
that the screen size is set to something tiny (320x240 I think).
Although this happens most often after switching from HDMI mode to
Pi Book Pro mode, it sometimes happens when I was already booted in
Pi Book Pro mode and just rebooted normally. 

When it happens I run:

```
pi@raspberrypi:~ sudo systemctl restart display-manager.service
```

If you are running VNC you can type this into a tiny little terminal
window. Or you can do it after connecting to your pi with SSH.

Maybe some future version of this tool set will add some sort of detect and
fix tool for this condition. It might be possible to just use xrandr to
force the resolution to match what the Pi Brook Pro expects, in the event that
it is detected and configured. This would have to run after Xorg startup, of
course, so probably something you have to put in your .profile or some other
post desktop startup mechanism.

###### VNC displays only a tiny screen if neither monitor type is attached.

It does not matter which mode the switcher has activated, if the target monitor is
not attached, then VNC only displays a tiny screen size, probably 320x240. I don't
know if this is a side effect of this mode switching process, or if it is expected on
a Pi 4. I think maybe the latter. Future versions of this tool set may offer a
solution to this, but for now you are on your own.

## Manual configuration for when the default configuration does not work

The first step in debugging these tools is to try to execute the switcher tool
manually to see what it does, as it may be having trouble when running during boot.

###### Manual switching

1. First return your Pi to a working state with both an HDMI monitor and your Pi Book Pro
   attached and with the Pi Book Pro displaying. If your Pi Book Pro no longer works, uninstall
   the display-link driver and reinstall it.

   ```
   pi@raspberrypi:~ displaylink-installer uninstall
   ```
   Reinstall according to the original instructions.


2. You should be able to run the switcher manaully to switch from whatever display is currently
   active to the other one. For example, if you have the Pi Book Pro displaying, then run these commands:

```
pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_set_mode.py -H
pi@raspberrypi:~ sudo /opt/pbp_switcher/bin/pbp_switch.py -u -n --force
```

The first one sets the target mode to HDMI. The second runs the switcher with the flags meaning
1. -u means update the system configuration to match the target display mode
2. -n means do not reboot after switching
3. --force means ignore the normal comparison of the current configuation with the expected state. This is normally not a good idea but    if used carefully it can uncover problems without creating any new ones.

The second command should product output such as this:

```
hdmi will not be used on reboot because evdi driver will be loaded
saving and deleting evdi driver file and running depmod, reboot required to remove it
not rebooting though reboot is required

```

If your output looks like this, this means that the switcher is able
to perform the OS configuration change steps without error as needed
to disable the Pi Book Pro. This should re-enable
the HDMI monitor.

If you don't get this output you'll probably get some kind of error.
In any event you are stuck for now, since the logic for switching does
not work.

Make sure you have followed all the instructions up to now
exactly, and if you have then create an issue and include the output
of the second command above. I make no guarantee that I will be able
to fix it soon, or indeed at all, but I promise to take a look and see
if there is anything I can do. This is just a hobby project for me, so
don't get to excited about the possibility of support for your issue.

If it does work, you can then switch back to your original working configuration
by running these commands:

```
pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_set_mode.py -P
pi@raspberrypi:~ sudo /opt/pbp_switcher/bin/pbp_switch.py -u -n --force
```

You should see output like this:

```
evdi driver not ready for next boot, need to install
restoring evdi driver file and running depmod
not rebooting though reboot is required
```

If your output looks like this, this means that the switcher is able
to perform the OS configuration change steps without error as needed
to enable the Pi Book Pro. This should disable the HDMI monitor.

If both of these tests worked, then you have proven that the pbp_switcher
is able to perform the switching steps without error. If the auto switching
on reboot does not work,  it probably means that the
configuration detection operations are not working.

Go back to the
[sanity check](https://github.com/dlparker/pbp_switcher#sanity-check) steps
and carefully compare your output to the example output provided. This
may provide a clue to what is not working. 

If you detect something that does not look right in the sanity test, you
might be able to fix the problem by generating your own comparison data
for the detector logic. 

###### Manually creating detect modes

The configuration check logic in the pbp_switcher.py tool relies on pre-generated
comparison data. It compares the output of some command line tools with data stored
in the file /opt/pbp_switcher/detected_modes.json to identify the current state. It
uses the "lsusb" command to check for the presence of the Pi Book Pro, and the "tvservice"
command to check for the presence of an HDMI monitor. It checks for the EVDI driver (displaylink)
configuration but using "lsmod" to find out if it is currently loaded and by looking in the
file system to see if it is in the right place to be re-loaded at next boot.

When the install process runs the detected_mods.json file is created by copy from the
"default_modes.json" and both are added to the /opt/pbp_switcher directory.

You can modify the detected_mods.json file to contain comparison data generated on your
own system.

The process of manually generating this data will be a bit tedious, as you
have to reboot five times between runs of the detector tool.

Run this tool to get instructions on how to do this:
```
pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_set_mode.py -i
```

Here is the recommended process:

1. Ensure that the Pi Book Pro is attached and working. Attach the HDMI monitor but remove
   any USB connected devices that may not always be present, such as keyboards, mice, external
   USB hubs, etc.

   Reboot
   
2. Ensure that the Pi Book Pro is still displaying. Run the detection tool:
   ```
   pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_detect.py --pibook_and_hdmi (or -B)
   ```

3. Disconnect the HDMI monitor, reboot and run:
   ```
   pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_detect.py --pibook (or -P)
   ```

3. Reattach the HDMI monitor, and configure the system to boot with HDMI selected:
   ```
   pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_set_mode.py -H
   pi@raspberrypi:~ sudo /opt/pbp_switcher/bin/pbp_switch.py -u -n --force
   ```
   Now reboot.

4. Run the detection tool:

   ```
   pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_detect.py --hdmi_and_pibook (or -b)
   ```

5. Disconnect the Pi Book Pro reboot, then run the tool:

   ```
   pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_detect.py --hdmi (or -H)

   ```

6. Disconnect the HDMI monitor, reboot and then run the tool (you may have to use SSH to do this):
   ```
   pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_detect.py --virtual (or -V)

   ```


Your /opt/pbp_switcher/detected_modes.json file will now contain the results of each run. This may
fix your auto select problem. You can try the steps in the
[sanity check](https://github.com/dlparker/pbp_switcher#sanity-check). If the output looks good,
auto select will probably work now.

If you don't see good results with the sanity check, then you may be out of luck unless you want
to do some coding.

###### How auto detect drives auto switching

The auto detect process answers two configuration questions:

1. What hardware is attached, Pi Book Pro, HDMI, nothing?

2. Is the displaylink driver installed and ready for use on reboot?

The hardware question is resolved by comparing the output of the lsusb
and tvservice commands to the stored versions in the
/opt/pbp_switcher/detected_modes.json file.

The presence of the pi book pro is detected by comparing the lsusb
output stored for the pibook pro attached mode to the lsusb output
stored for the hdmi attached mode. The logic assumes that the pibook
mode will have more lsusb lines than the hdmi mode when the pibook
is not attached. These might be called "trigger lines".
The current lsusb output is compared to this set and if the current
output contains the "trigger lines" then the Pi Book Pro is considered
detected. If it does not contain those lines then the Pi Book Pro is
considered detached.

The presence of the HDMI monitor is done by comparing the output of
the "tvservice" command in a similar way. The detected_modes.json
file contains the results of running this command in both attached
and detached conditions. In this case, however, the compare logic
is to consider the HDMI monitor attached if the current output
of the tvservice command is anything other than the output recorded
when only the Pi Book Pro was attached. That recorded version is
always the same, whereas the tvservice output recorded when an HDMI
monitor is attached will vary with which monitor is in use. 

If any of this is not working for you, then you may want to build your own
copy of the BaseCompare class in the compares.py file in the source
directory. Consider forking the repository so you can share your work.
If you make changes and get them to work you can submit a pull request.

# The TLDR; stuff

###### pre-install setup details

1. Install according to the instructions on the [Pi Book Pro site setup page](https://pibookpro.com/pages/setup)
  - Note that on my Pi 4 with the version of Raspbian I am useing, the xrandr commands did not work, but they
    also were not necessary. I just installed the DisplayLink driver, plugged in my Pi Book Pro, turned it on,
    rebooted, and everything worked. I did not have to disconnect the HDMI monitor.
  - Once you have it working, you will no longer see anything on the HDMI monitor, but your Pi Book Pro will
    show the desktop once boot is complete. You will not see the boot text messages or the splash screen, you
    will just have a blank screen until the desktop. If you don't see the desktop, read
    [this](https://github.com/dlparker/pbp_switcher#the-pi-book-pro-does-not-show-the-desktop)


###### Why do tools need sudo access?

The install tool needs sudo access to create the root directory and
to install the systemd services unit definition file. The switcher
tools need sudo access because they manipulate the EVDI driver that is
used to provide DisplayPort functionality over USB 3. The tools
install and uninstall the driver file according to which display is
requested, and this is a root level access task.

If you are concerned about giving root access to these tools, then you
should take a look at the code. The are Python and use nothing but
Python standard library functions, no additional libraries are
used. The code is therefore completely transparent so you should be
able to decide for yourself if the operations are safe. Furthermore,
the code has been written in a very plain style and uses very few
Python specific idioms, so you can probably follow the logic even
if you do not write Python.


###### Why this stuff this way?

The need for these tools is due to the fact that the Pi Book Pro depends
on the DisplayLink driver, and that driver has no provision for been
loaded but disabled. I don't know why this is true, but it also disables
the HDMI drivers when it is loaded. That means that the only way that I
could find to re-enable the HDMI ports is to reboot the Pi without loading
the DisplayPort driver.

The actual name of the driver in question is "evdi". You can find the
home page for it at [https://github.com/DisplayLink/evdi](https://github.com/DisplayLink/evdi).
Note that the readme file there points out that this driver is not the
complete DisplayLink driver, even though it is a key part.

So the basic operating technique of these tools is to add or remove the
driver file from the directory where it gets loaded at boot time and to
run the depmod tool to rebuild the module dependency data used at boot time.

So if the switch from one mode to another is actually made, it is always
necessary to reboot in order for this to take affect. Be aware that you
can build a nice infinite reboot loop if you mess with this code and
are not careful about how reboot is triggered.

###### Infinite reboot prevention needed

A nice enhancement for this tool set might be some kind of mechanism
that detects and prevents this problem. Maybe a file that records the
reason for the last reboot and interrupts the reboot process if it the
same reason triggers reboot twice?

Addition operations revolve around running the lsusb and tvservice commands
in order to determine which pieces of hardware are actually attached. 
