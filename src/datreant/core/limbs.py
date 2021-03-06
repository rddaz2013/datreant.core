"""
Limbs are interfaces for accessing stored data, as well as querying
the state of an object.

"""
import os
import functools
from six import string_types, with_metaclass
from collections import defaultdict

from fuzzywuzzy import process

from .collections import Bundle
from . import _TREELIMBS, _LIMBS


class _TreeLimbmeta(type):
    def __init__(cls, name, bases, classdict):
        type.__init__(type, name, bases, classdict)

        limbname = classdict['_name']
        _TREELIMBS[limbname] = cls


class _Limbmeta(type):
    def __init__(cls, name, bases, classdict):
        type.__init__(type, name, bases, classdict)

        limbname = classdict['_name']
        _LIMBS[limbname] = cls


class TreeLimb(with_metaclass(_TreeLimbmeta, object)):
    """Core functionality for Tree limbs.

    TreeLimbs are meant to attach to Trees, which lack a state file. Since
    Treants are subclasses of Tree, they will inherit attachments of TreeLimbs
    to that class. A TreeLimb, unlike a Limb, does not need access to state
    file data.

    """
    # name used when attached to a Tree's namespace
    _name = 'limb'

    def __init__(self, tree):
        self._tree = tree


class Limb(with_metaclass(_Limbmeta, object)):
    """Core functionality for Treant limbs.

    """
    # name used when attached to a Treant's namespace
    _name = 'limb'

    def __init__(self, treant):
        self._treant = treant

    @property
    def _logger(self):
        return self._treant._logger


@functools.total_ordering
class Tags(Limb):
    """Interface to tags.

    """
    _name = 'tags'

    def __init__(self, treant):
        super(Tags, self).__init__(treant)

        # init state if tags not already there;
        # if read-only, check that they are there,
        # and raise exception if they are not
        try:
            with self._treant._write:
                try:
                    self._treant._state['tags']
                except KeyError:
                    self._treant._state['tags'] = list()
        except (IOError, OSError):
            with self._treant._read:
                try:
                    self._treant._state['tags']
                except KeyError:
                    raise KeyError(
                            ("Missing 'tags' data, and cannot write to "
                             "Treant '{}'".format(self._treant.filepath)))

    def __repr__(self):
        return "<Tags({})>".format(self._list())

    def __str__(self):
        tags = self._list()
        agg = "Tags"
        majsep = "="
        seplength = len(agg)

        if not tags:
            out = "No Tags"
        else:
            out = agg + '\n'
            out = out + majsep * seplength + '\n'
            for i in xrange(len(tags)):
                out = out + "'{}'\n".format(tags[i])
        return out

    @staticmethod
    def _setter(self, val):
        """Used for constructing the property when attaching this Limb to a class.

        """
        if isinstance(val, (Tags, list, set)):
            val = list(val)
            self.tags.clear()
            self.tags.add(val)
        else:
            raise TypeError("Can only set with tags, a list, or set")

    def __getitem__(self, value):
        with self._treant._read:
            if isinstance(value, list):
                # a list of tags gives only members with ALL the tags
                fits = all([self[item] for item in value])
            elif isinstance(value, tuple):
                # a tuple of tags gives members with ANY of the tags
                fits = any([self[item] for item in value])
            if isinstance(value, set):
                # a set of tags gives only members WITHOUT ALL the tags
                # can be used for `not`, basically
                fits = not all([self[item] for item in value])
            elif isinstance(value, string_types):
                fits = value in self

            return fits

    def __iter__(self):
        return self._list().__iter__()

    def __len__(self):
        return len(self._list())

    def __eq__(self, other):
        if isinstance(other, (Tags, set, list)):
            return set(self) == set(other)
        else:
            raise TypeError("Operands must be tags, a set, or list.")

    def __lt__(self, other):
        if isinstance(other, (Tags, set, list)):
            return set(self) < set(other)
        else:
            raise TypeError("Operands must be tags, a set, or list.")

    def __sub__(self, other):
        """Return a set giving the Tags in `a` that are not in `b`.

        """
        from .agglimbs import AggTags
        if isinstance(other, (AggTags, Tags, set, list)):
            return set(self) - set(other)
        else:
            raise TypeError("Operands must be AggTags, tags, a set, or list.")

    def __rsub__(self, other):
        """Return a set giving the Tags in `a` that are not in `b`.

        """
        from .agglimbs import AggTags  # may not be necessary
        if isinstance(other, (AggTags, Tags, set, list)):
            return set(other) - set(self)
        else:
            raise TypeError("Operands must be AggTags, tags, a set, or list.")

    def __or__(self, other):
        """Return a set giving the union of Tags `a` and `b`.

        """
        if isinstance(other, (Tags, set, list)):
            return set(self) | set(other)
        else:
            raise TypeError("Operands must be tags, a set, or list.")

    def __ror__(self, other):
        """Return a set giving the union of Tags `a` and `b`.

        """
        if isinstance(other, (Tags, set, list)):
            return set(self) | set(other)
        else:
            raise TypeError("Operands must be tags, a set, or list.")

    def __and__(self, other):
        """Return a set giving the intersection of Tags `a` and `b`.

        """
        if isinstance(other, (Tags, set, list)):
            return set(self) & set(other)
        else:
            raise TypeError("Operands must be tags, a set, or list.")

    def __rand__(self, other):
        """Return a set giving the intersection of Tags `a` and `b`.

        """
        if isinstance(other, (Tags, set, list)):
            return set(self) & set(other)
        else:
            raise TypeError("Operands must be tags, a set, or list.")

    def __xor__(self, other):
        """Return a set giving the symmetric difference of Tags
        `a` and `b`.

        """
        if isinstance(other, (Tags, set, list)):
            return set(self) ^ set(other)
        else:
            raise TypeError("Operands must be tags, a set, or list.")

    def __rxor__(self, other):
        """Return a set giving the symmetric difference of Tags
        `a` and `b`.

        """
        if isinstance(other, (Tags, set, list)):
            return set(self) ^ set(other)
        else:
            raise TypeError("Operands must be tags, a set, or list.")

    def _list(self):
        """Get all tags for the Treant as a list.

        :Returns:
            *tags*
                list of all tags
        """
        with self._treant._read:
            tags = self._treant._state['tags']

        tags.sort()
        return tags

    def add(self, *tags):
        """Add any number of tags to the Treant.

        Tags are individual strings that serve to differentiate Treants from
        one another. Sometimes preferable to categories.

        Parameters
        ----------
        tags : str or list
            Tags to add. Must be strings or lists of strings.

        """
        outtags = list()
        for tag in tags:
            if isinstance(tag, (list, set, tuple)):
                outtags.extend(tag)
            else:
                outtags.append(tag)

        with self._treant._write:
            # ensure tags are unique (we don't care about order)
            # also they must be strings
            _outtags = []
            for tag in outtags:
                if not isinstance(tag, string_types):
                    raise ValueError("Only string can be added as tags. Tried "
                                     "to add '{}' which is '{}'".format(
                                         tag, type(tag)))
                _outtags.append(tag)
            outtags = set(_outtags)

            # remove tags already present in metadata from list
            outtags = outtags.difference(set(self._treant._state['tags']))

            # add new tags
            self._treant._state['tags'].extend(outtags)

    def remove(self, *tags):
        """Remove tags from Treant.

        Any number of tags can be given as arguments, and these will be
        deleted.

        :Arguments:
            *tags*
                Tags to delete.
        """
        with self._treant._write:
            # remove redundant tags from given list if present
            tags = set([str(tag) for tag in tags])
            for tag in tags:
                # remove tag; if not present, continue anyway
                try:
                    self._treant._state['tags'].remove(tag)
                except ValueError:
                    pass

    def clear(self):
        """Remove all tags from Treant.

        """
        with self._treant._write:
            self._treant._state['tags'] = list()

    def fuzzy(self, tag, threshold=80):
        """Get a tuple of existing tags that fuzzily match a given one.

        Parameters
        ----------
        tags : str or list
            Tag or tags to get fuzzy matches for.
        threshold : int
            Lowest match score to return. Setting to 0 will return every tag,
            while setting to 100 will return only exact matches.

        Returns
        -------
        matches : tuple
            Tuple of tags that match.
        """
        if isinstance(tag, string_types):
            tags = [tag]
        else:
            tags = tag

        matches = []

        for tag in tags:
            matches += [i[0] for i in process.extract(tag, self, limit=None)
                        if i[1] > threshold]

        return tuple(matches)


class Categories(Limb):
    """Interface to categories.

    """
    _name = 'categories'

    def __init__(self, treant):
        super(Categories, self).__init__(treant)

        # init state if categories not already there;
        # if read-only, check that they are there,
        # and raise exception if they are not
        try:
            with self._treant._write:
                try:
                    self._treant._state['categories']
                except KeyError:
                    self._treant._state['categories'] = dict()
        except (IOError, OSError):
            with self._treant._read:
                try:
                    self._treant._state['categories']
                except KeyError:
                    raise KeyError(
                            ("Missing 'categories' data, and cannot write to "
                             "Treant '{}'".format(self._treant.filepath)))

    def __repr__(self):
        return "<Categories({})>".format(self._dict())

    def __str__(self):
        categories = self._dict()
        agg = "Categories"
        majsep = "="
        seplength = len(agg)

        if not categories:
            out = "No Categories"
        else:
            out = agg + '\n'
            out = out + majsep * seplength + '\n'
            for key in categories.keys():
                out = out + "'{}': '{}'\n".format(key, categories[key])
        return out

    @staticmethod
    def _setter(self, val):
        """Used for constructing the property when attaching this Limb to a class.

        """
        if isinstance(val, (Categories, dict)):
            val = dict(val)
            self.categories.clear()
            self.categories.add(val)
        else:
            raise TypeError("Can only set with categories or dict")

    def __getitem__(self, keys):
        """Get values for given `keys`.

        If `keys` is a string, the single value for that string is returned.

        If `keys` is a list of keys, the values for each key are returned in a
        list, in order by the given keys.

        if `keys` is a set of keys, a dict with the keys as keys and values as
        values is returned.

        Parameters
        ----------
        keys : str, list, set
            Key(s) of value to return.

        Returns
        -------
        values : str, int, float, bool, list, or dict
            Value(s) corresponding to given key(s).

        """
        categories = self._dict()

        if isinstance(keys, (int, float, string_types, bool)):
            return categories[keys]
        elif isinstance(keys, list):
            return [categories[key] for key in keys]
        elif isinstance(keys, set):
            return {key: categories[key] for key in keys}
        else:
            raise TypeError("Key must be a string, list of strings, or set"
                            " of strings.")

    def __setitem__(self, key, value):
        """Set value at given key.

        Parameters
        ----------
        key : str
            Key of value to set.
        value : str, int, float, bool
            Value to set for given key.

        """
        outdict = {key: value}
        self.add(outdict)

    def __delitem__(self, category):
        """Remove category from Treant.

        """
        self.remove(category)

    def __eq__(self, other):
        if isinstance(other, (Categories, dict)):
            return dict(self) == dict(other)
        else:
            raise TypeError("Operands must be categories or dicts.")

    def __req__(self, other):
        if isinstance(other, (Categories, dict)):
            return dict(self) == dict(other)
        else:
            raise TypeError("Operands must be categories or dicts.")

    def __iter__(self):
        return self._dict().__iter__()

    def __len__(self):
        return len(self._dict())

    def _dict(self):
        """Get all categories for the Treant as a dictionary.

        :Returns:
            *categories*
                dictionary of all categories

        """
        with self._treant._read:
            return self._treant._state['categories']

    def add(self, categorydict=None, **categories):
        """Add any number of categories to the Treant.

        Categories are key-value pairs that serve to differentiate Treants from
        one another. Sometimes preferable to tags.

        If a given category already exists (same key), the value given will
        replace the value for that category.

        Keys must be strings.

        Values may be ints, floats, strings, or bools. ``None`` as a value
        will not the existing value for the key, if present.

        Parameters
        ----------
        categorydict : dict
            Dict of categories to add; keys used as keys, values used as
            values.
        categories : dict
            Categories to add. Keyword used as key, value used as value.

        """
        outcats = dict()
        if isinstance(categorydict, (dict, Categories)):
            outcats.update(categorydict)
        elif categorydict is None:
            pass
        else:
            raise TypeError("Invalid arguments; non-keyword"
                            " argument must be dict")

        outcats.update(categories)

        with self._treant._write:
            for key, value in outcats.items():
                if not isinstance(key, string_types):
                    raise TypeError("Keys must be strings.")

                if (isinstance(value, (int, float, string_types, bool))):
                    self._treant._state['categories'][key] = value
                elif value is not None:
                    raise TypeError("Values must be ints, floats,"
                                    " strings, or bools.")

    def remove(self, *categories):
        """Remove categories from Treant.

        Any number of categories (keys) can be given as arguments, and these
        keys (with their values) will be deleted.

        Parameters
        ----------
        categories : str
                Categories to delete.

        """
        with self._treant._write:
            for key in categories:
                # continue even if key not already present
                self._treant._state['categories'].pop(key, None)

    def clear(self):
        """Remove all categories from Treant.

        """
        with self._treant._write:
            self._treant._state['categories'] = dict()

    def keys(self):
        """Get category keys.

        :Returns:
            *keys*
                keys present among categories
        """
        with self._treant._read:
            return self._treant._state['categories'].keys()

    def values(self):
        """Get category values.

        :Returns:
            *values*
                values present among categories
        """
        with self._treant._read:
            return self._treant._state['categories'].values()
