<h2>Life</h2>

<ul>

  {% for post in site.categories.Life %}

    <li>

      <a href="{{ post.url }}">{{ post.title }}</a>

    </li>

  {% endfor %}

</ul>

<h2>Sec</h2>

<ul>

  {% for post in site.categories.Sec %}

    <li>

      <a href="{{ post.url }}">{{ post.title }}</a>

    </li>

  {% endfor %}

</ul>

<h2>Linux</h2>

<ul>

  {% for post in site.categories.Linux %}

    <li>

      <a href="{{ post.url }}">{{ post.title }}</a>

    </li>

  {% endfor %}

</ul>

<h2>CS</h2>

<ul>

  {% for post in site.categories.CS %}

    <li>

      <a href="{{ post.url }}">{{ post.title }}</a>

    </li>

  {% endfor %}

</ul>

<h2>Tools</h2>

<ul>

  {% for post in site.categories.Tools %}

    <li>

      <a href="{{ post.url }}">{{ post.title }}</a>

    </li>

  {% endfor %}

</ul>

<h2>Essay</h2>

<ul>

  {% for post in site.categories.Essay %}

    <li>

      <a href="{{ post.url }}">{{ post.title }}</a>

    </li>

  {% endfor %}

</ul>

<h2>Poem</h2>

<ul>

  {% for post in site.categories.Poem %}

    <li>

      <a href="{{ post.url }}">{{ post.title }}</a>

    </li>

  {% endfor %}

</ul>

<h2>Other</h2>

<ul>

  {% for post in site.categories.Other %}

    <li>

      <a href="{{ post.url }}">{{ post.title }}</a>

    </li>

  {% endfor %}

</ul>