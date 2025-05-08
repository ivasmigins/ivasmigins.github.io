section .data
    pr_1 db "Enter first number: ", 0
    pr_op db "Enter operator (+, -, *, /): ", 0
    pr_2 db "Enter second number: ", 0
    error_msg db "Invalid input!", 10, 0
    decimal_places dq 3 ; Number of decimal places to scale
    scaling_factor dq 1000 ; Scaling factor (Should match decimal_places, they are used in different places but should mean the same)
    out_buffer db "0000000000000", 10  ; Buffer for output (with newline at the end, space for 13 characters, 1 will be a decimal point)

section .bss
    input resb 32 ; Buffer to store user input
    num1 resq 1 ; First fixed-point result
    num2 resq 1 ; Second fixed-point result
    operator resb 1 ; Operator character
    result resq 1 ; Reserve space for result fixed-point integer

section .text
    global _start

_start:
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

    ; Convert to fixed-point number
    mov rsi, input ; Pass input to function
    call to_fixed_point
    mov [num1], rax ; Store result

    ; Ask for operator
    mov rax, 1
    mov rdi, 1
    mov rsi, pr_op
    mov rdx, 28
    syscall

    ; Read operator
    mov rax, 0
    mov rdi, 0
    mov rsi, input
    mov rdx, 32
    syscall

    ; Store operator
    mov al, [input] ; Can't move from memory to memory, so use a register, also we don't need the whole register
    mov [operator], al

    ; Ask for the second number
    mov rax, 1
    mov rdi, 1
    mov rsi, pr_2
    mov rdx, 20
    syscall

    ; Read the second number
    mov rax, 0
    mov rdi, 0
    mov rsi, input
    mov rdx, 32
    syscall

    ; Convert
    mov rsi, input
    call to_fixed_point
    mov [num2], rax

    ; Perform operation
    mov al, [operator]
    cmp al, '+'
    je addition
    cmp al, '-'
    je subtraction
    cmp al, '*'
    je multiplication
    cmp al, '/'
    je division

    jmp exit

addition:
    mov rax, [num1] ; num1 into rax
    add rax, [num2]
    mov [result], rax ; Save result
    jmp print_result

subtraction:
    mov rax, [num1]
    sub rax, [num2]
    mov [result], rax
    jmp print_result

multiplication:
    mov rax, [num1]
    imul rax, [num2]

    cqo ; Sign-extend; this took a while to find but fixed the issue with negatives
    mov rcx, [scaling_factor] ; Load scaling factor (I tried skipping this but nasm errored)
    idiv rcx ; Perform division: (num1 * num2) / scaling_factor
    mov [result], rax
    jmp print_result

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

; Convert string to a fixed-point integer based on a scaling factor
to_fixed_point:
    xor rax, rax ; Result accumulator
    xor rcx, rcx ; Decimal counter
    xor rdx, rdx ; Temporary storage for the characters
    xor rbx, rbx ; Decimal flag (0 = integer, 1 = decimal)
    xor r8, r8 ; Sign flag (0 = positive, 1 = negative)

    cmp byte [rsi], '-' ; Check if first character is a minus sign
    jne .parse_loop ; If not, continue normally
    mov r8, 1 ; Number is negative
    inc rsi ; Skip sign

.parse_loop:
    movzx rdx, byte [rsi] ; Load next character and clear the upper bits of rdx
    test rdx, rdx ; Check for null terminator
    ; Fun way to check for null terminator, instead of using cmp we can use test (bitwise AND) on itself
    jz .maybe_scale ; If yes, we're done

    ; Since rdx is 64 bit and we are only loading 8 bits, we can use dl to access the lower 8 bits
    cmp dl, '0' ; Check if it is over 0
    jb .check_point ; If not, check if it's a decimal point
    cmp dl, '9' ; Check if it is under 9
    ja .check_point ; If not, check if it's a decimal point

    sub dl, '0' ; ASCII to integer (0x30 to 0x39)
    imul rax, rax, 10 ; Multiply result by 10 to make room for the new digit
    add rax, rdx ; Add the new digit

    test rbx, rbx ; Are we in the fractional part?
    jz .integer_part_next ; If not, continue parsing the integer part
    inc rcx ; If yes, count decimal places
    cmp rcx, [decimal_places] ; Limit the decimal places
    ja error ; Too many decimals, error.

.integer_part_next:
    inc rsi ; Move to the next character
    jmp .parse_loop ; Continue

.check_point:
    cmp dl, '.' ; Decimal point?
    jne .maybe_scale ; If not, finish. No need for extra checks
    test rbx, rbx ; In fractional part?
    jnz error ; If yes, how? Error.
    mov rbx, 1 ; Switch to decimal mode
    inc rsi ; Move to the next character
    jmp .parse_loop ; Continue

.maybe_scale:
    sub rcx, [decimal_places] ; (Decimal places - Predefined decimal places)
    jge .apply_sign ; If rcx >= 0, skip scaling
    neg rcx ; Convert to positive if rcx < 0, since this is the amount of times to scale

.scale_loop:
    test rcx, rcx ; Check if we're done
    jz .apply_sign ; If yes, continue
    imul rax, 10 ; Multiply by 10
    dec rcx ; Decrement counter
    jmp .scale_loop ; Repeat

.apply_sign:
    test r8, r8 ; Check if number is negative
    jz .return ; If not, return normally
    neg rax ; Apply negative sign

.return: ; Ensure we return in the end
    ret

; Print the result (stored in fixed-point format) to the console, as a normal number
print_result:
    mov rax, qword [result] ; Load the number (specify qword to ensure 64-bit read)
    mov rsi, out_buffer + 12 ; Point to before newline

    ; Handle negative numbers
    mov rdi, 0 ; Flag for negative
    test rax, rax ; Is the number negative?
    jns .set_loop_counter ; If not, skip
    mov rdi, '-' ; Set flag to '-'
    neg rax ; Convert to positive

.set_loop_counter:
    mov rcx, [decimal_places] ; Counter for decimal placement

.decimal_loop:
    mov rdx, 0 ; Clear to ensure proper division
    mov rbx, 10 ; Divisor
    div rbx ; RAX /= 10, remainder (in our case the digit) in rdx

    ; dl is lower 8-bit part of rdx, so it has the remainder (it's one digit)
    add dl, '0' ; Convert remainder to ASCII
    dec rsi ; Move buffer pointer left
    mov [rsi], dl ; Store digit, [] around rsi because we want to use it as a memory address

    loop .decimal_loop ; Repeat [decimal_places] times (for decimal placement)

    dec rsi ; Go to where the point should be
    mov byte [rsi], '.' ; Insert decimal point

.integer_loop: ; This is where we continue after the decimal point, repeat until we're done
    test rax, rax ; Are we done?
    jz .sign_and_newline ; If RAX is zero, finish

    mov rdx, 0 ; Clear
    div rbx ; Extract next digit
    add dl, '0' ; Convert to ASCII

    dec rsi ; Move buffer pointer left
    mov [rsi], dl ; Store digit

    jmp .integer_loop ; Repeat

.sign_and_newline:
    test rdi, rdi ; Check if negative flag is set
    jz .print ; If not, skip
    dec rsi ; Move buffer pointer left
    mov byte [rsi], '-' ; Store '-' sign

    ; Append a newline at the end. I do this in .data but I am not sure why it does not work there. Same for the error message, but it is a minor problem.
    mov byte [out_buffer + 13], 10

.print:
    mov rdx, out_buffer + 14 ; Compute length of the string (including newline)
    sub rdx, rsi ; Length = end - start
    mov rdi, rsi ; String address for syscall

    ; Print the result
    mov rax, 1
    mov rdi, 1
    syscall

    jmp exit

error: ; Tell the user there was an error
    mov rax, 1
    mov rdi, 1
    mov rsi, error_msg
    mov rdx, 14
    syscall
    
    jmp exit

exit: ; Exit the program
    mov rax, 60
    xor rdi, rdi
    syscall