# EXAPUNKS Solitaire Solver

[EXAPUNKS](https://store.steampowered.com/app/716490/EXAPUNKS/), a fantastic Zachtronics game, includes a (fairly difficult) Solitaire mini-game. There’s a Steam achievement for winning 100 times, so I wrote a script to automate the process.

Because the game displays cards in a pixel-perfect way, I didn’t need to use any computer vision techniques to read the cards from the screen; I could just take a screenshot and compare pixels at a known location to reference images.

<img src="src/1.png"> <img src="src/2.png"> <img src="src/3.png"> <img src="src/4.png">

As for actually solving the game, the main challenge was representing the state of the game; once that was done, a straightforward graph search was fast enough.

It’s a relatively brittle solution (e.g. it assumes the game window is at a fixed location on the screen), but it was enough to get the job done :)

## Achievement Unlocked!

<img src="Achievement.png" />

## Video

[<img src="https://img.youtube.com/vi/YgyINuzdsIM/maxresdefault.jpg" width="50%">](https://youtu.be/YgyINuzdsIM)
