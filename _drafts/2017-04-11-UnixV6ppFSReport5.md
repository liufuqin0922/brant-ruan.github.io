---
title: Unix v6-plus-plus Filesystem Analysis | Part 5
category: CS
---

## Unix v6-plus-plus Filesystem Analysis | Part 5

### 0x05 Instance Analysis

In this part, we will analyse an example based on knowledge we have learnt.

{% highlight c %}
main()
{
	int fd = open("/usr/ast/Jerry", O_RDONLY);
	char data[500] = "abcde……………";
	……;
	seek(fd, 4500, 0);
	read(fd, data, 500);
	write(fd, data, 500);
	……;
}
{% endhighlight %}

### 0x06 Summary
