# Paneful
Paneful is a set of procedural tools and utilities for making weirder ai art

Concept: What if we could use stable diffusion to make wild segmentation collages based on your selfies or ai renders?
Well, it's fun and easy (relatively easy) to do! It just takes a shit ton of pre and post-processing, which is necessary, because this kind of art is VERY difficult to do by hand.

I'm actively writing these to make the process simpler.

Okay, so... 
I think these tools are obviously named, but here's some things you need to know about them.

* compressor.py - does what it says. Compresses your monster png files into much lighter jpegs. Runs on every image in a directory.
* jpegger.py - same as compressor.py, come to think of it. Older, probably a candidate for depracation.
* just-dither - takes every image in a directory, and dithers it, so you have noisier images to pass to the ai.
* slicer.py - chops every image in a directory and creates a folder tree with slices of your image, and creates a series of cusomized inpainting masks with different border widths.
* fixer.py - probably broken at the moment, but, reads a directory looking for slices, and re-assembles them, based on the changes that stable diffusion default makes to your naming convention.
* webp-converter.py - webp is the most useless and annoying file format there is, well, second only to avif, which is even more annoying. This script converts your webp's into nice happy little png's.
* randomize.py - probably also broken at the moment. This script takes a group of tiles, from a tiles directory, the same way fixer does. But, unlike fixer.py, it detects your groups of image variations from multiple slice directories,
obeys the grid, and randomly selects every tile in that grid, so that you can build out a more randomized collage. It also takes a number input, meaning that you can tell it to create multiple variations of the collage.

## Todo:

Fix fixer.py and randomize.py so that they work with the file trees that slicer.py is generating now.
No big deal.

Releasing it this way, so you can play with the pieces.

