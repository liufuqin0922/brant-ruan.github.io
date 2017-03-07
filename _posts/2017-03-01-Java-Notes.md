---
title: Java Notes
category: CS
---

## Java Notes

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

另外，使用缓冲区比不适用缓冲区更好（更有效率）：

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
- 只带有 finally 的 try 必须生命异常

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