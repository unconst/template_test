# The MIT License (MIT)
# Copyright © 2023 Yuma Rao

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import wandb
import bittensor as bt
from typing import List, Dict, Union, Tuple, Callable


def default_priority( self, request: bt.SynapseBaseCall ) -> float:
    # Check if the key is registered.
    registered = False
    if self.metagraph is not None:
        registered = request.src_hotkey in self.metagraph.hotkeys

    # Non-registered users have a default priority.
    if not registered:
        return self.config.miner.priority.default

    # If the user is registered, it has a UID.
    uid = self.metagraph.hotkeys.index( request.src_hotkey )
    stake_amount = self.metagraph.S[uid].item()
    return stake_amount


def priority( self, priority_func: Callable, request: bt.SynapseBaseCall ) -> float:

    # Check to see if the subclass has implemented a priority function.
    priority = None
    try:

        # Call the subclass priority function and return the result.
        priority = priority_func( request )

    except NotImplementedError:
        # If the subclass has not implemented a priority function, we use the default priority.
        priority = default_priority(self, request)

    except Exception as e:
        # An error occured in the subclass priority function.
        bt.logging.error(f"Error in priority function: {e}")

    finally:
        # If the priority is None, we use the default priority.
        if priority == None:
            priority = default_priority( self, request )

        # Log the priority to wandb.
        if self.config.wandb.on:
            wandb.log({ "priority": priority, "hotkey": request.hotkey })

        # Return the priority.
        return priority
