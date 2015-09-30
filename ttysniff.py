#!/usr/bin/env python3

import sys
import os
import termios

import hexdump

opt_hex_output = False

#port = "/dev/ttyUSB0"
#port = "/dev/ttyS0"
baud = 9600

# lifted the names from the Linux termios manpage
iflag_names = {
	termios.IGNBRK: "IGNBRK",
	termios.BRKINT: "BRKINT",
	termios.IGNPAR: "IGNPAR",
	termios.PARMRK: "PARMRK",
	termios.INPCK: "INPCK",
	termios.ISTRIP: "ISTRIP",
	termios.INLCR: "INLCR",
	termios.IGNCR: "IGNCR",
	termios.ICRNL: "ICRNL",
#	termios.IUCLC: "IUCLC",
	termios.IXON: "IXON",
	termios.IXANY: "IXANY",
	termios.IXOFF: "IXOFF",
	termios.IMAXBEL: "IMAXBEL",
}

oflag_names = { 
	termios.OPOST: "OPOST",
#	termios.OLCUC: "OLCUC",
	termios.ONLCR: "ONLCR",
	termios.OCRNL: "OCRNL",
	termios.ONOCR: "ONOCR",
	termios.ONLRET: "ONLRET",
	termios.OFILL: "OFILL",
	termios.OFDEL: "OFDEL",
	termios.NLDLY: "NLDLY",
	termios.CRDLY: "CRDLY",
	termios.TABDLY: "TABDLY",
	termios.BSDLY: "BSDLY",
	termios.VTDLY: "VTDLY",
	termios.FFDLY: "FFDLY",
}

cflag_names = {
#	termios.CBAUD: "CBAUD",
#	termios.CBAUDEX: "CBAUDEX",
	termios.CSIZE: "CSIZE",
	termios.CSTOPB: "CSTOPB",
	termios.CREAD: "CREAD",
	termios.PARENB: "PARENB",
	termios.PARODD: "PARODD",
	termios.HUPCL: "HUPCL",
	termios.CLOCAL: "CLOCAL",
#	termios.LOBLK: "LOBLK",
#	termios.CIBAUD: "CIBAUD",
	termios.CRTSCTS: "CRTSCTS",
}

lflag_names = {
	termios.ISIG: "ISIG",
	termios.ICANON: "ICANON",
#	termios.XCASE: "XCASE",
	termios.ECHO: "ECHO",
	termios.ECHOE: "ECHOE",
	termios.ECHOK: "ECHOK",
	termios.ECHONL: "ECHONL",
	termios.ECHOCTL: "ECHOCTL",
	termios.ECHOPRT: "ECHOPRT",
	termios.ECHOKE: "ECHOKE",
#	termios.DEFECHO: "DEFECHO",
	termios.FLUSHO: "FLUSHO",
	termios.NOFLSH: "NOFLSH",
	termios.TOSTOP: "TOSTOP",
	termios.PENDIN: "PENDIN",
	termios.IEXTEN: "IEXTEN",
}

baudrate_names = {
	termios.B0: "B0",
	termios.B50: "B50",
	termios.B75: "B75",
	termios.B110: "B110",
	termios.B150: "B150",
	termios.B300: "B300",
	termios.B1200: "B1200",
	termios.B2400: "B2400",
	termios.B4800: "B4800",
	termios.B9600: "B9600",
	termios.B19200: "B19200",
	termios.B38400: "B38400",
	termios.B57600: "B57600",
	termios.B115200: "B115200",
}

def get_baudrate_name( value ) :
	if value in baudrate_names :
		return baudrate_names[ value ]
	else :
		return "(unknown baud rate)"

def get_flag_names( value, flag_names ) :
	setflags = []
	for k in list(flag_names.keys()) :
		if value & k :
			setflags.append( flag_names[k] )
	return "|".join( setflags )

def get_char_size( cflag ) :
	charsize = cflag & termios.CSIZE

	if cflag & termios.CSIZE :
		if charsize == termios.CS5 :
			return "5bit char"
		elif charsize == termios.CS6 :
			return "6bit char"
		elif charsize == termios.CS7 :
			return "7bit char"
		elif charsize == termios.CS8 :
			return "8bit char"
		else :
			assert 0, cflags & termios.CSIZE 
	else :
		return "CSIZE not set"		

def print_tty_attr( tty_attr ) :
	# tty_attr = [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
	iflag = tty_attr[0]
	print("iflag=%#x %s" % (iflag,get_flag_names(iflag,iflag_names)))

	oflag = tty_attr[1]
	print("oflag=%#x %s" % (oflag,get_flag_names(oflag,oflag_names)))

	cflag = tty_attr[2]
	print("cflag=%#x %s" % (cflag,get_flag_names(cflag,cflag_names)))
	charsize = cflag & termios.CSIZE
	print("termios.CSIZE=%#x charsize=%#x (%s)" % (termios.CSIZE,charsize,get_char_size(cflag)))

	lflag = tty_attr[3]
	print("lflag=%#x %s" % (lflag, get_flag_names(lflag,lflag_names)))

	ispeed = tty_attr[4]
	name = get_baudrate_name( ispeed )
	print("ispeed=%#x %s" % (ispeed,name))

	ospeed = tty_attr[5]
	name = get_baudrate_name( ospeed )
	print("ospeed=%#x %s" % (ospeed,name))

	cc = tty_attr[6]
#	print type(cc),len(cc)
#	print cc

def serial_setup( port_path ) :
	fd = os.open( port_path, os.O_RDWR|os.O_NOCTTY|os.O_SYNC)
	# TODO add error checking! also probably should set the baud rate, etc
	assert fd >= 0 

	# set to 115200 
	# returns [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
	attr = termios.tcgetattr( fd )
	print_tty_attr( attr )

	# davep 20-July-06 ; these settings seem to work with our firmware
	# iflag
	attr[0] = termios.IGNBRK
	# oflag
	attr[1] = 0
	# cflag
#	attr[2] = termios.CBAUDEX|termios.CREAD|termios.CBAUD|termios.CSIZE|termios.CLOCAL
	attr[2] = termios.CSIZE|termios.CLOCAL
	# lflag
	attr[3] = 0
	
	# baud rate	
	attr[4] = termios.B115200
	attr[5] = termios.B115200

	# attr[6] is cc 
	attr[6][termios.VTIME] = 0  # blocking
	attr[6][termios.VMIN] = 1  # char at a time

	# push the settings to the serial port
	termios.tcsetattr( fd, termios.TCSANOW, attr )

	# retrieve and print to make sure they stuck
	attr = termios.tcgetattr( fd )
	print_tty_attr( attr )

	return fd

if __name__ == '__main__' :
	if len(sys.argv) != 2 :
		print("usage: %s ttypath" % sys.argv[0], file=sys.stderr)
		sys.exit(1)

	port = sys.argv[1]

	fd = serial_setup( port )
#	os.close(fd)
#	sys.exit(1)

	#fd = os.open( port, os.O_RDWR|os.O_NOCTTY|os.O_NONBLOCK )
	#fd = os.open( port, os.O_RDWR|os.O_NOCTTY )
#	fd = os.open( port, os.O_RDWR|os.O_NOCTTY|os.O_SYNC)

	# returns [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
	attr = termios.tcgetattr( fd )
	print_tty_attr( attr )

	attr[4] = termios.B9600
	attr[5] = termios.B9600
#	attr[4] = termios.B115200
#	attr[5] = termios.B115200
	termios.tcsetattr( fd, termios.TCSANOW, attr )
	attr = termios.tcgetattr( fd )
	print_tty_attr( attr )

	#termios.tcflush( fd, termios.TCIOFLUSH )
	#print retcode

	with os.fdopen(fd) as f:
		for s in f:
			print(s,end="")

#	while 1 :
#		s = f.readline()
#		print("{}".format(s),end="")

#	while 1 :
#		print("read in")
#		buf = os.read( fd, 1 )
#		print("read out")
#		if opt_hex_output :
#			for c in buf :
#				sys.stdout.write( "{0:02x} ".format(c) )
#		else :
#			s = buf.decode("utf-8")
#			sys.stdout.write(s)
#		sys.stdout.flush()

	os.close( fd )

