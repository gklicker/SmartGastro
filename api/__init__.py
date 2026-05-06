from api import auth, users, ingredients, menu, events, tickets, foodtrucks, inventory


def register_blueprints(app):
    for bp_module in (auth, users, ingredients, menu, events, tickets, foodtrucks, inventory):
        app.register_blueprint(bp_module.bp)
