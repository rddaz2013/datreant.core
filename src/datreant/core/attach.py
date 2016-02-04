"""
Modifications made to :mod:`datreant` classes on import of module.

"""

from .treants import Treant
from .limbs import Tags, Categories

# Treants get tags and categories
for limb in (Tags, Categories):
    Treant._attach_limb_class(limb)
