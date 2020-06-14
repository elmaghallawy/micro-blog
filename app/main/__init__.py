from flask import Blueprint

# blueprints are used to hook the routes and error handlres to an app 
# but they are used because the app now is initialized too late in runtime with this new 
# structure so we define the routes and error handlers with a blueprint then register this
# blueprint to the app


main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission

@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)