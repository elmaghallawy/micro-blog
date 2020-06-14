from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


class Permission:
    """class of permissions names and values"""
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    """Role model"""
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        # initialize the permission with 0 if None
        if self.permissions is None:
            self.permissions = 0

    def add_permission(self, perm):
        """add a permission to a role"""
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        """remove a permission from a role"""
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        """reset permissions for a role"""
        self.permissions = 0

    def has_permission(self, perm):
        """check if a role has a certain permission"""
        return self.permissions & perm == perm

    def __repr__(self):
        """role string represntation with its name"""
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        """insert roles into the database"""
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE,
                          Permission.MODERATE],
            'Admin': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE,
                      Permission.MODERATE, Permission.ADMIN],
        }
        default_role = 'User'

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()


class User(db.Model, UserMixin):
    """User model"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # check if the user has a role if not then check if s/he is admin
        # if not then assign the default role to the uers
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Admin').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        """raise an error when trying to get the password"""
        raise AttributeError('password is not readable attribute')

    @password.setter
    def password(self, password):
        """generate hash value for a given password"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """verify a given password"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    def generate_confirmation_token(self, expiration=3600):
        """generate a JWT for email confirmation"""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        """confirm the token recieved"""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def can(self, perm):
        """check of the user has a certain permission"""
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self):
        """check if the user is admin """
        return self.can(Permission.ADMIN)


class AnonymousUser(AnonymousUserMixin):
    """class of anonymous user"""

    def can(self, permissions):
        return False

    def is_admin(self):
        return False


login_manager.anonymous_user = AnonymousUser
