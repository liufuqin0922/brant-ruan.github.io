---
title: Bash Notes
category: Linux
---

## Bash Notes

> Yesterday you said tomorrow.

### 条件语句

注意`[]`内紧挨括号的空格，它们是必需的。

```
directory="./BashScripting"

# bash check if directory exists
if [ -d $directory ]; then
	echo "Directory exists"
else 
	echo "Directory does not exists"
fi 
```

嵌套：

```
choice=4
echo "1. Bash"
echo "2. Scripting"
echo "3. Tutorial"
echo -n "Please choose a word [1,2 or 3]? "
# Loop while the variable choice is equal 4
# bash while loop
while [ $choice -eq 4 ]; do
	read choice
# bash nested if/else
	if [ $choice -eq 1 ] ; then
		echo "You have chosen word: Bash"
	else
	    if [ $choice -eq 2 ] ; then
             echo "You have chosen word: Scripting"
   		else
   	        if [ $choice -eq 3 ] ; then
                echo "You have chosen word: Tutorial"
            else
                echo "Please make a choice between 1-3 !"
                echo "1. Bash"
                echo "2. Scripting"
                echo "3. Tutorial"
                echo -n "Please choose a word [1,2 or 3]? "
                choice=4
            fi   
        fi
	fi
done
```

总结一下，就是

```
if [ xxx ]; then
	...
else
	...
fi
```

谈到`if`就必须了解一下比较运算：

算数比较：

```
-lt <
-le <=
-gt >
-ge >=
-eq ==
-ne !=
```

字符串比较：

```
=
!=
<
>
-n s1 # s1 is not empty
-z s1 # s1 is empty
```

### 文件测试

这个也算是 Bash 的特色了。它也是用做逻辑判断的。

|Expression|Description|
|:-:|:-:|
|-b filename|Block special file|
|-c filename|Special character file|
|-d dirname|Check for directory existence|
|-e filename|Check for file existence|
|-f filename|Check for regular file existence not a directory|
|-G filename|Check if file exists and is owned by effective group ID|
|-g filename|true if file exists and is set-group-id|
|-k filename|Sticky bit|
|-L filename|Symbolic link|
|-O filename|True if file exists and is owned by the effective user id|
|-r filename|Check if file is a readable|
|-S filename|Check if file is socket|
|-s filename|Check if file is nonzero size|
|-u filename|Check if file set-user-id bit is set|
|-w filename|Check if file is writable|
|-x filename|Check if file is executable|

```
myfile="./config.txt"

while [ ! -e $myfile ]; do
# Sleep until file does exists/is created
sleep 1
done
```

注意，这里它用了`!`来表示否定。

### 循环语句

`while`

```
while [ xxx ]; do
	...
done
```

`for`

```
for f in $( ls /var/ ); do
	echo $f
done
```

如果在命令行中按一行输入，则：

```
for f in $( ls /var/ ); do echo $f; done
```

`until`

```
COUNT=0
until [ $COUNT -gt 5 ]; do
	echo Value of count is: $COUNT
    let COUNT=COUNT+1
```

注意上面有一个`let`，它用作整数运算。不加`let`会出错。

看下面一个很有趣的文件名批量替换的例子：

```
DIR="."
find $DIR -type f | while read file; do
	if [[ "$file" = *[[:space:]]* ]]; then
    	mv "$file" `echo $file | tr ' ' '_'`
    fi;
done
```

把当前目录下所有文件的名字中的空格替换为下划线。

为什么这里的`if`用了`[[  ]]`？

`*[[:space:]]*`又是什么？

### 数组

```
#Declare array with 4 elements
ARRAY=( 'Debian Linux' 'Redhat Linux' Ubuntu Linux )
# get number of elements in the array
ELEMENTS=${#ARRAY[@]}

# echo each element in array 
# for loop
for (( i=0;i<$ELEMENTS;i++ )); do
    echo ${ARRAY[${i}]}
done 
```

上面有数组定义、数组计数和数组元素引用的例子。`for`循环中对变量`i`的引用时`${i}`，但是`$i`也是可以的。

**从文件中读取数据到数组**

```
# Declare array
declare -a ARRAY
# Link filedescriptor 10 with stdin
exec 10<&0
# stdin replaced with a file supplied as a first argument
exec < $1
let count=0
while read LINE; do

    ARRAY[$count]=$LINE
    ((count++))
done
echo Number of elements: ${#ARRAY[@]}
# echo array's content
echo ${ARRAY[@]}
# restore stdin from filedescriptor 10
# and close filedescriptor 10
exec 0<&10 10<&-
```

这里`exec`是干嘛的？

### 脚本参数

```
# ./test.sh
echo $0 $1 $2 $3
# root:~# ./test.sh ab cd ef
```

另外，`$@`是除`$0`外的参数组合：

```
args=("$@")
echo ${args[0]} ${args[1]} ${args[2]}
echo $@
```

`$#`是传入的参数个数（不算`$0`）。

### 变量

```
# 执行命令并返回它的标准输出
echo $(date)
echo `date`
```

```
# 注意等号两边不要有空格
STRING="hello, world"
STRING=myhome_$(date +%Y%m%d).tar.gz
echo $STRING
```

全局和局部：

```
# global and can be used anywhere in this bash script
VAR="global variable"
function bash {
# Define bash local variable
# This variable is local to bash function only
	local VAR="local variable"
	echo $VAR
}
echo $VAR
bash
# Note the bash global variable did not change
# "local" is bash reserved word
echo $VAR
```

### 读取用户输入

```
echo -e "Hi, please type the word: \c "
read  word
echo "The word you entered is: $word"
echo -e "Can you please enter two words? "
read word1 word2
echo "Here is your input: \"$word1\" \"$word2\""
```

如果你在`read`后没有给出接受内容的变量，则它们被存到了内置的缺省变量`$REPLY`中。

```
echo -e "How do you feel about bash scripting? "
read
echo "You said $REPLY, I'm glad to hear that! "
```

加`-a`则会把所有内容读入一个数组。

```
echo -e "What are your favorite colours ? "
read -a colours
echo "My favorite colours are also ${colours[0]}, ${colours[1]} and ${colours[2]}:-)"
```

### 函数

注意函数名与`{`之间有空格。

```
function func {
	echo $1
}

func "Hello, world"
```

### 信号捕获

Bash 还可以捕获信号！

```
# bash trap command
trap bashtrap INT
# bash trap function is executed when CTRL-C is pressed:
bashtrap()
{
    echo "CTRL+C Detected !...executing bash trap !"
}
# for loop from 1/10 to 10/10
for a in `seq 1 10`; do
    echo "$a/10 to Exit." 
    sleep 1;
done
echo "Exit Bash Trap Example!!!" 
```

另外，上面的`seq 1 10`是生成数字。

### Bash Select

```
PS3='Choose one word: '
select word in "Linux" "Windows" "Mac OS"
do
	echo "Your choose: $word"
    break
done
exit 0
```

注意那个`break`，没有它就会无限循环。

### 参考资料

- [Bash scripting Tutorial](https://linuxconfig.org/bash-scripting-tutorial)