# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# AppConfig configuration made easy. Look inside private/appconfig.ini
# Auth is for authenticaiton and access control
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig
from gluon.tools import Auth

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.15.5":
    raise HTTP(500, "Requires web2py 2.15.5 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
configuration = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL(
        configuration.get("db.uri"),
        pool_size=configuration.get("db.pool_size"),
        migrate_enabled=configuration.get("db.migrate"),
        check_reserved=["all"],
    )
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL("google:datastore+ndb")
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = []
if request.is_local and not configuration.get("app.production"):
    response.generic_patterns.append("*")

# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
from custom_form import custom_formstyle

response.formstyle = custom_formstyle
response.form_label_separator = ""

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=configuration.get("host.names"))

# -------------------------------------------------------------------------
# create all tables needed by auth, maybe add a list of extra fields
# -------------------------------------------------------------------------
auth.settings.extra_fields["auth_user"] = [
    Field("cargo", "integer"),
    Field("chapa", "integer"),
    Field("dependencia", "string"),
]
auth.settings.actions_disabled = ["retrieve_password"]
auth.define_tables(username=False, signature=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = (
    "logging" if request.is_local else configuration.get("smtp.server")
)
mail.settings.sender = configuration.get("smtp.sender")
mail.settings.login = configuration.get("smtp.login")
mail.settings.tls = configuration.get("smtp.tls") or False
mail.settings.ssl = configuration.get("smtp.ssl") or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------
# read more at http://dev.w3.org/html5/markup/meta.name.html
# -------------------------------------------------------------------------
response.meta.author = configuration.get("app.author")
response.meta.description = configuration.get("app.description")
response.meta.keywords = configuration.get("app.keywords")
response.meta.generator = configuration.get("app.generator")
response.show_toolbar = configuration.get("app.toolbar")

# -------------------------------------------------------------------------
# your http://google.com/analytics id
# -------------------------------------------------------------------------
response.google_analytics_id = configuration.get("google.analytics_id")

# -------------------------------------------------------------------------
# maybe use the scheduler
# -------------------------------------------------------------------------
if configuration.get("scheduler.enabled"):
    from gluon.scheduler import Scheduler

    scheduler = Scheduler(db, heartbeat=configuration.get("scheduler.heartbeat"))

# -------------------------------------------------------------------------
# Include the necessary files by adding this to your model/db.py:
response.files.append("https://unpkg.com/leaflet@1.5.1/dist/leaflet.css")
response.files.append("https://unpkg.com/leaflet@1.5.1/dist/leaflet.js")
response.files.append(
    "https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.css"
)
response.files.append(
    "https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js"
)

# New widget geocoder
def geocoder_widget(field, value):
    wrapper = DIV()
    input_latlng = SQLFORM.widgets.string.widget(field, value, _type="hidden")
    javascript = SCRIPT(
        """
        var map = L.map('map').setView([51.505, -0.09], 13);
        L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        var marker
        
        function onMapClick(e) {
            if (marker) map.removeLayer(marker);
            marker = new L.Marker(e.latlng, { draggable: true });
            map.addLayer(marker);
            $("#%s").val(e.latlng.lat + ", " + e.latlng.lng);
            // marker.bindPopup("<b>Hello world!</b><br />I am a popup.").openPopup();
        }
        map.on('click', onMapClick);
        
        L.Control.geocoder({
            defaultMarkGeocode: false
            })
            .on('markgeocode', function (e) {
                if (marker) map.removeLayer(marker);
                marker = new L.Marker(e.geocode.center, { draggable: true });
                map.addLayer(marker);
                map.setView(e.geocode.center, 12);
                $("#%s").val(e.geocode.center.lat + ", " + e.geocode.center.lng);
            })
            .addTo(map);
    """
        % (input_latlng["_id"], input_latlng["_id"]),
        _type="text/javascript",
    )
    wrapper.components.extend(
        [input_latlng, DIV(_id="map", _style="width: 800px; height: 500px"), javascript]
    )
    return wrapper


# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)
from widget import date_widget

db.define_table(
    "jerarquia",
    Field("nombre"),
)

db.define_table(
    "Provision",
    Field("apellido"),
    Field("nombre"),
    Field("jerarquia", db.jerarquia, represent=lambda id, r: db.jerarquia[id].nombre),
    Field(
        "numero_cargo",
        "integer",
        label="Cargo",
        requires=IS_NOT_EMPTY(),
    ),
    Field(
        "numero_chapa",
        "integer",
    ),
    Field("arma_provista"),
    Field("marca"),
    Field(
        "calibre",
    ),
    Field("numero_arma"),
    Field("serie"),
    Field("fecha_provision", "string", widget=date_widget, default=request.now),
    Field("recibo_numero", "integer"),
    Field("cargadores", "integer"),
    Field("fecha_provision_cartuchos", "string", widget=date_widget),
    Field("cantidad_cartuchos", "integer"),
    Field("observaciones", "text"),
    Field("destino_actual"),
    Field(
        "uurr",
        label="UURR",
        requires=IS_IN_SET(["Capital", "Norte", "Sur", "Este", "Oeste"]),
    ),
    Field("fecha_alta", "string", widget=date_widget),
    Field("numero_seguro_social", "integer"),
    Field("fecha_nacimiento", "string", widget=date_widget, label="Nacimiento"),
    Field(
        "numero_documento",
        "integer",
        requires=IS_LENGTH(minsize=6, maxsize=8),
        label="Documento",
        required=True,
    ),
    Field("cuil", "integer"),
    Field("domicilio", "string", widget=geocoder_widget),
    plural="Provisiones",
)

db.define_table(
    "Registro",  # Registro de Transacciones
    Field("user_id", db.auth_user),
    Field("transaccion", "string"),
)

db.Provision._after_update.append(
    lambda s, f: db.Registro.insert(
        user_id=auth.user_id, transaccion="Update: {}".format(str(f))
    )
)
db.Provision._after_delete.append(
    lambda s: db.Registro.insert(
        user_id=auth.user_id, transaccion="Delete: {}".format(str(s))
    )
)
db.Provision._after_insert.append(
    lambda f, id: db.Registro.insert(
        user_id=auth.user_id, transaccion="Insert: {}".format(str(f))
    )
)
