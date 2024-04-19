#define F_CPU 16000000UL //Definir velocidad del micro
#include <avr/io.h>
#include <util/delay.h>

int main (void)
{ 
    DDRB |= _BV(PORTB0);      // set pin 0 of port B as an output pin

    for (;;) {
        PORTB |= _BV(PORTB0);  // set pin 0 of port B high
        _delay_ms(1500);  // loop for 62500 iterations * 4 cycles / 1MHz clock ~= 250ms
        PORTB &= ~_BV(PORTB0); // set pin 0 of port B low
        _delay_ms(1500);  // loop for 62500 iterations * 4 cycles / 1MHz clock ~= 250ms
    }
    return 0;
}