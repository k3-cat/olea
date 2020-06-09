from flask import current_app

from . import bp


@bp.route('/site-map', methods=['GET'])
def site_map():
    return current_app.url_map
