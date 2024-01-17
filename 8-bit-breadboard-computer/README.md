# 8-bit Breadboard Computer

https://eater.net/8bit

Ben Eater created an incredible series of videos and kits about building an 8-bit computer on breadboards; he takes “I built my own computer” to the next level.

I followed along and built one. It took me about a month, and through the process I learned a LOT about digital electronics. Though I have to admit, it feels like 95% of the effort was in trying to keep wires organized :)

## Final Result

<img src="final.jpg" width="800px" />

## Modifications / Optimizations

I made a few modifications / optimizations, that turned out to be extremely helpful. Some were based on various YouTube comments and Reddit posts, others were from me:

- Used LEDs with built-in resistors, which saved a lot of space
- Upgraded from a generic power supply to a much more reliable Apple one
- Passed clock signal through a “double buffer” (aka two inverters) before connecting it to the RC circuit, to avoid “bouncing”
- Added lots of extra pull-up resistors to avoid floating voltage values
- In the output display, suppressed leading 0's and put the minus sign immediately in front of the value (instead of always at the leftmost position)
- Used 1kΩ instead of 10kΩ for bus pulldown resistors

## Fibonacci Program

The video included in this directory (that's printing out Fibonacci numbers) is running the following program:

```
Address   Data        Meaning
-------------------------------
 0        0001 1111   LDA 15
 1        1110 0000   OUT
 2        0010 1110   ADD 14
 3        0111 1010   JC  10
 4        0100 1101   STA 13
 5        0001 1111   LDA 15
 6        0100 1110   STA 14
 7        0001 1101   LDA 13
 8        0100 1111   STA 15
 9        0110 0000   JMP 0
10        1111 0000   HLT
11        -
12        -
13        -
14        0000 0001   1
15        0000 0001   1
```
