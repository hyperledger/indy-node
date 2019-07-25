import json

import pytest

from indy_node.server.request_handlers.domain_req_handlers.context_handler import ContextHandler


def test_validate_context_fail_on_empty():
	with pytest.raises(Exception):
		ContextHandler._validate_context({})

def test_validate_context_fail_no_context_property():
	input_dict = {
		"name": "Thing"
	}
	with pytest.raises(Exception):
		ContextHandler._validate_context(input_dict)

def test_validate_context_fail_context_not_dict():
	input_dict = {
		"@context": "Thing"
	}
	with pytest.raises(Exception):
		ContextHandler._validate_context(input_dict)

def test_validate_context_pass_context_single_name_value():
	input_dict = {
 		"@context": {
    		"favoriteColor": "https://example.com/vocab#favoriteColor"
		}
	}
	
	ContextHandler._validate_context(input_dict)