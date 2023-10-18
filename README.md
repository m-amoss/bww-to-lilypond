BWW To LilyPond
===============

Overview
---

This project is a Python script to convert old bagpipe music scores written in the Bagpipe Music Writer format to LilyPond notation.

The initial idea for this was not my own, but my discovery of Jezra Lickter's bwwtolily project inspired me to do some additional work and extension of his original code, [which is available here](https://www.jezra.net/projects/bwwtolily.html).

Using The Script
---

To convert a bww file to a lilypond file, run the following in a shell:

`python script.py -i scotland-the-brave.bww`

The `-i` option specifies that an filename will be given.

As long as no errors in the input are encountered, the file will be translated to LilyPond and output into an `.ly` file with the same name as the input. For the above example, the output LilyPond file would be:

`scotland-the-brave.ly` 

