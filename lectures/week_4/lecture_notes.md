- Everything you need to know from CompArch, OS and UNIX, the lecture
    - CPU
        - Instructions
            - The CPU just grabs the next instruction to execute, and executes it
                - How does it know? Registers! (We'll get to it)
                - (Lie to children here: NX matters! We'll get to that during Page Tables!)
            - Many different types
                - Data movement
                    - `mov rax, [rsp - 0x40]`
                        - We'll gloss over the memory here and get back to it later
                - Arithmetic
                    - `add rbx, rcx`
                        - We'll *really* gloss over things like imul and idiv, with the joined register stuff. Might be worth mentioning, however
                - Control-flow movement
                    - `jmp 0x8000400`
                    - `jne 0x8000400`
                        - Note that it doesn't say what must be equal
                        - We'll get to that soon (flags registers)
                - Maybe mention some really crazy instructions just to wow them?
            - We refer to various parts of the instruction in various ways
                - `mov rax, 0xdeadbeef`
                -           ^^^^^^^^^^-- immediate (a literal value)
                -      ^^^-------------- register
                -  ^^^------------------ operation
                - `mov rax, [0xdeadbeef + rbx * 4]
                -            ^^^^^^^^^^^^^^^^^^^^-- effective address
        - Registers
            - These are like the "local variables" of the CPU.
            - Some have special meanings:
                - rip: "the instruction pointer"
                - rsp: "the stack pointer"
                - rbp: "the base pointer"
                - some more, but they're less important
            - Some are general purpose:
                - rax: "the a register"
                - rbx: "the b register"
                - rcx: you get the idea
                - rdx: again, same deal
            - There are plenty more
                - Some instructions use them implicitly. If you're not sure, RTFM!
            - Sized accesses on x86_64
                - |------------- rax -------------|
                -                 |----- eax -----|
                -                          |- ax -|
                -                          |ah |al|
            - Flags registers set by certain instructions
                - Most importantly, the comparison
        - It's all just bytes
            - Show some encoded instructions
                - `add rax, rbx` == 48 01 d8
                - `mov rax, 0xdeadbeef` == 48 c7 c0 ef be ad de
                    - Note that 0xdeadbeef is backwards -- We'll get to endianness in a bit!
                - `mov rax, [0xdeadbeef]` == 67 48 8b 05 ef be ad de
                    - Look at how differently that instruction is encoded!
                    - the only shared bytes are the 0xdeadbeef imm and the 0x48 opcode
                        - bonus points for explaining the leading 0x67
            - This will matter during Pwning :)
    - Memory
        - The Bytes!
            - It's all just bytes, in the end
        - Addresses
            - Memory is kinda like a big array
                - This is a lie that we'll break, but it's a good model
                - The "indices" to the array are called "addresses"
            - Dereferencing in instructions
                - Remember `mov rax, [0xdeadbeef]`?
                - The [0xdeadbeef] means "get the data at address 0xdeadbeef"
        - The Stack
            - There's a stack in most computers
                - The data structure
                - <insert quick refresher about push and pop here>
            - The stack isn't really some unique data structure.
                - It's just memory!
                - Remember the "rsp" register from earlier?
                    - That's the "stack pointer"
                    - It's just a register that points to the top of the stack
                        - When you push, it decreases
                        - When you pop, it increases
                    - Wait, what? why does it decrease when I push, but increase when I pop?
                        - THE STACK GROWS DOWN!!
            - The "push" and "pop" instructions do what you think
                - `push rax` decrements rsp by 8, and then pushes rax to the stack
                    - It's sorta eqivalent to:
                        sub rsp, 8
                        mov [rsp], rax
                - `pop rax` pops the top thing on the stack into rax, and then increments rsp by 8
                    - equivalent to:
                        mov rax, [rsp]
                        add rsp, 8
            - TODO: something about rbp here? Or maybe that goes in the calling convention section
        - Page Tables
            - Virtual Addressing
                - All my programs are loaded at 0x600000, how can that be?
                    - They're not *actually* at the physical location 0x600000 in memory
                    - We lie about addresses, and we do it in hardware!
                        - The OS controls this with Page Tables
                - WTF is a Page Table? (the short version)
                    - The Page Table is mapping of some range of virtual addresses to a range of phyiscal addresses
                        - The OS deals with making sure each program has it's own set of page tables
                        - Modern processors generally support two page sizes:
                            - Normal (1KB or 0x1000 bytes)
                            - Huge (4MB or 0x4000000 bytes)
                            - you'll mostly see Normal pages.
                        - You can even set a handler for when a Page Fault happens, letting you react to it
                            - This lets you do some really clever stuff, like Copy-On-Write mappings.
            - Permissions
                - We can set permissions on a page too!
                    - Read
                    - Write
                    - Execute
                - The processor will enforce these for us, so it's real fast!
                    - A lot of modern binary protections involve using Page Table permissions.
                        - We'll get to this in the Pwning section of the course
    - The OS
        - Interrupts
            - Q: How can you do:
                - Network access
                - Read files
                - Allocate pages
                - A zillion other things
            - A: Interrupts!
            - Interrupts are the way you ask the OS to perform actions on your behalf
            - There is a special instruction (`int 0x80` on 32-bit, `syscall` on 64-bit) that "traps" into the kernel in order to ask it to do things
                - It's basically a way to call a function in the kernel
                - The state of registers when you syscall determines the function and the arguments
                    - On 64-bit Linux:
                        - rax: syscall number (what function we call)
                        - rdi, rsi, rdx, r10, r8, r9: args
        - UNIX
            - Everything is a file
                - Actual files
                - stdin, stdout
                - The network
    - Putting it together
        - Reviewing the class-entrance problem, 64-bit version
            32-bit version:
                mov eax, 0x0f010203
                xor eax, 0x0f404040
                push eax
                push esp
                call puts
            64-bit version:
                mov rax, 0x0f010203
                xor rax, 0x0f404040
                push rax
                mov rdi, rsp
                call puts
            - Calling conventions
                - The first thing you'll notice is the different instruction: instead of `push esp`, you get a `mov rdi, rsp`
            - Calling conventions
            - Instructions
            - Endianness
            - The stack
        - Writing "Hello, World" in assembly
            - Calling conventions
