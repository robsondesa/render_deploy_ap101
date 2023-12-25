import dash
import dash_bootstrap_components as dbc
import dash_auth

estilos = ["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css", "https://fonts.googleapis.com/icon?family=Material+Icons", dbc.themes.COSMO]
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"
# FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"

VALID_USERNAME_PASSWORD_PAIRS = {
    'melodesa101': 'Mari@2021'
}

app = dash.Dash(__name__, external_stylesheets=estilos + [dbc_css])
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

app.config['suppress_callback_exceptions'] = True
app.scripts.config.serve_locally = True
server = app.server
