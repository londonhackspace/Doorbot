Prerequisites
=============

```
 sudo apt-get install python-serial python-pyscard pcscd pcsc-tools python-lxml python-crypto python-daemon curl

 sudo wget http://ludovic.rousseau.free.fr/softwares/pcsc-tools/smartcard_list.txt -O /usr/share/pcsc/smartcard_list.txt
```

On some versions of Debian, edit:

```
 /usr/lib/pcsc/drivers/ifd-ccid.bundle/Contents/Info.plist
```

changing ifdDriverOptions from 0x0000 to 0x0004.

```
 sudo service pcscd restart

 pcsc_scan
```

For glados:

```
apt-get install mpg123 bplay alsa-oss
```

Then use alsamixer to boost the volume, don't forget to unmute ('m')!
