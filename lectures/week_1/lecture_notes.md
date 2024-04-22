# Week 1: Introduction and Overview

## What is CTF?
* "Learn security in a controlled environment"
* Categories
    * Web - exploiting web applications
    * Reverse engineering (RE) - figuring out what a binary does
    * Binary exploitation (pwnables) - breaking binaries
    * Cryptography - breaking secured communications
    * Programming - It's important to be able to code!
    * Forensics
        * We won't really be covering this
* 2 formats:
    * Jeopardy
        * Set of challenges created by the competition organizers
        * Each challenge has a flag associated with it
            * Encoded/embedded in it (RE, Crypto)
            * On a remote server that you need to exploit (Web, Pwn)
    * Attack/Defense
        * Each team is given a set of vulnerable services on their own server in a virtual network that they must patch (keeping functionality)
        * The team also has to exploit all other team's services to get flags


## Why are we teaching this course?
* CTF is fun! We want you to come out of this course enjoying playing in CTFs
    * Possibly playing CTFs with the lab


## Homework & Grading

* Throughout the course, we will be running a CTF which is available any time at [https://class.osiris.cyber.nyu.edu](https://class.osiris.cyber.nyu.edu).
    * New set of challenges each week
    * If you score at least 300 CTF points in the week, you will recieve credit for that week's homework.
    * Points will be tallied at the beginning of class one week after it is assigned.
* You need to play in at least one CTFTime-ranked CTF during the course, and give us a writeup
    * Group writeups are permitted, but the amount of content should be proportional to the amount of people listed
    * Please send an email to the teachers with your team name and writeup within one week of the CTF ending.
    * We recommend CSAW CTF Quals (on Sept. 15-17), as we run it and it is geared towards beginners.

* Homework will be worth 90% of your final grade.
* CTF participation & writeup will be worth 10% of your final grade, however this is *required*. You will not pass the course if you do not compete in a CTFTime CTF.

## Materials

* You will need a reverse-engineering toolkit during the Reverse Engineering and Binary Exploitation units of the class.
    * We recommend [Binary Ninja](http://binary.ninja), which has a reasonably-priced student option.
* We will provide a VM with many common tools. Instructions for setting up the VM can be found at https://class.osiris.cyber.nyu.edu/vm

## Office Hours

The teachers will be in the OSIRIS Lab (RH 219) much of the time, but we guarantee at least one of us will be around from 12:00pm to 6:00pm on Fridays, unless we give notice to the contrary. If you need to find another time, feel free to email us so we can work out a time we can be available.

## Collaboration Policy

While CTF is largely a team sport, we believe that all members of the team should be capable of solving problems themselves. Therefore, direct collaboration on homework problems is *not* permitted until the due date has passed.




## Syllabus overview
* https://class.isis.poly.edu/syllabus
* Highlights:
    * Each week, there will be new challenges related to that week's lecture.
    * You need to solve at least 300 points worth of new ("hot") challenges each week to get credit for that week's homework.
    * No collaboration on homework (until after it's due, then feel free to talk as much as you want)
    * At some point in the semester, you need to play in a CTFTime-ranked CTF
        * Can be with others
        * CSAW Quals is good
    * You'll need to get an RE toolkit (binja is recommended because of price and usability)
        * Feel free to try and use r2 if you want (it's on the VM)
    * Other things on the VM:
        * GDB (debugger) & pwndbg (nice additions to GDB to make it nicer)
        * angr
            * Symbolic execution engine
        * radare2
            * RE toolkit, but not the most friendly to beginners
        * ipython
        * pwntools
            * Very nice python library to make common functions easier
                * Sockets, pack/unpack,binary parsing, etc.
        * binutils (objdump and friends)
            * Super dumb tools for working with binaries
    * Feel free to install the tools on another linux machine if you have one and don't want to use the VM. None of them are too hard to setup.
* This is a new class that we're trying out. Please give us feedback.
    * Seriously, drop by RH219 or send us an email if you have any feedback (good or bad).


## Environment setup
* Go to https://class.isis.poly.edu/vm if you haven't already and follow the instructions
* If you've done that, start on the week's homework
