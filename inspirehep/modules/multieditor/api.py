# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Module for backend of multi record editor used in http://inspirehep.net."""

from __future__ import absolute_import, print_function, division

from flask import Blueprint, request, jsonify, session
import copy
from inspire_schemas.api import load_schema
from inspirehep.modules.multieditor import tasks
from inspirehep.modules.migrator.tasks import chunker
from . import actions
from . import queries
from .permissions import multieditor_use_permission


blueprint = Blueprint(
    'inspirehep_multieditor',
    __name__,
    template_folder='templates',
    url_prefix='/multieditor',
)


@blueprint.route("/update", methods=['POST'])
@multieditor_use_permission.require(http_exception=403)
def update():
    """Apply the user actions to the database records."""
    user_actions = request.json['userActions']
    all_selected = request.json['allSelected']
    searched_records = session.get('multieditor_searched_records', [])
    if searched_records:
        ids = searched_records['ids']
        index = searched_records['schema']
        schema = load_schema(index, resolved=True)
        if all_selected:
            ids = filter(lambda x: x not in request.json['ids'], ids)
        else:
            ids = filter(lambda x: x in request.json['ids'], ids)
    else:
        return jsonify({'message': 'Please use the search before you apply actions'}), 400
    for i, chunk in enumerate(chunker(ids, 20)):
        tasks.process_records.delay(records_ids=chunk, user_actions=user_actions, schema=schema)
    return jsonify({'message': 'Records are being updated'})


@blueprint.route("/preview", methods=['POST'])
@multieditor_use_permission.require(http_exception=403)
def preview():
    """Preview the user actions in the first (page size) records."""
    user_actions = request.json['userActions']
    query_string = request.json['queryString']
    page_size = int(request.json['pageSize'])
    page_num = request.json['pageNum']
    searched_records = session.get('multieditor_searched_records', [])
    if searched_records:
        index = searched_records['schema']
    else:
        return jsonify({'message': 'Please use the search before you apply actions'}), 400
    schema = load_schema(index, resolved=True)
    records = queries.get_records_from_query(query_string, page_size, page_num, index)['json_records']
    old_records = copy.deepcopy(records)
    actions.process_records_no_db(user_actions, records, schema)
    records_diff, errors = actions.diff_and_validate_records(old_records, records, schema)
    return jsonify({'json_records': old_records, 'errors': errors, 'records_diff': records_diff})


@blueprint.route("/search", methods=['GET'])
@multieditor_use_permission.require(http_exception=403)
def search():
    """Search for records using the query and store the result's ids"""
    query_string = request.args.get('queryString', '')
    page_num = int(request.args.get('pageNum', 1))
    page_size = int(request.args.get('pageSize', 1))
    index = request.args.get('index', '')
    paginated_records = queries.get_records_from_query(query_string, page_size, page_num, index)
    if paginated_records['total_records'] > 10000:
        return jsonify({'message': 'Please narrow the results using a query'}), 400
    session['multieditor_searched_records'] = {
        'ids': queries.get_record_ids_from_query(query_string, index),
        'schema': index
    }
    return jsonify(paginated_records)
