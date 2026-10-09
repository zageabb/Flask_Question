"""UDA and LAN routing checks for Flask Question."""
from app import app

def test_uda_and_lan():
    client = app.test_client()
    for path in ("/", "/templates"):
        local = client.get(path)
        assert local.status_code == 200
        assert '<base href="/">' in local.get_data(as_text=True)
        headers = {"X-Forwarded-Prefix":"/apps/flask-question",
                   "X-Forwarded-Host":"tanyaanne.ddns.net",
                   "X-Forwarded-Proto":"https"}
        proxied = client.get(path,headers=headers)
        assert proxied.status_code == 200
        text = proxied.get_data(as_text=True)
        assert '<base href="/apps/flask-question/">' in text
        assert '/apps/flask-question/static/css/style.css' in text
