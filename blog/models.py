from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from markdown import markdown
import bleach
from main import app,login_manager


# SQLAlchemy 会自动从app对象中的DevConfig中加载连接数据库的配置项
db=SQLAlchemy(app)

class User(UserMixin,db.Model):
    """
    Represents protected user
    """
    # set table name
    __tablename__="users"
    id=db.Column(db.String(45),primary_key=True)
    username=db.Column(db.String(255))
    password_hash=db.Column(db.String(128))
    # establish contact with post's foreignKey:user_id
    posts=db.relationship(
        'Post',
        backref='user',
        lazy='dynamic'
    )

    def __init__(self,id,username):
        self.id=id
        self.username=username

    def __repr__(self):
        return "<Model User '{}'>".format(self.username)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

# 这个callback函数用于reload User object，根据session中存储的user id
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class Category(db.Model):
    """
    Represents categories
    """
    __tablename__="categories"
    id=db.Column(db.String(45),primary_key=True)
    name=db.Column(db.String(255))
    posts=db.relationship(
        'Post',
        backref='category',
        lazy='dynamic'
    )

    def __init__(self,id,name):
        self.id=id
        self.name=name

    def __repr__(self):
        return "<Model Category '{}'>".format(self.name)


posts_tags=db.Table(
    'posts_tags',
    db.Column('post_id',db.String(45),db.ForeignKey('posts.id')),
    db.Column('tag_id',db.String(45),db.ForeignKey('tags.id'))
)

class Post(db.Model):
    """
    Represents posts
    """
    __tablename__="posts"
    id=db.Column(db.String(45),primary_key=True)
    title=db.Column(db.String(255))
    body=db.Column(db.Text())
    body_html=db.Column(db.Text())
    brief=db.Column(db.Text())
    publish_date=db.Column(db.DateTime)
    publish_year=db.Column(db.String(4))    #为了归档的时候分组查询
    # set the foreign key for post
    user_id=db.Column(db.String(45),db.ForeignKey('users.id'))
    category_id=db.Column(db.String(45),db.ForeignKey('categories.id'))
    # many to many : posts <==> tags
    tags=db.relationship(
        'Tag',
        secondary=posts_tags,
        backref=db.backref('posts',lazy='dynamic')
    )

    def __init__(self,id,title,body,brief,publish_date,publish_year):
        self.id=id
        self.title=title
        self.body=body
        self.brief=brief
        self.publish_date=publish_date
        self.publish_year=publish_year
        self.user=User.query.first()

    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        """
        处理body字段变化
        """
        # 需要转换的标签
        allowed_tags=['a','abbr','acronym','b','blockquote','code',
                        'em','i','li','ol','pre','strong','ul',
                        'h1','h2','h3','p','img'
                    ]
        # 需要提取的标签属性，否则会被忽略掉
        allowed_attrs={
            '*':['class'],
            'a':['href','ref'],
            'img':['src','alt']
        }
        target.body_html=bleach.linkify(
            bleach.clean(
                markdown(value,output_format='html'),
                tags=allowed_tags,
                attributes=allowed_attrs,
                strip=True
            )
        )

    def __repr__(self):
        return "<Model Post '{}'>".format(self.title)

db.event.listen(Post.body,'set',Post.on_changed_body)


class Tag(db.Model):
    """
    Represents tags
    """
    __tablename__="tags"
    id=db.Column(db.String(45),primary_key=True)
    name=db.Column(db.String(255))

    def __init__(self,id,name):
        self.id=id
        self.name=name

    def __repr__(self):
        return "<Model Tag '{}'>".format(self.name)