import os
import tornado.ioloop
import tornado.web
import tornado.locale
import tornado.escape
from sys import getsizeof
from tornado.options import define, options

import uimodules


from utils import *

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, type=bool)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_id = self.get_secure_cookie("user")
        if not user_id: return None
        user = get_user(u_id=int(user_id))
        return user


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        self.write("Hello, " + name)


class RegisterHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("register.html")
    def post(self):
        res = {"success": False, "msg": ""}
        username = self.get_argument("username")
        email = self.get_argument("email")
        password = self.get_argument("password")
        confirm_password = self.get_argument("confirm_password")

        if not username:
            res["msg"] = "用户名不能为空"
            self.finish(res)

        if not email:
            res["msg"] = "邮箱不能为空"
            self.finish(res)

        if not password:
            res["msg"] = "密码不能为空"
            self.finish(res)

        if confirm_password != password:
            res["msg"] = "密码不一致"
            self.finish(res)

        info = {
            "username": username,
            "email": email,
            "password": password
        }
        user = create_user(info)
        if not user:
            res["msg"] = "创建失败"
            self.finish(res)
        else:
            res["msg"] = "注册成功"
            self.write(res)


class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("login.html")
    def post(self):
        email = self.get_argument("email")
        password = self.get_argument("password")
        auth = authenticate(email=email, password=password)
        if auth["success"]:
            self.set_secure_cookie("user", str(auth["user_id"]))
        self.write(auth)


class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect("/index")


class IndexHandler(BaseHandler):
    def get(self):
        articles = get_articles()
        self.render("index.html", articles=articles)


class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        u_id = self.current_user.id
        articles = get_articles(u_id=u_id)
        print(type(articles))
        print(dir(articles))
        self.render("home.html", articles=articles)


class DetailHandler(BaseHandler):
    def get(self, a_id):
        article = get_article(a_id=int(a_id))
        comments = get_comments(a_id=int(a_id))
        self.render("detail.html", article=article, comments=comments)


class LikeHandler(BaseHandler):
    def get(self, a_id):
        res = {"success": False, "msg": ""}
        if not self.current_user:
            res["msg"] = "请登录"
            self.finish(res)
        else:
            u_id = self.current_user.id
            result = add_like_count(a_id=a_id, u_id=u_id)
            if result:
                res["success"] = True
            else:
                res["msg"] = "你已赞过"
            self.write(res)


class CommentLikeHandler(BaseHandler):
    def get(self, c_id):
        res = {"success": False, "msg": ""}
        if not self.current_user:
            res["msg"] = "请登录"
            self.finish(res)
        else:
            u_id = self.current_user.id
            result = add_comment_like_count(c_id=int(c_id), u_id=u_id)
            if result:
                res["success"] = True
            else:
                res["msg"] = "你已赞过"
            self.write(res)


class CommentHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, a_id):
        article = get_article(a_id=int(a_id))
        self.render("comment.html", article=article)

    @tornado.web.authenticated
    def post(self, a_id):
        res = {"success": False, "msg": ""}
        try:
            content = self.get_argument("content")
            info = {
                "content": content,
                "article_id": a_id,
                "author_id": self.current_user.id
            }
            result = create_comment(**info)
            if result["success"]:
                res["success"] = True
                self.write(res)
            else:
                res["msg"] = "提交出错"
                self.write(res)
        except:
            res["msg"] = "提交出错"
            self.write(res)


class ProfileHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('profile.html')


class SettingHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('setting.html')


class AvatarHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        res = {"success": False, "msg": ""}
        try:
            file1 = self.request.files['avatar'][0]
            original_fname = file1['filename']
            extension = os.path.splitext(original_fname)[1]
            if file1.content_type not in ('image/jpg', 'image/jpeg', 'image/png', 'image/gif'):
                res["msg"] = "格式不正确"
                self.finish(res)
            file_size = getsizeof(file1.body)
            if file_size > 1024 * 1024 * 2:
                res["msg"] = "图片最大2MB"
                self.finish(res)
            else:
                fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6)) + str(int(time.time() * 1000))
                final_filename = fname + extension
                output_file = open("static/media/avatar/" + final_filename, 'wb')
                output_file.write(file1['body'])
                old_avatar = self.current_user.profile.avatar
                self.current_user.profile.avatar = final_filename
                result = change_avatar(p_id=self.current_user.profile.id, avatar=final_filename)
                if result["success"]:
                    try:
                        os.remove("static/media/avatar/" + old_avatar)
                    except:
                        pass
                    res["success"] = True
                    res["msg"] = "设置成功"
                    self.write(res)
                else:
                    res["msg"] = "设置出错"
                    self.write(res)
        except Exception as e:
            print(str(e))
            res["msg"] = "设置出错"
            self.finish(res)


class PublishHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("publish.html")

    @tornado.web.authenticated
    def post(self):
        res = {"success": False, "msg": ""}
        try:
            image_name = None
            if self.request.files:
                file1 = self.request.files['image'][0]
                original_fname = file1['filename']
                extension = os.path.splitext(original_fname)[1]
                if file1.content_type not in ('image/jpg', 'image/jpeg', 'image/png', 'image/gif'):
                    res["msg"] = "格式不正确"
                    self.finish(res)
                file_size = getsizeof(file1.body)
                if file_size > 1024 * 1024 * 2:
                    res["msg"] = "图片最大2MB"
                    self.finish(res)
                else:
                    fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6)) + str(
                        int(time.time() * 1000))
                    final_filename = fname + extension
                    output_file = open("static/media/image/" + final_filename, 'wb')
                    output_file.write(file1['body'])
                    image_name = final_filename

            content = self.get_argument("content")
            info = {
                "author": self.current_user,
                "author_id": self.current_user.id,
                "content": content,
                "image": image_name
            }
            result = create_article(info)
            if result["success"]:
                res["success"] = True
                self.write(res)
            else:
                res["msg"] = "发布出错"
                self.finish(res)
        except Exception as e:
            print(str(e))
            res["msg"] = "发布出错"
            self.finish(res)


settings = {
        "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o",
        "login_url": "/login",
        "template_path": os.path.join(os.path.dirname(__file__), "templates"),
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "xsrf_cookies": True,
        "ui_modules": uimodules,
        "debug": options.debug,
}

application = tornado.web.Application([
    (r"/", IndexHandler),
    (r"/register", RegisterHandler),
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
    (r'/profile', ProfileHandler),
    (r'/home', HomeHandler),
    (r"/index", IndexHandler),
    (r"/comment/([0-9]+)", CommentHandler),
    (r"/avatar", AvatarHandler),
    (r'/publish', PublishHandler),
    (r'/detail/([0-9]+)', DetailHandler),
    (r'/like/([0-9]+)', LikeHandler),
    (r'/comment/like/([0-9]+)', CommentLikeHandler),


    ], **settings)

if __name__ == '__main__':
    i18n_path = os.path.join(os.path.dirname(__file__), 'i18n/locales')
    tornado.locale.load_gettext_translations(i18n_path, 'zh_CN')
    tornado.locale.set_default_locale('zh_CN')

    application.listen(8888)
    print("App Start running at: http://127.0.0.1:8888")
    tornado.ioloop.IOLoop.instance().start()