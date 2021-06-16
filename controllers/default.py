# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------


def index():
    if db(db.auth_user).count() == 0:
        db.auth_group.insert(role="admin")
        user_admin_id = db.auth_user.insert(
            first_name="admin",
            email="admin@admin.com",
            password=db.auth_user.password.requires[0]("admin")[0],
        )
        auth.add_membership("admin", db.auth_user(user_admin_id))
    if db(db.jerarquia).count() == 0:
        db.jerarquia.insert(nombre="Agte.")
        db.jerarquia.insert(nombre="Cabo")
        db.jerarquia.insert(nombre="Cabo 1er")
        db.jerarquia.insert(nombre="Sgto")
        db.jerarquia.insert(nombre="Sgto Ayte.")
        db.jerarquia.insert(nombre="Sgto 1er")
        db.jerarquia.insert(nombre="Subof.")
        db.jerarquia.insert(nombre="Subof. Ppal")
        db.jerarquia.insert(nombre="Of. Subayte.")
        db.jerarquia.insert(nombre="Of. Ayte.")
        db.jerarquia.insert(nombre="Of. Ppal")
        db.jerarquia.insert(nombre="Subcrio")
        db.jerarquia.insert(nombre="Crio")
        db.jerarquia.insert(nombre="Crio Ppal")
        db.jerarquia.insert(nombre="Crio Insp.")
        db.jerarquia.insert(nombre="Crio My.")
        db.jerarquia.insert(nombre="Crio Gral.")
        db.commit()
    return redirect(URL("default", "provision"))


@auth.requires_login()
def provision():
    db.Provision.id.readable = db.Provision.id.writable = False

    fields = [
        db.Provision.numero_documento,
        db.Provision.apellido,
        db.Provision.nombre,
        db.Provision.numero_cargo,
        db.Provision.jerarquia,
        db.Provision.marca,
        db.Provision.destino_actual,
    ]

    grid = SQLFORM.smartgrid(
        db.Provision,
        fields=fields,
        create=True,
        deletable=True,
        editable=True,
        breadcrumbs_class="breadcrumb",
        csv=False,
        advanced_search=False,
    )
    return dict(grid=grid)


@auth.requires(auth.has_membership("admin"))
def users():
    grid_user = SQLFORM.smartgrid(
        db.auth_user, breadcrumbs_class="breadcrumb", formname="a"
    )
    return locals()


@auth.requires(auth.has_membership("admin"))
def provisiones():
    grid_provision = SQLFORM.smartgrid(
        db.Provision, breadcrumbs_class="breadcrumb", formname="c"
    )
    return locals()


@auth.requires(auth.has_membership("admin"))
def registros():
    grid_registro = SQLFORM.smartgrid(
        db.Registro, breadcrumbs_class="breadcrumb", formname="b"
    )
    return locals()


# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == "GET":
        raise HTTP(403)
    return response.json({"status": "success", "email": auth.user.email})


# ---- Smart Grid (example) -----
@auth.requires_membership("admin")  # can only be accessed by members of admin groupd
def grid():
    response.view = "generic.html"  # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables:
        raise HTTP(403)
    grid = SQLFORM.smartgrid(
        db[tablename], args=[tablename], deletable=False, editable=False
    )
    return dict(grid=grid)


# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu()  # add the wiki to the menu
    return auth.wiki()


# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
