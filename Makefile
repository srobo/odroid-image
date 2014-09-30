
boot.scr: boot.in
	mkimage -A arm -T script -C none -n "SR boot.scr for ODROID-U3" -d boot.in boot.scr
