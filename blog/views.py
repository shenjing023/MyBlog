from flask import render_template,jsonify,request,flash,redirect,url_for,abort
from datetime import datetime
from flask_login import login_user,login_required

from main import app
from models import db,User,Category,Post,Tag
from forms import PostForm,CategoryForm,LoginForm

import random
from uuid import uuid4

def sidebar_data():
    """
    获取右侧栏的分类与标签数据
    """
    categories=[]
    for category in db.session.query(Category).all():
        item={}
        item['id']=category.id
        item['name']=category.name
        item['count']=db.session.query(Post).filter(Post.category_id==category.id).count()
        categories.append(item)
    # 标签
    tags=[]
    for tag in db.session.query(Tag).all():
        tags.append({
            'id':tag.id,
            'name':tag.name
        })
    return categories,tags


@app.route('/')
@app.route('/page/<int:page>')
def home(page=1):
    """
    View of home page
    """
    # 文章
    posts=Post.query.order_by(
        Post.publish_date.desc()
    ).paginate(page,10)
    if posts is None:
        abort(404)
    # 总页数
    total_page=posts.pages
    # 当前页数
    current_page=1
    # 分类与标签
    categories,tags=sidebar_data()

    return render_template(
                            'home.html',
                            posts=posts.items,
                            categories=categories,
                            tags=tags,
                            current_page=current_page,
                            total_page=total_page
                        )

@app.route('/archives')
def archives():
    """
    View of the archives
    """
    # 归档
    archives=[]
    publish_years=db.session.query(Post.publish_year).group_by(Post.publish_year).order_by(Post.publish_year.desc()).all()
    for year in publish_years:
        archive={}
        archive['year']=year[0]
        archive['posts']=[]
        posts=db.session.query(Post.id,Post.publish_date,Post.title).order_by(Post.publish_date.desc()).filter(Post.publish_year==year[0]).all()
        for p in posts:
            post={
                'post_id':p[0],
                'post_publish_date':p[1].strftime("%Y/%m/%d"),
                'post_title':p[2]
            }
            archive['posts'].append(post)
        archives.append(archive)
        # 分类与标签
        categories,tags=sidebar_data()

    return render_template(
                                'archives.html',
                                archives=archives,
                                categories=categories,
                                tags=tags
                            )


@app.route('/about')
def about():
    """
    About me
    """
    # 分类与标签
    categories,tags=sidebar_data()
    return render_template(
                            'about_me.html',
                            categories=categories,
                            tags=tags
                            )


@app.route('/post/<post_id>')
def post(post_id):
    """
    查看文章内容
    """
    post_tmp=db.session.query(Post).filter(Post.id==post_id).first()
    if post_tmp is None:
        abort(404)
    if post_tmp:
        post={
            'title':post_tmp.title,
            'publish_date':post_tmp.publish_date.strftime("%Y/%m/%d"),
            'category':{
                'id':post_tmp.category_id,
                'name':post_tmp.category.name
            },
            'body_html':post_tmp.body_html,
            'tags':post_tmp.tags,
            'pre':get_prepost(post_tmp.publish_date),
            'next':get_nextpost(post_tmp.publish_date)
        }
        categories,tags=sidebar_data()
        return render_template(
                                'post.html',
                                post=post,
                                categories=categories,
                                tags=tags
                            )


@app.route('/category/<category_id>')
def category(category_id):
    """
    分类
    """
    # 归档
    category=db.session.query(Category).filter(Category.id==category_id).one()
    if category is None:
        abort(404)
    archives=[]
    publish_years=db.session.query(Post.publish_year).filter(Post.category_id==category_id).group_by(Post.publish_year).order_by(Post.publish_year.desc()).all()
    for year in publish_years:
        archive={}
        archive['year']=year[0]
        archive['posts']=[]
        posts=db.session.query(Post.id,Post.publish_date,Post.title).filter(Post.category_id==category_id).order_by(Post.publish_date.desc()).filter(Post.publish_year==year[0]).all()
        for p in posts:
            post={
                'post_id':p[0],
                'post_publish_date':p[1].strftime("%Y/%m/%d"),
                'post_title':p[2]
            }
            archive['posts'].append(post)
        archives.append(archive)
        # 分类与标签
        categories,tags=sidebar_data()
    

    return render_template(
                                'tag.html',
                                archives=archives,
                                categories=categories,
                                tags=tags,
                                title=category.name
                            )


@app.route('/tag/<tag_id>')
def tag(tag_id):
    """
    标签
    """
    # 归档
    tag=db.session.query(Tag).filter(Tag.id==tag_id).one()
    archives=[]
    publish_years=db.session.query(Post.publish_year).filter(Post.tags.any(id=tag_id)).group_by(Post.publish_year).order_by(Post.publish_year.desc()).all()
    for year in publish_years:
        archive={}
        archive['year']=year[0]
        archive['posts']=[]
        posts=db.session.query(Post.id,Post.publish_date,Post.title).filter(Post.tags.any(id=tag_id)).order_by(Post.publish_date.desc()).filter(Post.publish_year==year[0]).all()
        for p in posts:
            post={
                'post_id':p[0],
                'post_publish_date':p[1].strftime("%Y/%m/%d"),
                'post_title':p[2]
            }
            archive['posts'].append(post)
        archives.append(archive)
        # 分类与标签
        categories,tags=sidebar_data()
    

    return render_template(
                                'category.html',
                                archives=archives,
                                categories=categories,
                                tags=tags,
                                title=tag.name
                            )


@app.route('/admin/post/new',methods=['GET','POST'])
@login_required
def post_new():
    """
    添加新文章
    """
    form=PostForm()
    if request.method=='POST':
        id=str(uuid4())
        title=form.title.data
        body=form.body.data
        brief=form.brief.data
        publish_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        publish_year=datetime.now().year
        post=Post(id,title,body,brief,publish_date,publish_year)
        post.category=db.session.query(Category).filter(Category.name==form.category.data).one()
        # tag,先检测是否已存在
        tags=[]
        for tag in form.tags.data.split(', '):
            if db.session.query(Tag).filter(Tag.name==tag).all():
                # 该标签已存在
                t=db.session.query(Tag).filter(Tag.name==tag).one()
            else:
                t=Tag(str(uuid4()),tag)
            tags.append(t)
        post.tags=tags
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('post_management'))
    return render_template('./admin/admin_post_edit.html',form=form)


@app.route('/admin/post/edit/<post_id>',methods=['GET','POST'])
@login_required
def post_edit(post_id):
    """
    编辑文章
    """
    form=PostForm()
    if request.method=='GET':
        post_tmp=db.session.query(Post).filter(Post.id==post_id).one()
        form.id.data=post_tmp.id
        form.title.data=post_tmp.title
        form.brief.data=post_tmp.brief
        form.category.data=post_tmp.category.name
        tags=[tag.name for tag in post_tmp.tags]
        form.tags.data=",".join(tags)
        form.body.data=post_tmp.body
    if request.method=='POST':
        # tag,还要检测是否已存在
        tags=[]       
        for tag in form.tags.data.split(', '):
            if db.session.query(Tag).filter(Tag.name==tag).all():
                # 该标签已存在
                t=db.session.query(Tag).filter(Tag.name==tag).one()
            else:
                t=Tag(str(uuid4()),tag)
            tags.append(t)
        db.session.query(Post).filter(Post.id==form.id_.data).update({
            'title':form.title.data,
            'body':form.body.data,
            'publish_date':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'brief':form.body.data[:10],
            'publish_year':datetime.now().year
        })
        db.session.commit()
        post=db.session.query(Post).filter(Post.id==form.id_.data).one()
        post.tags=tags
        post.category=db.session.query(Category).filter(Category.name==form.category.data).one()
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('post_management'))
    return render_template('./admin/admin_post_edit.html',form=form)


@app.route('/admin/post-delete',methods=['POST'])
def post_delete():
    post=db.session.query(Post).filter(Post.id==request.values['id']).one()
    db.session.delete(post)
    db.session.commit()
    return jsonify({'response':'ok'})


@app.route('/admin/category',methods=['GET','POST'])
@login_required
def category_management():
    form=CategoryForm()
    if request.method=="POST":
        id=request.values['id']
        if not id:
            #添加分类
            category=Category(id=str(uuid4()),name=request.values['name'])
            db.session.add(category)
            db.session.commit()
            flash("添加成功")
            return jsonify({'response':'ok'})
        else:
            #修改分类
            category=db.session.query(Category).filter(Category.id==request.values['id']).one()
            category.name=request.values['name']
            db.session.add(category)
            db.session.commit()
            flash("修改成功")
            return jsonify({'response':'ok'})
    return render_template('./admin/admin_category.html',form=form)


def get_category():
    """
    获取分类数据
    """
    return [category.name for category in db.session.query(Category).all()]


@app.route('/admin/category-delete',methods=['POST'])
def category_delete():
    """
    删除分类
    """
    # 先查看该分类是否还有文章关联 
    post=db.session.query(Post).filter(Post.category_id==request.values['id']).first()
    if post:
        return jsonify({'response':'error'})
    else:
        category=db.session.query(Category).filter(Category.id==request.values['id']).one()
        db.session.delete(category)
        db.session.commit()
        return jsonify({'response':'ok'})


@app.route('/admin/category-data',methods=['GET'])
@login_required
def category_data():
    """
    返回分类的数据
    """
    categories=[]
    for category in db.session.query(Category).all():
        item={}
        item['id']=category.id
        item["name"]=category.name
        categories.append(item)
    info=request.values
    limit=info.get('limit',10)
    offset=info.get('offset',0)
    return jsonify({'total':len(categories),'rows':categories[int(offset):(int(offset)+int(limit))]})


@app.route('/admin/post-data',methods=['GET'])
@login_required
def post_data():
    """
    返回所有文章的数据
    """
    posts=[]
    for post in db.session.query(Post).all():
        item={}
        item['id']=post.id
        item['title']=post.title
        item['category']=post.category.name
        item['publish_date']=str(post.publish_date)
        posts.append(item)
    info=request.values
    limit=info.get('limit',10)
    offset=info.get('offset',0)
    return jsonify({'total':len(posts),'rows':posts[int(offset):(int(offset)+int(limit))]})


@app.route('/admin/post')
@login_required
def post_management():
    return render_template('./admin/admin_post.html')


def get_prepost(publish_date):
    """
    获取当前文章的前一篇文章

    param: publish_date 当前文章的发布时间
    """
    post=db.session.query(Post).filter(Post.publish_date<publish_date).order_by(Post.publish_date.desc()).first()
    return post


def get_nextpost(publish_date):
    """
    获取当前文章的前一篇文章

    param: publish_date 当前文章的发布时间
    """
    post=db.session.query(Post).filter(Post.publish_date>publish_date).order_by(Post.publish_date.asc()).first()
    return post


@app.route('/admin',methods=['GET','POST'])
def login():
    """
    登录
    """
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('home'))
        flash('用户名或密码错误')
    return render_template('./admin/admin_login.html',form=form)


@app.errorhandler
def page_not_found(e):
    return render_template('404.html'),404