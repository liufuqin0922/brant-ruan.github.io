<ul>
    <li>
      <a href="{{ site.url/Daily }}">
    </li>

  {% for post in site.posts %}

    <li>

      <a href="{{ post.url }}">{{ post.date | date_to_string }} &gt;&gt; {{ post.title }}</a>

    </li>

  {% endfor %}

</ul>