Treants
=======
Treants are the core units of functionality of ``datreant``. They function as
specially marked directories with distinguishing characteristics. They are
designed to be subclassed, with their functionality extendable with attachable
Limbs.

The components documented here are those included within ``datreant.core``.

.. _Treant_api:

Treant
------
The class :class:`datreant.core.Treant` is the central object of ``datreant.core``. 

.. autoclass:: datreant.core.Treant
    :members:
    :inherited-members:

.. _Tags_api:

Tags
````
The class :class:`datreant.core.limbs.Tags` is the interface used by Treants to
access their tags. 

.. autoclass:: datreant.core.limbs.Tags
    :members:
    :inherited-members:

.. _Categories_api:

Categories
``````````
The class :class:`datreant.core.limbs.Categories` is the interface used by
Treants to access their categories.

.. autoclass:: datreant.core.limbs.Categories
    :members:
    :inherited-members:
