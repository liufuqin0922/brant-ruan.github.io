## Hello, world


```c
#include <stdio.h>

int main()
{
	printf("Welcome to my blog\n");
	printf("by brant-ruan\n");
	printf("Just hack[ing]\n");
	printf(":)\n");

	return 0;
}

```

<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url }}">{{ post.title }}</a>
    </li>
  {% endfor %}
</ul>