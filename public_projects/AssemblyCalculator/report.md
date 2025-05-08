# x86-64 Assembly Calculator
Written Report

###### I have commented all of the code inside the .asm file, going step by step. This file contains more of the thought process behind the code than an actual explanation, that can be found within the comments of the code

## Requierments
- Nasm - For assembling
- Gdb - For debugging
- Ubuntu - Platform 

## Features

- Accepts user input for two numbers with 3 decimals max (Can easily be changed inside the code).
- Allows selection of an arithmetic operation.
- Performs addition, subtraction, multiplication, and division.
- Implements fixed-point arithmetic to support decimal precision.
- Provides error handling for invalid inputs and division by zero.
- Outputs the result.

## Assembly general information
The code is split into 3 sections:
* .data : Where initialized data goes.
* .bss : Where uninitialized data goes.
* .text : The actual code.

For instance, in .data we might store prompt messages:
```
prompt_1 db "Enter the first number: ", 0
```
```db``` means that this is a byte (8 bits) which each character is put into. The 0 at the end is the null terminator.

Now, on .bss we can separate some space for the number the user inputs:
```
num1 resd 1
```
```resd``` reserves space for 32 bit values, and the 1 is how many of these 32 bit spaces we want.

Finally, on .text we can put the code:
```
section .text
    global _start

_start:
```
```global _start``` is done so the assembler and linker can recognize the entry point (in this case _start)

Functions in assembly work different. For instance _start is a label, a point in memory, where we can go to later on. Parameters need to be put into separate registers before using ```call``` to the label, then these registers can be read from within the code and operations can happen.

To run our code, first it is sent to nasm
```nasm -f elf64 test.asm -o test.o```, then to ```ld -o test test.o```. This gives us the executionable file, to debug it using gdb we can do ```gdb test``` (assuming the file is named "test")

# The calculator

## Part 1: Integer calculator

I first started by creating a simple calculator only for integers, leaving out a lot of the complexity that would come later on. The workflow was to first output the prompt, then read the input and put it into a buffer. If it was the turn for a number, then it would be parsed and stored into a variable (num1 or num2). However if it was the turn for the operator then it would be put into another variable so I could then easily tell which operation needed to take place.
The first step towards a calculator is reading the numbers that are inputed by the user. Reading from the console can be done by configuring a few registers (basically to tell the system that we want to read) and then doing a ```syscall```, storing the result into a buffer than we define in ```.bss```.
```
    ; Ask for the first number
    mov rax, 1 ; Tell the system we want to write
    mov rdi, 1 ; We are writing to standard output
    mov rsi, pr_1 ; The string to write
    mov rdx, 19 ; length of the string
    syscall

    ; Read the first number
    mov rax, 0 ; Read
    mov rdi, 0 ; From standard input
    mov rsi, input ; Store input here
    mov rdx, 32 ; Max bytes to read
    syscall
```
To parse the string I made a function, ```parse_integer```. Parse integer works by looping through each character of the string and making sure it is between 0 and 9 by using comparisons. Here the ASCII value is compared, and then if it is a number, the ASCII value of '0' is subtracted, leaving us with only the integer that is in that character ('1' = 0x31, '0' = 0x30, '1' - '0' = 1). This integer is then added to our accumulator. For the next iteration, before adding the next number, we multiply the value in the accumulator by 10, therefore making room for the next number and we only have to add it. 
This will require some changes when we do floating points, possibly requiring another accumulator for the decimal part and a flag for it, at least that is my idea for now. Also this doesn't consider negative numbers yet, but for these I believe I can flag them whenever I detect a '-' (that isn't a subtraction), so these shouldn't be much of an issue. Either way, now that we can extract numbers from strings, we can perform the calculations. x86-64 Assembly provides us with functions to add, multiply, subtract, and divide. For instance, the addition function looks like this:
```
addition:
    mov eax, [num1]
    add eax, [num2]
    mov [result], eax  ; [result] is a variable holding our result.
    jmp exit  ; Exit the program once calculations are over.
```
To confirm our results ```gdb``` is used. We can set a breakpoint in exit then check the value of ```result``` and see if it is our expected output. Outputting the result will be done in the floating point calculator.

## Part 2: Floating point calculator

I will do this part with fixed-point arithmetic. I did find there are some floating point registers (x87 FPU), but I believe these might end up giving several problems. So for the sake of simplicity, and the fact that I am doing this by myself, I will only allow up to 3 decimal places. However, this will be easy to change, as using fixed-point arithmetic is rather a simple process. The downside of allowing more decimal places is that with bigger numbers, it might cause an integer overflow. We have to make sure we stay within the 64-bit limits, also considering there are negative numbers.
To start things off I made a new parsing function and called it ```to_fixed_point```. This function handles the conversion from a string like "3.25" into the fixed-point value, 3250. It starts off by clearing registers that I will use to store flags, and results.
```
    xor rax, rax ; Result accumulator
    xor rcx, rcx ; Decimal counter
    xor rdx, rdx ; Temporary storage for the characters
    xor rbx, rbx ; Decimal flag (0 = integer, 1 = decimal)
    xor r8, r8 ; Sign flag (0 = positive, 1 = negative)
```
 I also check if the first character is a '-' that and enable a flag if it is, that way I can just ignore it for now and make the end result negative. Then I have a loop similar to the one I made in the integer calculator. It checks the character to see if its the null terminator, and also makes sure it is a number between 0 and 9. If it isn't, then it enables a flag to tell that we are in the fractional part now and it skips that character (the "."). This process also contains multiple checks to make sure that there aren't multiple points and that the character is indeed a point. I am also counting how many digits have been processed after the decimal point, to make sure that we keep the decimals within the limit (this is stored in rcx). 
 ```
    sub dl, '0' ; ASCII to integer (0x30 to 0x39)
    imul rax, rax, 10 ; Multiply result by 10 to make room for the new digit
    add rax, rdx ; Add the new digit

    test rbx, rbx ; Are we in the fractional part?
    jz .integer_part_next ; If not, continue parsing the integer part
    inc rcx ; If yes, count decimal places
    cmp rcx, [decimal_places] ; Limit the decimal places
    ja error ; Too many decimals, error.
```
 When it is all done, I check if we processed 3 digits after the decimal point and if we didn't I multiply the value by 10^(3-rcx) to get us our desired result. I also check for the sign to make negate the number if needed.

The writing of that function process took most of the time and it was the hardest part of the calculator, as the rest could be easily done with assembly. I encountered multiple problems, such as the decimal part being left infront of the number, like 3.25 becoming 25003. And that was when the program showed something somewhat decent. Other times random values would show up in the register and I had to check step by step what the problems were. I came to realize that error handling wasn't something to be built after the program was working (at least for the expected input), but something that I also needed in order to debug my own code. It was easier this way to find out what was wrong using gdb. At the end of the day, errors were mostly caused due to the repeated multiplications and the combination of the decimal and fractional part.
Moving on, I took the flow from the integer calculator (asking for input, storing, asking again) and put it on this one. The division and multiplication functions that I did for the integers needed some tweaks, since I wasn't working with negatives before. I also had scaled up numbers. One important part about these was cqo, since when working with signed numbers in division, we need to ensure that the dividend is properly extended. In integer division, this is usually done by moving the numerator into rax and then using cqo to extend it into rdx. This ensures that the sign of the number is properly maintained. Since our numbers are scaled up (due to fixed-point arithmetic), we need to scale down after the operation to get the correct result. For division, this means multiplying by 1000 after the operation, whereas for multiplication, we divide the result by 1000 to bring it back to the correct scale.
```
division:
    mov rax, [num1] ; Numerator
    mov rbx, [num2] ; Denominator
    
    test rbx, rbx ; Is the denominator zero?
    jz error ; If yes, error

    imul rax, [scaling_factor] ; Scale numerator (num1 * scaling_factor)
    
    cqo
    idiv rbx ; Perform signed division: (num1 * scaling_factor) / num2
    mov [result], rax
    jmp print_result
```

## Part 3: Outputting Results

Once the calculations were working correctly, I needed a way to convert the fixed-point numbers back into readable strings for output. This required a function to convert the integer back into a decimal representation. The process for outputting numbers was to first load the number into rax, where I can manipulate it. Second set a negative flag if the number was negative. Third, format the decimal part first. 
```
.decimal_loop:
    mov rdx, 0 ; Clear to ensure proper division
    mov rbx, 10 ; Divisor
    div rbx ; RAX /= 10, remainder (in our case the digit) in rdx

    ; dl is lower 8-bit part of rdx, so it has the remainder (it's one digit)
    add dl, '0' ; Convert remainder to ASCII
    dec rsi ; Move buffer pointer left
    mov [rsi], dl ; Store digit, [] around rsi because we want to use it as a memory address

    loop .decimal_loop ; Repeat [decimal_places] times (for decimal placement)
```
Fourth, insert the decimal point. Fifth, format the integer part. Sixth, add the negative sign. And finally, printing to the console. For example if I want to store -3250 to the output buffer, this is the process:

First we point to the end of the buffer, and start inputting the 3 "decimals", which are just the first 3 numbers.
- ..[ ][ ][0][\n]
- ..[ ][5][0][\n]
- ..[2][5][0][\n]

Afterwards, the point is added, and then we make a loop that goes through the number until it is done.
Finally the '-' is put to the left of wherever we ended.

Of course this implementation might run into issues if the number is too big, but so does the rest of the code. So doing something to fix that only here makes no sense.

## Debugging

Debugging in assembly was pretty complex, but I managed by using gdb. I mostly used x/d to check for variable results, and info registers to check the values of the registers after I did some operations. These gave me a lot of insight on what the problems were.

## Improvements

- Allowing for user-configurable precision. (Its already very easy to edit this in the code)
- Adding more error handling and provide meaningful error messages.
- Putting the calculator into a loop perhaps, so it doesn't need to be run again.

Overall, this project was very challenging and took a while, but I believe the end product is acceptable. I took my time making sure the code didn't delve into bad practices.

## Resources
- **https://github.com/yds12/x64-roadmap**
- http://www.egr.unlv.edu/~ed/assembly64.pdf
- https://www.cs.uaf.edu/2017/fall/cs301/reference/x86_64.html
- https://cs.lmu.edu/~ray/notes/nasmtutorial/
- https://en.wikipedia.org/wiki/Fixed-point_arithmetic


