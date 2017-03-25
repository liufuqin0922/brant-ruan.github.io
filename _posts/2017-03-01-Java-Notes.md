---
title: Java Notes
category: CS
---

## Java Notes

### 2017-03-25

#### 匿名内部类



### 2017-03-25

#### 集合与泛型

`Java Collections Framework`能够支持绝大多数你会用到的数据结构。

**排序**

首先，`ArrayList`没有自带排序功能。然而，它并非唯一的集合，下面几个也比较常用：

|Name|Function|
|:-:|:-:|
|TreeSet|保持有序状态并防止重复|
|HashMap|可用成对的name/value来存取|
|LinkedList|针对经常插入/删除中间元素设计的高效集合|
|HashSet|防止重复的集合，快速寻找所要元素|
|LinkedHashMap|类似HashMap，可记录元素插入顺序|

在不需要元素保持有序时，尽量不要用`TreeSet`，开销挺大。

`Collections`类有一个`sort`方法，它的参数是`List`类，而`ArrayList`实现了`List`的接口，所以你可以传入`ArrayList`去排序。

下面是一个解析文件中的歌名并排序输出的例子：

```
ArrayList<String> songList = new ArrayList<String>();
... // 向 songList 中添加一些歌曲
Collections.sort(songList); // 排序
```

现在，假设开发人员使用`Song`对象代替了直接作为歌名的`String`，这样可以有更多信息被输出。`Song`对象如下：

{% highlight java %}
class Song{
	String title;
	String artist;
	String rating;
	String bpm;
	Song(String t, String a, String r, String b){
		title = t;
		artist = a;
		rating = r;
		bpm = b;
	}
	public String getTitle(){
		return title;
	}
	public String getArtist(){
		return artist;
	}
	public String getRating(){
		return rating;
	}
	public String getBpm(){
		return bpm;
	}
	public String toString(){
		return title;
	}
}
{% endhighlight %}

注意上面的`Song`重写了`toString()`方法，因为`System.out.println(anObject)`时会调用对象的`toString()`。

我们需要把`ArrayList<String>`改为`ArrayList<Song>`，然而仅仅这样编译是不报错的，因为`Collections.sort()`不知道按什么来排序。

参考 API 文档，我们发现，`sort()`的定义是`sort(List<T> list)`，这是什么鬼......

好吧，`<>`这叫做`泛型（generic）`，从`Java 5.0`开始加入。泛型意味着更好的安全性，几乎所有你会以泛型写的程序都与处理集合有关，防止你把`Dog`加入到一群`Cat`中。

在泛型之前，编译器无法得知你加入集合中的东西是什么，因为它们处理的都是`Object`类型，你可以把任何东西放进`ArrayList`中，出来就变成了`Object`。

一旦使用泛型：`ArrayList<Fish>`，你就只能把`Fish`以引用形式放进去，不能放进`Cat`，而且提取出来的也是`Fish`的引用。

有三个事情是你需要知道的：

- 创建被泛型化类的实例时要指定它容许的对象
- 声明与指定泛型类型的变量（多态遇到泛型会怎么样？）

我们看一下`ArrayList`的定义：

```
public class ArrayList<E>
extends AbstractList<E>
implements List<E> ... {
	public boolean add(E o)
}
```

`E`代表你声明的真正类型。

- 声明（与调用）取用泛型类型的方法（遇到多态会怎么样？）

在方法中的类型参数有几种不同运用方式：

1 使用定义在类声明的类型参数：

```
public class ArrayList<E> extends AbstractList<E>{
	public boolean add(E o)
}
```

上面的方法只能使用`E`作为类型，因为它已经被定义成类的一部分。

2 使用未定义在类声明的类型参数。

```
public <T extends Animal> void takeThing(ArrayList<T> list)
```

这意味着`T`可以是`Animal`，也可以是任何一种`Animal`。

我们再回过头看报错的`sort()`方法。看一下`sort()`方法的定义：

```
public static <T extends Comparable<? super T>> void sort(List<T> list)
```

它只接受`Comparable`对象的`list`，而我们的`Song`很明显不是`Comparable`的子型，所以不可以。然而，`String`也没有继承`Comparable`，仅仅是实现了它（`Comparable`是一个接口）。事实上，`<T extends Comparable>`意思是`T`要么实现了`Comparable`接口，要么是它的子类。

因此，解决方案是，我们的`Song`类要实现`Comparable`接口。而它只有一个方法需要被实现：

```
// java.lang.Comparable
public interface Comparable<T>{
	int compareTo(T o);
}
```

这个`compareTo(T o)`是这样要求的：

```
Returns:
a negative integer, zero, or a positive integer as this object is less than, equal to, or greater than the specified object.
```

所以很简单了，修改一下`Song`类的定义：

{% highlight java %}
class Song implements Comparable<Song>{
	...
	public int compareTo(Song s){
		return title.compareTo(s.getTitle());
	}
}
{% endhighlight %}

完美解决。

现在客户又加需求啦（客户总是有需求。。。）他希望除了依照歌名来排序外，还要有依照歌星名来排序的功能。然而，我们只能实现一个`compareTo()`方法，当然，我们可以通过传入额外的判断条件来改变`compareTo()`的行为，但是这样很不好。

事实上，还有另一个重载版的`sort()`方法：

```
public static <T> void sort(List<T> list, Comparator<? super T> c)
```

这个和`C++`中的排序函数很像，就是让你自己传进去一个东西用来排序，这里传入的是一个`Comparator`：

```
// java.util.Comparator
public interface Comparator<T>{
	int compare(T o1, T o2);
}
```

这个`sort()`方法不再取用元素内置的`compareTo()`方法排序。也就是说，你的`Song`类不必实现`Comparable`接口。

假设我们的主类是`Jukebox`，我们实现一个`ArtistCompare`内部类作为`Comparator`，`Song`类参考上面的代码，大体结构如下：

{% highlight java %}
public class Jukebox{
	ArrayList<Song> songList = new ArrayList<Song>();
	public static void main(String[] args){
		new Jukebox().go()；
	}
	class ArtistCompare implements Comparator<Song>{
		public int compare(Song one, Song two){
			return one.getArtist().compareTo(two.getArtist());
		}
	}
	...
	public void go(){
		getSongs();
		ArtistCompare artistCompare = new ArtistCompare();
		Collections.sort(songList, artistCompare);
	}
}
{% endhighlight %}

**下面要考察元素重复问题**

场景是刚刚的点歌系统，有人点了多次同一首歌，所以歌曲文件记录中有重复，我们要去重并排序。

重新回到最开始：`Collection` API 手册中主要有三个接口`List`/`Set`/`Map`。`List`是知道索引位置的集合，帮助排序；`Set`注重不重复；`Map`用`key`来搜索，即字典。

下面两张图展示了 Java 集合之间的关系，其中`interface`之间都是继承关系，具体类与`interface`之间都是实现关系：

![HeadFirstJava-collection]({{ site.url }}/resources/pictures/HeadFirstJava-Collection.png)

![HeadFirstJava-Map]({{ site.url }}/resources/pictures/HeadFirstJava-Map.png)

我们把点歌系统中的`ArrayList`用`HashSet`取代（在上面代码中加入`HashSet`）：

{% highlight java %}
HashSet<Song> songSet = new HashSet<Song>();
songSet.addAll(songList);
System.out.println(songSet);
{% endhighlight %}

依然有重复，而且顺序又乱了。这里我们讨论一个问题：对象怎样才算相等（重复）？于是引出了“引用相等性”和“对象相等性”。

**引用相等性** 这个很好说明，也就是两个引用指向同一个对象，对两个引用调用`hashCode()`将得到同一个结果。可以用`==`来判断是否相等。

**对象相等性** 指两个对象的意义是相同的，但很明显，它们在内存中是两个。如果你希望把两个不同的`Song`视为相等，那么需要覆盖它们从`Object`继承下来的`equals()`和`hashCode()`方法，使得它俩都返回`true`，即如下：

```
if(foo.equals(bar) && foo.hashCode() == bar.hashCode()){}
```

`HashSet`就是用对象的`hashCode()`来检查重复的。如果不同，则当做新对象加入，如果相同，接着调用`equals()`来进一步检查。如果`add()`方法返回`false`，那么说明新对象与集合中某项目被认为是重复的。

所以我们给`Song`重写两个方法：

{% highlight java %}
public boolean equals(Object aSong){
	Song s= (Song)aSong;
	return this.getTitle().equals(s.getTitle());
}
public int hashCode(){
	return title.hashCode();
}
{% endhighlight %}

OK.解决掉重复问题了。

注意，具有相同的`hashcode`的两个对象不一定相等，但是两个对象相等则它们的`hashcode`一定相同（存在`hash碰撞`问题）。如果`equals()`被覆盖过，那么`hashCode()`也必须被覆盖。`equals()`默认行为是`==`比较。

**TreeSet** 它在防止重复方面和`HashSet`相同，但却可以保持有序。用法与上面的`HashSet`代码一样。要注意的是，由于`TreeSet`具有默认排序功能，所以要么你需要在被添加元素上实现`Comparable`并实现`compareTo()`方法，要么你需要实现一个`Comparator`并把它的一个对象作为参数传给重载版的构造函数：`TreeSet<Book>(bCompare)`。

下面，我们来玩一玩`Map`。有时候`Map`才是最好的选择。

`Map`中的值可以重复，关键字不行。

举例：

{% highlight java %}
public class TestMap{
    public static void main(String[] args){
        HashMap<String, Integer> scores = new HashMap<String, Integer>();
        scores.put("Kathy", 42);
        scores.put("Bert", 343);
        System.out.println(scores);
        System.out.println(scores.get("Bert"));
    }   
}
{% endhighlight %}

**再次回到泛型**

我们知道如果方法的参数是`Animal`的数组，那么也可以传入`Animal`子类型，如`Dog`的数组，如下：

{% highlight java %}
public void go(){
	Animal[] animals = {new Dog(), new Cat(), new Dog()};
	Dog[] dogs = {new Dog(), new Dog()};
	takeAnimals(animals);
	takeAnimals(dogs);
}
public void takeAnimals(Animal[] animals){
	for(Animal a: animals){
		a.eat();
	}
}
{% endhighlight %}

但是如果换成`ArrayList`：

{% highlight java %}
public void go(){
	ArrayList<Animal> animals = new ArrayList<Animal>();
	animals.add(new Dog());
	animals.add(new Cat());
	takeAnimals(animals);
}
public void takeAnimals(ArrayList<Animals> animals){
	for(Animal a: animals){
		a.eat();
	}
}
{% endhighlight %}

这样是可以的。但如果我们在`go()`中加入下面的语句：

```
ArrayList<Dog> dogs = new ArrayList<Dog>();
dogs.add(new Dog());
takeAnimals(dogs);
```

这样编译时会出错。因为如果你在`takeAnimals`中做了`animals.add(new Cat());`这样岂不是就是把猫扔到狗群里了？所以出现`ArrayList<Animal>`的地方传入`ArrayList<Dog>`不行。事实上，对于数组来说也存在这个问题，但是数组的类型是在运行时检查的，而集合的类型检查在编译期。（也就是说，如果你对数组这样做，在运行期间会报错）

**然而我们说，路往往不止一条（卡塞尔学院录取路明非时候貌似也是这么说的）。**

有个叫做`万用字符（wildcard）`的东西，可以用来创建接收`Animal`子型参数的方法：

{% highlight java %}
public void takeAnimals(ArrayList<? extends Animal> animals){
	for(Animal a: animals){
		a.eat();
	}
}
{% endhighlight %}

上面的`extends`同事代表`继承`和`实现`。

为了保障安全，编译器允许你操作几何元素，但不允许你新增集合元素。

我们之前在对于`sort()`关于泛型的讨论时提到了另一种写法：

```
public <T extends Animal> void takeThing(ArrayList<T> list)
```

这与

```
public void takeThing(ArrayList<? extends Animal> list)
```

是等价的。

如果某个方法需要多个泛型的参数，那么第一个方法写起来显然省力一些。

### 2017-03-21

#### 发布程序

跳过一章，先到这里。

##### 本机部署

首先，要养成良好的开发习惯，开发时建立如下目录：

```
-myProject
  -source
  -classes
```

在`source`中存放源码，编译时指定输出：`javac -d ../classes *.java`。
要执行程序，就进入`classes`目录执行`java MyApp`。

进入正题。

###### Executable Jar

`JAR`就是`Java ARchive`的意思，它是一个`pkzip`格式的文件，交付时只用交付一个`JAR`就好。我们提到全大写的`JAR`意思是说集合起来的文件，全小写的`jar`是用来整理文件用的工具。`JAR`文件可执行，程序可以在类文件保存在`JAR`的情况下执行。秘诀在于`manifest`带有`JAR`的信息，来告诉`Java虚拟机`那个类带有`main()`方法。

下面我们来创建可执行的`JAR`：

首先要确定所有类文件都在`classes`目录下；  
接着在该目录下创建`manifest.txt`描述哪个类中带有`main()`方法：

```
Main-Class: MyApp

```

如上，第一行后面要有换行；  
最后使用`jar`来创建：

```
jar -cvmf manifest.txt app1.jar *.class
```

执行`JAR`：

```
java -jar ./app1.jar
```

下面的命令分别可以列出`JAR`中的文件组织架构/解压文件：

```
jar -tf ./app1.jar
jar -xf ./app1.jar
```

**把类包进包里**

写出可重复使用的类时，你会把它们放到内部的函数库给其他程序员使用。为了防止命名冲突，也为了规范和整齐，你应该把类文件放在`package`中。

为了防止`package`也命名冲突，我们可以采用`Sun`建议的命名规则：加上你的域名，并且反向使用域名。例如我有一个类是`Chart`，我的域名是`brant_ruan.com`。那么我的包名就可以是`com.brant_ruan.Chart`，我需要在每个属于这个包的`.java`文件第一行写上

```
package com.brant_ruan;
```

注意，你需要在`source`目录下建立对应的文件夹`mkdir -p ./com/brant_ruan`并且把`Chart.class`文件放进去。之后在`source`目录下使用命令`javac -d ../classes com/brant_ruan/Chart.java`。你不必在`../classes`目录下也建立相同的目录架构，因为`javac`的`-d`选项会自动帮你完成这件事。

如果你要直接执行类文件，则需要进入`classes`目录下，`java com.brant_ruan.Chart`。

为了创建可执行`JAR`，你需要在`classes`目录下的`manifest.txt`中写入：

`Main-Class: com.brant_ruan.Chart`

然后`jar -cvmf manifest.txt app1.jar com`。

你的`manifest`文件内容信息会被写入`JAR`中的`META-INF/MANIFEST.MF`中。`META-INF`代表`META INFormation`。

###### 半本机半远程 Java Web Start

JWS -- Java Web Start

用户首次通过点网页上的链接来启动 JWS ，之后一旦程序下载后，它就能独立于浏览器之外执行。当然，客户端要有`Java`和`JWS`环境。

工作方式：

- 客户点击某个链接

```
<a href="MyApp.jnlp">Click</a>
```

- 服务器收到请求发出`.jnlp`给浏览器（它是个描述`JAR`的`XML`文件）
- 浏览器启动`JWS`，`JWS`的`helper app`读取`.jnlp`，向服务器请求`MyApp.jar`
- 服务器发送`.jar`文件
- `JWS`取得`JAR`并调用指定的`main()`来启动程序

创建/部署`JWS`的步骤：

- 将程序制成`JAR`
- 编写`.jnlp`
- 把`JAR`和`.jnlp`放到服务器目录下
- 对服务器设定新的`MIME`类型`application/x-java-jnlp-file`
- 设定超链接到`.jnlp`文件

`JWS`与`applet`的不同：`applet`无法独立于浏览器之外，是网页的一部分。

### 2017-03-21

【学习不可半途而废，就像长跑，需要专注与坚持】

#### 多线程并发

下面我们要写出一个“可发送，可接收”的客户端。问题在于，怎么接收服务器发送的信息？轮询？注意目前只有一个线程！

`Thread`是 Java 中用来标识线程的类，要建立线程就得创建`Thread`。每个 Java 应用程序会启动一个主线程——将`main()`放在执行空间的开始处。

常用方法：

|Thread|
|:-:|
|void join()|
|void start()|
|static void sleep()|

如何启动新的线程？

- 建立`Runnable`对象作为线程的任务
- 建立`Thread`对象并赋值`Runnable`任务
- 启动`Thread`

`Runnable`是一个接口。线程的任务可以被定义在任何实现`Runnable`接口的类上，该类需要实现接口的`run()`方法，且类型必须是`public void`，`run()`方法将作为线程任务的入口。一旦`start()`，线程就处于`可执行`/`执行中`/`阻塞中`的交替中。每个线程都有独立的执行空间。

例子：

{% highlight java %}
public class MyRunnable implements Runnable{
	public void run(){
		go();
	}
	public void go(){
		doMore();
	}
	public void doMore(){
		System.out.println("top on the stack");
	}
}
class ThreadTester{
	public static void main(String[] args){
		Runnable threadJob = new MyRunnable();
		Thread myThread = new Thread(threadJob);
		myThread.start(); // means the thread is OK
		System.out.println("back in main");
	}
}
{% endhighlight %}

**程序设计新手会在单一的机器上测试多线程程序，并假设其他机器的调度器都有相同行为。**

另外一种创建线程的方法：不使用`Runnable`，而是用`Thread`的子类覆盖掉`run()`方法，并调用`Thread`的无参构造函数来创建出新线程。但这通常不是个好主意（另一种设计理念）。

一旦线程的`run()`完成后，线程就不能再重新启动。

`Thread.sleep(2000)`可以让线程小睡。它可能抛出`InterruptedException`，所以要放在`try/catch`块中。

线程可以有名字。我们可以用名字来区别线程：

{% highlight java %}
public class RunThreads implements Runnable{
	public static void main(String[] args){
		RunThreads runner = new RunThreads();
		Thread alpha = new Thread(runner);
		Thread beta = new Thread(runner);
		alpha.setName("Alpha thread");
		beta.setName("Beta thread");
		alpha.start();
		beta.start();
	}
	public void run(){
		for(int i = 0; i < 25; i++){
			String threadName = Thread.currentThread().getName();
			System.out.println(threadName + " is running");
		}
	}
}
{% endhighlight %}

下面讨论多线程并发的通病：`race condition`（Linux 内核因为竞争条件爆了不少高危提权漏洞，呃，你知道筛子长什么样吗？）

对于临界资源的使用，其操作必须是原子操作，满足不同线程之间的互斥关系，否则会因为竞争条件导致结果与期望不一致。我们只需要给方法加上`synchronized`标识，它每次就只能位于单一线程的执行空间内。每个对象都有一个锁，大部分时间都没有锁上。锁不是配在方法上，而是配在对象上。线程只有获得钥匙，才能够进入对象的方法。一个对象可能有多个同步化方法，但是只有一个锁。一旦一个线程进入某个同步化方法，其他线程都无法再进入该对象的任何同步化方法。

[这里]({{ site.url }}/resources/code/RyanAndMonicaJob.java)有一个竞争条件的形象化例子：两个人共享一个银行账户，都是先检查账户余额，再睡觉，睡一觉起来去取钱，两个人生活节奏不同导致一个人检查发现账户余额可用时一觉起来去取钱时发现钱没了。

如果仅仅是某个方法内部的某些操作需要原子化，我们可以使用下面的：

```
public void go(){
	doOthers();
	synchronized(this){
		i = balance;
		balance = i + 1;
	}
}
```

**然而，同步可能导致死锁！**

另外，类本身也有锁。这意味着，如果某个类有被同步化过的静态方法且它会操作这个类的静态变量，那么线程也需要取得类的锁才可以进入该方法。

好了。利用多线程，我们可以写出能够同时接受信息/发出信息的[客户端]({{ site.url }}/resources/code/SimpleChatClient.java)，服务端使用[之前的]({{ site.url }}/resources/code/VerySimpleChatServer.java)就可以,其实客户端也就是在之前的基础上添加了几行代码：

{% highlight java %}
// go() 中
Thread readerThread = new Thread(new IncomingReader());
readerThread.start();
// 在 SimpleCharClient 中新增一个内部类
public class IncomingReader implements Runnable{
	public void run(){
		String message;
		try{
			while((message = reader.readLine()) != null){
				System.out.println("read " + message);
				incoming.append(message + "\n");
			}
		}
		catch(Excetion ex){
			ex.printStackTrace();
		}
	}
}
{% endhighlight %}

上面提到的服务端程序也使用了多线程。主线程在一个`while`循环中`accept`并分配子线程去做接收信息和广播某个客户端消息的工作。

注：Java 中`args[0]`指的是你传入的第一个参数，与 C 不同。

P.S. 有一个 *Head First Java* 上的`BeatBox`最终版，很有意思，可以多人共享自己制作的节奏：

- [客户端]({{ site.url }}/resources/code/BeatBoxFinal.java)
- [服务端]({{ site.url }}/resources/code/MusicServer.java)

另外，书中习题有一段有意思的代码，它将构造函数私有化，并自己创建一个静态对象，其他类只能够通过它提供的方法获得这个对象。这样保证了整个程序中只能有一份实例：

{% highlight java %}
class Accum{
	private static Accum a = new Accum();
	private int counter = 0;
	private Accum(){} // private construct function
	public static Accum getAccum(){
		return a;
	}
	...
}
{% endhighlight %}

### 2017-03-08

#### 网络编程

我们要用到`java.net.Socket`。

使用`BufferedReader`从`Socket`上读取数据，使用`PrintWriter`向`Socket`上写数据。数据流如下：

```
Client <- BufferedReader <- InputStreamReader <- Socket <- Server
Client -> PrintWriter -> Socket -> Server
```

`InputStreamReader`是低层串流与高层串流之间的桥梁，`PrintWriter`是字符数据与字节之间的转换桥梁。

下面是一个简单的“建议小程序”。客户端连接到服务端获取每日建议并打印：

{% highlight java %}
// Client
import java.io.*;
import java.net.*;

public class DailyAdviceClient{
	public void go(){
		try{
			Socket s = new Socket("127.0.0.1", 4242);

			InputStreamReader streamReader = new InputStreamReader(s.getInputStream());
			BufferedReader reader = new BufferedReader(streamReader);

			String advice = reader.readLine();
			System.out.println("Today you should: " + advice);

			reader.close();
		}
		catch(IOException ex){
			ex.printStackTrace();
		}
	}

	public static void main(String[] args){
		DailyAdviceClient client = new DailyAdviceClient();
		client.go();
	}
}
{% endhighlight %}

{% highlight java %}
// Server
import java.io.*;
import java.net.*;

public class DailyAdviceServer{
	String[] adviceList = {"Take smaller bites",
		"Go for the tight jeans. No they do NOT make you look fat.", 
		"One word: inappropriate", "Just for today, be honest. Tell your boss what you *really* think",
		"You might want to rethink that haircut."};
	
	public void go(){
		try{
			ServerSocket serverSock = new ServerSocket(4242);
			while(true){
				Socket sock = serverSock.accept();

				PrintWriter writer = new PrintWriter(sock.getOutputStream());
				String advice = getAdvice();
				writer.println(advice);
				writer.close();
				System.out.println(advice);
			}
		}
		catch(IOException ex){
			ex.printStackTrace();
		}
	}

	private String getAdvice(){
		int random = (int)(Math.random() * adviceList.length);
		return adviceList[random];
	}

	public static void main(String[] args){
		DailyAdviceServer server = new DailyAdviceServer();
		server.go();
	}
}
{% endhighlight %}

这与我们的第一个 C 语言版服务端一样，同一时间只能够为一个用户服务。

下面是一个简单聊天客户端的示例： [SimpleChatClientA]({{ site.url }}/resources/code/SimpleChatClientA.java)，服务端在[这里]({{ site.url }}/resources/code/VerySimpleChatServer.java)。

### 2017-03-07

#### 保存对象

对象是可以被序列化也可以被展开的。储存对象的状态有很多选择，后面将讨论两种方法：

- serialization 序列化

即，将被序列化的对象写入文件中，然后可以让你的程序从文件中读取序列化的对象，并把它们展开。条件是只有你自己写的程序会用到这些数据。

- 写入一个纯文本文件

用其他程序可以解析的特殊字符写到文件中。比如写成用`tab`字符分隔的形式。如果要让类能够被序列化，就要实现`Serializable`接口（但是这个接口又没有任何方法需要被实现，属于标记用接口）。

##### 对象序列化与反序列化

{% highlight java %}
import java.io.*;
public class Box implements Serializable{
	private int width;
	private int height;
	
	public void setWidth(int w){
		width = w;
	}
	public void setHeight(int h){
		height = h;
	}
	public static void main(String[] args){
		Box myBox = new Box();
		myBox.setWidth(50);
		myBox.setHeight(20);
		
		try{
			FileOutputStream fs = new FileOutputStream("foo.ser");
			ObjectOutputStream os = new ObjectOutputStream(fs);
			os.writeObject(myBox);
			os.close();
		}
		catch(Exception ex){
			ex.printStackTrace();
		}
	}
}
{% endhighlight %}

当对象被序列化时，它引用的实例变量也会被序列化，且所有被引用的对象也会被序列化。序列化是全有或者全无的，整个对象版图都必须正确地序列化，不然就得全部失败。例如，`Pond`类有一个对`Duck`类的引用，但`Duck`没有实现`Serializable`接口，那么`Pond`也不能序列化。

如果某示例变量不能或者不应该被序列化，就该把它标记为`transient`（瞬时）的。这时如果你序列化对象，被标记的引用实例变量就会返回`null`。

如果两个对象都有引用实例变量指向相同的对象，那么那个对象只会被存储一次。

Deserialization 解序列化：

{% highlight java %}
// 1
FileInputStream fileStream = new FileInputStream("MyGame.ser");
// 2
ObjectInputStream os = new ObjectInputStream(fileStream);
// 3
Object one = os.readObject();
Object twp = os.readObject();
Object three = os.readObject();
// 4
GameCharacter elf = (GameCharacter)one;
GameCharacter troll = (GameCharacter)two;
GameCharacter magician = (GameCharacter)three;
// 5
os.close();
{% endhighlight %}

正常情况下，新的对象的构造函数不会执行。但是如果该对象在继承树上有一个不可序列化的祖先类，那么从该不可序列化的祖先类往上的所有类的构造函数都会执行。

静态变量不会被序列化，因为它们属于类而不是单个对象。

**Java Deserialization Vulneribility**

【留坑】

http://www.tuicool.com/articles/ZvMbIne  
http://www.freebuf.com/vuls/90840.html

##### 写入文本文件

注意输入输出相关的操作都要包含在`try/catch`块中。

{% highlight java %}
import java.io.*;

class WriteAFile{
	public static void main(String[] args){
		try{
			FileWriter writer = new FileWriter("Foo.txt");
			writer.write("Hello foo!");
			writer.close();
		}
		catch(IOException ex){
			ex.printStackTrace();
		}
	}
}
{% endhighlight %}

下面通过一个`e-Flashcard`的程序来学习文本文件的处理，同时学习`GUI`中从目录中选择文件的方法，具体代码见[此处]({{ site.url }}/resources/code/QuizCard.tar.gz)，这里仅仅列出值得学习的地方:

- GUI`Menu`的添加方法
- GUI调用存盘和打开文件的对话框

**java.io.File 类**

`File`类代表磁盘上的文件，但并非文件的内容。可以把它想象成文件的路径，而非文件本身。`File`并没有读写文件的方法，但它有一个很有用的功能，即它提供一种比使用字符串文件名来表示文件更安全的方式。

你可以对`File`对象做一些事情：

- 创建代表现存盘文件的对象

```
File f = new File("MyCode.txt");
```

- 建立新目录

```
File dir = new File("Chapter7");
dir.mkdir();
```

- 列出目录下内容

```
if(dir.isDirectory()){
	String[] dirContents = dir.list();
	for(int i = 0; i < dirContents.length; i++){
		System.out.println(dirContents[i]);
	}
}
```

- 取得文件或目录的绝对路径

```
System.out.println(dir.getAbsolutePath());
```

- 删除文件或目录

```
boolean isDeleted = f.delete();
```

另外，使用缓冲区比不使用缓冲区更好（更有效率）：

{% highlight java %}
private void saveFile(File file){
	try{
		BufferedWriter writer = new BufferedWriter(new FileWriter(file));
		writer.write(card.getQuestion());
		writer.write(card.getAnswer());
		writer.close();
	}
	catch(IOException ex){
		...
	}
}
{% endhighlight %}

这样只有在缓冲区满时才会写入磁盘，你也可以调用`writer.flush()`强制写入。

##### 读取文本文件

{% highlight java %}
import java.io.*;

class ReadAFile{
	public static void main(String[] args){
		try{
			File myFile = new File("MyText.txt");
			FileReader fileReader = new FileReader(myFile);
			BufferedReader reader = new BufferedReader(fileReader);
			String line = null;
			while((line = reader.readLin()) != null){
				System.out.println(line);
			}
			reader.close();
		}
		catch(Exception ex){
			ex.printStackTrace();
		}
	}
}
{% endhighlight %}

`String`的`split()`可以把字符串拆开。  
用到`String`文件名的串流大部分可以用`File`对象来替代`String`。  
使用`BufferedReader`配合`FileReader`以及`BufferedWriter`配合`FileWriter`都会很有效率。

**serialVersionUID**

对象被序列化时，该对象都会带有一个该类的版本识别ID。在反序列化时， Java 会对比它与虚拟机上的ID，如果不同，则还原操作会失败。但是你可以控制这件事情，即把`serialVersionUID`放在类中，让类在演化的过程中还维持相同的ID。方法是对类使用`serialver`工具获得它的ID，然后放到类中：

```
// e.g.
// in Command line
serialver Dog
// then
public class Dog{
	static final long serialVersionUID = ....;
}
```

这章对上一章的`BeatBox`程序做了升级，添加了存储节奏和还原节奏的功能，原理就是对象的序列化和反序列化，代码见[此处]({{ site.url }}/resources/code/BeatBoxSaveOnly.java)。

### 2017-03-06

#### Swing

所有组件都继承于`javax.swing.JComponent`。`Swing`中几乎所有组件都能够安置其他组件。但一般我们会把按钮等组件放在框架或面板上而不是反过来。

布局管理器（`Layout Managers`）是与特定组件相关联的对象，用来控制所关联组件上携带的其他组件。

三大管理器：

- BorderLayout

这就是我们之前用到的管理器，它是**框架**默认的布局管理器。如同之前提到的，它会把背景组件分为 5 个区域，所以被安置的组件一般不会取得默认的大小。

- FlowLayout

它是**面板**默认的布局管理器，它会把每个组件都按照理想大小呈现，并按从左到右依次加入且可能换行的规则去排列。

- BoxLayout

同`FlowLayout`，它让组件使用默认大小，并按照加入顺序排列，但BoxLayout通常以垂直方向排列组件。它不会自动换行，你需要插入某种类似换行的机制来强制换行。

`BorderLayout`类在`java.awt`包中。

下面的例子中，`BorderLayout`处理`button`尺寸的方式如下：

```
frame.getContentPane().add(BorderLayout.EAST, button);
```

[1] 询问按钮它的理想尺寸。
[2] 按钮在东边，所以管理器认可按钮的宽度，但高度要和它依附的组件一样；如果按钮在北边，则默认认可按钮的高度。在东边时，按钮使用更大的字体会把自己撑宽。
[3] 对于中间区域来说，它会在南北扣除预设高度，东西扣除预设宽度后看剩下什么。

把面板的布局管理器从默认的`FlowLayout`改为`BoxLayout`:

```
panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
```

下列`Swing`组件不再具体说明，使用时参考文档即可（或许你不怎么会用代码来构图）：

- JTextField
- JTextArea
- JCheckBox
- JList

在这个部分 *Head First Java* 有一个 BeatBox 的 GUI 作品，书上的代码见[此处]({{ site.url }}/resources/code/BeatBox.java)。

### 2017-03-05

#### GUI

一切从`window`开始，`JFrame`是一个代表它的对象，各种`widget`添加在上面。`widget`通常在`javax.swing`包中。最常用的如`JButton`/`JRadioButton`/`JCheckBox`/`JLabel`/`JList`/`JScrollPane`/`JSlider`/`JTextArea`/`JTextField`/`JTable`等。

{% highlight java %}
import javax.swing.*;

public class SimpleGui1{
	public static void main(String[] args){
		// create frame
		JFrame frame = new JFrame();
		// create widget
		JButton button = new JButtion("click me");
		// to kill program when window turned off
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		// add widget to frame
		frame.getContentPane().add(button);
		// set size of frame
		frame.setSize(300, 300);
		// make frame visible
		frame.setVisible(true);
	}
}
{% endhighlight %}

接着，我们希望在用户按下按钮时做出相应动作。此时，`button`是事件源，我们要实现监听接口。这样，在相关事件源发生相关事件时，我们相关的处理方法就会被调用。

如下，取得`button`的`ActionEvent`我们需要：

- 实现`ActionListener`接口
- 向`button`注册（告诉它你要监听事件）
- 定义事件的处理方法（也就是把接口的方法实现）

{% highlight java %}
import javax.swing.*;
import java.awt.event.*;

public class SimpleGui1B implements ActionListener{
	JButton button;
	public static void main(String[] args){
		SimpleGui1B gui = new SimpleGui1B();
		gui.go();
	}
	public void go(){
		JFrame frame = new JFrame();
		button = new JButton("click me");
		// sign up
		button.addActionListener(this);
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.getContentPane().add(button);
		frame.setSize(300, 300);
		frame.setVisible(true);
	}
	public void actionPerformed(ActionEvent event){
		button.setText("I've been clicked!");
	}
}
{% endhighlight %}

**通过查询 Java API 手册可以得知某个对象是哪些事件的来源。可以看以`add`开头，`Listener`结尾且取用`listener`接口参数的方法。比如上面的`button.addActionListener(this)`，就说明按钮是`Action`事件的来源。**

在 GUI 上添加东西的三个方法：

- 在`frame`上放置`widget`

```
frame.getContentPane().add(myButton);
```

- 在`widget`上绘制 2D 图形

```
graphics.fileOval(70, 70, 100, 100);
```

- 在`widget`上绘制 JPEG 图

```
Image image = new ImageIcon("FILEPATH".getImage());
graphics.drawImage(image, 10, 10, this);
```

**自己创建绘图组件**

在屏幕上放自己的图形，最好的方式是自己创建出有绘图功能的`widget`。把`widget`放在`frame`上，很简单。如下，创建`JPanel`的子类，并覆盖掉它的`paintComponent()`，所有的绘图程序代码都放在这个方法里面。这个方法不是你自己调用的，它的参数是跟实际屏幕有关的`Graphics`对象，你无法取得这个对象，它必须由系统交给你。然而，你可以通过调用`repaint()`来要求系统重新绘制显示装置，之后会它会调用你的`paintComponent()`。

{% highlight java %}
// draw circle with random colors on black background
import java.awt.*;
import javax.swing.*;

class MyDrawPanel extends JPanel{
	public void paintComponent(Graphics g){
		g.fillRect(0, 0, this.getWidth(), this.getHeight());

		int red = (int)(Math.random() * 255);
		int green = (int)(Math.random() * 255);
		int blue = (int)(Math.random() * 255);

		Color randomColor = new Color(red, green, blue);
		g.setColor(randomColor);
		g.fillOval(70, 70, 100, 100);
	}
}
{% endhighlight %}

上面例子中参数`g`引用的实际上是`Grahpics2D`类的实例，由于多态，这样是可以的。但另一方面，这个引用也会限制你只能调用属于`Graphics`类的方法。我们可以把它转换为`Graphics2D`来使用新方法（下面的功能是画渐变色圆）：

{% highlight java %}
public void paintComponent(Graphics g){
	Graphics2D g2d = (Graphics2D)g;
	GradientPaint gradient = new GradientPaint(70, 70, Color.blue, 150, 150, Color.orange);
	g2d.setPaint(gradient);
	g2d.fillOval(70, 70, 100, 100);
}
{% endhighlight %}

讨论一下`frame`的布局：  
一个`frame`默认有 5 个区域来安置`widget`。

|north|north|north|
|:-:|:-:|:-:|
|west|center|east|
|south|south|south|

下面的代码会画一个按钮和一个圆圈，按下按钮就会改变圆圈的颜色：

{% highlight java %}
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;

public class SimpleGui3C implements ActionListener{
	JFrame frame;
	public static void main(String[] args){
		SimpleGui3C gui = new SimpleGui3C();
		gui.go();
	}
	public void go(){
		JButton button = new JButton("change colors");
		button.addActionListener(this);
		frame = new JFrame();
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		MyDrawPanel drawPanel = new MyDrawPanel();
		frame.getContentPane().add(BorderLayout.SOUTH, button);
		frame.getContentPane().add(BorderLayout.CENTER, drawPanel);
		frame.setSize(300, 300);
		frame.setVisible(true);
	}
}
{% endhighlight %}

现在我们尝试使用两个按钮，一个同上面的相同，用于控制圆圈的颜色；新增一个`label`，用一个新增的按钮来控制这个`label`文字的改变。我们目前只有一个`SimpleGui3C`实现了一个监听器，但现在需要两个监听器对两个按钮进行监听。根据需求，我们引入**内部类**。顾名思义，内部类就是指一个类嵌套在另一个类内部。内部的类可以自由调用或存取它的外部类的方法或变量。一般我们在外部类的方法中实现内部类的实例化（即`new`一个内部类对象），当然你也可以通过`Outer.Inner`的方法从外部类以外的程序代码来创建内部类实例，但这并不常用。

借助内部类，实现一个类内部多个监听器：

{% highlight java %}
public class TwoButtons{
	JFrame frame;
	JLabel label;
	public static void main(String[] args){
		TwoButtons gui = new TwoButtons();
		gui.go();
	}
	public void go(){
		frame = new JFrame();
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		
		JButton labelButton = new JButton("Change Label");
		labelButton.addActionListener(new LabelListener());
		
		JButton colorButton = new JButton("Change Circle");
		colorButton.addActionListener(new ColorListener());
		
		label = new JLabel("I'm a label");
		MyDrawPanel drawPanel = new MyDrawPanel();
		
		frame.getContentPane().add(BorderLayout.SOUTH, colorButton);
		frame.getContentPane().add(BorderLayout.CENTER, drawPanel);
		frame.getContentPane().add(BorderLayout.EAST, labelButton);
		frame.getContentPane().add(BorderLayout.WEST, label;
		frame.setSize(300, 300);
		frame.setVisible(true);
	}
	
	class LabelListener implements ActionListener{
		public void actionPerformed(ActionEvent event){
			label.setText("Ouch!");
		}
	}
	class ColorListener implements ActionListener{
		public void actionPerformed(ActionEvent event){
			frame.repaint();
		}
	}
}
{% endhighlight %}

```
// sleep for 1 second
Thread.sleep(1000) 
```

### 2017-03-03

#### 异常处理

如果某个方法的声明语句中包含`throws`语句，它就会在某些条件下抛出异常。所有异常都是`Exception`或者其子类的对象。除了`RuntimeException`和它的子类外，编译器会要求：

1. 如果你有抛出异常，一定要用`throw`来声明；
2. 如果你调用会抛出异常的方法，你必须通过`try/catch`或再次抛出异常来通过编译。

{% highlight java %}
// e.g. throw
public void takeRisk() throws BadException{
	if(abandonAllHope){
		throw new BadException();
	}
}
{% endhighlight %}

{% highlight java %}
// e.g. try/catch/finally
import javax.sound.midi.*;
public class MusicTest1{
	public void play(){
		try{
			Sequencer sequencer = MidiSystem.getSequencer();
			System.out.println("Successfully got a sequencer");
		}
		catch(MidiUnavaiableException ex){
			System.out.println("Bummer");
		}
		finish{
			System.out.println("finish");
		}
	}
	public static void main(String[] args){
		MusicTest1 mt = new MusicTest1();
		mt.play();
	}
}
{% endhighlight %}

`finally`块存放无论是不是有异常都要执行的程序。如果`try`或`catch`中有`return`指令，则在`return`前会先执行`finally`块内指令再`return`。

处理多重异常时最好分开单独`catch`，有多个`catch`块时要从小排到大（如果这些异常类之间有继承关系的话）。

不想处理异常的话你可以把它再次抛给你的调用方，但最终总要有程序处理，否则就是`Java虚拟机`的结束。

{% highlight java %}
public class Washer{
	Laundry laundry = new Laundry();
	public void foo() throws ClothingException{
		laundry.doLaundry();
	}
	public static void main(String[] args) throws ClothingException{
		Washer a = new Washer();
		a.foo();
	}
}
{% endhighlight %}

最后：

- catch 与 finally 不能没有 try
- try 与 catch 之间不能有程序
- try 一定要有 catch 或 finally
- 只带有 finally 的 try 必须声明异常

### 2017-03-02

#### 继承与构造函数

每个父类都有一个构造函数，每个构造函数都会在子类对象创建时期执行。在子类构造函数中调用父类构造函数，即`Constructor Chaining`。子类向上递归调用父类构造函数，一层一层直到`Object`。

在自己的构造函数中手动调用父类构造函数，父类构造函数一定要是子类构造函数中的第一句指令：

```
public class Duck extends Animal{
	int size;
	public Duck(int newSize){
		super();
		size = newSize;
	}
}
```

即使不自己手动调用，编译器也会帮你加上一个父类无参的构造函数。

如果某子类有多个构造函数（重载），而且它们只是参数类型不同，那么可以把代码都放到一个构造函数中，在其他构造函数中调用`this()`，`this()`和`super()`都要求出现在构造函数第一行，所以它俩不可同时存在：

```
class Mini extends Car{
	Color color;
	public Mini(){
		thie(Color.Red);
	}
	// main constructor
	public Mini(Color c){
		super("Mini");
		color = c;
	}
	public Mini(int size){
		this(Color.Red);
	}
}
```

**构造函数的公私有问题**

【留坑】

**对象的生命周期**

对象生命周期由它的引用变量决定，继而由它的引用变量是局部变量还是实例变量决定，实例变量的寿命与其所属对象相同。

**静态/非静态方法**

调用对象的静态方法不要求创建对象，因为静态方法不依赖于对象的实例变量，如`Math.round()`可直接使用（事实上，由于`Math`类的构造函数被标记为`private`，你也无法创建它的对象，即，除了通过把类标识为`abstract`来防止它被初始化外，你也可以把它的构造函数标记为`private`来达到目的）。静态方法通过类名来执行。

**静态变量**

被某个类的所有实例共享的量。**静态变量在该类任何对象创建之前或它的任何静态方法执行之前就完成初始化。**静态变量通过类名来存取。静态方法可以存取静态变量。

**final**

- final 变量的值不能被改变（常数），一般都用大写字母表示
- final 的方法说明你不能覆盖它
- final 的类说明你不能继承它

静态初始化程序很适合放`static final`变量的初始化程序：

```
class Foo{
	final static int x;
	static{
		x = 42;
	};
}
```

|Math|
|:-:|
|Math.random()|
|Math.abs()|
|Math.round()|
|Math.min()|
|Math.max()|

#### primitive 主数据类型的包装

在 5.0 版本之前，你无法直接把`primitive`主数据类型放进`ArrayList`或`HashMap`中，需要包装成类：

```
Boolean Character Byte
Short Integer Long
Double Float
// Wrap
int i = 288;
Integer iWrap = new Integer(i);
// Unwrapp
int unWrapped = iWrap.intValue();
```

5.0 版本开始加入`autoboxing`功能，自动将主数据类型转换为包装后的对象：

```
ArrayList<Integer> listOfNumbers = new ArrayList<Integer>();
listOfNumbers.add(3);
```

一个编译通过，但会出运行时错误的程序：

```
public class TestBox{
	Integer i;
	int j;
	public static void main(String[] args){
		TestBox t = new TestBox();
		t.go();
	}
	public void go(){
		j = i;
		System.out.println(j);
		System.out.println(i);
	}
}
```

上例中，由于`Integer i`并未`new`，所以它是`null`，所以运行时`j = i`会出错。

包装的一些常用方法：

```
String s = "2";
int x = Integer.parseInt(s);
double d = Double.parseDouble("420.24");
boolean b = new Boolean("true").booleanValue();
// to string
double d = 42.5;
String doubleString = "" + d;
// or you can:
String doubleString = Double.toString(d);
```

#### 数字的格式化

5.0 开始，通过`java.util`中的`Formatter`类格式化。便利的是，已经可以通过调用静态的`String.format()`就可以格式化了：

```
public class TestFormats{
	public static void main(String[] args){
		String s = String.format("%,d", 1000000000);
		System.out.println(s);
	}
}
```

上面很像 C 语言中的格式化字符串，逗号是表示数字以逗号来分开。

**关于时间**

```
import java.util.Date;
...
// date and time
String.format("%tc", new Date());
// time
String.format("%tr", new Date());
```

要取得当前日期用`Date`，其余功能可以从`java.util.Calendar`上找。`Calendar`是个抽象类，所以不能取得它的实例。我们使用`getInstance()`返回一个它的子类的实例（一般是`java.utl.GregorianCalendar`）。

```
// obtain an object
Calendar cal = Calendar.getInstance();
cal.set(2004, 1, 7, 15, 40);
// millisecond
long day1 = c.getTimeInMillis();
// add an hour
day1 += 1000 * 60 * 60;
c.setTimeInMillis(day1);
```

更多可参考 Java API 手册。

**static import**

这是 5.0 的新功能。让你少打几个字。个人不推荐使用。

### 2017-03-01

之前说的`Animal`父类本身是没有意义的，没有一种叫做`Animal`的动物，只有它的子类时有意义的。所以`Animal`本身不可以被初始化，只有它的子类才可以。这样的类要标记为`抽象类`来防止它被初始化（`new`出来）：

```
abstract public class Animal{
...
}
abstract public class Canine extends Animal{
...
}
```

```
// 这不是在创建 Animal 对象
// 只是一个保存 Animal 的数组对象
private Animal[] animals = new Animal[5];
```

`方法`也可以标记为`abstract`，代表该方法一定要子类的方法被覆盖过才可以。另外，同为抽象类的子类不必覆盖抽象父类的抽象方法，向下继承直到一个具体类才需要覆盖抽象方法。当然，它也可以覆盖，这样它的子类就不必覆盖。

```
// 抽象方法没有实体，直接结束
// 抽象方法只能出现在抽象类中
public abstract void eat();
```

一方面，`动物`不是一个具体的生物，动物的进食也会千差万别，而例如`猫通过吃鱼进食`就都是具体的；另一方面，所有动物又几乎都要进食，所以为了多态性，把猫狗抽象为动物是合适的，把猫狗的进食抽象为动物的进食也是合适的。抽象又是相对而言的，如果某个程序只涉及到所有猫，但是又对不同种类的猫加以区别对待，则此时`猫`便成了抽象类。

Java 中`Ojbect`类是所有类的父类，你的类可以视为如下：

```
public class Dog extends Object{
...
}
```

|Object|
|:-:|
|boolean|
|equals()|
|Class getClass()|
|int hashCode()|
|String toString()|
|...|

HeadFirst 强烈建议使用自己的`equals()`/`hashCode()`/`toString()`覆盖原方法，但是其他有些方法标记了`final`是无法被覆盖的。

```
// o 是一个 Object 类型的引用，所以不能调用 Dog 类独有的方法
// d 则可以调用 Dog 类独有方法
Object o = new Dog();
Dog d = (Dog)o;
// 可以通过下面判断某个对象是否属于某个类型的实例
if(o instanceof Dog){
	Dog d = (Dog)o;
}
```

#### 接口 - interface

如果类 B/C/D/E 都继承自类 A，我们希望给 B/C 两个类加上一种方法，却不希望给 D/E 加上这个方法（换句话说， B/C 具有某种特性是 D/E 没有的）。所以，我们不能把这个方法放入类 A 中。然而， Java 中规定子类只能继承一个父类，所以也不能让 B/C 继承自另一个父类。这时候，我们使用接口，以此来继承`超过一个以上`的资源。

`接口`可以看做所有`方法`都是抽象方法的类。

```
// definition
public interface Pet{
...
}
// realization
public class Dog extends Canine implements Pet{
...
}
```

接口的方法直接会是`public`和`abstract`的，我们可写可不写。

Java 方法调用和局部变量生存在栈上，对象保存在堆上（实例变量保存在堆上）。即，如果局部变量是个对某对象的引用（非`primitive`的变量都是保存对某对象的引用），则变量本身在栈上，对象在堆上。对于实例变量来说，当它是某对象的引用时，如果仅仅是声明了变量但没有赋值：`private Antenna ant;`，则堆上不存在`Antenna`对象的空间，在`ant = new Antenna();`时堆上才会存在它的空间。

声明对象和赋值有三个步骤：

1. 声明引用变量
2. 创建对象
3. 连接对象和引用

`Duck myDuck = new Duck();`是在调用`Duck()`构造函数：

```
// 构造函数无返回类型
public Duck(){

}
```

构造函数往往用于初始化实例变量。构造函数不会被继承。给构造函数加上参数可以强制用户用特定值初始化对象。为了方便程序员，你可以写两个构造函数（重载），一个不带参数，你给出默认值；一个带参数，程序员初始化对象时给值。与`C++`相同，如果你写了一个带参数的构造函数，那么另一个不带参数的构造函数也需要你自己写，编译器不再为你保留原来的那个默认的构造函数。

### 2017-02-27

{% highlight java %}
public class Animal{
	public void overwrite(){
	
	}
	public void noOverwrite(){
	
	}
}
public class Lion extends Animal{
	public void overwrite(){
	
	}
	public void noOverwrite(){
		super.noOverwrite(); // here!
		...
	}
}
{% endhighlight %}

父类可以通过存取权限来限制子类：

`private`/`default`/`protected`/`public`

```
public 成员会被继承。
private 成员不会被继承。
当你定义处一组类的父型时，你可以用子类的任何类来填补任何需要或期待父型的位置。（多态）
所以通过声明为父型类型的对象引用来引用它的子型对象是可以的。
Animal myDog = new Lion();
```

```
三种让类不被继承的方法：
1. 不把类标记为公有，非公有类只能被同一个包的类继承；
2. 使用 final 修饰符，标识它是继承树末端，不能被继承（final也可以施加于某方法）；
3. 让类只拥有 private 的构造方法（暂时留坑）。
```

```
子类要覆盖父类的方法，则是否有参数，以及是否有返回值这些都要和父类方法相同，存取权限只能更开放不能更小。
重载与多态不同。重载要求使用不同参数，返回类型则可以自有定义。
子类只能继承于一个父类。
```

### 2017-02-26

#### 封装 - Encapsulation

不要暴露出实例变量，要让外部通过`Getter`方法来获取它，通过`Setter`方法来修改它：

```
class Test{
	private int size; // use 'private' to encapsulate it
	public int getSize(){ // Setter
		return size;
	}
	public void setSize(int s){ // Getter
		size = s;
	}
}
```

实例变量有默认值，但是局部变量必须初始化才可以使用。

使用`equals()`来判断两个对象在意义上是否相等。

```
& 和 | 在 boolean 表达式中将强制 Java 虚拟机计算运算符两边的算式而不是短路运算。
```

`java.lang`是基础包，不必指定名称；`import`只是帮你少写包名称而已。和C语言的`include`不同。

Java API 查询网站：  
http://docs.oracle.com/javase/1.5.0/docs/api/

### 2017-02-25

今日学习 Java 时有一个例子中有三个类分别是`GameLauncher`/`GuessGame`/`Player`。它们都属于`chap02`这个`package`，`GameLauncher`调用了`GuessGame`的方法，`GuessGame`调用了`Player`的方法。编译它们时需要退到上级目录中进行`javac chap02/GameLauncher.java`才能够编译成功。

另外，`main()`在真正的面向对象编程中只有两类用途：

- 测试真正的类
- 启动你的 Java 应用程序

任何类中的任何程序都可以存取`public static`的方法；任何变量只要加上`public`、`static`、和`final`基本上都会变成全局变量取用的常数。

数量庞大的分散文件可以打包进依据`pkzip`格式存档的`.jar`文件，其中引入了`manifest`这个文字格式的文件来定义`jar`中哪一个文件带有启动应用程序的`main()`方法。

Java primitive data type: `long`/`int`/`short`/`byte`/`boolean`/`char`/`float`/`double`

```
// c and d refer to the same object
Book c = new Book();
Book d = c;
// how to create an object array:
Dog[] pets;
pets = new Dog[7];
pets[0] = new Dog();
pets[1] = new Dog();
...
```