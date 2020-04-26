"""
    Routes
    ~~~~~~
"""
from flask import Blueprint
from flask import flash
import json
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from wiki.core import Processor
from wiki.web.forms import EditorForm, DeletionForm
from wiki.web.forms import LoginForm
from wiki.web.forms import SearchForm
from wiki.web.forms import URLForm
from wiki.web import current_wiki
from wiki.web import current_users
from wiki.web.user import protect
from wiki.web.forms import RegisterForm

bp = Blueprint('wiki', __name__)


@bp.route('/')
@protect
def home():
    page = current_wiki.get('home')
    if page:
        return display('home')
    return render_template('home.html')


@bp.route('/index/')
@protect
def index():
    pages = current_wiki.index()
    return render_template('index.html', pages=pages)


@bp.route('/<path:url>/')
@protect
def display(url):
    page = current_wiki.get_or_404(url)
    return render_template('page.html', page=page)


@bp.route('/create/', methods=['GET', 'POST'])
@protect
def create():
    form = URLForm()
    if form.validate_on_submit():
        return redirect(url_for(
            'wiki.edit', url=form.clean_url(form.url.data)))
    return render_template('create.html', form=form)


@bp.route('/edit/<path:url>/', methods=['GET', 'POST'])
@protect
def edit(url):
    page = current_wiki.get(url)
    form = EditorForm(obj=page)
    if form.validate_on_submit():
        if not page:
            page = current_wiki.get_bare(url)
        form.populate_obj(page)
        page.save()
        flash('"%s" was saved.' % page.title, 'success')
        return redirect(url_for('wiki.display', url=url))
    return render_template('editor.html', form=form, page=page)


@bp.route('/preview/', methods=['POST'])
@protect
def preview():
    data = {}
    processor = Processor(request.form['body'])
    data['html'], data['body'], data['meta'] = processor.process()
    return data['html']


"""page_preview is called on hover of any anchor tag elements. It performs validation to make sure it is only an anchor 
tag on the body of the page and not a tab at the top of the screen for example
Returns back an html version of the page to be rendered in the pagePreview div

"""


@bp.route('/pagePreview')
def page_preview():
    url = request.args.get('currentTag', 0)
    url = url.strip("/")

    is_delete = request.args.get('isDeleteBtn', 0)
    is_riki_tab = request.args.get('isRikiLink', 0)

    if is_normal_href_link(url) and is_delete == '' and is_riki_tab != ('Riki' and 'Cancel' and 'Wikielodeon'):
        page = current_wiki.get_or_404(url)

        data = {}
        processor = Processor(page.content)
        data['html'], data['body'], data['meta'] = processor.process()
        return jsonify(result=data['html'])

    return "None"


""" performs some validation used in page_preview
    Checks to see that it is not the home page or one of the buttons on the right side of the UI
    edit, tags, move
"""


def is_normal_href_link(url):
    if ('edit/' not in url) and ('move/' not in url) and (url != '/') and (
            'tag/' not in url):
        return True
    else:
        return False


@bp.route('/move/<path:url>/', methods=['GET', 'POST'])
@protect
def move(url):
    page = current_wiki.get_or_404(url)
    form = URLForm(obj=page)
    if form.validate_on_submit():
        newurl = form.url.data
        current_wiki.move(url, newurl)
        return redirect(url_for('wiki.display', url=newurl))
    return render_template('move.html', form=form, page=page)


@bp.route('/delete/<path:url>/')
@protect
def delete(url):
    page = current_wiki.get_or_404(url)
    current_wiki.delete(url)
    flash('Page "%s" was deleted.' % page.title, 'success')
    return redirect(url_for('wiki.home'))


@bp.route('/tags/')
@protect
def tags():
    tags = current_wiki.get_tags()
    return render_template('tags.html', tags=tags)


@bp.route('/tag/<string:name>/')
@protect
def tag(name):
    tagged = current_wiki.index_by_tag(name)
    return render_template('tag.html', pages=tagged, tag=name)


@bp.route('/search/', methods=['GET', 'POST'])
@protect
def search():
    form = SearchForm()
    if form.validate_on_submit():
        results = current_wiki.search(form.term.data, form.ignore_case.data)
        return render_template('search.html', form=form,
                               results=results, search=form.term.data)
    return render_template('search.html', form=form, search=None)


@bp.route('/user/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = current_users.get_user(form.name.data)
        login_user(user)
        user.set('authenticated', True)
        flash('Login successful.', 'success')
        return redirect(request.args.get("next") or url_for('wiki.index'))
    return render_template('login.html', form=form)


@bp.route('/user/logout/')
@login_required
def user_logout():
    current_user.set('authenticated', False)
    logout_user()
    flash('Logout successful.', 'success')
    return redirect(url_for('wiki.index'))


@bp.route('/user/list')
@protect
def user_list():
    """
    This will get all the user that are regestered
    in the system, it will format the output into
    a table.

    This will list the names, passwords, authentication method, and
    any roles that these users have.
    """
    with open('user/users.json') as f:
        user_info = json.loads(f.read())
    user_names = [k for k in user_info]
    users_data = [v for v in user_info.values()]
    count = len(user_names)
    return render_template('user_list.html', names=user_names, data=users_data, count=count)


@bp.route('/user/create/', methods=['POST', 'GET'])
def user_create():
    form = RegisterForm()
    if form.name.data is not None and form.password.data is not None:
        user_found = False
        if current_users.get_user(request.form.get('name')) is not None:
            user_found = True
            flash('Username was taken, please try again.', 'error')
        if user_found is False:
            current_users.add_user(name=form.name.data, password=form.password.data)
            flash('User creation successful.', 'success')
            return redirect(url_for('wiki.user_login'))
    return render_template('signup.html', form=form)


@bp.route('/admin/')
@protect
def admin():
    """
    This is the admin route, this will only
    allow certain user in and redirect those without
    the permissions to the index with a message.

    The admin page will have the option of deleting a user
    , or listing the users with relevant info
    """
    roles = current_user.get('roles')

    if 'ADMIN' in roles:
        return render_template('admin.html')
    else:
        flash('Insufficient Permissions to access this page', 'danger')
        return redirect(url_for('wiki.home'))


@bp.route('/user/delete/', methods=['GET', 'POST'])
@protect
def user_delete():
    """
    This rout will create a Deletion form
    which will ask for the username of the
    user they want to delete, it will give them an error
    when the user does not exists
    """
    form = DeletionForm()
    if form.validate_on_submit():
        current_users.delete_user(form.name.data)
        flash(form.name.data + " successfully deleted", "success")
        return redirect(url_for('wiki.admin'))
    return render_template('user_delete.html', form=form)


"""
    Error Handlers
    ~~~~~~~~~~~~~~
"""


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
