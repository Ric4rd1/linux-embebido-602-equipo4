
compile:
	avr-gcc -Os -mmcu=atmega328p -I/usr/lib/avr/include -c blink.c

link:
	avr-gcc -mmcu=atmega328p -o blink.elf blink.o

firmwareImage:
	avr-objcopy -j .text -j .data -O ihex blink.elf blink.hex

upload: 
	sudo avrdude -P /dev/spidev0.0 -c usbasp -p m328p -U flash:w:blink.hex

dump:
	avr-objdump -h -S blink.elf > blink.dump
