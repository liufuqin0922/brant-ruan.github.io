---
title: Java Notes
category: CS
---

## Java Notes

### 2017-03-02

**继承与构造函数**

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

被某个类的所有实例共享的量。静态变量在该类任何对象创建之前或它的任何静态方法执行之前就完成初始化。静态变量通过类名来存取。静态方法可以存取静态变量。

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

**primitive 主数据类型的包装**

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

**数字的格式化**


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

**接口 - interface**

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

封装 - Encapsulation

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