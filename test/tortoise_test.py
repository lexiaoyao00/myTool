import asyncio
from tortoise import Tortoise, fields
from tortoise.models import Model

class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    age = fields.IntField()

    def __str__(self):
        return f"{self.name} ({self.age})"

async def run():
    # 1. 初始化并建表
    await Tortoise.init(
        db_url='sqlite://test.db',
        modules={'models': ['__main__']}
    )
    await Tortoise.generate_schemas()

    # 2. 增加
    await User.create(name='Alice', age=25)
    await User.create(name='Bob', age=30)

    # 3. 查询
    all_users = await User.all()
    print("所有用户:", all_users)

    # 条件查询
    young_users = await User.filter(age__lt=30).all()
    print("30岁以下用户:", young_users)

    # 4. 修改
    user = await User.get(name='Alice')
    user.age = 26
    await user.save()
    print("修改后:", await User.get(name='Alice'))

    # 5. 删除
    await user.delete()
    print("删除后:", await User.all())

    # 6. 关闭连接
    await Tortoise.close_connections()

asyncio.run(run())
