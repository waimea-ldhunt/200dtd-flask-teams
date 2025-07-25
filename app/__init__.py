#===========================================================
# App Creation and Launch
#===========================================================

from flask import Flask, render_template, request, flash, redirect
import html

from app.helpers.session import init_session
from app.helpers.db      import connect_db
from app.helpers.errors  import init_error, not_found_error
from app.helpers.logging import init_logging
from app.helpers.time    import init_datetime, utc_timestamp, utc_timestamp_now


# Create the app
app = Flask(__name__)

# Configure app
init_session(app)   # Setup a session for messages, etc.
init_logging(app)   # Log requests
init_error(app)     # Handle errors and exceptions
init_datetime(app)  # Handle UTC dates in timestamps


#-----------------------------------------------------------
# Home page route
#-----------------------------------------------------------
@app.get("/")
def index():
    with connect_db() as client:
        sql = "SELECT code, name FROM teams ORDER BY name ASC"
        result = client.execute(sql)
        teams = result.rows

        sql = "SELECT id, name, team FROM members ORDER BY id ASC"
        result = client.execute(sql)
        members = result.rows

    return render_template("pages/home.jinja",teams=teams, members=members)


#-----------------------------------------------------------
# About page route
#-----------------------------------------------------------
@app.get("/about/")
def about():
    return render_template("pages/about.jinja")


#-----------------------------------------------------------
# Things page route - Show all the things, and new thing form
#-----------------------------------------------------------
@app.get("/things/")
def show_all_things():
    with connect_db() as client:
        # Get all the things from the DB
        sql = "SELECT id, name FROM things ORDER BY name ASC"
        params = []
        result = client.execute(sql, params)
        things = result.rows

        # And show them on the page
        return render_template("pages/things.jinja", things=things)


#-----------------------------------------------------------
# Thing page route - Show details of a single thing
#-----------------------------------------------------------
@app.get("/team/<string:code>")
def show_one_team(code):
    with connect_db() as client:
        # Get the thing details from the DB
        sql = "SELECT * FROM teams WHERE code=?"
        params = [code]
        result = client.execute(sql, params)

        # Did we get a result?
        if result.rows:
            # yes, so show it on the page
            team = result.rows[0]

            sql = "SELECT id, name FROM members WHERE team=?"
            params = [code]
            result = client.execute(sql, params)
            members = result.rows

            return render_template("pages/team.jinja", team=team, members=members)

        else:
            # No, so show error
            return not_found_error()
        
@app.get("/member/<int:id>")
def show_one_player(id):

    with connect_db() as client:

        sql = """SELECT * FROM members WHERE id=?"""
        params = [id]
        result = client.execute(sql, params)

        member = result.rows[0]

        return render_template("pages/member.jinja", member=member)



#-----------------------------------------------------------
# Route for adding a thing, using data posted from a form
#-----------------------------------------------------------

@app.post("/add/member/<string:code>")
def add_a_player_to_specific_team(code):
    # Get the data from the form
    name  = request.form.get("name")

    # Sanitise the text inputs
    name = html.escape(name)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO members (name, team) VALUES (?, ?)"
        params = [name, code]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Member '{name}' added", "success")
        return redirect(f"/team/{code}")
    
@app.post("/add/team")
def add_a_team():
    # Get the data from the form
    name  = request.form.get("name")
    code  = request.form.get("code")
    desc  = request.form.get("description")
    site  = request.form.get("website")

    # Sanitise the text inputs
    name = html.escape(name)
    code = html.escape(code)
    desc = html.escape(desc)
    site = html.escape(site)

    with connect_db() as client:
        # Add the thing to the DB
        sql = "INSERT INTO teams (code, name, description, website) VALUES (?, ?, ?, ?)"
        params = [code, name, desc, site]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Team '{name}' added", "success")
        return redirect(f"/team/{code}")


#-----------------------------------------------------------
# Route for deleting a thing, Id given in the route
#-----------------------------------------------------------
@app.get("/delete/member/<int:id>")
def delete_a_member(id):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM members WHERE id=?"
        params = [id]
        client.execute(sql, params)

        # Go back to the home page
        flash("Member deleted", "success")
        return redirect("/")
    
@app.get("/delete/team/<string:code>")
def delete_a_team(code):
    with connect_db() as client:
        # Delete the thing from the DB
        sql = "DELETE FROM teams WHERE code=?"
        params = [code]
        client.execute(sql, params)

        # Go back to the home page
        flash(f"Team deleted", "success")
        return redirect("/")
    
@app.post("/note/<int:id>")
def update_notes(id):
    with connect_db() as client:
        notes = request.form.get("notes")

        sql = "UPDATE members SET notes=? WHERE id=?"
        params = [notes, id]
        client.execute(sql, params)

        flash("Notes Updated", "success")
        return redirect(f"/member/{id}")