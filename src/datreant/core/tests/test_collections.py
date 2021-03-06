"""Tests for Bundle.

"""

import numpy as np
import pytest

import datreant.core as dtr


def do_stuff(cont):
    return cont.name + cont.uuid


def return_nothing(cont):
    b = cont.name + cont.uuid


class CollectionsTests(object):
    """Mixin tests for collections"""
    class TestGetitem(object):
        @pytest.mark.parametrize('slx', (
            [1, 2],
            np.array([1, 2]),
        ))
        def test_fancy_index(self, filled_collection, slx):
            b, (t1, t2, t3) = filled_collection
            sl = b[slx]
            assert len(sl) == 2
            assert t2 == sl[0]
            assert t3 == sl[1]

        @pytest.mark.parametrize('slx', (
            [False, False, True],
            np.array([False, False, True]),
        ))
        def test_boolean_index(self, filled_collection, slx):
            b, (t1, t2, t3) = filled_collection
            sl = b[slx]
            assert len(sl) == 1
            assert t3 == sl[0]

        @pytest.mark.parametrize('slx', (
            slice(0, 1, None),
            slice(1, None, None),
            slice(None, None, -1),
            slice(None, None, 2),
        ))
        def test_slice_index(self, filled_collection, slx):
            b, ts = filled_collection
            sl = b[slx]
            ref = ts[slx]
            for x, y in zip(sl, ref):
                assert x == y

        def test_getitem_IE(self, filled_collection):
            bundle = filled_collection[0]
            with pytest.raises(IndexError):
                bundle[4.0]

    class TestSetOperations(object):
        def test_sub_single(self, filled_collection):
            b, (t1, t2, t3) = filled_collection
            b1 = b[[0, 1, 2]]
            b2 = b[1]
            b3 = b1 - b2
            assert len(b3) == 2
            assert t1 in b3
            assert t2 not in b3
            assert t3 in b3

        def test_sub_many(self, filled_collection):
            b, (t1, t2, t3) = filled_collection
            b1 = b[[0, 1]]
            b2 = b[[1, 2]]
            b3 = b1 - b2
            assert len(b3) == 1
            assert t1 in b3
            assert t2 not in b3

        def test_or(self, filled_collection):
            b, (t1, t2, t3) = filled_collection
            b1 = b[[0, 1]]
            b2 = b[[1, 2]]
            b3 = b1 | b2
            assert t1 in b3
            assert t2 in b3
            assert t3 in b3

        def test_and(self, filled_collection):
            b, (t1, t2, t3) = filled_collection
            b1 = b[[0, 1]]
            b2 = b[[1, 2]]
            b3 = b1 & b2
            assert t1 not in b3

        def test_xor(self, filled_collection):
            b, (t1, t2, t3) = filled_collection
            b1 = b[[0, 1]]
            b2 = b[[1, 2]]
            b3 = b1 ^ b2
            assert len(b3) == 2
            assert t1 in b3
            assert t2 not in b3
            assert t3 in b3

        def test_sub_TypeError(self, filled_collection):
            b = filled_collection[0]
            with pytest.raises(TypeError):
                b - ['this']

        def test_or_TypeError(self, filled_collection):
            b = filled_collection[0]
            with pytest.raises(TypeError):
                b | ['this']

        def test_and_TypeError(self, filled_collection):
            b = filled_collection[0]
            with pytest.raises(TypeError):
                b & ['this']

        def test_xor_TypeError(self, filled_collection):
            b = filled_collection[0]
            with pytest.raises(TypeError):
                b ^ ['this']

    class TestAddition(object):
        def test_add_many(self, filled_collection):
            b, (t1, t2, t3) = filled_collection
            b1 = b[[0, 1]]
            b2 = b[[1, 2]]
            b3 = b1 + b2
            assert len(b3) == 3
            assert t1 in b3
            assert t2 in b3
            assert t3 in b3

        def test_add_singular(self, filled_collection):
            b, (t1, t2, t3) = filled_collection
            b1 = b[[0, 1]]
            b2 = b[2]
            b3 = b1 + b2
            assert len(b3) == 3
            assert t1 in b3
            assert t2 in b3
            assert t3 in b3

        def test_add(self, filled_collection):
            b = filled_collection[0]
            with pytest.raises(TypeError):
                b + 25


class TestView(CollectionsTests):
    """Tests for Views"""

    @pytest.fixture
    def collection(self):
        return dtr.View()

    @pytest.fixture
    def filled_collection(self, tmpdir):
        # returns (a bundle of [t1, t2, t3], then individal references to each)
        with tmpdir.as_cwd():
            b = dtr.View()
            t1 = dtr.Tree('larry')
            t2 = dtr.Leaf('curly')
            t3 = dtr.Treant('moe')
            b.add(t1, t2, t3)
            return b, (t1, t2, t3)

    class TestGetitem(CollectionsTests.TestGetitem):
        def test_getitem_name_string(self, filled_collection):
            b, (t1, t2, t3) = filled_collection
            n = t1.name

            b_new = b[n]
            assert isinstance(b_new, dtr.View)
            assert b_new[0] == t1

    class TestAddition(CollectionsTests.TestAddition):
        def test_tree_addition(self, filled_collection):
            b, (t1, t2, t3) = filled_collection
            b1 = b[[1, 2]]
            b3 = b1 + t1
            assert len(b3) == 3
            assert isinstance(b3, dtr.View)
            assert t1 in b3

        def test_leaf_addition(self, filled_collection):
            b, (t1, t2, t3) = filled_collection
            b1 = b[[0, 2]]
            b3 = b1 + t2
            assert len(b3) == 3
            assert isinstance(b3, dtr.View)
            assert t2 in b3

        def test_treant_addition(self, filled_collection):
            b, (t1, t2, t3) = filled_collection
            b1 = b[[0, 1]]
            b3 = b1 + t3
            assert len(b3) == 3
            assert isinstance(b3, dtr.View)
            assert t2 in b3

    def test_exists(self, collection, tmpdir):
        pass


class TestBundle(CollectionsTests):
    """Tests for elements of Bundle"""

    @pytest.fixture
    def collection(self):
        return dtr.Bundle()

    @pytest.fixture
    def filled_collection(self, tmpdir):
        # returns (a bundle of [t1, t2, t3], then individal references to each)
        with tmpdir.as_cwd():
            b = dtr.Bundle()
            t1 = dtr.Treant('larry')
            t2 = dtr.Treant('curly')
            t3 = dtr.Treant('moe')
            b.add(t1, t2, t3)
            return b, (t1, t2, t3)

    @pytest.fixture
    def testtreant(self, tmpdir, request):
        with tmpdir.as_cwd():
            t = dtr.Treant('dummytreant')
        return t

    @pytest.fixture
    def testtreant2(self, tmpdir, request):
        with tmpdir.as_cwd():
            t = dtr.Treant('dummytreant2')
        return t

    def test_additive(self, tmpdir, testtreant, testtreant2, collection):
        """Test that addition of treants and collections give Bundles.

        """
        with tmpdir.as_cwd():
            assert isinstance(testtreant + testtreant2, dtr.Bundle)
            assert len(testtreant + testtreant2) == 2

            b = collection + testtreant + testtreant2

            # beating a dead horse
            assert len(b) == 2

    class TestGetitem(CollectionsTests.TestGetitem):
        def test_getitem_name_string(self, filled_collection):
            b, (t1, t2, t3) = filled_collection
            n = t1.name

            b_new = b[n]
            assert isinstance(b_new, dtr.Bundle)
            assert b_new[0] == t1

        def test_getitem_uuid_string(self, filled_collection):
            b, (t1, t2, t3) = filled_collection
            n = t2.uuid
            t_new = b[n]
            assert t_new == t2

        def test_getitem_string_KeyError(self, filled_collection):
            b = filled_collection[0]
            with pytest.raises(KeyError):
                b['not there']

    def test_add_members(self, collection, tmpdir):
        """Try adding members in a number of ways"""
        with tmpdir.as_cwd():
            t1 = dtr.Treant('lark')
            t2 = dtr.Treant('hark')
            t3 = dtr.Treant('linus')

            collection.add(t1, [t3, t2])

            for cont in (t1, t2, t3):
                assert cont in collection

            t4 = dtr.Treant('snoopy')
            collection.add([[t4], t2])
            assert t4 in collection

            # the group won't add members it alrady has
            # (operates as an ordered set)
            assert len(collection) == 4

    def test_add_members_glob(self, collection, tmpdir):
        """Try adding members with globbing"""
        with tmpdir.as_cwd():
            t1 = dtr.Treant('lark')
            t2 = dtr.Treant('hark')
            t3 = dtr.Treant('linus')

            collection.add('*ark')

            for treant in (t1, t2):
                assert treant in collection

            assert t3 not in collection

    def test_get_members(self, collection, tmpdir):
        """Access members with indexing and slicing"""
        with tmpdir.as_cwd():
            t1 = dtr.Treant('larry')
            t2 = dtr.Treant('curly')
            t3 = dtr.Treant('moe')

            collection.add([[[t1, [t2, [t3]]]]])

            assert collection[1] == t2

            t4 = dtr.treants.Treant('shemp')
            collection.add(t4)

            for member in (t1, t2, t3):
                assert member in collection[:3]

            assert t4 not in collection[:3]
            assert t4 == collection[-1]

    def test_remove_members(self, collection, tmpdir):
        """Try removing members"""
        with tmpdir.as_cwd():
            t1 = dtr.Treant('lion-o')
            t2 = dtr.Treant('cheetara')
            t3 = dtr.Treant('snarf')

            collection.add(t3, t1, t2)

            for cont in (t1, t2, t3):
                assert cont in collection

            collection.remove(1)
            assert t1 not in collection

            collection.remove(t2)
            assert t2 not in collection

    def test_remove_members_name(self, collection, tmpdir):
        """Try removing members with names and globbing"""
        with tmpdir.as_cwd():
            t1 = dtr.Treant('lark')
            t2 = dtr.Treant('elsewhere/lark')
            t3 = dtr.Treant('hark')
            t4 = dtr.Treant('linus')

            stuff = [t1, t2, t3, t4]

            # test removal by name
            collection.add(stuff)
            for item in stuff:
                assert item in collection

            # should remove both treants with name 'lark'
            collection.remove('lark')

            for item in (t3, t4):
                assert item in collection

            for item in (t1, t2):
                assert item not in collection

            # test removal by a unix-style glob pattern
            collection.add(stuff)
            for item in stuff:
                assert item in collection

            # should remove 'lark' and 'hark' treants
            collection.remove('*ark')

            assert t4 in collection

            for item in (t1, t2, t3):
                assert item not in collection

    def test_member_attributes(self, collection, tmpdir):
        """Get member uuids, names, and treanttypes"""
        with tmpdir.as_cwd():
            t1 = dtr.Treant('bigger')
            t2 = dtr.Treant('faster')
            t3 = dtr.Treant('stronger')

        collection.add(t1, t2, t3)

        uuids = [cont.uuid for cont in [t1, t2, t3]]
        assert collection.uuids == uuids

        names = [cont.name for cont in [t1, t2, t3]]
        assert collection.names == names

        treanttypes = [cont.treanttype for cont in [t1, t2, t3]]
        assert collection.treanttypes == treanttypes

    def test_map(self, collection, tmpdir):
        with tmpdir.as_cwd():
            t1 = dtr.Treant('lark')
            t2 = dtr.Treant('hark')
            t3 = dtr.Treant('linus')

        collection.add(t1, t2, t3)

        comp = [cont.name + cont.uuid for cont in collection]
        assert collection.map(do_stuff) == comp
        assert collection.map(do_stuff, processes=2) == comp

        assert collection.map(return_nothing) is None
        assert collection.map(return_nothing, processes=2) is None

    class TestAggTags:
        """Test behavior of manipulating tags collectively.

        """
        def test_add_tags(self, collection, testtreant, testtreant2, tmpdir):
            with tmpdir.as_cwd():
                collection.add(testtreant, testtreant2)

                assert len(collection.tags) == 0

                collection.tags.add('broiled', 'not baked')

                assert len(collection.tags) == 2
                for tag in ('broiled', 'not baked'):
                    assert tag in collection.tags

        def test_tags_setting(self, collection, testtreant,
                              testtreant2, tmpdir):
            with tmpdir.as_cwd():
                collection.add(testtreant, testtreant2)

                assert len(collection.tags) == 0

                # add as list
                collection.tags = ['broiled', 'not baked']

                assert len(collection.tags) == 2
                for tag in ('broiled', 'not baked'):
                    assert tag in collection.tags

                collection.tags.clear()

                # add as set
                collection.tags = {'broiled', 'not baked'}

                assert len(collection.tags) == 2
                for tag in ('broiled', 'not baked'):
                    assert tag in collection.tags

                collection.tags.clear()

                # add as Tags
                t = dtr.Treant('mark twain')
                t.tags.add('literature', 'quotables')
                collection.tags = t.tags

                assert len(collection.tags) == 2
                for tag in ('literature', 'quotables'):
                    assert tag in collection.tags

        def test_tags_all(self, collection, tmpdir):
            with tmpdir.as_cwd():

                moe = dtr.Treant('moe',
                                 tags=['smartest', 'mean', 'stooge'])
                larry = dtr.Treant('larry',
                                   tags=['weird', 'means well', 'stooge'])
                curly = dtr.Treant('curly',
                                   tags=['dumb', 'nyuk-nyuk', 'stooge'])

                collection.add(moe, larry, curly)

                assert len(collection.tags.all) == 1
                assert 'stooge' in collection.tags.all

        def test_tags_any(self, collection, testtreant, testtreant2, tmpdir):
            with tmpdir.as_cwd():

                moe = dtr.Treant('moe',
                                 tags=['smartest', 'mean', 'stooge'])
                larry = dtr.Treant('larry',
                                   tags=['weird', 'means well', 'stooge'])
                curly = dtr.Treant('curly',
                                   tags=['dumb', 'nyuk-nyuk', 'stooge'])

                collection.add(moe, larry, curly)

                assert len(collection.tags.any) == 7
                for tag in ('smartest', 'mean', 'weird', 'means well',
                            'dumb', 'nyuk-nyuk', 'stooge'):
                    assert tag in collection.tags.any

        def test_tags_set_behavior(self, collection, tmpdir):
            with tmpdir.as_cwd():

                t1 = dtr.Treant('maple')
                t2 = dtr.Treant('pine')
                t3 = dtr.Treant('juniper')
                t1.tags.add({'tree', 'new jersey', 'deciduous'})
                t2.tags.add({'tree', 'new york', 'evergreen'})
                t3.tags.add({'shrub', 'new york', 'evergreen'})
                collection.add(t1, t2, t3)
                trees = dtr.Bundle('maple', 'pine')
                evergreens = dtr.Bundle('pine', 'juniper')
                tags = collection.tags

                assert len(tags.any) == 6

                # test equality: __eq__ (==)
                assert t1.tags == {'tree', 'new jersey', 'deciduous'}
                assert t2.tags == {'tree', 'new york', 'evergreen'}
                assert t3.tags == {'shrub', 'new york', 'evergreen'}

                # test subset: __lt__ (<)
                assert not t1.tags < {'tree', 'new jersey', 'deciduous'}
                assert tags < {'tree', 'new jersey', 'deciduous'}
                assert t1.tags < tags.any
                assert t2.tags < tags.any
                assert t3.tags < tags.any

                # test difference: __sub__ (-)
                assert t1.tags - {'tree'} == {'new jersey', 'deciduous'}
                assert trees.tags - {'tree'} == set()

                # test right difference: __rsub__ (-)
                evergreen_ny_shrub = {'evergreen', 'new york', 'shrub'}
                dec_nj_sh = {'deciduous', 'new jersey', 'shrub'}
                assert tags.any - t1.tags == evergreen_ny_shrub
                assert tags.any - evergreens.tags - trees.tags == dec_nj_sh
                assert {'tree'} - trees.tags == set()

                # test union: __or__ (|)
                evergreen_ny_shrub = {'evergreen', 'new york', 'shrub'}
                assert evergreens.tags | t3.tags == evergreen_ny_shrub
                assert t1.tags | t2.tags | t3.tags == tags.any

                # test right union: __ror__ (|)
                assert {'shrub'} | evergreens.tags == evergreen_ny_shrub
                assert t3.tags | {'tree'} == {'tree'} | t3.tags

                # test intersection: __and__ (&)
                evergreen_ny = {'evergreen', 'new york'}
                assert evergreens.tags & t3.tags == evergreen_ny
                assert t1.tags & t2.tags & t3.tags == tags.all

                # test right intersection: __rand__ (&)
                assert evergreen_ny_shrub & evergreens.tags == evergreen_ny
                assert t3.tags & {'shrub'} == {'shrub'} & t3.tags

                # test symmetric difference: __xor__ (^)
                evergreen_ny_tree = {'evergreen', 'new york', 'tree'}
                assert trees.tags ^ evergreens.tags == evergreen_ny_tree
                assert evergreens.tags ^ t3.tags == {'shrub'}
                assert t1.tags ^ t2.tags ^ t3.tags == dec_nj_sh

                # test right symmetric difference: __rxor__ (^)
                assert {'new york'} ^ evergreens.tags == {'evergreen'}
                assert {'shrub'} ^ trees.tags == t2.tags ^ t3.tags

                # type_error_msg = "Operands must be AggTags, Tags, or a set."
                with pytest.raises(TypeError) as e:
                    ['tree'] == trees.tags
                # assert e.value.message == type_error_msg
                with pytest.raises(TypeError) as e:
                    trees.tags < ['tree']
                # assert e.value.message == type_error_msg
                with pytest.raises(TypeError) as e:
                    ['tree'] - trees.tags
                # assert e.value.message == type_error_msg
                with pytest.raises(TypeError) as e:
                    trees.tags - ['tree']
                # assert e.value.message == type_error_msg
                with pytest.raises(TypeError) as e:
                    ['tree'] | trees.tags
                # assert e.value.message == type_error_msg
                with pytest.raises(TypeError) as e:
                    trees.tags | ['tree']
                # assert e.value.message == type_error_msg
                with pytest.raises(TypeError) as e:
                    ['tree'] & trees.tags
                # assert e.value.message == type_error_msg
                with pytest.raises(TypeError) as e:
                    trees.tags & ['tree']
                # assert e.value.message == type_error_msg
                with pytest.raises(TypeError) as e:
                    ['tree'] ^ trees.tags
                # assert e.value.message == type_error_msg
                with pytest.raises(TypeError) as e:
                    trees.tags ^ ['tree']
                # assert e.value.message == type_error_msg

        def test_tags_getitem(self, collection, testtreant,
                              testtreant2, tmpdir):
            with tmpdir.as_cwd():

                t1 = dtr.Treant('maple')
                t2 = dtr.Treant('pine')
                t1.tags.add({'tree', 'new jersey', 'deciduous'})
                t2.tags.add({'tree', 'new york', 'evergreen'})
                collection.add(t1, t2)
                tags = collection.tags

                assert len(tags.any) == 5
                # test single tags
                assert tags['tree'] == [True, True]
                assert tags['deciduous'] == [True, False]
                assert tags['evergreen'] == [False, True]
                assert tags['new jersey'] == [True, False]
                assert tags['new york'] == [False, True]
                assert tags[{'tree'}] == [False, False]
                assert tags[{'deciduous'}] == [False, True]
                assert tags[{'evergreen'}] == [True, False]
                assert tags[{'new jersey'}] == [False, True]
                assert tags[{'new york'}] == [True, False]

                # test for Treants with ALL the given tags
                assert tags[['tree', 'deciduous']] == [True, False]
                assert tags[['tree', 'evergreen']] == [False, True]
                assert tags[['new jersey', 'evergreen']] == [False, False]

                # test for Treants with ANY of the given tags
                assert tags[('tree', 'deciduous')] == [True, True]
                assert tags[('deciduous', 'evergreen')] == [True, True]
                assert tags[('new york', 'evergreen')] == [False, True]

                # test for Treants without at least one of the given tags
                assert tags[{'deciduous', 'evergreen'}] == [True, True]
                assert tags[{'tree', 'deciduous'}] == [False, True]
                assert tags[{'tree', 'new york', 'evergreen'}] == [True, False]

                # complex logic tests

                # give those that are evergreen or in NY AND also not deciduous
                selection = [('evergreen', 'new york'), {'deciduous'}]
                assert tags[selection] == [False, True]
                # give those that are evergreen or in NY AND also not a tree
                selection = [('evergreen', 'new york'), {'tree'}]
                assert tags[selection] == [False, False]
                # give a tree that's in NJ OR anything that's not evergreen
                selection = (['tree', 'new jersey'], {'evergreen'})
                assert tags[selection] == [True, False]
                # cannot be a tree in NJ, AND must also be deciduous
                # I.e., give all deciduous things that aren't trees in NJ
                selection = [{'tree', 'new jersey'}, 'deciduous']
                assert tags[selection] == [False, False]

        def test_tags_fuzzy(self, collection, testtreant, testtreant2, tmpdir):
            with tmpdir.as_cwd():

                t1 = dtr.Treant('maple')
                t2 = dtr.Treant('pine')
                t1.tags.add({'tree', 'new jersey', 'deciduous'})
                t2.tags.add({'tree', 'new york', 'evergreen'})
                collection.add(t1, t2)
                tags = collection.tags

                assert len(tags.any) == 5

                all_tree1 = tags.fuzzy('tree', threshold=80, scope='all')
                all_tree2 = tags.fuzzy('tree')
                assert all_tree1 == all_tree2
                assert all_tree2 == ('tree',)

                any_deciduous = tags.fuzzy('deciduous', scope='any')
                assert any_deciduous == ('deciduous',)
                all_evergreen = tags.fuzzy('evergreen')
                assert all_evergreen == ()

                # check that fuzzy matching is independent of threshold when
                # exact tag is present in all members
                all_tree_strict = tags.fuzzy('tree', threshold=99)
                assert all_tree_strict == ('tree',)
                all_tree_tolerant = tags.fuzzy('tree', threshold=0)
                assert all_tree_tolerant == ('tree',)

                # check that fuzzy matching will give differing tags when
                # members have similar tag names ('new') and the threshold is
                # varied
                all_ny = tags.fuzzy('new york')
                assert all_ny == ()
                any_ny_strict = tags.fuzzy('new york', scope='any')
                assert any_ny_strict == ('new york',)
                any_ny_tol = tags.fuzzy('new york', threshold=50, scope='any')
                assert set(any_ny_tol) == {'new york', 'new jersey'}

                # check fuzzy matching for multiple tags (scope='all')
                new_ever = ['new', 'evergreen']
                all_mul_strict = tags.fuzzy(new_ever, threshold=80)
                assert all_mul_strict == ()
                all_mul_tol = tags.fuzzy(new_ever, threshold=30)
                assert all_mul_tol == ('tree',)

                # check fuzzy matching for multiple tags (scope='any')
                new_tree = ['new', 'tree']
                any_mul_stric = tags.fuzzy(new_tree, threshold=90, scope='any')
                assert any_mul_stric == ('tree',)
                any_mul_tol = tags.fuzzy(new_tree, threshold=80, scope='any')
                assert set(any_mul_tol) == {'new york', 'new jersey', 'tree'}
                nj_decid = ['new jersey', 'decid']
                any_mul_njdec = tags.fuzzy(nj_decid, threshold=80, scope='any')
                assert set(any_mul_njdec) == {'new jersey', 'deciduous'}

        def test_tags_filter(self, collection, testtreant,
                             testtreant2, tmpdir):
            with tmpdir.as_cwd():

                maple = dtr.Treant('maple')
                pine = dtr.Treant('pine')
                maple.tags.add({'tree', 'new jersey', 'deciduous'})
                pine.tags.add({'tree', 'new york', 'evergreen'})
                collection.add(maple, pine)
                tags = collection.tags

                maple_bund = dtr.Bundle(maple)
                pine_bund = dtr.Bundle(pine)

                assert len(tags.any) == 5

                # filter using single tags
                assert tags.filter('tree') == collection
                assert tags.filter({'tree'}) == dtr.Bundle()
                assert tags.filter('deciduous') == maple_bund
                assert tags.filter('evergreen') == pine_bund
                assert tags.filter('new jersey') == maple_bund
                assert tags.filter('new york') == pine_bund

                # filter Treants that DON'T have a given tag
                assert tags.filter({'new york'}) == maple_bund
                assert tags.filter({'deciduous'}) == pine_bund

                # filter Treants containing all of the tags
                assert tags.filter(['deciduous', 'tree']) == maple_bund
                assert tags.filter(['evergreen', 'tree']) == pine_bund
                assert tags.filter(['deciduous', 'new york']) == dtr.Bundle()

                # filter Treants containing any of the tags tags
                assert tags.filter(('evergreen', 'tree')) == collection
                assert tags.filter(('deciduous', 'new york')) == collection
                assert tags.filter(('evergreen', 'new york')) == pine_bund

                # filter Treants that exclude any of the provided tags
                assert tags.filter({'deciduous', 'new york'}) == collection
                assert tags.filter({'deciduous', 'new jersey'}) == pine_bund
                assert tags.filter({'evergreen', 'tree'}) == maple_bund

                # complex logic tests

                # give those that are evergreen or in NY AND also not deciduous
                selection = [('evergreen', 'new york'), {'deciduous'}]
                assert tags.filter(selection) == pine_bund
                # give those that are evergreen or in NY AND also not a tree
                selection = [('evergreen', 'new york'), {'tree'}]
                assert tags.filter(selection) == dtr.Bundle()
                # give a tree that's in NJ OR anything that's not evergreen
                selection = (['tree', 'new jersey'], {'evergreen'})
                assert tags.filter(selection) == maple_bund
                # cannot be a tree in NJ, AND must also be deciduous
                # I.e., give all deciduous things that aren't trees in NJ
                selection = [{'tree', 'new jersey'}, 'deciduous']
                assert tags.filter(selection) == dtr.Bundle()

    class TestAggCategories:
        """Test behavior of manipulating categories collectively.

        """
        def test_add_categories(self, collection, testtreant, testtreant2,
                                tmpdir):
            with tmpdir.as_cwd():
                # add a couple test Treants to collection
                collection.add(testtreant, testtreant2)
                assert len(collection.categories) == 0

                # add 'age' and 'bark' as categories of this collection
                collection.categories.add({'age': 42}, bark='smooth')
                assert len(collection.categories) == 2

                for member in collection:
                    assert member.categories['age'] == 42
                    assert member.categories['bark'] == 'smooth'
                for key in ['age', 'bark']:
                    assert key in collection.categories.any

                t1 = dtr.Treant('hickory')
                t1.categories.add(bark='shaggy', species='ovata')
                collection.add(t1)
                assert len(collection.categories) == 1
                assert len(collection.categories.all) == 1
                assert len(collection.categories.any) == 3

                collection.categories.add(location='USA')
                assert len(collection.categories) == 2
                assert len(collection.categories.all) == 2
                assert len(collection.categories.any) == 4
                for member in collection:
                    assert member.categories['location'] == 'USA'

        def test_categories_getitem(self, collection, testtreant, testtreant2,
                                    tmpdir):
            with tmpdir.as_cwd():
                # add a couple test Treants to collection
                collection.add(testtreant, testtreant2)
                # add 'age' and 'bark' as categories of this collection
                collection.categories.add({'age': 42, 'bark': 'smooth'})

                t1 = dtr.Treant('maple')
                t2 = dtr.Treant('sequoia')
                t1.categories.add({'age': 'seedling', 'bark': 'rough',
                                   'type': 'deciduous'})
                t2.categories.add({'age': 'adult', 'bark': 'rough',
                                   'type': 'evergreen', 'nickname': 'redwood'})
                collection.add(t1, t2)
                assert len(collection.categories) == 2
                assert len(collection.categories.any) == 4

                # test values for each category in the collection
                age_list = [42, 42, 'seedling', 'adult']
                assert age_list == collection.categories['age']
                bark_list = ['smooth', 'smooth', 'rough', 'rough']
                assert bark_list == collection.categories['bark']
                type_list = [None, None, 'deciduous', 'evergreen']
                assert type_list == collection.categories['type']
                nick_list = [None, None,  None, 'redwood']
                assert nick_list == collection.categories['nickname']

                # test list of keys as input
                cat_list = [age_list, type_list]
                assert cat_list == collection.categories[['age', 'type']]

                # test set of keys as input
                cat_set = {'bark': bark_list, 'nickname': nick_list}
                assert cat_set == collection.categories[{'bark', 'nickname'}]

        def test_categories_setitem(self, collection, testtreant, testtreant2,
                                    tmpdir):
            with tmpdir.as_cwd():
                # add a couple test Treants to collection
                collection.add(testtreant, testtreant2)
                # add 'age' and 'bark' as categories of this collection
                collection.categories.add({'age': 42, 'bark': 'smooth'})

                t1 = dtr.Treant('maple')
                t2 = dtr.Treant('sequoia')
                t1.categories.add({'age': 'seedling', 'bark': 'rough',
                                   'type': 'deciduous'})
                t2.categories.add({'age': 'adult', 'bark': 'rough',
                                   'type': 'evergreen', 'nickname': 'redwood'})
                collection.add(t1, t2)

                # test setting a category when all members have it
                for value in collection.categories['age']:
                    assert value in [42, 42, 'seedling', 'adult']
                collection.categories['age'] = 'old'
                for value in collection.categories['age']:
                    assert value in ['old', 'old', 'old', 'old']

                # test setting a new category (no members have it)
                assert 'location' not in collection.categories.any
                collection.categories['location'] = 'USA'
                for value in collection.categories['location']:
                    assert value in ['USA', 'USA', 'USA', 'USA']

                # test setting a category that only some members have
                assert 'nickname' in collection.categories.any
                assert 'nickname' not in collection.categories.all
                collection.categories['nickname'] = 'friend'
                for value in collection.categories['nickname']:
                    assert value in ['friend', 'friend', 'friend', 'friend']

                # test setting values for individual members
                assert 'favorite ice cream' not in collection.categories
                ice_creams = ['rocky road',
                              'americone dream',
                              'moose tracks',
                              'vanilla']
                collection.categories['favorite ice cream'] = ice_creams

                for member, ice_cream in zip(collection, ice_creams):
                    assert member.categories['favorite ice cream'] == ice_cream

        def test_categories_all(self, collection, testtreant, testtreant2,
                                tmpdir):
            with tmpdir.as_cwd():
                # add a couple test Treants to collection
                collection.add(testtreant, testtreant2)
                # add 'age' and 'bark' as categories of this collection
                collection.categories.add({'age': 42}, bark='bare')

                # add categories to 'hickory' Treant, then add to collection
                t1 = dtr.Treant('hickory')
                t1.categories.add(bark='shaggy', species='ovata')
                collection.add(t1)
                # check the contents of 'bark', ensure 'age' and 'species' are
                # not shared categories of the collection
                collection.add(t1)
                common_categories = collection.categories.all
                assert len(collection.categories) == len(common_categories)
                assert 'age' not in common_categories
                assert 'species' not in common_categories
                assert common_categories['bark'] == ['bare', 'bare', 'shaggy']

                # add 'location' category to collection
                collection.categories.add(location='USA')
                common_categories = collection.categories.all
                # ensure all members have 'USA' for their 'location'
                assert len(collection.categories) == len(common_categories)
                assert 'age' not in common_categories
                assert 'species' not in common_categories
                assert common_categories['bark'] == ['bare', 'bare', 'shaggy']
                assert common_categories['location'] == ['USA', 'USA', 'USA']

                # add 'location' category to collection
                collection.categories.remove('bark')
                common_categories = collection.categories.all
                # check that only 'location' is a shared category
                assert len(collection.categories) == len(common_categories)
                assert 'age' not in common_categories
                assert 'bark' not in common_categories
                assert 'species' not in common_categories
                assert common_categories['location'] == ['USA', 'USA', 'USA']

        def test_categories_any(self, collection, testtreant, testtreant2,
                                tmpdir):
            with tmpdir.as_cwd():
                # add a couple test Treants to collection
                collection.add(testtreant, testtreant2)
                # add 'age' and 'bark' as categories of this collection
                collection.categories.add({'age': 42}, bark='smooth')
                assert len(collection.categories.any) == 2

                # add categories to 'hickory' Treant, then add to collection
                t1 = dtr.Treant('hickory')
                t1.categories.add(bark='shaggy', species='ovata')
                collection.add(t1)
                # check the contents of 'bark', ensure 'age' and 'species' are
                # not shared categories of the collection
                every_category = collection.categories.any
                assert len(every_category) == 3
                assert every_category['age'] == [42, 42, None]
                assert every_category['bark'] == ['smooth', 'smooth', 'shaggy']
                assert every_category['species'] == [None, None, 'ovata']

                # add 'location' category to collection
                collection.categories.add(location='USA')
                every_category = collection.categories.any
                # ensure all members have 'USA' for their 'location'
                assert len(every_category) == 4
                assert every_category['age'] == [42, 42, None]
                assert every_category['bark'] == ['smooth', 'smooth', 'shaggy']
                assert every_category['species'] == [None, None, 'ovata']
                assert every_category['location'] == ['USA', 'USA', 'USA']

                # add 'sprout' to 'age' category of 'hickory' Treant
                t1.categories['age'] = 'sprout'
                every_category = collection.categories.any
                # check 'age' is category for 'hickory' and is 'sprout'
                assert len(every_category) == 4
                assert every_category['age'] == [42, 42, 'sprout']
                assert every_category['bark'] == ['smooth', 'smooth', 'shaggy']
                assert every_category['species'] == [None, None, 'ovata']
                assert every_category['location'] == ['USA', 'USA', 'USA']

                # add 'location' category to collection
                collection.categories.remove('bark')
                every_category = collection.categories.any
                # check that only 'location' is a shared category
                assert len(every_category) == 3
                assert every_category['age'] == [42, 42, 'sprout']
                assert every_category['species'] == [None, None, 'ovata']
                assert every_category['location'] == ['USA', 'USA', 'USA']
                assert 'bark' not in every_category

        def test_categories_remove(self, collection, testtreant, testtreant2,
                                   tmpdir):
            with tmpdir.as_cwd():
                t1 = dtr.Treant('maple')
                t2 = dtr.Treant('sequoia')
                collection.add(t1, t2)
                collection.categories.add({'age': 'sprout'}, bark='rough')

                # add a couple test Treants to collection
                collection.add(testtreant, testtreant2)
                assert len(collection.categories) == 0
                assert len(collection.categories.any) == 2

                # add 'USA', ensure 'location', 'age', 'bark' is a category in
                # at least one of the members
                collection.categories.add(location='USA')
                assert len(collection.categories) == 1
                for key in ['location', 'age', 'bark']:
                    assert key in collection.categories.any
                # ensure 'age' and 'bark' are each not categories for all
                # members in collection
                assert 'age' not in collection.categories
                assert 'bark' not in collection.categories

                # remove 'bark', test for any instance of 'bark' in the
                # collection
                collection.categories.remove('bark')
                assert len(collection.categories) == 1
                for key in ['location', 'age']:
                    assert key in collection.categories.any
                assert 'bark' not in collection.categories.any

                # remove 'age', test that 'age' is not a category for any
                # member in collection
                collection.categories.remove('age')
                for member in collection:
                    assert 'age' not in member.categories
                # test that 'age' is not a category of this collection
                assert 'age' not in collection.categories.any

        def test_categories_keys(self, collection, testtreant, testtreant2,
                                 tmpdir):
            with tmpdir.as_cwd():
                # add a couple test Treants to collection
                collection.add(testtreant, testtreant2)
                collection.categories.add({'age': 42, 'bark': 'smooth'})

                t1 = dtr.Treant('maple')
                t2 = dtr.Treant('sequoia')
                t1.categories.add({'age': 'seedling', 'bark': 'rough',
                                   'type': 'deciduous'})
                t2.categories.add({'age': 'adult', 'bark': 'rough',
                                   'type': 'evergreen', 'nickname': 'redwood'})
                collection.add(t1, t2)

                for k in collection.categories.keys(scope='all'):
                    for member in collection:
                        assert k in member.categories

                for k in collection.categories.keys(scope='any'):
                    for member in collection:
                        if k == 'nickname':
                            if member.name == 'maple':
                                assert k not in member.categories
                            elif member.name == 'sequoia':
                                assert k in member.categories
                        elif k == 'type':
                            if (member.name != 'maple' and
                                    member.name != 'sequoia'):
                                assert k not in member.categories

                        else:
                            assert k in member.categories

        def test_categories_values(self, collection, testtreant, testtreant2,
                                   tmpdir):
            with tmpdir.as_cwd():
                # add a couple test Treants to collection
                collection.add(testtreant, testtreant2)
                collection.categories.add({'age': 'young', 'bark': 'smooth'})

                t1 = dtr.Treant('maple')
                t2 = dtr.Treant('sequoia')
                t1.categories.add({'age': 'seedling', 'bark': 'rough',
                                   'type': 'deciduous'})
                t2.categories.add({'age': 'adult', 'bark': 'rough',
                                   'type': 'evergreen', 'nickname': 'redwood'})
                collection.add(t1, t2)

                for scope in ('all', 'any'):
                    for i, v in enumerate(
                            collection.categories.values(scope=scope)):
                        assert v == collection.categories[
                                collection.categories.keys(scope=scope)[i]]

        def test_categories_groupby(self, collection, testtreant, testtreant2,
                                    tmpdir):
            with tmpdir.as_cwd():
                t1 = dtr.Treant('maple')
                t2 = dtr.Treant('sequoia')
                t3 = dtr.Treant('elm')
                t4 = dtr.Treant('oak')
                t1.categories.add({'age': 'young', 'bark': 'smooth',
                                   'type': 'deciduous'})
                t2.categories.add({'age': 'adult', 'bark': 'fibrous',
                                   'type': 'evergreen', 'nickname': 'redwood'})
                t3.categories.add({'age': 'old', 'bark': 'mossy',
                                   'type': 'deciduous', 'health': 'poor'})
                t4.categories.add({'age': 'young', 'bark': 'mossy',
                                   'type': 'deciduous', 'health': 'good'})
                collection.add(t1, t2, t3, t4)

                age_group = collection.categories.groupby('age')
                assert {t1, t4} == set(age_group['young'])
                assert {t2} == set(age_group['adult'])
                assert {t3} == set(age_group['old'])

                bark_group = collection.categories.groupby('bark')
                assert {t1} == set(bark_group['smooth'])
                assert {t2} == set(bark_group['fibrous'])
                assert {t3, t4} == set(bark_group['mossy'])

                type_group = collection.categories.groupby('type')
                assert {t1, t3, t4} == set(type_group['deciduous'])
                assert {t2} == set(type_group['evergreen'])

                nick_group = collection.categories.groupby('nickname')
                assert {t2} == set(nick_group['redwood'])
                for bundle in nick_group.values():
                    assert {t1, t3, t4}.isdisjoint(set(bundle))

                health_group = collection.categories.groupby('health')
                assert {t3} == set(health_group['poor'])
                assert {t4} == set(health_group['good'])
                for bundle in health_group.values():
                    assert {t1, t2}.isdisjoint(set(bundle))

                # test list of keys as input
                age_bark = collection.categories.groupby(['age', 'bark'])
                assert len(age_bark) == 4
                assert {t1} == set(age_bark[('young', 'smooth')])
                assert {t2} == set(age_bark[('adult', 'fibrous')])
                assert {t3} == set(age_bark[('old', 'mossy')])
                assert {t4} == set(age_bark[('young', 'mossy')])

                type_health = collection.categories.groupby(['type', 'health'])
                assert len(type_health) == 2
                assert {t3} == set(type_health[('deciduous', 'poor')])
                assert {t4} == set(type_health[('deciduous', 'good')])
                for bundle in type_health.values():
                    assert {t1, t2}.isdisjoint(set(bundle))

                type_health = collection.categories.groupby(['health', 'type'])
                assert len(type_health) == 2
                assert {t3} == set(type_health[('poor', 'deciduous')])
                assert {t4} == set(type_health[('good', 'deciduous')])
                for bundle in type_health.values():
                    assert {t1, t2}.isdisjoint(set(bundle))

                age_nick = collection.categories.groupby(['age', 'nickname'])
                assert len(age_nick) == 1
                assert {t2} == set(age_nick['adult', 'redwood'])
                for bundle in age_nick.values():
                    assert {t1, t3, t4}.isdisjoint(set(bundle))

                keys = ['age', 'bark', 'health']
                age_bark_health = collection.categories.groupby(keys)
                assert len(age_bark_health) == 2
                assert {t3} == set(age_bark_health[('old', 'mossy', 'poor')])
                assert {t4} == set(age_bark_health[('young', 'mossy', 'good')])
                for bundle in age_bark_health.values():
                    assert {t1, t2}.isdisjoint(set(bundle))

                keys = ['age', 'bark', 'type', 'nickname']
                abtn = collection.categories.groupby(keys)
                assert len(abtn) == 1
                assert {t2} == set(abtn[('adult', 'fibrous', 'evergreen',
                                         'redwood')])
                for bundle in abtn.values():
                    assert {t1, t3, t4}.isdisjoint(set(bundle))

                keys = ['bark', 'nickname', 'type', 'age']
                abtn2 = collection.categories.groupby(keys)
                assert len(abtn2) == 1
                assert {t2} == set(abtn2[('fibrous', 'redwood', 'evergreen',
                                          'adult')])
                for bundle in abtn2.values():
                    assert {t1, t3, t4}.isdisjoint(set(bundle))

                keys = ['health', 'nickname']
                health_nick = collection.categories.groupby(keys)
                assert len(health_nick) == 0
                for bundle in health_nick.values():
                    assert {t1, t2, t3, t4}.isdisjoint(set(bundle))

                # Test key TypeError in groupby
                with pytest.raises(TypeError) as e:
                    collection.categories.groupby({'health', 'nickname'})
