from flask import Blueprint, request, jsonify, abort, Response
from sqlalchemy import inspect, asc, desc
from datetime import datetime
import csv
import io
import json

from database import db_session
from database.models import Question, CompletedForm

api = Blueprint('api', __name__, url_prefix='/api')

API_KEY = None

def init_api(api_key: str | None = None):
    global API_KEY
    API_KEY = api_key

def _require_api_key():
    if API_KEY is None:
        return
    key = request.headers.get('X-API-KEY') or request.args.get('api_key')
    if key != API_KEY:
        abort(403, description='Invalid API key.')

def _model_to_dict(obj):
    mapper = inspect(obj).mapper
    data = {}
    for col in mapper.columns:
        val = getattr(obj, col.key)
        if col.key == 'form_json' and isinstance(val, str):
            try:
                data[col.key] = json.loads(val)
                continue
            except Exception:
                data[col.key] = val
                continue
        if hasattr(val, 'isoformat'):
            data[col.key] = val.isoformat()
        else:
            data[col.key] = val
    return data

@api.route('/health')
def health():
    return jsonify({'status': 'ok', 'time': datetime.utcnow().isoformat() + 'Z'})

@api.route('/questions', methods=['GET'])
def get_questions():
    _require_api_key()

    q = db_session.query(Question)

    search = request.args.get('search')
    if search:
        q = q.filter(
            (Question.title.ilike(f'%{search}%')) |
            (Question.text.ilike(f'%{search}%'))
        )

    updated_since = request.args.get('updated_since')
    if updated_since:
        ts = updated_since.replace('Z', '+00:00')
        try:
            dt = datetime.fromisoformat(ts)
            q = q.filter(Question.updated_at >= dt)
        except Exception:
            abort(400, description='updated_since must be ISO8601 timestamp.')

    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc').lower()
    col = getattr(Question, sort, None)
    if col is None:
        abort(400, description=f'Unsupported sort column: {sort}')
    q = q.order_by(desc(col) if order == 'desc' else asc(col))

    page = max(int(request.args.get('page', 1)), 1)
    page_size = min(max(int(request.args.get('page_size', 100)), 1), 1000)
    total = q.count()
    rows = q.offset((page - 1) * page_size).limit(page_size).all()

    data = [_model_to_dict(r) for r in rows]
    return jsonify({
        'page': page,
        'page_size': page_size,
        'total': total,
        'items': data,
    })

@api.route('/questions/<int:item_id>', methods=['GET'])
def get_question(item_id: int):
    _require_api_key()
    row = db_session.query(Question).get(item_id)
    if not row:
        abort(404)
    return jsonify(_model_to_dict(row))

@api.route('/questions.csv', methods=['GET'])
def get_questions_csv():
    _require_api_key()

    q = db_session.query(Question)

    search = request.args.get('search')
    if search:
        q = q.filter(
            (Question.title.ilike(f'%{search}%')) |
            (Question.text.ilike(f'%{search}%'))
        )

    q = q.order_by(asc(Question.id))

    rows = q.all()
    dicts = [_model_to_dict(r) for r in rows]

    if not dicts:
        csv_text = ''
    else:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(dicts[0].keys()))
        writer.writeheader()
        writer.writerows(dicts)
        csv_text = output.getvalue()

    return Response(
        csv_text,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=questions.csv'},
    )


@api.route('/forms', methods=['GET'])
def get_forms():
    """Return paginated list of completed forms."""
    _require_api_key()

    q = db_session.query(CompletedForm)

    search = request.args.get('search')
    if search:
        q = q.filter(CompletedForm.template_name.ilike(f'%{search}%'))

    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc').lower()
    col = getattr(CompletedForm, sort, None)
    if col is None:
        abort(400, description=f'Unsupported sort column: {sort}')
    q = q.order_by(desc(col) if order == 'desc' else asc(col))

    page = max(int(request.args.get('page', 1)), 1)
    page_size = min(max(int(request.args.get('page_size', 100)), 1), 1000)
    total = q.count()
    rows = q.offset((page - 1) * page_size).limit(page_size).all()

    data = [_model_to_dict(r) for r in rows]
    return jsonify({
        'page': page,
        'page_size': page_size,
        'total': total,
        'items': data,
    })


@api.route('/forms/<int:item_id>', methods=['GET'])
def get_form(item_id: int):
    """Return a single completed form by ID."""
    _require_api_key()
    row = db_session.query(CompletedForm).get(item_id)
    if not row:
        abort(404)
    return jsonify(_model_to_dict(row))


@api.route('/forms.csv', methods=['GET'])
def get_forms_csv():
    """Return all completed forms as CSV."""
    _require_api_key()

    q = db_session.query(CompletedForm)

    search = request.args.get('search')
    if search:
        q = q.filter(CompletedForm.template_name.ilike(f'%{search}%'))

    q = q.order_by(asc(CompletedForm.id))

    rows = q.all()
    dicts = [_model_to_dict(r) for r in rows]

    if not dicts:
        csv_text = ''
    else:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(dicts[0].keys()))
        writer.writeheader()
        writer.writerows(dicts)
        csv_text = output.getvalue()

    return Response(
        csv_text,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=forms.csv'},
    )
