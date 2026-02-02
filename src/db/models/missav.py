from tortoise import fields
from tortoise.models import Model

class Missav(Model):
    id = fields.IntField(pk=True)
    releasedate = fields.DateField()    # 发行日期
    title = fields.CharField(max_length=256)    # 标题
    num_code = fields.CharField(max_length=100) # 番号
    plot = fields.TextField(default="")  # 简介
    actresses : fields.ManyToManyRelation['Actress'] = fields.ManyToManyField("missav.Actress", related_name="missav")  # 女优
    actors : fields.ManyToManyRelation['Actor'] = fields.ManyToManyField("missav.Actor", related_name="missav")   # 男优
    genres : fields.ManyToManyRelation['Genre'] = fields.ManyToManyField("missav.Genre", related_name="missav")   # 类型
    series : fields.ManyToManyRelation['Series'] = fields.ManyToManyField("missav.Series", related_name="missav")   # 系列
    makers : fields.ManyToManyRelation['Maker'] = fields.ManyToManyField("missav.Maker", related_name="missav")    # 发行商
    directors : fields.ManyToManyRelation['Director'] = fields.ManyToManyField("missav.Director", related_name="missav")   # 导演
    tags : fields.ManyToManyRelation['Tag'] = fields.ManyToManyField("missav.Tag", related_name="missav")    # 标签


    def __str__(self):
        return self.title



class Actress(Model):
    """ 女优 """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    href = fields.CharField(max_length=256,null=True)

    missav : fields.ReverseRelation[Missav]
    def __str__(self):
        return self.name

class Actor(Model):
    """ 男优 """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    href = fields.CharField(max_length=256,null=True)

    missav : fields.ReverseRelation[Missav]
    def __str__(self):
        return self.name

class Genre(Model):
    """ 类型 """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    href = fields.CharField(max_length=256,null=True)

    missav : fields.ReverseRelation[Missav]
    def __str__(self):
        return self.name

class Series(Model):
    """ 系列 """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    href = fields.CharField(max_length=256,null=True)

    missav : fields.ReverseRelation[Missav]
    def __str__(self):
        return self.name

class Maker(Model):
    """ 制作商 """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    href = fields.CharField(max_length=256,null=True)

    missav : fields.ReverseRelation[Missav]
    def __str__(self):
        return self.name

class Director(Model):
    """ 导演 """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    href = fields.CharField(max_length=256,null=True)

    missav : fields.ReverseRelation[Missav]
    def __str__(self):
        return self.name

class Tag(Model):
    """ 标签 同 label"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    href = fields.CharField(max_length=256,null=True)

    missav : fields.ReverseRelation[Missav]
    def __str__(self):
        return self.name