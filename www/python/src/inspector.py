"""Inspector to view data set entries and model decisions.

"""
from flask import Blueprint, jsonify, request

inspector = Blueprint('inspector', __name__)

SUPPORTED_WIKIS = ["de"]

USER_AGENT = "kokolores Inspector <kokolores.api@wmflabs.org"
sessions = {}


