# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, print_function, division

import json
import os
import pytest

from inspirehep.modules.multieditor.actions import Addition, Deletion, Update, create_object_from_path


@pytest.fixture
def get_schema():
    curr_path = os.path.dirname(__file__)
    with open(os.path.join(curr_path, 'fixtures/schema.json')) \
            as data_file:
        schema = json.load(data_file)
    return schema


def test_addition_root_key(get_schema):
    """Should test adding a root primitive key"""
    record = {
    }
    expected_map = {
        'preprint_date': '2016'
    }
    add = Addition(keypath=['preprint_date'], value='2016')
    add.apply(record, get_schema)
    assert record == expected_map


def test_addition_root_object(get_schema):
    """Should test adding a root primitive key"""
    record = {
    }
    expected_map = {
        'abstracts': [
            {
                'source': 'AIP',
                'value': 'Variational principles presented as a logical extension.'
             }
        ]
    }
    object_to_add = {
                'source': 'AIP',
                'value': 'Variational principles presented as a logical extension.'
             }
    add = Addition(keypath=['abstracts'], value=object_to_add)
    add.apply(record, get_schema)
    assert record == expected_map


def test_addition_missing_root_key(get_schema):
    """Should test adding an object with a non allready existing key"""
    record = {
    }
    expected_map = {
        '_collections': ['Literature']
    }
    add = Addition(keypath=['_collections'], value='Literature',
                   conditions=[{'keypath': ['_collections'], 'match_type':'missing', 'value': ''}])
    add.apply(record, get_schema)
    assert record == expected_map


def test_addition_missing_deeper_key(get_schema):
    """Should test adding an object with condition on a non existing deep key"""
    record = {
    }
    expected_map = {
        'public_notes': [
            {
                'value': 'Preliminary results'
            }
        ]
    }
    add = Addition(keypath=['public_notes'], value={'value': 'Preliminary results'},
                   conditions=[{'keypath': ['public_notes', 'value'], 'match_type':'missing', 'value': ''}])
    add.apply(record, get_schema)
    assert record == expected_map


def test_addition_root_key_with_deeper_condition(get_schema):
    """Should test adding a primitive key with multiple deeper conditions"""
    record = {
        'public_notes': [
            {
                'value': 'Preliminary results'
            },
            {
                'value': 'test'
            }
        ],
        'core': True,
    }
    expected_map = {
        'public_notes': [
            {
                'value': 'Preliminary results'
            },
            {
                'value': 'test'
            }
        ],
        'core': True,
        'preprint_date': '2016'
    }
    add = Addition(keypath=['preprint_date'],
                   conditions=[{'keypath': ['public_notes', 'value'], 'value': 'Preliminary results',
                                'match_type': 'exact'},
                               {'keypath': ['core'], 'value': 'True', 'match_type': 'exact'}],
                   value='2016')
    add.apply(record, get_schema)
    assert record == expected_map


def test_addition_root_key_with_deeper_condition_negative(get_schema):
    """Should test adding an object with negative condition"""
    record = {
        'public_notes': [
            {
                'value': 'Preliminary results'
            }
        ],
        'core': True,
        'titles': [
            {
                'title': 'test'
            }
        ],
    }
    expected_map = {
        'public_notes': [
            {
                'value': 'Preliminary results'
            }
        ],
        'core': True,
        'titles': [
            {
                'title': 'test'
            }
        ],
    }
    add = Addition(keypath=['preprint_date'],
                   conditions=[{'keypath': ['public_notes', 'value'], 'value': 'Preliminary results',
                                'match_type': 'exact'},
                               {'keypath': ['core'], 'value': 'False', 'match_type': 'exact'}],
                   match_type='exact',
                   value='2016')
    add.apply(record, get_schema)
    assert record == expected_map


def test_addition_object_with_conditions(get_schema):
    """Should test adding an object with condition"""
    record = {
        'public_notes': [
            {
                'value': 'Preliminary results'
            }
        ],
        'core': True,
        'titles': [
            {
                'title': 'test'
            }
        ],
    }
    expected_map = {
        'public_notes': [
            {
                'value': 'Preliminary results'
            }
        ],
        'core': True,
        'titles': [
            {
                'title': 'test',
            },
            {
                'title': 'success'
            }
        ],
    }
    add = Addition(keypath=['titles'],
                   conditions=[{'keypath': ['public_notes', 'value'], 'value': 'Preliminary results',
                                'match_type': 'exact'},
                               {'keypath': ['core'], 'value': 'True', 'match_type': 'exact'}],
                   value={'title': 'success'})
    add.apply(record, get_schema)
    assert record == expected_map


def test_addition_object(get_schema):
    """should test record addition for object"""
    record = {
        'key_a': {
            'key_c': 'test'
        }
    }
    expected_map = {
        'key_a': {
            'key_b': 'success',
            'key_c': 'test'
        }
    }
    custom_schema = {
        'properties': {
            'key_a': {
                'properties': {
                    'key_b': {
                        'type': 'string'
                    },
                    'key_c': {
                        'type': 'string'
                    }
                },
                'required': [
                    'value'
                ],
                'type': 'object'
            },
            'type': 'object',
        },
        'type': 'object',
    }
    add = Addition(keypath=['key_a', 'key_b'], value='success')
    add.apply(record, custom_schema)
    assert record == expected_map


def test_addition_array_with_condition(get_schema):
    """should test record addition for object using condition check"""
    record = {
        'key_a': {
            'key_b': ['Hello'],
            'key_c': 'test'
        }
    }

    expected_map = {
        'key_a': {
            'key_b': ['Hello', 'World'],
            'key_c': 'test'
        }
    }

    custom_schema = {
        'properties': {
            'key_a': {
                'properties': {
                    'key_b': {
                        'items': {
                            'type': 'string'
                        },
                        'type': 'array',
                    },
                    'key_c': {
                        'type': 'string'
                    }
                },
                'required': [
                    'value'
                ],
                'type': 'object'
            },
            'type': 'object',
        },
        'type': 'object',
    }
    add = Addition(keypath=['key_a', 'key_b'],
                   conditions=[{'keypath': ['key_a', 'key_c'],
                                'match_type': 'exact',
                                'value':'test'}],
                   value='World')
    add.apply(record, custom_schema)
    assert record == expected_map


def test_addition_array(get_schema):
    """should test record addition for nested array"""
    record = {
        'titles': [
            {
                'title': 'test'
            },
            {
                'title': 'test'
            }
        ],
        'document_type': ['book']
    }
    expected_map = {
        'titles': [
            {
                'title': 'test',
                'subtitle': 'success'
            },
            {
                'title': 'test',
                'subtitle': 'success'
            }
        ],
        'document_type': ['book']
    }
    add = Addition(keypath=['titles', 'subtitle'], value='success')
    add.apply(record, get_schema)
    assert record == expected_map


def test_addition_array_with_condition_condition(get_schema):
    record = {
        'titles': [
            {
                'title': 'test_1'
            },
            {
                'title': 'test'
            }
        ],
        'document_type': ['book']
    }
    expected_map = {
        'titles': [
            {
                'title': 'test_1',
                'subtitle': 'success'
            },
            {
                'title': 'test',
                'subtitle': 'success'
            }
        ],
        'document_type': ['book']
    }
    add = Addition(keypath=['titles', 'subtitle'],
                   conditions=[{'keypath': ['titles', 'title'],
                                'match_type': 'contains',
                                'value':'test'}],
                   value='success')
    add.apply(record, get_schema)
    assert record == expected_map


def test_addition_array_with_condition_missing_record():
    record = {}

    expected_map = {}

    custom_schema = {
        'properties': {
            'key_a': {
                'properties': {
                    'key_b': {
                        'items': {
                            'type': 'string'
                        },
                        'type': 'array',
                    },
                    'key_c': {
                        'type': 'string'
                    }
                },
                'required': [
                    'value'
                ],
                'type': 'object'
            },
            'type': 'object',
        },
        'type': 'object',
    }
    add = Addition(keypath=['key_a', 'key_b'],
                   conditions=[{'keypath': ['key_a', 'key_c'],
                                'match_type': 'exact',
                                'value':'test'}],
                   value='World')
    add.apply(record, custom_schema)
    assert record == expected_map


def test_addition_object_with_condition(get_schema):
    record = {
        'authors': [
            {
                'affiliations': [
                    {
                        'value': 'Rome'
                    }
                ],
                'signature_block': 'BANARo'
            },
            {
                'affiliations': [
                    {
                        'value': 'Rome U.'
                    }
                ],
                'signature_block': 'MANl',
            }
        ]
    }
    expected_map = {
        'authors': [
            {
                'affiliations': [
                    {
                        'value': 'Rome'
                    },
                    {
                        'curated_relation': True,
                        'value': 'Success'
                    }
                ],
                'signature_block': 'BANARo'
            },
            {
                'affiliations': [
                    {
                        'value': 'Rome U.'
                    }
                ],
                'signature_block': 'MANl',
            }
        ]
    }
    add = Addition(keypath=['authors', 'affiliations'],
                   conditions=[{'keypath': ['authors', 'signature_block'],
                                'match_type': 'exact',
                                'value':'BANARo'}],
                   value={'curated_relation': True,
                          'value': 'Success'})
    add.apply(record, get_schema)
    assert record == expected_map


def test_deletion_array_to_empty(get_schema):
    """should test record deletion for nested array"""
    record = {'texkeys': ['test', 'test', 'test2', 'test'],
              'cited': True}
    expected_map = {
        'cited': True
    }

    delete = Deletion(update_value='test',
                      keypath=['texkeys'],
                      match_type='contains')
    delete.apply(record, get_schema)
    assert record == expected_map


def test_deletion_array(get_schema):
    """should test record deletion for nested array"""
    record = {'texkeys': ['test', 'test', 'test2', 'test'],
              'cited': True}
    expected_map = {
        'texkeys': ['test2'],
        'cited': True
    }

    delete = Deletion(update_value='test',
                      keypath=['texkeys'],
                      match_type='exact')
    delete.apply(record, get_schema)
    assert record == expected_map


def test_deletion_array_contains(get_schema):
    """should test record deletion for nested array"""
    record = {'inspire_categories': [{'term': 'Val'},
                                     {'term': 'value'},
                                     {'term': 'value5'}],
              'cited': True}
    expected_map = {
        'cited': True
    }

    delete = Deletion(update_value='val',
                      keypath=['inspire_categories', 'term'],
                      match_type='contains')
    delete.apply(record, get_schema)
    assert record == expected_map


def test_deletion_array_regex(get_schema):
    """should test record deletion for nested array"""
    record = {'inspire_categories': [{'term': 'val'},
                                     {'term': 'value'},
                                     {'term': 'value5'}],
              'cited': True}
    expected_map = {
        'cited': True
    }

    delete = Deletion(update_value='va.*',
                      keypath=['inspire_categories', 'term'],
                      match_type='regex')
    delete.apply(record, get_schema)
    assert record == expected_map


def test_deletion_contains(get_schema):
    record = {'inspire_categories': [{'term': 'val'}]}
    expected_map = {}
    delete = Deletion(update_value='v',
                      keypath=['inspire_categories', 'term'],
                      match_type='contains')
    delete.apply(record, get_schema)
    assert record == expected_map


def test_deletion_regex(get_schema):
    record = {'inspire_categories': [{'term': 'val'}]}
    expected_map = {}
    delete = Deletion(update_value='v.*',
                      keypath=['inspire_categories', 'term'],
                      match_type='regex')
    delete.apply(record, get_schema)
    assert record == expected_map


def test_record_creation_root_array(get_schema):
    """should test sub_record creation for missing object"""
    key = ['corporate_author']
    value = 'success'
    target_object = {'corporate_author': ['success']}
    assert create_object_from_path(get_schema, key, value) == target_object


def test_record_creation_root_object(get_schema):
    """should test sub_record creation for missing object"""
    key = ['self', '$ref']
    value = 'success'
    target_object = {'self': {'$ref': 'success'}}
    assert create_object_from_path(get_schema, key, value) == target_object


def test_record_creation():
    """should test sub_record creation for missing object"""
    schema_2 = {
        'properties': {
            'source': {
                'type': 'string'
            }},
        'type': 'object',
    }
    key = ['source']
    value = 'success'
    target_object = {'source': 'success'}
    assert create_object_from_path(schema_2, key, value) == target_object


def test_record_creation_complex_array(get_schema):
    """should test sub_record creation for missing object"""
    key = ['arxiv_eprints', 'categories']
    value = 'astro-ph'
    target_object = {'arxiv_eprints': [{'categories': ['astro-ph']}]}
    assert create_object_from_path(get_schema, key, value) == target_object


def test_record_creation_complex(get_schema):
    """should test sub_record creation for missing object"""
    key = ['authors', 'affiliations', 'value']
    value = 'success'
    target_object = {'authors': [{'affiliations': [{'value': 'success'}]}]}
    assert create_object_from_path(get_schema, key, value) == target_object


def test_record_creation_array(get_schema):
    """should test sub_record creation for missing object"""
    key = ['authors']
    value = {'full_name': 'success'}
    target_object = {'authors': [{'full_name': 'success'}]}
    assert create_object_from_path(get_schema, key, value) == target_object


def test_update_regex(get_schema):
    record = {'inspire_categories': [{'term': 'val'}]}
    expected_map = {'inspire_categories': [{'term': 'success'}]}
    update = Update(update_value='v.*',
                    value='success',
                    keypath=['inspire_categories', 'term'],
                    match_type='regex')
    update.apply(record, get_schema)
    assert record == expected_map


def test_update_contains(get_schema):
    record = {'inspire_categories': [{'term': 'val'}, {'term': 'Val'}]}
    expected_map = {'inspire_categories': [{'term': 'success'}, {'term': 'success'}]}
    update = Update(update_value='v',
                    value='success',
                    keypath=['inspire_categories', 'term'],
                    match_type='contains')
    update.apply(record, get_schema)
    assert record == expected_map


def test_update_boolean(get_schema):
    record = {'citeable': True}
    expected_map = {'citeable': False}
    update = Update(update_value='True',
                    value='False',
                    keypath=['citeable'],
                    match_type='exact')
    update.apply(record, get_schema)
    assert record == expected_map


def test_update_number(get_schema):
    record = {'number_of_pages': 1984}
    expected_map = {'number_of_pages': 1990}
    update = Update(update_value='1984',
                    value='1990',
                    keypath=['number_of_pages'],
                    match_type='exact')
    update.apply(record, get_schema)
    assert record == expected_map


def test_record_update_field_not_existing(get_schema):
    """should test sub_record creation for missing object"""
    record = {'abstracts': [{'not_source': 'success'}]}
    expected_map = {'abstracts': [{'not_source': 'success'}]}
    update = Update(keypath=['abstracts', 'source'],
                    update_value='success',
                    match_type='exact',
                    value='failure')
    update.apply(record, get_schema)
    assert record == expected_map


def test_update_array_exact(get_schema):
    """should test record edit for nested complex array."""
    record = {
        'references': [{'reference': {'collaborations': ['Val', 'val4']}},
                       {'reference': {'collaborations': ['val1', 'test val']}}],
    }
    expected_map = {
        'references': [{'reference': {'collaborations': ['Val', 'success']}},
                       {'reference': {'collaborations': ['val1', 'test val']}}],
    }
    update = Update(update_value='val4',
                    keypath=['references', 'reference', 'collaborations'],
                    match_type='exact',
                    value='success')
    update.apply(record, get_schema)
    assert record == expected_map


def test_update_array_contains(get_schema):
    """should test record edit for nested complex array."""
    record = {
        'references': [{'reference': {'collaborations': ['Val', 'val']}},
                       {'reference': {'collaborations': ['val1', 'test val']}}],
    }
    expected_map = {
        'references': [{'reference': {'collaborations': ['success', 'success']}},
                       {'reference': {'collaborations': ['success', 'success']}}],
    }
    update = Update(update_value='val',
                    keypath=['references', 'reference', 'collaborations'],
                    match_type='contains',
                    value='success')
    update.apply(record, get_schema)
    assert record == expected_map


def test_update_array_regex(get_schema):
    """should test record edit for nested complex array."""
    record = {
        'references': [{'reference': {'collaborations': ['val5', 'val']}},
                       {'reference': {'collaborations': ['val1', 'val6']}}],
    }
    expected_map = {
        'references': [{'reference': {'collaborations': ['success', 'success']}},
                       {'reference': {'collaborations': ['success', 'success']}}],
    }
    update = Update(update_value='val.*',
                    keypath=['references', 'reference', 'collaborations'],
                    match_type='regex',
                    value='success')
    update.apply(record, get_schema)
    assert record == expected_map


def test_update_condition_array_regex(get_schema):
    """should test action for nested complex array and multiple check values"""
    record = {
        'references': [{'reference': {'collaborations': ['val5', 'tes4'], 'title':{'title': 'test'}}},
                       {'reference': {'collaborations': ['val1', 'tes4'], 'title':{'title': 'not'}}}]
    }
    expected_map = {
        'references': [{'reference': {'collaborations': ['success', 'tes4'], 'title':{'title': 'test'}}},
                       {'reference': {'collaborations': ['val1', 'tes4'], 'title':{'title': 'not'}}}]
    }

    update = Update(update_value='val5',
                    keypath=['references', 'reference', 'collaborations'],
                    conditions=[{'keypath': ['references', 'reference', 'title', 'title'],
                                'match_type': 'regex',
                                 'value':'tes.*'}],
                    match_type='exact',
                    value='success')
    update.apply(record, get_schema)
    assert record == expected_map


def test_update_with_missing_keypath(get_schema):
    """should test sub_record update handling for missing object"""
    record = {
        'abstracts': [
            {
                'value': 'A dataset corresponding to $2.8~\\mathrm{fb}^{-1}$'
            }
        ],
    }
    expected_map = {
        'abstracts': [
            {
                'value': 'A dataset corresponding to $2.8~\\mathrm{fb}^{-1}$'
            },
        ],
    }

    update = Update(update_value='test',
                    keypath=['abstracts', 'source'],
                    value='success',
                    match_type='exact')
    update.apply(record, get_schema)
    assert record == expected_map


def test_update_check_regex_condition(get_schema):
    record = {
        'document_type': ['book chapter'],
        'texkeys': ['Braendas:1972ts'],
        'authors': [
            {
                'affiliations': [
                    {
                        'value': 'INFN, Rome'
                    },
                    {
                        'value': 'Rome'
                    },
                    {
                        'value': 'INFN'
                    }
                ],
                'signature_block': 'BANARo'
            },
            {'affiliations': [
                {
                    'value': 'Rome U.'
                },
                {
                    'value': 'Not INF'
                }
            ],
                'signature_block': 'MANl',
            }
        ],
        'number_of_pages': 184
    }
    expected_map = {
        'document_type': ['book chapter'],
        'texkeys': ['Braendas:1972ts'],
        'authors': [
            {
                'affiliations': [
                    {
                        'value': 'Success'
                    },
                    {
                        'value': 'Success'
                    },
                    {
                        'value': 'INFN'
                    }
                ],
                'signature_block': 'BANARo'
            },
            {
                'affiliations': [
                    {
                        'value': 'Rome U.'
                    },
                    {
                        'value': 'Not INF'
                    }
                ],
                'signature_block': 'MANl',
            }
        ],
        'number_of_pages': 184
    }
    update = Update(update_value='Rome.*',
                    keypath=['authors', 'affiliations', 'value'],
                    conditions=[{'keypath': ['authors', 'signature_block'],
                                'match_type':'exact',
                                 'value':'BANARo'},
                                {'keypath': ['document_type'],
                                 'match_type': 'contains',
                                 'value': 'book'},
                                {'keypath': ['texkeys'],
                                 'match_type': 'exact',
                                 'value': 'Braendas:1972ts'},
                                {'keypath': ['number_of_pages'],
                                 'match_type': 'exact',
                                 'value': '184'}
                                ],
                    match_type='regex',
                    value='Success')
    update.apply(record, get_schema)
    assert record == expected_map


def test_update_for_missing_key(get_schema):
    record = {
        'document_type': ['book chapter'],
        'authors': [
            {
                'affiliations': [
                    {
                        'value': 'INFN, Rome'
                    },
                    {
                        'value': 'Rome'
                    },
                    {
                        'value': 'INFN'
                    }
                ],
                'signature_block': 'BANARo'
            },
            {'affiliations': [
                {
                    'value': 'Rome U.'
                },
                {
                    'value': 'Not INF'
                }
            ]
            }
        ]
    }
    expected_map = {
        'document_type': ['book chapter'],
        'authors': [
            {
                'affiliations': [
                    {
                        'value': 'INFN, Rome'
                    },
                    {
                        'value': 'Rome'
                    },
                    {
                        'value': 'INFN'
                    }
                ],
                'signature_block': 'BANARo'
            },
            {
                'affiliations': [
                    {
                        'value': 'Success'
                    },
                    {
                        'value': 'Not INF'
                    }
                ]
            }
        ]
    }
    update = Update(update_value='Rome U.',
                    keypath=['authors', 'affiliations', 'value'],
                    conditions=[{'keypath': ['authors', 'signature_block'],
                                'match_type':'missing',
                                 'value': ''},
                                {'keypath': ['document_type'],
                                 'match_type': 'regex',
                                 'value': 'book.*'},
                                ],
                    match_type='exact',
                    value='Success')
    update.apply(record, get_schema)
    assert record == expected_map
