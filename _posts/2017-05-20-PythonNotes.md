---
title: Python Notes
category: CS
---

## Python Notes

> 　　断断续续跟着各种资料学了 Python，发现自己的知识很零碎，不成体系。另外，也为了向 Python 3 迁移，这里再过一遍 Python 3 的官方手册，做一些笔记，方便日后查看。  
> 　　现在学习新语言的方法已经定下来：  
> 　　　　1. 学习一遍语法规则  
> 　　　　2. 写代码  
> 　　　　3. 读代码  
> 　　　　4. repeat 1~3
>
> 　　后面将使用 Python 3.6。

### Socket 编程



### 基本

Python 3 中`input`和`raw_input`合二为一为`input`。

字符串直接用`Unicode`编码了。不过在开头还是加上：

```
# -*- coding: utf-8 -*-
```

列表可以修改，元组不能。

通用序列操作：分片/检查是否属于(in)

初始化列表：

```
sequence = [None] * 10
```

删除元素：`del names[2]`

一个值的元组：`(42,)`。

格式化字符串。

字典的浅复制和深复制：

```
# shallow copy
y = x.copy()
# deep copy
z = copy.deepcopy(x)
```

使用`x.get("a")`而不是`x["a"]`。这样当`"a"`键不存在时可以返回`None`而不是出错。

`keys`/`iterkeys`  
`items`/`iteritems`

`elif`

`is`是`同一性运算符`。

断言：`assert 'i' in myStr`

`pass`

给函数加`"""this is a function"""`文档字符串`__doc__`。

`参数默认值`/`关键字参数`。

### Classes

Python 的类系统非常强大，允许多基类，允许子类重写父类方法，可以调用基类方法。类对象在运行时创建，在创建后可以被修改（想想 C 的面向对象写法，结构体+回调函数）。类成员默认是`public`类型。

##### Scope and Namespaces

引用顺序举例：

{% highlight python %}
def scope_test():
    def do_local():
        spam = "local spam"

    def do_nonlocal():
        nonlocal spam
        spam = "nonlocal spam"

    def do_global():
        global spam
        spam = "global spam"

    spam = "test spam"
    do_local()
    print("After local assignment:", spam)
    do_nonlocal()
    print("After nonlocal assignment:", spam)
    do_global()
    print("After global assignment:", spam)

scope_test()
print("In global scope:", spam)
{% endhighlight %}

测试结果：

```
After local assignment: test spam
After nonlocal assignment: nonlocal spam
After global assignment: nonlocal spam
In global scope: global spam
```

很有意思的。

##### Classes

基本定义：

```
class ClassName(ParentClass):
	"""A simple class"""
	def __init__(self, a, b): # 构造函数
    	print(a)
        print(b)
	def f(self):
    	print(self.__doc__)
```

实例化：

```
x = ClassName(1, 2)
x.f()
```

`self`指的是当前类的实例，`self.__class__`指向类。

类中定义的变量是同一个类的所有实例共享的，在修改后才成为实例独有的一份拷贝。

### Modules

`Module`是为了既能够把代码用于其它的程序中，又能够直接使用解释器运行。

文件名就是模块名，例如我们后面使用的`myLovelyMod.py`，你可以通过全局变量`__name__`获取它。

{% highlight python %}
# my lovely module

token = "in the name of love"

def SayModName():
    print(__name__)
{% endhighlight %}

在当前目录下打开解释器，然后就可以导入：

```
import myLovelyMod

myLovelyMod.SayModName()
myLovelyMod.token
```

模块可以包含一些非函数的执行语句，在第一次被加载时执行。每个模块有自己的私有符号表，供模块内定义的所有函数使用，不必担心与其他文件的符号冲突，你可以定义全局变量。

你也可以通过`from myLovelyMod import *`引入所有无`_`前缀的符号，然而最好不要这么做。

当处于解释器交互环境时，如果你在`import`后改动了你的模块，需要重新载入：

```
import importlib
importlib.reload(myLovelyMod)
```

直接执行模块时，`__name__`被置为`__main__`，所以模块最好加上：

```
if __name__ == "__main__":
	...
```

这对于直接测试模块很有帮助（有点 Lisp 的感觉）。

模块搜索路径：

- 首先在`built-in`模块找
- 找不到则在`sys.path`中找：
	- 当前目录
	- `PYTHONPATH`
	- Python 安装目录

为了加快模块加载速度，Python 会生成`__pycache__`目录，包含编译过的`.pyc`文件。这个文件是平台无关，可以通用的。

`dir()`用于列出当前模块定义的符号名。

`Packages`是个很棒的东西。

`A.B`意味着模块`B`放在包`A`中。这防止了不同模块的重名（分层思想）。

目录名即包名，目录下要有`__init__.py`，可以为空，但建议在其中定义`__all__`变量，将包内想要暴露到外面的符号都写进去，否则使用时需要先找文件，很麻烦。下面是一个嵌套包的示例：

```
main.py
testPack
|- __init__.py
|- subPackA
	|- __init__.py
    |- myLovelyMod.py
|- subPackB
	|- __init__.py
    |- myLovelyMod.py
```

`main.py`中可以使用如下示例：

```
import testPack.subPackA.myLovelyMod

def main():
    print("I love programming")
    testPack.subPackA.myLovelyMod.SayModName()

if __name__ == "__main__":
    main()
```

注意，此时打印的模块名将是`testPack.subPackA.myLovelyMod`。

`__init__.py`如下：

```
# testPack/__init__.py
__all__ = ["subPackA", "subPackB"]
# testPack/subPackA/__init__.py
__all__ = ["myLovelyMod"]
# testPack/subPackB/__init__.py
__all__ = ["myLovelyMod"]
```

需要注意的是，

```
import testPack.subPackA.myLovelyMod
```

和

```
testPack.subPackA.myLovelyMod.SayHelloWorld()
```

的层次是对应的。如果我仅仅

```
import testPack.subPackA
```

那么是不能执行`SayHelloWorld()`的。也就是说，我们能且只能使用`import`的层次下一层次的符号。

在同一包内也可以使用相对路径来加载，如`from . import`。

当包的`__init__.py`分布于多个目录时，可以通过在顶层`__init__.py`中使用`__path__`指定需要被执行的其他`__init__.py`。

### Python 2 or 3?

可以看【参考1】。至少为了中文编码，我会选择 3。

### PyCharm

工欲善其事，必先利其器。好的 IDE 的确是提高生产力的工具，美观的界面让人首先由一个编程的好心情。下面记录的是 PyCharm 的 tips（其实 JetBrains 出的 IDE 的 tips 很多是通用的）：

`CTRL + ALT + L` | 格式化代码

`ALT + Enter` | 万能键，常用于补全`import`

`SHIFT + F10` | Run

`CTRL + P` | 在调用函数时括号中按下，显示参数

`CTRL + ALT + Enter` | 向上另起一行

`Double SHIFT` | 搜索一切

`CTRL + /` | 快速注释当前行

搭配上 Github 用，编程体验真是棒极了。我看，要培养普通人的编程能力，首先给他们一个优雅的 IDE，配置流畅的 build 过程，再搭配上 VCS 如 Github 或 Gitlab，这分明就是另一种艺术形式嘛！

### 参考

- [Should I use Python 2 or Python 3 for my development activity?](https://wiki.python.org/moin/Python2orPython3)
- [Python Tutorial](https://docs.python.org/3/tutorial)
- [开源软件架构](http://www.ituring.com.cn/book/miniarticle/5486)