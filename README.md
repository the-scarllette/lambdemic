# Pandemicai
*Pandemicai* is a reinforcement learning agent being trained to play the board game *Pandemic*.

## Pandemic the board game
Pandemic is a cooperative board game for 2-4 players where
people work together to cure 4 diseases spreading across the world.
Detailed rules of the game can be found
[here](https://images-cdn.zmangames.com/us-east-1/filer_public/25/12/251252dd-1338-4f78-b90d-afe073c72363/zm7101_pandemic_rules.pdf)
and a how-to-play video can be found [here](https://www.shutupandsitdown.com/videos/how-play-pandemic-legacy/).

## Usage
Pandemicai has a built-in representation of the board game Pandemic.
This can be ran with or without graphics in order to train learning agents.

## Current Agent
Currently, pandemicai uses *Q-learning* to play Pandemic.

## Roadmap
The next step in pandemic is update the current Q-learning agent to add more detail into it's state representation,
and to refine the state-transition rewards.<br>

However, the future plan is to use *function-approximation methods* to create better agents,
namely adding a TD Gamma agent.

## Acknowledgments
Pandemic was designed by Matt Leecock who can be found [here](https://www.leacock.com/).
