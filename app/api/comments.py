from flask import g, jsonify, request, url_for
from ..models import Comment, db, Permission
from .decorators import permission_required


@api.route('/comments/')
def get_comments():
    comments = Comment.query.all()
    return jsonify({'comments': [comment.to_json() for comment in comments]})


@api.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())


@api.route('posts/<int:id>/comments/')
def get_post_comments():
    post = Post.query.get_or_404(id)
    return jsonify({'comments': [comment.to_json() for comment in comments]})


@api.route('posts/<int:id>/comments/', method=['POST'])
@permission_required(Permission.COMMENT)
def new_comment():
    post = Post.query.get_or_404(id)
    comment = Comment.from_json(request.json)
    comment.author = g.current_user
    comment.post = post
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json, 201, {'Location': url_for('api.get_comment', id=comment.id)})
