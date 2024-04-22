# CS-UY 3943-G: Intro to Offensive Security

Brendan Dolan-Gavitt - [brendandg@nyu.edu](mailto:brendandg@nyu.edu)

Nick Gregory - [nmg355@nyu.edu](mailto:nmg355@nyu.edu)

Josh Hofing - [jlh627@nyu.edu](mailto:jlh627@nyu.edu)

## Course overview

This course aims to teach offensive security in the context of Capture the Flag (CTF) competitions.
We will cover common flaws in websites, techniques and methods to reverse x86 assembly, exploitation strategies for binaries, and basic cryptographic flaws.


## Homework & Grading

Throughout the course, we will be running a CTF which is available any time at [https://class.osiris.cyber.nyu.edu](https://class.osiris.cyber.nyu.edu).

Each week, a set of challenges related to that week's material will be released and marked as "hot" which indicates that they count towards that week's homework.
Grading will be based on the number of points you score in the CTF each week.
If you score at least 300 CTF points in the week, you will recieve credit for that week's homework.
Points will be tallied for hot challenges at the beginning of class one week after it is assigned.
Past challenges will continue to be available for the entire semester, and we recommend that you solve as many of them as you can.

You will be required to compete in at least one [CTFTime](http://ctftime.org)-ranked CTF, and provide a writeup about at least one non-trivial problem that your team worked on.
We encourage you to form teams with classmates and submit a group writeup.
Please send an email to the teachers with your team name and writeup within one week of competing.
We recommend CSAW CTF Quals (on Sept. 15-17), as we run it and it is geared towards beginners.

* Homework will be worth 90% of your final grade.
* CTF participation & writeup will be worth 10% of your final grade, however this is *required*. You will not pass the course if you do not compete in a CTFTime CTF.

## Materials

You will need a reverse-engineering toolkit during the Reverse Engineering and Binary Exploitation units of the class.
We recommend [Binary Ninja](http://binary.ninja), which has a reasonably-priced student option.

We will provide a VM with many common tools. Instructions for setting up the VM can be found at [https://class.osiris.cyber.nyu.edu/vm](https://class.osiris.cyber.nyu.edu/vm).

## Office Hours

The teachers will be in the OSIRIS Lab (RH 219) much of the time, but we guarantee at least one of us will be around from 12:00pm to 6:00pm on Fridays, unless we give notice to the contrary. If you need to find another time, feel free to email us so we can work out a time we can be available.

## Collaboration Policy

While CTF is largely a team sport, we believe that all members of the team should be capable of solving problems themselves. Therefore, direct collaboration on homework problems is *not* permitted until the due date has passed.

## Syllabus

* Week 1: Introduction
    * What is CTF
    * Syllabus overview
    * Environment Setup

* Weeks 2-4: Web
    * SQL Injection
    * XSS
    * Command injection
    * File inclusion
    * PHP

* Weeks 5-8: Reversing/assembly
    * Basics of assembly
    * x86 semantics
    * Techniques
    * GDB
    * Structs
    * Constraint solving

* Weeks 9-11: Binary Exploitation
    * Integer underflow
    * Stack overflows
    * Modern protections
    * Return Oriented Programming

* Weeks 12 & 13: Cryptography
    * Frequency analysis
    * XOR
    * Block ciphers
    * Common RSA attacks/mistakes
    * Padding oracle attacks
    * Hash-length extension
    * CRIME attack

* Week 14: Wrap up
    * TBD
