from tortoise import fields
from tortoise.models import Model


# 一对多示例：Author -> Post
class Author(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)

    # 一对多反向关系：author.posts
    # 不需要声明字段，只要 related_name 即可。
    posts : fields.ReverseRelation["Post"]
    def __str__(self):
        return self.name

# 多对多关联表目标模型
class Tag(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)

    posts : fields.ManyToManyRelation["Post"]

    def __str__(self):
        return self.name

class Post(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=100)
    content = fields.TextField()
    author : fields.ForeignKeyRelation[Author]  = fields.ForeignKeyField("models.Author", related_name="posts")

    # 多对多示例：Post -> Tag
    tags : fields.ManyToManyRelation[Tag] = fields.ManyToManyField("models.Tag", related_name="posts")

    def __str__(self):
        return self.title



