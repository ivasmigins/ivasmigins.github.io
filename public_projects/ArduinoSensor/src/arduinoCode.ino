#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>
#include <stdio.h>

#define F_CPU 16000000UL

#define SDA_PIN PC4 // Arduino A4
#define SCL_PIN PC5 // Arduino A5

// Found these using an I2C ID finder
#define MCP23017_ADDR 0x20 // (extender) I2C address when A0 to A2 is on ground
#define DS1621_ADDR 0x48 // (digital thermometer) I2C address when A0 to A2 is on ground

#define TENS_DISPLAY_PIN PB1 // Pin for the tens display (acts as power)
#define ONES_DISPLAY_PIN PB2 // Pin for the ones display

#define BAUD 9600
#define MYUBRR F_CPU/16/BAUD-1

volatile uint8_t current_display = 0; // 0 for tens and 1 for ones
volatile float temperature = 0;

void i2cInit() {
    TWSR = 0x00; // Set prescaler to 1, 
    TWBR = ((F_CPU / 100000UL) - 16) / 2; // Set SCL to 100kHz ((F_CPU / SCL) - 16) / 2), standard for I2C
    TWCR = (1 << TWEN); // Enable TWI
}

void i2cStart() {
    TWCR = (1 << TWSTA) | (1 << TWEN) | (1 << TWINT);
    // TWSTA: Send start condition
    // TWEN: Enable TWI
    // TWINT: Clear TWI interrupt flag when operation is complete
    while (!(TWCR & (1 << TWINT))); // Waits until TWINT is set
}

void i2cStop() {
    TWCR = (1 << TWSTO) | (1 << TWEN) | (1 << TWINT);
    // TWSTO: Send stop condition
    // TWEN: Enable TWI
    // TWINT: Clear TWI interrupt flag when operation is complete
    while (TWCR & (1 << TWSTO)); // Wait until stop condition is executed
}

void i2cWrite(uint8_t data) {
    TWDR = data; // Load data into TWI data register
    TWCR = (1 << TWEN) | (1 << TWINT); // Start transmission
    // TWEN: Enable TWI
    // TWINT: Clear TWI interrupt flag when operation is complete
    while (!(TWCR & (1 << TWINT))); // Wait until transmission is complete
}

uint8_t i2cReadAck() {
    TWCR = (1 << TWINT) | (1 << TWEN) | (1 << TWEA); 
    // TWINT: Clear TWI interrupt flag when operation is complete
    // TWEN: Enable TWI
    // TWEA: Enable ACK
    while (!(TWCR & (1 << TWINT))); // Wait until transmission is complete
    return TWDR; // Return received data
}

uint8_t i2cReadNack() {
    TWCR = (1 << TWINT) | (1 << TWEN); // Disable ACK (End communication)
    // TWEN: Enable TWI
    // TWINT: Clear TWI interrupt flag when operation is complete
    while (!(TWCR & (1 << TWINT))); // Wait until transmission is complete
    return TWDR; // Return received data
}

void extenderInit() {
    i2cStart();
    i2cWrite(MCP23017_ADDR << 1); // Write mode
    i2cWrite(0x01); // IODIRB register (for GPIOB)
    i2cWrite(0x00); // Set all B pins as outputs
    i2cStop();
}

void extenderWriteGPIO(uint8_t port, uint8_t value) {
    i2cStart();
    i2cWrite(MCP23017_ADDR << 1); // Write mode
    i2cWrite(port); // GPIOA or GPIOB register (I only use GPIOB in this code)
    i2cWrite(value); // Which pins to set HIGH or LOW
    i2cStop();
}

void startTempConversion() {
    i2cStart();
    i2cWrite(DS1621_ADDR << 1);  // Write mode
    i2cWrite(0xEE);  // Start temperature conversion (Page 11 Datasheet)
    i2cStop();
}

float readTemperature() {
    i2cStart();
    i2cWrite(DS1621_ADDR << 1);  // Write mode
    i2cWrite(0xAA);  // Read temperature command (Page 11 Datasheet)
    i2cStop();

    // Read 2 bytes, MSB and LSB
    i2cStart();
    i2cWrite((DS1621_ADDR << 1) | 1);  // Read mode
    uint8_t msb = i2cReadAck(); // Use ACK because we need more bytes
    uint8_t lsb = i2cReadNack(); // Use NACK because it's the last byte needed
    i2cStop();

    // Combine MSB and LSB into a 16-bit value
    // MSB contains the whole part and LSB contains the fractional part
    int16_t temp = (msb << 1) | (lsb >> 7);  // 0.5°C increments
    // MSB is moved to the left by 1 bit which basically multiplies it by 2
    // LSB's MSB indicates wether we need to add 0.5°C or not, so this is the only bit we need
    return temp / 2.0;  // Number was multiplied by 2 so divide by 2 to get the real value
}

void displaysWrite(uint8_t pin, uint8_t state) {
    // Set the pin to HIGH or LOW for the display pin depending if its needed or not
    if (state == HIGH) {
        PORTB |= (1 << pin);
    } else {
        PORTB &= ~(1 << pin);
    }
}

void updateDisplay() {
    uint8_t map[] = {
        0b11000000,
        0b11111001,
        0b10100100,
        0b10110000,
        0b10011001,
        0b10010010,
        0b10000010,
        0b11111000,
        0b10000000,
        0b10010000
    };

    // Clear GPIOB before setting new data
    extenderWriteGPIO(0x13, 0xFF); // Page 18 Datasheet

    if (current_display == 0) { // tens place
        int tens_digit = (int)temperature / 10;
        displaysWrite(TENS_DISPLAY_PIN, HIGH);
        extenderWriteGPIO(0x13, map[tens_digit]);
        _delay_us(50); // Makes it not so flashy
        displaysWrite(TENS_DISPLAY_PIN, LOW);
    } else { // ones place
        int ones_digit = (int)temperature % 10;
        displaysWrite(ONES_DISPLAY_PIN, HIGH);
        extenderWriteGPIO(0x13, map[ones_digit]);
        _delay_us(50);
        displaysWrite(ONES_DISPLAY_PIN, LOW);
    }

    // Change to the next display
    current_display = !current_display;
}

void aurtInit(unsigned int ubrr) {
    // Set baud rate, it is split into 2 bytes because that is how it is stored
    UBRR0H = (unsigned char)(ubrr >> 8); // Ensure it fits in 8 bits, high byte
    UBRR0L = (unsigned char)ubrr; // Low byte
    // Enable transmitter (TXEN0)
    UCSR0B = (1 << TXEN0);
    // Set the data format
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);
    // UCSZ01 and UCSZ00: 8 data bits
    // No parity, default
    // 1 stop bit, default
}

void uartChar(char c) {
    while (!(UCSR0A & (1 << UDRE0))); // Wait for the transmit buffer to be empty (UDRE0)
    UDR0 = c; // Send character
}

void uartStr(const char *str) {
    while (*str) {
        uartChar(*str++); // Send each character while incrementing the pointer
    }
}

ISR(TIMER0_COMPA_vect) { // Display multiplexing
    updateDisplay();
}

ISR(TIMER1_COMPA_vect) { // Read temperature
    startTempConversion();
    _delay_ms(10); // Needed to make sure that conversion starts (Page 11 Datasheet)
    temperature = readTemperature();

    // Send to the serial monitor
    uartStr("Temp: ");
    char buffer[10];
    int int_part = (int)temperature;
    int dec_part = (int)((temperature - int_part) * 10); 
    // Extract 1 decimal place since the temperature is in 0.5 increments, and 
    // while this is not shown in the displays, it is shown on the website
    sprintf(buffer, "%d.%d", int_part, dec_part); // Convert number to string, truncating it to 1 decimal place
    uartStr(buffer); // Send temperature as a string
    uartStr("°C\n");
}

void timersInit() {
    // Timer 0 is used for display multiplexing
    TCCR0A = (1 << WGM01); // CTC mode
    OCR0A = 249; // Compare value for 2ms, [ 2ms = (64*(OCR0A+1))/FCPU ] -> OCR0A = 249
    TCCR0B = (1 << CS01) | (1 << CS00); // Prescaler 64
    TIMSK0 = (1 << OCIE0A); // Enable Timer 0 Compare Match A interrupt

    // Timer 1 is used for updating the temperature
    TCCR1B = (1 << WGM12); // CTC mode
    OCR1A = 7812; // Compare value for 500ms,[ 500ms = (1024*(OCR1A+1))/FCPU ] -> OCR1A = 7812
    TCCR1B |= (1 << CS12) | (1 << CS10); // Prescaler 1024, slower rate than Timer 0 so higher prescaler
    TIMSK1 = (1 << OCIE1A); // Enable Timer 1 Compare Match A interrupt
}

int main() {
    i2cInit(); // Initialize I2C
    extenderInit(); // Set GPIOB as outputs
    DDRB |= (1 << TENS_DISPLAY_PIN) | (1 << ONES_DISPLAY_PIN); // Make output
    aurtInit(MYUBRR); // Initialize UART
    cli(); // Disable global interrupts
    timersInit();
    sei(); // Enable global interrupts
    while (1) {} // All handled by timers & interrupts :)
}
