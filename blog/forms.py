from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,TextAreaField,PasswordField,BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required

from models import db,Category

class PostForm(FlaskForm):
    """
    Post form
    """
    def get_category():
        return [category.name for category in db.session.query(Category).all()]

    def get_pk(obj):
        return obj

    id=StringField('id',validators=[Required()])
    title=StringField('title',validators=[Required()])
    brief=StringField('brief',validators=[Required()])
    category=QuerySelectField('category',query_factory=get_category,get_pk=get_pk)
    tags=StringField('tag',validators=[Required()])
    body=TextAreaField('body',validators=[Required()])
    submit=SubmitField('提交')


class CategoryForm(FlaskForm):
    """
     Category form
    """
    id=StringField('id',validators=[Required()])
    category=StringField('category',validators=[Required()])


class LoginForm(FlaskForm):
    """
    Login form
    """
    username=StringField('username',validators=[Required()])
    password=PasswordField('password',validators=[Required()])
    remember_me=BooleanField('Remember me',default=False)
    submit=SubmitField('登录')